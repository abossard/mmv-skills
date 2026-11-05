#!/usr/bin/env python3
"""Check a .magic project, optionally load it into the RUNNING Magic and prove it renders.

    python3 mmv_verify.py FILE                      # static check only (safe)
    python3 mmv_verify.py FILE --live --yes         # + load in Magic, look for error dialogs, grab a frame over Syphon
    python3 mmv_verify.py FILE --live --yes --restore   # + reopen the project that was open before
    python3 mmv_verify.py FILE --live --yes --osc /addr=0.8 --osc-port 17011   # send OSC while grabbing

--live needs --yes (or MMV_ALLOW_LIVE=1): it replaces whatever project Magic has open, so the person
using Magic must have agreed first.

Magic is a single-instance app: --live REPLACES the open project (no save prompt appears for a
clean project; if one does, the run stops). Ask the user first, never run it while they perform.
--restore reopens the old project afterwards; it needs that project saved with a file name that is
unique among Magic's recent files, and --live --restore refuses to start when Magic cannot tell.
The Syphon server name comes from the project (videoSharingName, default "Main Server").
Exit code 1 = static errors, 2 = live failure. Needs syphon-python for the grab (magicproj re-runs
itself under python3.13, see SYPHON_PYTHON) and the terminal allowed under macOS Privacy & Security >
Accessibility and Automation (Magic is driven through System Events).
"""
import argparse
import os
import socket
import struct
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import magicproj as m  # noqa: E402

ERROR_WORDS = ("error", "could not", "failed", "warning", "invalid", "missing")


def osc_packet(addr, val):
    pad = lambda b: b + b"\0" * (-len(b) % 4)
    return pad(addr.encode() + b"\0") + pad(b",f\0") + struct.pack(">f", val)


def osc_stream(addr, val, port, seconds):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end = time.time() + seconds
    while time.time() < end:
        sock.sendto(osc_packet(addr, val), ("127.0.0.1", port))
        time.sleep(0.03)


def dismiss_dialogs(names):
    """Close Magic's error/warning dialogs with Return (they expose no accessible buttons).
    Brings Magic to the front first and stops with RuntimeError if it does not get there."""
    for _ in names:
        m.press("key code 36")
        time.sleep(0.4)


def grab_json(server, out, wait):
    """magicproj grab runs under python3.13 with syphon-python when this interpreter lacks it."""
    import json
    import subprocess
    argv = [sys.executable, os.path.join(HERE, "magicproj.py"), "grab", "--server", server, "--wait", "0", "--timeout", str(wait)]
    if out:
        argv += ["--out", out]
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip().splitlines() or ["grab failed"])[-1])
    return json.loads(r.stdout)


def current_project_path():
    """(name, path) of the project open in Magic now, from the editor title + the app's recent files;
    (None, None) when none is open. The path is None unless exactly one existing recent file has that name."""
    wins = m.magic_windows() or []
    title = next((w for w in wins if " - Editor" in w), None)
    if not title:
        return None, None
    base = title.split(" - Editor")[0]
    paths = set()
    if os.path.exists(m.MAGIC_PREFS):
        for f in m.ET.parse(m.MAGIC_PREFS).iter("file"):          # recentFiles holds <file name=...>
            n = f.get("name") or ""
            if os.path.basename(n) == base and os.path.exists(n):
                paths.add(n)
    return base, (paths.pop() if len(paths) == 1 else None)


def restore(a, before):
    if not (a.restore and before):
        return
    try:
        ok, _ = m.load(before, timeout=25)
    except RuntimeError as e:
        print("live: could not restore %s: %s" % (before, e))
        return
    print("live: restored %s" % before if ok else "live: could NOT confirm that %s is open again; check Magic's windows" % before)


def grab_live(a, server, osc):
    """Optionally play the audio file, send OSC, grab frames. -> exit code."""
    playing = False
    try:
        if a.play:
            m.toggle_playback()
            playing = True
            time.sleep(1.5)
        for addr, val in osc:
            threading.Thread(target=osc_stream, args=(addr, val, a.osc_port, a.wait + 6), daemon=True).start()
        time.sleep(1.0)
        res = None
        for k in range(max(1, a.frames)):
            out = a.out if a.frames == 1 or not a.out else "%s.%d.png" % (os.path.splitext(a.out)[0], k)
            r = grab_json(server, out, a.wait if k == 0 else 3)
            print("live: frame %d mean_rgb=%s lit=%s" % (k, r.get("mean_rgb"), r.get("lit")))
            if res is None or sum(r.get("mean_rgb") or [0]) > sum(res.get("mean_rgb") or [0]):
                res = r
            time.sleep(0.6)
        print("live: frame %s mean_rgb=%s lit=%s" % (res.get("size"), res.get("mean_rgb"), res.get("lit")))
        if res.get("png"):
            print("live: png", res["png"])
        if (res.get("lit") or 0) < 0.002:
            print("live: frame is black")
            return 2
        return 0
    except Exception as e:          # noqa: BLE001
        print("live: no frame:", e)
        return 2
    finally:
        if playing:
            try:
                m.toggle_playback()
            except RuntimeError as e:
                print("live: could not stop playback:", e)


def live(a, server, osc):
    name, before = current_project_path()
    if a.restore and name and not before:
        print("live: cannot tell which file '%s' was loaded from (not saved, moved, or two recent files share the name), "
              "so it could not be reopened afterwards. Save it first, or drop --restore to replace it anyway." % name)
        return 2
    if name:
        print("live: replacing %s%s" % (before or name, "" if a.restore else " (no --restore, it stays replaced)"))
    try:
        ok, wins = m.load(a.file, timeout=25)
        print("live: windows:", wins)
        if not ok:
            print("live: FAILED, the editor never named the project (a dialog may be open)")
            return 2
        bad = [w for w in wins if " - Editor" not in w and any(k in w.lower() for k in ERROR_WORDS)]
        if bad:
            print("live: error/warning dialogs:", bad)
            if a.dismiss:
                dismiss_dialogs(bad)
            return 2
        return grab_live(a, server, osc)
    finally:
        restore(a, before)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--yes", action="store_true", help="confirm that replacing the project open in Magic is fine (also MMV_ALLOW_LIVE=1)")
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--out", help="PNG path for the grabbed frame")
    ap.add_argument("--wait", type=float, default=10)
    ap.add_argument("--osc", action="append", default=[], help="/addr=value, sent for the whole grab (needs --osc-port)")
    ap.add_argument("--osc-port", type=int)
    ap.add_argument("--dismiss", action="store_true", help="click away error/warning dialogs it reports")
    ap.add_argument("--frames", type=int, default=1,
                    help="grab N frames 0.6 s apart and keep the brightest (audio reactive scenes); with --out X.png and N>1 "
                         "they are written to X.0.png, X.1.png, ...")
    ap.add_argument("--play", action="store_true", help="toggle audio file playback (Shift+Cmd+Space) before the grab")
    a = ap.parse_args()
    osc = []
    for spec in a.osc:
        addr, _, val = spec.partition("=")
        try:
            osc.append((addr, float(val)))
        except ValueError:
            ap.error("--osc expects /addr=value, got %r" % spec)
    if osc and a.osc_port is None:
        ap.error("--osc needs --osc-port")

    try:
        root = m.read(a.file)
    except (OSError, ValueError, m.zlib.error, m.ET.ParseError) as e:
        print("error: cannot read %s as a .magic project: %s" % (a.file, e))
        return 1
    issues = m.check(root, os.path.dirname(os.path.abspath(a.file)))
    for level, msg in issues:
        print("%s: %s" % (level, msg))
    errors = [i for i in issues if i[0] == "error"]
    print("static: %d errors, %d warnings" % (len(errors), len(issues) - len(errors)))
    if errors:
        return 1
    if not a.live:
        return 0

    if not (a.yes or os.environ.get("MMV_ALLOW_LIVE") == "1"):
        print("live: --live replaces the project open in Magic. Ask the person using Magic, then add --yes "
              "(or set MMV_ALLOW_LIVE=1). Nothing was loaded.")
        return 2
    server = root.get("videoSharingName") or "Main Server"
    if root.get("videoSharing") != "1":
        print("live: videoSharing is off, cannot grab a frame; enable it with Builder(syphon=NAME) or `magicproj set --syphon on`")
        return 2
    try:
        return live(a, server, osc)
    except RuntimeError as e:
        print("live:", e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
