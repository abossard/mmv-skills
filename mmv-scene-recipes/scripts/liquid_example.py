#!/usr/bin/env python3
"""Liquid looks for Magic Music Visuals: one GPU fluid solver (ISF multipass, persistent buffers), one render
style per look, driven by the Music X-Ray analysis Globals (music_xray_example.py next to this script).

    python3 liquid_example.py OUT.magic [--looks A,C] [--size 1920x1080] [--fps 60] [--probe PORT]
                            [--audio-file WAV] [--syphon Liquid] [--audio-device NAME] [--first A]

Shaders: assets/isf/liquid-src/fluid_common.glsl (solver) + Liquid<X>.glsl (look) -> assets/isf/Liquid<X>.fs (header and pass
list generated here). One scene per look ("Liquid A", ...). --probe adds an always-on scene that sends
/liquid/<Global> over OSC (Fps from Internals "Graphics FPS", KickCount, SnareCount, DropPulse).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "isf", "liquid-src")
OUT_ISF = os.path.join(HERE, "..", "assets", "isf")
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))

PRESSURE = 7        # pressure passes, 2 Jacobi iterations each; 7 keeps the shader at 15 sampled buffers (Magic max 16)
SIM = {"WIDTH": "$WIDTH/6", "HEIGHT": "$HEIGHT/6", "FLOAT": True}
FULL = {"FLOAT": True}
QUARTER = {"WIDTH": "$WIDTH/4", "HEIGHT": "$HEIGHT/4", "FLOAT": True}
HALF = {"WIDTH": "$WIDTH/2", "HEIGHT": "$HEIGHT/2", "FLOAT": True}


def f(name, label, default, lo, hi):
    return {"NAME": name, "LABEL": label, "TYPE": "float", "DEFAULT": default, "MIN": lo, "MAX": hi}


AUDIO_INPUTS = [f("kick", "Kick", 0, 0, 1), f("snare", "Snare", 0, 0, 1), f("hat", "Hat", 0, 0, 1),
                f("bass", "Bass", 0, 0, 1), f("energy", "Energy", 0, 0, 1), f("drop", "Drop", 0, 0, 1),
                f("tension", "Tension", 0, 0, 1), f("phase", "Phase", 0, 0, 4)]
SOLVER_INPUTS = [f("flowRate", "Flow", 1.0, 0.0, 3.0), f("curlAmt", "Swirl", 30.0, 0.0, 100.0),
                 f("swirlKick", "Swirl Kick", 1.5, 0.0, 6.0),
                 f("viscosity", "Viscosity", 0.15, 0.0, 1.0), f("velFade", "Velocity Fade", 0.25, 0.0, 5.0),
                 f("pressureKeep", "Pressure Keep", 0.8, 0.0, 1.0), f("onset", "Onset", 0.15, 0.02, 0.8),
                 f("splatForce", "Splat Force", 2.5, 0.0, 10.0), f("splatSize", "Splat Size", 0.06, 0.01, 0.3),
                 f("fade", "Fade", 0.35, 0.0, 5.0), f("emit", "Emit", 1.0, 0.0, 4.0),
                 f("exposure", "Exposure", 1.4, 0.1, 6.0), f("bloom", "Bloom", 0.8, 0.0, 4.0),
                 f("bloomThresh", "Bloom Threshold", 0.6, 0.0, 3.0), f("shine", "Shine", 1.0, 0.0, 4.0),
                 f("palette", "Palette", 0.0, 0.0, 1.0),
                 f("openFlow", "Open Flow", 0.0, 0.0, 1.0), f("pourForce", "Pour Force", 0.0, 0.0, 1.0),
                 f("pixelate", "Pixelate", 0.0, 0.0, 64.0), f("zoom", "Zoom", 1.0, 0.25, 4.0),
                 f("zoomKick", "Zoom Kick", 0.0, 0.0, 0.5), f("cloud", "Pixel Cloud", 0.0, 0.0, 1.0), f("cloudSpread", "Cloud Spread", 3.0, 0.0, 10.0),
                 f("cubes", "Cubes", 0.6, 0.0, 1.0),
                 f("slowMo", "Slow Motion", 0.0, 0.0, 1.0), f("paletteSpeed", "Palette Speed", 0.0, 0.0, 1.0),
                 f("dropHue", "Drop Hue", 0.0, 0.0, 0.5), f("pop", "Pop", 0.35, 0.0, 1.5),
                 f("hdr", "HDR", 0.3, 0.0, 2.0), f("flare", "Flare", 0.3, 0.0, 2.0),
                 f("speedLimit", "Speed Limit", 3000.0, 20.0, 3000.0)]

LOOKS = {
    "A": {"desc": "Neon ink jets in dark water",
          "layout": {"sim": 4},
          "inputs": [{"NAME": "flatStyle", "LABEL": "Glass", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0},
                     f("hdrPop", "HDR Pop", 0.15, 0.0, 1.0), f("popAuto", "Pop Auto", 0.7, 0.0, 1.5)],
          "defaults": {"curlAmt": 8.0, "viscosity": 0.05, "fade": 0.4, "velFade": 0.45, "swirlKick": 0.6,
                       "pressureKeep": 0.97,
                       "splatSize": 0.12, "splatForce": 2.0, "exposure": 2.6, "shine": 1.0,
                       "flare": 0.0, "hdr": 0.0, "pop": 0.0}},
    "C": {"desc": "Oily fire: buoyant flames with oil streaks",
          "layout": {"pressure": 4, "bloom": False, "phase": 3},
          "inputs": [f("ribbon", "Burner", 0.085, 0.01, 0.3), f("lift", "Lift", 1.2, 0.0, 5.0),
                     f("fiber", "Fiber", 40.0, 12.0, 120.0), f("iridescence", "Sheen", 1.0, 0.0, 3.0),
                     f("hitGain", "Hit", 0.5, 0.0, 3.0), f("gust", "Gust", 6.0, 0.0, 150.0),
                     f("smokeAmt", "Smoke", 1.0, 0.0, 4.0), f("smokeFade", "Smoke Fade", 0.45, 0.0, 2.0),
                     f("smokeDensity", "Smoke Density", 1.1, 0.1, 6.0), f("smokeBright", "Smoke Light", 0.8, 0.0, 2.0),
                     f("smokeBlur", "Smoke Blur", 14.0, 0.0, 40.0), f("fireEdge", "Fire Edge", 0.09, 0.02, 0.5), f("variety", "Variety", 0.05, 0.0, 0.3),
                     {"NAME": "flatStyle", "LABEL": "Flat", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 1.0}],
          "defaults": {"curlAmt": 18.0, "viscosity": 0.15, "velFade": 0.6, "fade": 0.9, "flowRate": 1.0,
                       "openFlow": 0.0, "pourForce": 0.0, "exposure": 1.0, "bloom": 0.0, "splatForce": 1.0, "splatSize": 0.08,
                       "speedLimit": 140.0, "flare": 0.0, "hdr": 0.15, "iridescence": 0.8, "exposure": 1.3,
                       "paletteSpeed": 0.15, "dropHue": 0.13}},
}


def layout(look):
    """Pass layout of a look: pressure passes, bloom on/off, phase-field substeps (look B: Cahn-Hilliard cells)."""
    cfg = {"pressure": PRESSURE, "bloom": True, "phase": 0, "sim": 6}     # sim: velocity grid = frame / sim
    cfg.update(LOOKS[look].get("layout", {}))
    return cfg


def passes(cfg):
    # one TARGET per pass: Magic declares a uniform per pass entry, a repeated TARGET fails to compile
    sim = {"WIDTH": "$WIDTH/%d" % cfg["sim"], "HEIGHT": "$HEIGHT/%d" % cfg["sim"], "FLOAT": True}
    ps = [dict(TARGET="ctl", WIDTH="5", HEIGHT="1", PERSISTENT=True, FLOAT=True),
          dict(TARGET="velF", **sim), dict(TARGET="divB", **sim)]
    ps += [dict(TARGET="p%d" % k, **sim) for k in range(cfg["pressure"])]
    ps[-1]["PERSISTENT"] = True
    ps += [dict(TARGET="vel", PERSISTENT=True, **sim), dict(TARGET="dye", PERSISTENT=True, **FULL)]
    for k in range(cfg["phase"]):
        ps.append(dict(TARGET="m%d" % k, **QUARTER))
        ps.append(dict(TARGET="phi" if k == cfg["phase"] - 1 else "f%d" % k, **QUARTER))
    if cfg["phase"]:
        ps[-1]["PERSISTENT"] = True                # the final phase buffer (phi) carries over to the next frame
    if cfg["bloom"]:
        ps += [dict(TARGET=t, **QUARTER) for t in ("b1", "b2", "b3")]
    return ps + [{}]


def pressure_glsl(n):
    """pPrev(k, uv): the buffer pressure pass k reads (k == 0: last frame's result); pLastRaw: the solved pressure."""
    lines = ["float pLastRaw(vec2 uv) { return IMG_NORM_PIXEL(p%d, uv).x; }" % (n - 1),
             "float pPrev(int k, vec2 uv) {", "\tif (k == 0) return clean(IMG_NORM_PIXEL(p%d, uv)).x;" % (n - 1)]
    lines += ["\tif (k == %d) return IMG_NORM_PIXEL(p%d, uv).x;" % (k, k - 1) for k in range(1, n - 1)]
    lines += ["\treturn IMG_NORM_PIXEL(p%d, uv).x;" % (n - 2), "}"]
    return "\n".join(lines) + "\n"


def phase_glsl(n):
    """phiIn(k, uv): the phase field substep k starts from (k == 0: last frame's phi); muAt(k, uv): its potential."""
    if not n:
        return ""
    lines = ["float phiIn(int k, vec2 uv) {", "\tif (k == 0) return clean(IMG_NORM_PIXEL(phi, uv)).x;"]
    lines += ["\tif (k == %d) return IMG_NORM_PIXEL(f%d, uv).x;" % (k, k - 1) for k in range(1, n)]
    lines += ["\treturn 0.0;", "}", "float muAt(int k, vec2 uv) {"]
    lines += ["\tif (k == %d) return IMG_NORM_PIXEL(m%d, uv).x;" % (k, k) for k in range(n)]
    lines += ["\treturn 0.0;", "}", "float phiAt(vec2 uv) { return clean(IMG_NORM_PIXEL(phi, uv)).x; }"]
    return "\n".join(lines) + "\n"


def dispatch(cfg, debug=False):
    p0, after = 3, 3 + cfg["pressure"]
    lines = ["void main() {",
             "\tif (PASSINDEX == 0) passCtl();",
             "\telse if (PASSINDEX == 1) passForce();",
             "\telse if (PASSINDEX == 2) passDiv();",
             "\telse if (PASSINDEX < %d) passPressure(PASSINDEX - %d);" % (after, p0),
             "\telse if (PASSINDEX == %d) passAdvectVel();" % after,
             "\telse if (PASSINDEX == %d) passDye();" % (after + 1)]
    i = after + 2
    for k in range(cfg["phase"]):
        lines += ["\telse if (PASSINDEX == %d) passMu(%d);" % (i, k), "\telse if (PASSINDEX == %d) passPhase(%d);" % (i + 1, k)]
        i += 2
    if cfg["bloom"]:
        lines += ["\telse if (PASSINDEX == %d) passBloomPre();" % i,
                  "\telse if (PASSINDEX == %d) passBlur(0);" % (i + 1),
                  "\telse if (PASSINDEX == %d) passBlur(1);" % (i + 2)]
    lines += ["\telse %s();" % ("passDebug" if debug else "passRender"), "}"]
    return "\n".join(lines) + "\n"


def assemble(look, debug=False):
    spec = LOOKS[look]
    inputs = AUDIO_INPUTS + [dict(i) for i in SOLVER_INPUTS] + spec["inputs"]
    for i in inputs:
        if i["NAME"] in spec["defaults"]:
            i["DEFAULT"] = spec["defaults"][i["NAME"]]
    cfg = layout(look)
    header = {"DESCRIPTION": "Liquid %s: %s. GPU fluid (vorticity confinement, %d Jacobi iterations) driven by audio." % (look, spec["desc"], 2 * cfg["pressure"]),
              "CREDIT": "music-xray liquid", "ISFVSN": "2.0", "CATEGORIES": ["Generator", "Audio Visualizer"],
              "INPUTS": inputs, "PASSES": passes(cfg)}
    with open(os.path.join(SRC, "fluid_common.glsl")) as fh:
        common = fh.read()
    with open(os.path.join(SRC, "Liquid%s.glsl" % look)) as fh:
        body = fh.read()
    defines = "#define LIQ_BLOOM %d\n#define LIQ_PHASE %d\n" % (int(cfg["bloom"]), cfg["phase"])
    text = "/*%s*/\n\n%s%s\n%s\n%s\n%s\n%s" % (json.dumps(header, indent="\t"), defines, common, pressure_glsl(cfg["pressure"]),
                                              phase_glsl(cfg["phase"]), body, dispatch(cfg, debug))
    os.makedirs(OUT_ISF, exist_ok=True)
    out = os.path.join(OUT_ISF, "Liquid%s.fs" % look)
    with open(out, "w") as fh:
        fh.write(text)
    return out


PROBE = ["Fps", "KickCount", "SnareCount", "DropPulse", "Bpm", "Volume"]


def build(skills, looks, syphon, size, fps, audio_device, probe_port=None, audio_files=(), first=None, params=None, debug=False):
    sys.path.insert(0, os.path.join(skills, "mmv-core", "scripts"))
    sys.path.insert(0, os.path.join(skills, "mmv-audio-reactivity", "scripts"))
    sys.path.insert(0, os.path.join(skills, "mmv-scene-recipes", "scripts"))
    import audio_bank
    import music_xray_example as build_xray
    import magicproj as m
    b = m.Builder(syphon=syphon, size=size, fps=fps, audio_device=audio_device)
    build_xray.add_globals(b, audio_bank)
    b.glob("Fps", 0, "internal:Graphics FPS")
    live = lambda band, expr: ("audio:Source 0:Freq. Range:" + band, [("Expression", expr), ("Clamp", 1)], 0)
    audio = {"Kick": live("80-320 Hz", "max(x*Gain*4, y*exp(-Dt/0.12))"),
             "Snare": live("1.2k-5k Hz", "max(clamp((x*Gain*4 - SnareAvg*1.1)*8, 0, 1), y*exp(-Dt/0.1))"),
             "Hat": live("5k-20k Hz", "max(clamp((x*Gain*4 - HatAvg*1.1)*8, 0, 1), y*exp(-Dt/0.05))"),
             "Bass": live("20-80 Hz", "y + (min(1, x*Gain*4) - y)*(1 - exp(-Dt/0.06))"),
             "Energy": ("global:Energy", [], 0), "Drop": ("global:DropFlash", [], 0),
             "Tension": ("global:Tension", [], 0), "Phase": ("global:Phase", [], 0)}
    names, shown = [], []
    for look in looks:          # look scenes first: Magic outputs scene 0 (the editor's first tab), not the playlist entry
        s = b.scene("Liquid " + look)
        vals = dict(audio)
        vals.update((params or {}).get(look, {}))
        shown.append((s, s.node("Liquid" + look, vals, isf=assemble(look, debug))))
        names.append("Liquid " + look)
    probe = None
    if probe_port:
        probe = b.scene("Probe")
        probe.output(*[probe.node("OSCSender", {"IP Addr.": "127.0.0.1", "Port": str(probe_port), "Message": "/liquid/" + n,
                                                "Value": ("global:" + n, [], 0)}) for n in PROBE])
    for s, node in shown:
        s.output(node, *([s.scene_module(probe)] if probe else []))
    root = b.build()
    for path in audio_files or ():
        root = m.add_audio(root, path, source="Source 0", loop=True)
    if first:
        i = names.index("Liquid " + first)
        names = names[i:] + names[:i]
    root = m.set_playlist(root, names=names, seconds=3600)
    return m, root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--looks", default="A,C")
    ap.add_argument("--first")
    ap.add_argument("--syphon", default="Liquid")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--audio-device", default=os.environ.get("MMV_AUDIO_DEVICE"))
    ap.add_argument("--skills", default=os.environ.get("MMV_SKILLS", SKILLS))
    ap.add_argument("--probe", type=int, metavar="PORT")
    ap.add_argument("--audio-file", action="append")
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.lower().split("x"))
    m, root = build(a.skills, a.looks.split(","), a.syphon, (w, h), a.fps, a.audio_device, a.probe, a.audio_file, a.first)
    for level, msg in m.check(root, HERE):
        print(level, msg)
    m.write(a.out, root)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
