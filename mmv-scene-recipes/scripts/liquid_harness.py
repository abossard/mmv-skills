#!/usr/bin/env python3
"""Dev harness for the Liquid looks: build, static checks, live run in Magic, judge.

    python3 liquid_harness.py static [--looks A,C]              build + isf_lint + glslang compile + project check
    python3 liquid_harness.py live LOOK --yes [--seconds 50]    load into the RUNNING Magic (replaces its project),
                                                         play the test track, capture Syphon + OSC probe
    python3 liquid_harness.py report LOOK                       sheets vs reference frames, FPS, kick reaction
    python3 liquid_harness.py all LOOK --yes                    static + live + report
    python3 liquid_harness.py restore PATH                      reopen a project in Magic

Outputs in $LIQUID_WORK (default ./liquid-work)/<LOOK>/: Liquid<LOOK>.magic, capture.json, osc.json, f_*.png,
sheet.png, motion.png, report.json. Reference videos: $LIQUID_VIDEOS (see liquid_refs.py).
Test track: <work>/track126.wav, made by music_xray_testtrack.py when missing (126 BPM: intro 0-7.6 s, buildup to 22.9 s, drop to 45.7 s,
breakdown to 60.9 s, buildup to 76.2 s, drop to 91.4 s).
"""
import argparse
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("LIQUID_WORK", os.path.join(os.getcwd(), "liquid-work"))      # captures, sheets, test projects
SKILLS = os.environ.get("MMV_SKILLS", os.path.abspath(os.path.join(HERE, "..", "..")))
sys.path.insert(0, os.path.join(SKILLS, "mmv-core", "scripts"))
sys.path.insert(0, HERE)
import magicproj as m  # noqa: E402
import liquid_example as build_liquid  # noqa: E402
import liquid_refs as refs  # noqa: E402

_windows = m.magic_windows


def _windows_retry():
    """Magic's window list can change while System Events walks it ('Invalid index'): retry."""
    for k in range(6):
        try:
            return _windows()
        except RuntimeError as e:
            if "Invalid index" not in str(e) or k == 5:
                raise
            time.sleep(0.3)


m.magic_windows = _windows_retry


def toggle_playback(tries=4):
    """Shift+Cmd+Space in Magic; magicproj.press gives Magic 3 s to come to the front, which can miss while the
    user works in another app, so retry."""
    for k in range(tries):
        try:
            return m.toggle_playback()
        except RuntimeError:
            if k == tries - 1:
                raise
            time.sleep(0.5)

PORT = 9310
SYPHON = "Liquid"
TRACK = os.path.join(OUT, "track126.wav")


def ensure_track():
    if not os.path.exists(TRACK):
        os.makedirs(OUT, exist_ok=True)
        subprocess.run([sys.executable, os.path.join(HERE, "music_xray_testtrack.py"), TRACK], check=True)
SYPHON_PY = os.environ.get("SYPHON_PYTHON", "python3.13")
SYPHON_PATH = os.environ.get("SYPHON_PYTHONPATH", os.path.expanduser("~/.local/lib/python3.13/site-packages"))
PNG_AT = [16.0, 24.0, 27.5, 31.0, 36.0, 42.0]          # buildup, then the first drop
SEQ = "28.0,2.0,10"                                    # 2 s of the drop at 10 fps for the motion strip
UNIFORM = {"float": "float", "bool": "bool", "long": "int", "event": "bool", "point2D": "vec2", "color": "vec4",
           "image": "sampler2D", "audio": "sampler2D", "audioFFT": "sampler2D"}


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---- static -----------------------------------------------------------------

def glsl_wrap(fs_path):
    """ISF -> plain GLSL 1.20 fragment shader for glslangValidator."""
    with open(fs_path) as fh:
        text = fh.read()
    header, end = m.isf_header(text)
    body = text[end:]
    decl = ["#version 130",          # 130: Magic 3.0b6 accepts isnan/isinf (measured), 1.20 has none
            "uniform float TIME; uniform float TIMEDELTA; uniform vec2 RENDERSIZE; uniform int PASSINDEX; uniform int FRAMEINDEX;",
            "uniform vec4 DATE; varying vec2 isf_FragNormCoord;",
            "#define IMG_NORM_PIXEL(i, c) texture2D(i, c)",
            "#define IMG_PIXEL(i, c) texture2D(i, (c) / RENDERSIZE)",
            "#define IMG_SIZE(i) RENDERSIZE"]
    for i in header.get("INPUTS", []):
        decl.append("uniform %s %s;" % (UNIFORM[i["TYPE"]], i["NAME"]))
    for t in dict.fromkeys(p["TARGET"] for p in header.get("PASSES", []) if p.get("TARGET")):
        decl.append("uniform sampler2D %s;" % t)
    return "\n".join(decl) + "\n" + body, len(decl), text[:end].count("\n")


def static(looks):
    ok = True
    os.makedirs(OUT, exist_ok=True)
    proj = os.path.join(OUT, "static.magic")
    mm, root = build_liquid.build(SKILLS, looks, SYPHON, (1920, 1080), 60, None, PORT, [TRACK] if os.path.exists(TRACK) else [])
    mm.write(proj, root)
    for look in looks:
        fs = os.path.join(build_liquid.OUT_ISF, "Liquid%s.fs" % look)
        r = sh([sys.executable, os.path.join(SKILLS, "mmv-shaders-isf-glsl", "scripts", "isf_lint.py"), fs])
        print(r.stdout.strip().splitlines()[-1])
        ok &= r.returncode == 0
        with open(fs) as fh:
            tg = [p.get("TARGET") for p in m.isf_header(fh.read())[0].get("PASSES", []) if p.get("TARGET")]
        with open(fs) as fh:
            persist = {p.get("TARGET") for p in m.isf_header(fh.read())[0].get("PASSES", []) if p.get("PERSISTENT")}
        lost = {"ctl", "vel", "dye"} - persist
        if lost:                         # a lost PERSISTENT flag shows as flicker, then black (happened to look A)
            print("Liquid%s: buffers not persistent: %s" % (look, ", ".join(sorted(lost))))
            ok = False
        if len(tg) != len(set(tg)):      # measured in Magic 3.0b6: "'X' may not be redeclared"
            print("Liquid%s: repeated pass TARGET (Magic declares one uniform per pass)" % look)
            ok = False
        with open(fs) as fh:
            code = fh.read()
        hd = m.isf_header(code)[0]
        images = {i["NAME"] for i in hd.get("INPUTS", []) if i["TYPE"] in ("image", "audio", "audioFFT")} | set(tg)
        used = images & set(re.findall(r"IMG_(?:NORM_PIXEL|PIXEL|SIZE)\s*\(\s*(\w+)", code))
        if len(used) > 16:      # measured in Magic 3.0b6: 17+ sampled buffers -> the module draws nothing, no dialog
            print("Liquid%s: samples %d buffers, Magic draws nothing above 16" % (look, len(used)))
            ok = False
        else:
            print("Liquid%s: %d sampled buffers (max 16)" % (look, len(used)))
        src, pre, hdr = glsl_wrap(fs)
        frag = os.path.join(OUT, "Liquid%s.frag" % look)
        with open(frag, "w") as fh:
            fh.write(src)
        r = sh(["glslangValidator", "-l", frag])      # -l links: a declared-but-undefined function makes Magic draw black, no dialog
        errs = [l for l in r.stdout.splitlines() if "ERROR" in l]
        for l in errs[:12]:      # map wrapper lines back to .fs lines
            mt = re.search(r":(\d+):", l)
            print("  ", l, "(fs line %d)" % (int(mt.group(1)) - pre + hdr) if mt else "")
        print("Liquid%s glslang: %s" % (look, "ok" if r.returncode == 0 else "%d errors" % len(errs)))
        ok &= r.returncode == 0
    r = sh([sys.executable, os.path.join(SKILLS, "mmv-core", "scripts", "mmv_verify.py"), proj])
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    ok &= r.returncode == 0
    return ok


# ---- live -------------------------------------------------------------------

def current_project():
    sys.path.insert(0, os.path.join(SKILLS, "mmv-core", "scripts"))
    import mmv_verify
    return mmv_verify.current_project_path()


def osc_listen(port, log, stop):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", port))
    s.settimeout(0.1)
    while not stop.is_set():
        try:
            data, _ = s.recvfrom(65535)
        except socket.timeout:
            continue
        now = time.time()
        try:
            for addr, _t, args, _b in m.parse_packet(data):
                log.append((now, addr.split("/")[-1], args[0] if args else None))
        except Exception:      # noqa: BLE001
            pass
    s.close()


def live(look, seconds, size=(1920, 1080), fps=60, params=None, tag=None, debug=False, manual=False):
    ensure_track()
    d = os.path.join(OUT, tag or look)
    os.makedirs(d, exist_ok=True)
    for fn in os.listdir(d):
        if fn.startswith("f_"):
            os.remove(os.path.join(d, fn))
    name, before = current_project()
    print("magic had open:", before or name)
    mm, root = build_liquid.build(SKILLS, [look], SYPHON, size, fps, None, PORT, [TRACK], look, params, debug)
    proj = os.path.join(d, "Liquid%s.magic" % look)
    mm.write(proj, root)
    ok, wins = m.load(proj, timeout=25)
    bad = [w for w in wins if " - Editor" not in w and any(k in w.lower() for k in ("error", "warning", "could not"))]
    print("loaded:", ok, "windows:", wins)
    if not ok or bad:
        print("load failed or dialogs:", bad)
        return False
    time.sleep(2.0)
    log, stop = [], threading.Event()
    th = threading.Thread(target=osc_listen, args=(PORT, log, stop))
    th.start()
    env = dict(os.environ, PYTHONPATH=SYPHON_PATH)
    def loud(since, until):
        return max([v for t, n, v in log if n == "Volume" and since <= t <= until] or [0.0]) > 0.01
    if manual:                      # someone presses Play in Magic's Input Sources window; timestamps start at the first level
        print("READY: press Play now", flush=True)
        end = time.time() + 40
        while time.time() < end and not loud(time.time() - 1.0, time.time()):
            time.sleep(0.05)
        t_play = min([t for t, n, v in log if n == "Volume" and v > 0.01] or [time.time()]) - 0.3
    else:
        # Magic keeps the play state across loads: pause first if the track is already running
        time.sleep(1.5)
        if loud(time.time() - 1.2, time.time()):
            print("audio was already playing: pausing first")
            toggle_playback()
            time.sleep(1.5)
        for attempt in range(3):         # a keystroke can get lost right after a load: retry until a level arrives
            toggle_playback()
            t_play = time.time()
            time.sleep(2.0)
            if loud(t_play + 0.3, time.time()):
                break
            print("no audio level after play (attempt %d)" % (attempt + 1))
            if loud(time.time() - 3.0, time.time()):
                break
    cap = subprocess.Popen([SYPHON_PY, os.path.join(HERE, "liquid_capture.py"), SYPHON, str(seconds), d,
                            "--png", ",".join(str(t) for t in PNG_AT), "--seq", SEQ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = cap.communicate(timeout=seconds + 60)
    alive = bool(m.magic_windows())
    if manual:
        print("DONE: press Pause now", flush=True)
    elif alive:
        try:
            toggle_playback()
        except RuntimeError as e:
            print("could not stop playback:", e)
    else:
        print("MAGIC IS GONE after the capture (quit or crashed)")
    stop.set()
    th.join()
    print("capture:", out.strip(), err.strip()[-300:])
    with open(os.path.join(d, "osc.json"), "w") as fh:
        json.dump({"play": t_play, "before": before, "msgs": log}, fh)
    cj = json.load(open(os.path.join(d, "capture.json")))
    w, h, stride = cj["size"]
    for fn in os.listdir(d):
        if fn.startswith("s_") and fn.endswith(".png"):
            os.remove(os.path.join(d, fn))
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".bgra"):
            src = os.path.join(d, fn)
            sh(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "%dx%d" % (w, h), "-i", src,
                "-vf", "vflip,format=rgb24", "-frames:v", "1", src.replace(".bgra", ".png")])
            os.remove(src)
    return True


# ---- report -----------------------------------------------------------------

def sheet(look, d):
    ours = sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("f_") and f.endswith(".png"))
    theirs = refs.frames()[look]
    imgs = (theirs[:6] + ours[:6])
    if len(imgs) < 12:
        return None
    args = []
    for p in imgs:
        args += ["-i", p]
    lay = "|".join("%d_%d" % (640 * (k % 3), 360 * (k // 3)) for k in range(12))
    fc = "".join("[%d]scale=640:360:force_original_aspect_ratio=increase,crop=640:360[v%d];" % (k, k) for k in range(12))
    fc += "".join("[v%d]" % k for k in range(12)) + "xstack=inputs=12:layout=%s" % lay
    out = os.path.join(d, "sheet.png")
    sh(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", fc, "-frames:v", "1", out])
    return out


def motion(look, d):
    """20 consecutive frames at 10 fps (ours) and the same from the reference video -> motion.png (top: reference)."""
    ours = sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("s_") and f.endswith(".png"))[:20]
    if len(ours) < 20:
        return None
    video, t = refs.REFS[look][refs.MOTION[look]]
    os.makedirs(refs.WORK, exist_ok=True)
    ref_strip = os.path.join(refs.WORK, "motion_%s.png" % look)
    if not os.path.exists(ref_strip):
        refs.strip(video, t, ref_strip)
    our_strip = os.path.join(d, "motion_ours.png")
    args = []
    for p in ours:
        args += ["-i", p]
    lay = "|".join("%d_%d" % (384 * (k % 5), 216 * (k // 5)) for k in range(20))
    fc = "".join("[%d]scale=384:216[v%d];" % (k, k) for k in range(20)) + "".join("[v%d]" % k for k in range(20))
    sh(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", fc + "xstack=inputs=20:layout=" + lay, "-frames:v", "1", our_strip])
    out = os.path.join(d, "motion.png")
    sh(["ffmpeg", "-v", "error", "-y", "-i", ref_strip, "-i", our_strip, "-filter_complex", "[0][1]vstack", out])
    return out


QW, QH = 160, 90


def _raw_frames(args):
    """ffmpeg args producing frames -> list of rgb24 byte strings at QWxQH."""
    out = subprocess.run(["ffmpeg", "-v", "error"] + args + ["-vf_placeholder"], capture_output=True).stdout if False else \
        subprocess.run(["ffmpeg", "-v", "error"] + args, capture_output=True).stdout
    n = QW * QH * 3
    return [out[i:i + n] for i in range(0, len(out) - n + 1, n)]


def frame_stats(frames):
    """Look and motion numbers for a list of rgb24 frames at 10 fps (cuts, frames changing > 3x the median, skipped)."""
    import math
    col, luma, dark, si, ti = [], [], [], [], []
    prev = None
    for f in frames:
        r, g, b = f[0::3], f[1::3], f[2::3]
        n = len(r)
        y = [0.299 * r[i] + 0.587 * g[i] + 0.114 * b[i] for i in range(n)]
        rg = [r[i] - g[i] for i in range(n)]
        yb = [0.5 * (r[i] + g[i]) - b[i] for i in range(n)]
        mrg, myb = sum(rg) / n, sum(yb) / n
        srg = math.sqrt(sum((v - mrg) ** 2 for v in rg) / n)
        syb = math.sqrt(sum((v - myb) ** 2 for v in yb) / n)
        col.append(math.sqrt(srg ** 2 + syb ** 2) + 0.3 * math.sqrt(mrg ** 2 + myb ** 2))   # Hasler-Suesstrunk
        luma.append(sum(y) / n)
        dark.append(sum(1 for v in y if v < 20) / n)
        si.append(sum(abs(y[i + 1] - y[i]) + abs(y[i + QW] - y[i]) for i in range(n - QW - 1) if (i + 1) % QW) / n)
        if prev is not None:
            ti.append(sum(abs(y[i] - prev[i]) for i in range(n)) / n)
        prev = y
    med = sorted(ti)[len(ti) // 2] if ti else 0
    ti = [v for v in ti if v <= 3 * med + 1] or [0]
    mean = lambda v: sum(v) / max(1, len(v))
    tm = mean(ti)
    steady = math.sqrt(mean([(v - tm) ** 2 for v in ti])) / tm if tm else 0
    return {"colourfulness": round(mean(col), 1), "luma": round(mean(luma), 1), "dark_share": round(mean(dark), 2),
            "spatial_detail": round(mean(si), 1), "temporal_change": round(tm, 2), "change_unsteadiness": round(steady, 2)}


def quality(look, d):
    """Our 10 fps sequence vs 2 s of the reference at 10 fps."""
    ours = sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("s_") and f.endswith(".png"))[:20]
    if len(ours) < 5:
        return None
    of = []
    for p in ours:
        of += _raw_frames(["-i", p, "-vf", "scale=%d:%d" % (QW, QH), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    video, t = refs.REFS[look][refs.MOTION[look]]
    rf = _raw_frames(["-ss", str(t), "-t", "2", "-i", os.path.join(refs.VID, video), "-vf",
                      "fps=10,%s,scale=%d:%d" % (refs.vf(video, 640), QW, QH), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return {"ours": frame_stats(of), "reference": frame_stats(rf)}


def reaction(d):
    cj = json.load(open(os.path.join(d, "capture.json")))
    oj = json.load(open(os.path.join(d, "osc.json")))
    t_play = oj["play"]
    drops = [t - t_play for t, n, v in oj["msgs"] if n == "DropPulse" and v > 0.5 and t - t_play > 10]
    if drops:                         # the playback position may not start at 0: align to the first real drop
        t_play += drops[0] - 22.86
    res_offset = round(drops[0] - 22.86, 2) if drops else None
    fr = [(t - t_play, bytes.fromhex(g)) for t, g in cj["frames"]]
    diffs = []
    for (t0, a), (t1, b) in zip(fr, fr[1:]):
        diffs.append((t1, sum(abs(x - y) for x, y in zip(a, b)) / len(a)))
    kicks, last = [], None
    fps = []
    for t, name, v in oj["msgs"]:
        if name == "KickCount":
            if last is not None and v > last:
                kicks.append(t - t_play)
            last = v
        elif name == "Fps":
            fps.append((t - t_play, v))
    drop_kicks = [k for k in kicks if 23.5 < k < 45.0]
    bins = [i / 60.0 for i in range(-12, 37)]               # -0.2 .. +0.6 s
    def window(k):
        return [max((dv for t, dv in diffs if k + b - 1 / 120 <= t < k + b + 1 / 120), default=None) for b in bins]
    acc = [[] for _ in bins]
    hits = 0
    for k in drop_kicks:
        wv = window(k)
        for i, v in enumerate(wv):
            if v is not None:
                acc[i].append(v)
        pre = [v for b, v in zip(bins, wv) if v is not None and -0.2 <= b < 0.0]
        post = [v for b, v in zip(bins, wv) if v is not None and 0.0 <= b <= 0.25]
        if pre and post and max(post) > 1.5 * (sum(pre) / len(pre)):
            hits += 1
    avg = [sum(a) / len(a) if a else 0 for a in acc]
    base = sorted(dv for t, dv in diffs if 23.5 < t < 45.0)
    base = base[len(base) // 2] if base else 0
    peak = max(range(len(avg)), key=lambda i: avg[i]) if avg else 0
    span = fr[-1][0] - fr[0][0] if len(fr) > 1 else 0
    fv = [v for t, v in fps if t > 3]
    res = {"track_offset_s": res_offset, "syphon_fps": round((len(fr) - 1) / span, 1) if span else 0,
           "graphics_fps": {"n": len(fv), "min": min(fv) if fv else None, "median": sorted(fv)[len(fv) // 2] if fv else None,
                            "max": max(fv) if fv else None},
           "kicks_in_drop": len(drop_kicks), "kick_hits": hits,
           "diff_median_drop": round(base, 2), "kick_avg_peak": round(avg[peak], 2) if avg else 0,
           "kick_peak_ratio": round(avg[peak] / base, 2) if base else None, "kick_peak_lag_ms": round(bins[peak] * 1000),
           "kick_profile": [round(v, 2) for v in avg[::3]]}
    sections = {"intro": (1, 7.6), "buildup": (8, 22.9), "drop": (23.5, 45.7), "breakdown": (46, 60.9)}
    res["diff_by_section"] = {k: round(sum(dv for t, dv in diffs if a <= t < b) / max(1, sum(1 for t, _ in diffs if a <= t < b)), 2)
                              for k, (a, b) in sections.items()}
    return res


def report(look, tag=None):
    d = os.path.join(OUT, tag or look)
    res = reaction(d)
    res["sheet"] = sheet(look, d)
    res["motion"] = motion(look, d)
    res["quality"] = quality(look, d)
    with open(os.path.join(d, "report.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["static", "live", "report", "all", "restore"])
    ap.add_argument("look", nargs="?")
    ap.add_argument("--looks", default="A,C")
    ap.add_argument("--seconds", type=float, default=50)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--tag")
    ap.add_argument("--manual-play", action="store_true", help="wait for Play pressed in Magic instead of the keyboard shortcut")
    ap.add_argument("--debug", action="store_true", help="render a tile view of every buffer instead of the look")
    ap.add_argument("--yes", action="store_true", help="the person using Magic agreed that its project gets replaced")
    a = ap.parse_args()
    size = tuple(int(v) for v in a.size.split("x"))
    if a.cmd == "restore":
        print(m.load(a.look, timeout=25))
        return 0
    if a.cmd in ("static", "all") and not static(a.looks.split(",") if a.cmd == "static" else [a.look]):
        return 1
    if a.cmd in ("live", "all"):
        if not a.yes:
            print("live replaces the project open in Magic; ask first, then pass --yes")
            return 2
        if not live(a.look, a.seconds, size, a.fps, tag=a.tag, debug=a.debug, manual=a.manual_play):
            return 2
    if a.cmd in ("report", "all"):
        report(a.look, a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
