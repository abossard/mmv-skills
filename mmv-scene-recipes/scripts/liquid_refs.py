#!/usr/bin/env python3
"""Reference frames from the two videos, tone mapped (the HDR one is PQ BT.2020; this ffmpeg has no zscale).

    python3 liquid_refs.py lut                     write pq2srgb.cube (PQ BT.2020 -> BT.709 sRGB, highlight roll-off)
    python3 liquid_refs.py sheet VIDEO EVERY OUT   contact sheet, one frame every EVERY seconds
    python3 liquid_refs.py frames                  the per-type reference frames listed in REFS -> $LIQUID_WORK/refs/<type>_<t>.png

HDR route: ffmpeg converts YUV to RGB with the BT.2020 matrix only (no transfer change), lut3d does
PQ EOTF -> nits -> BT.709 primaries -> tone map (203 nit white, soft knee) -> sRGB OETF.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# the reference videos are not in the repo: point LIQUID_VIDEOS at the folder that holds them
VID = os.environ.get("LIQUID_VIDEOS", os.getcwd())
WORK = os.path.join(os.environ.get("LIQUID_WORK", os.path.join(os.getcwd(), "liquid-work")), "refs")
LUT = os.path.join(WORK, "pq2srgb.cube")
HDR = "magic_fluid.webm"

# type -> [(video, seconds)]; picked from tone-mapped contact sheets (ANALYSIS.md times were a few seconds off)
REFS = {
    "A": [("fluid_sim.webm", t) for t in (100, 160, 170, 260, 380, 390)],
    "C": [(HDR, t) for t in (85, 90, 117, 120, 123, 125)],
}


# which REFS entry the 10 fps motion strip uses per type
MOTION = {"A": 4, "C": 3}


def strip(video, t, out, fps=10, n=20):
    """n consecutive frames at fps from t, 5 per row, 384 px wide each."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(VID, video), "-vf",
                    "fps=%d,%s,scale=384:216,tile=5x%d" % (fps, vf(video, 768), n // 5), "-frames:v", "1", out], check=True)


def pq_eotf(e):
    m1, m2 = 2610 / 16384, 2523 / 4096 * 128
    c1, c2, c3 = 3424 / 4096, 2413 / 4096 * 32, 2392 / 4096 * 32
    p = max(e, 0.0) ** (1 / m2)
    return 10000.0 * (max(p - c1, 0.0) / (c2 - c3 * p)) ** (1 / m1)


M2020_709 = ((1.6605, -0.5876, -0.0728), (-0.1246, 1.1329, -0.0083), (-0.0182, -0.1006, 1.1187))


def tone(x, white=203.0, peak=1000.0):
    """nits -> display 0..1: linear up to 0.6 of SDR white, then a soft shoulder that reaches 1 at `peak`."""
    v = x / white
    k, top = 0.6, peak / white
    if v <= k:
        return v
    t = (v - k) / (top - k)
    return k + (1 - k) * (1 - math.exp(-3.0 * t)) / (1 - math.exp(-3.0))


def srgb(v):
    v = min(max(v, 0.0), 1.0)
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def write_lut(n=65):
    os.makedirs(os.path.dirname(LUT), exist_ok=True)
    lin = [pq_eotf(i / (n - 1)) for i in range(n)]
    with open(LUT, "w") as f:
        f.write("LUT_3D_SIZE %d\n" % n)
        for b in range(n):
            for g in range(n):
                for r in range(n):
                    c = (lin[r], lin[g], lin[b])
                    o = [sum(M2020_709[i][j] * c[j] for j in range(3)) for i in range(3)]
                    f.write("%.6f %.6f %.6f\n" % tuple(srgb(tone(max(v, 0.0))) for v in o))


def vf(video, w):
    s = "scale=%d:-2:flags=lanczos" % w
    if video == HDR:
        if not os.path.exists(LUT):
            write_lut()
        return s + ":in_color_matrix=bt2020:in_range=tv:out_range=pc,format=rgb48le,lut3d=file='%s',format=rgb24" % LUT
    return s


def frame(video, t, out, w=1920):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", os.path.join(VID, video), "-frames:v", "1",
                    "-vf", vf(video, w), out], check=True)


def sheet(video, every, out, w=480, cols=6):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(VID, video), "-vf",
                    "fps=1/%s,%s,tile=%dx8:padding=4" % (every, vf(video, w), cols), "-frames:v", "1", out], check=True)


def frames():
    out = {}
    for typ, lst in REFS.items():
        for video, t in lst:
            os.makedirs(WORK, exist_ok=True)
            p = os.path.join(WORK, "%s_%05.1f.png" % (typ, t))
            if not os.path.exists(p):
                frame(video, t, p)
            out.setdefault(typ, []).append(p)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "lut":
        write_lut()
    elif cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "frames":
        print(frames())
