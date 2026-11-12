"""Live check in Magic: build a probe project (first scene SCENE) that plays WAV, load it into the RUNNING Magic,
log the /xray/* OSC probe with timestamps for SECONDS and grab Syphon frames at the given seconds.

    python3 music_xray_probe.py WAV SCENE SECONDS GRAB_AT[,GRAB_AT...]     # writes XRayProbe_SCENE.magic, probe_scene.json, scene_NNN.png

Loading replaces the project open in Magic: ask whoever uses Magic first. Test track: music_xray_testtrack.py."""
import json, os, socket, subprocess, sys, threading, time
WAV, SCENE, SECS, GRABS = os.path.abspath(sys.argv[1]), sys.argv[2], float(sys.argv[3]), [float(x) for x in sys.argv[4].split(",") if x]
HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, SK + "/mmv-core/scripts")
import music_xray_example as build_xray
m, root = build_xray.build(SK, "MusicXRay", (1920, 1080), None, probe_port=9300)
root = m.add_audio(root, WAV, source="Source 0", loop=False)
order = ["Pulse", "Terrain", "Tempo"]; i = order.index(SCENE)
root = m.set_playlist(root, names=order[i:] + order[:i], seconds=3600)
proj = os.path.abspath("XRayProbe_%s.magic" % SCENE); m.write(proj, root)
assert not [p for p in m.check(root, ".") if p[0] == "error"]
MP = SK + "/mmv-core/scripts/magicproj.py"
print(subprocess.run([sys.executable, MP, "load", proj], capture_output=True, text=True).stdout.strip()[-300:])
time.sleep(6)
log = []
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.bind(("127.0.0.1", 9300)); sock.settimeout(0.2)
stop = False
def rx():
    while not stop:
        try: data, _ = sock.recvfrom(65535)
        except socket.timeout: continue
        try:
            for addr, _t, args, _b in m.parse_packet(data): log.append((time.time() - t0, addr[6:], args[0] if args else None))
        except Exception: pass
th = threading.Thread(target=rx); 
print(subprocess.run([sys.executable, MP, "play"], capture_output=True, text=True).stdout.strip())
t0 = time.time(); th.start()
for g in GRABS:
    while time.time() - t0 < g: time.sleep(0.05)
    out = os.path.abspath("%s_%03d.png" % (SCENE.lower(), int(g)))
    r = subprocess.run([sys.executable, MP, "grab", "--server", "MusicXRay", "--out", out, "--wait", "2"], capture_output=True, text=True)
    print("grab", g, "ok" if r.returncode == 0 else r.stderr[-200:])
while time.time() - t0 < SECS: time.sleep(0.2)
stop = True; th.join()
print(subprocess.run([sys.executable, MP, "play"], capture_output=True, text=True).stdout.strip())
json.dump(log, open("probe_%s.json" % SCENE.lower(), "w"))
print("messages", len(log))
