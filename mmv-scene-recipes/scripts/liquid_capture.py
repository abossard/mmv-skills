#!/usr/bin/env python3
"""Continuous Syphon capture from Magic (runs under the syphon-python interpreter, see liquid_harness.py).

    liquid_capture.py SERVER SECONDS OUT_DIR [--png T1,T2,...] [--seq START,DURATION,FPS]  (T = seconds after start)

Writes OUT_DIR/capture.json: start (epoch s), frames [[t_epoch, grey samples hex]] on a 64x36 grid,
and raw BGRA frames OUT_DIR/f_<T>.bgra for each --png time (flipped later by ffmpeg, Magic sends bottom-up).
"""
import json
import os
import sys
import time

import syphon
from Foundation import NSDate, NSRunLoop
from syphon.utils.raw import copy_mtl_texture_to_bytes

GW, GH = 64, 36


def main():
    server, seconds, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    pngs = []
    if "--png" in sys.argv:
        pngs = sorted(float(x) for x in sys.argv[sys.argv.index("--png") + 1].split(","))
    seq = []                      # --seq START,DURATION,FPS: consecutive frames for motion review
    if "--seq" in sys.argv:
        a, dur, fps = (float(x) for x in sys.argv[sys.argv.index("--seq") + 1].split(","))
        seq = [a + k / fps for k in range(int(dur * fps))]
    os.makedirs(out, exist_ok=True)
    pump = lambda s: NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(s))
    d = syphon.SyphonServerDirectory()
    client, end = None, time.time() + 8
    while client is None and time.time() < end:
        pump(0.2)
        for desc in d.servers:
            if desc.app_name == "Magic" and desc.name == server:
                client = syphon.SyphonMetalClient(desc)
    if client is None:
        print("no syphon server %s; have %s" % (server, [s.name for s in d.servers]), file=sys.stderr)
        return 2
    t0 = time.time()
    frames, size = [], None
    while time.time() - t0 < seconds:
        pump(0.002)
        if not client.has_new_frame:
            continue
        now = time.time()
        tex = client.new_frame_image
        w, h = tex.width(), tex.height()
        raw = copy_mtl_texture_to_bytes(tex)
        stride = len(raw) // h
        size = (w, h, stride)
        g = bytearray(GW * GH)
        k = 0
        for j in range(GH):
            row = (int((j + 0.5) * h / GH)) * stride
            for i in range(GW):
                o = row + int((i + 0.5) * w / GW) * 4
                g[k] = (raw[o] + 2 * raw[o + 1] + raw[o + 2]) >> 2
                k += 1
        frames.append([now, g.hex()])
        if seq and now - t0 >= seq[0]:
            with open(os.path.join(out, "s_%06.2f.bgra" % seq.pop(0)), "wb") as fh:
                fh.write(bytes(raw) if stride == w * 4 else b"".join(bytes(raw[y * stride:y * stride + w * 4]) for y in range(h)))
            while seq and now - t0 >= seq[0]:
                seq.pop(0)
        while pngs and now - t0 >= pngs[0]:
            tag = pngs.pop(0)
            with open(os.path.join(out, "f_%06.2f.bgra" % tag), "wb") as fh:
                fh.write(bytes(raw) if stride == w * 4 else b"".join(bytes(raw[y * stride:y * stride + w * 4]) for y in range(h)))
    client.stop()
    with open(os.path.join(out, "capture.json"), "w") as fh:
        json.dump({"start": t0, "size": size, "grid": [GW, GH], "frames": frames}, fh)
    print("frames", len(frames), "in %.1f s" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
