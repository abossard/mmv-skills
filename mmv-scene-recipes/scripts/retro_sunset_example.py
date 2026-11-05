#!/usr/bin/env python3
"""Retro sunset starter project, built with mmv-core's magicproj.Builder.

    python3 retro_sunset_example.py OUT.magic [--palette synthwave|miami|vapor|tron|sunset] [--syphon NAME] [--size 1920x1080] [--audio-device NAME]

Scenes: Sunset (the picture), Look (post chain used as a scene effect), Main (Sunset through Look).
Globals: Gain (manual sensitivity), Highs, KickRaw/Kick and Energy drive the picture; every visible param
that moves is linked to a Global, so MIDI/OSC can later replace the audio source without touching the
scenes. Bass and Hue (a 0..1 drift) are spare controls that nothing is linked to yet. Time, TimeLag and Dt
give Kick a decay in seconds. --audio-device defaults to $MMV_AUDIO_DEVICE, else the device Magic is set to.
The custom shaders live in ../assets/isf and are referenced by absolute path (isfFilename), so no
Additional Module Folder is needed.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "mmv-core", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "mmv-audio-reactivity", "scripts"))
import audio_bank  # noqa: E402
import magicproj as m  # noqa: E402

ISF = os.path.join(HERE, "..", "assets", "isf")
isf = lambda name: os.path.join(ISF, name + ".fs")


PALETTES = {      # RGB 0..1 per ISF color input
    "synthwave": dict(sky_top=(0.02, 0.0, 0.12), sky_mid=(0.45, 0.04, 0.45), sky_hor=(1.0, 0.35, 0.3), sun_top=(1.0, 0.92, 0.25),
                      sun_bot=(1.0, 0.1, 0.55), glow=(1.0, 0.25, 0.6), line=(1.0, 0.2, 0.75), floor=(0.06, 0.0, 0.14),
                      hglow=(1.0, 0.35, 0.5), edge=(0.2, 0.9, 1.0), body=(0.04, 0.0, 0.1)),
    "miami": dict(sky_top=(0.05, 0.0, 0.25), sky_mid=(0.85, 0.2, 0.6), sky_hor=(1.0, 0.65, 0.3), sun_top=(1.0, 0.95, 0.4),
                  sun_bot=(1.0, 0.3, 0.4), glow=(1.0, 0.4, 0.5), line=(0.1, 0.9, 1.0), floor=(0.02, 0.02, 0.14),
                  hglow=(1.0, 0.5, 0.6), edge=(1.0, 0.4, 0.8), body=(0.05, 0.0, 0.12)),
    "vapor": dict(sky_top=(0.1, 0.05, 0.3), sky_mid=(0.6, 0.35, 0.9), sky_hor=(1.0, 0.7, 0.85), sun_top=(1.0, 0.95, 0.7),
                  sun_bot=(1.0, 0.45, 0.75), glow=(0.7, 0.9, 1.0), line=(0.4, 1.0, 0.9), floor=(0.1, 0.05, 0.25),
                  hglow=(0.9, 0.7, 1.0), edge=(1.0, 0.7, 0.95), body=(0.12, 0.06, 0.28)),
    "tron": dict(sky_top=(0.0, 0.0, 0.02), sky_mid=(0.0, 0.08, 0.18), sky_hor=(0.0, 0.4, 0.6), sun_top=(0.7, 1.0, 1.0),
                 sun_bot=(0.0, 0.5, 1.0), glow=(0.0, 0.6, 1.0), line=(0.0, 0.9, 1.0), floor=(0.0, 0.02, 0.06),
                 hglow=(0.0, 0.5, 0.8), edge=(1.0, 1.0, 1.0), body=(0.0, 0.02, 0.05)),
    "sunset": dict(sky_top=(0.05, 0.02, 0.1), sky_mid=(0.5, 0.1, 0.2), sky_hor=(1.0, 0.5, 0.1), sun_top=(1.0, 1.0, 0.4),
                   sun_bot=(1.0, 0.3, 0.1), glow=(1.0, 0.45, 0.15), line=(1.0, 0.55, 0.1), floor=(0.1, 0.02, 0.02),
                   hglow=(1.0, 0.5, 0.1), edge=(1.0, 0.8, 0.3), body=(0.06, 0.01, 0.03)),
}


def rgba(prefix, c):
    """ISF color param values: 'Sky Top' -> Sky Top R/G/B/A."""
    return {"%s %s" % (prefix, k): v for k, v in zip("RGBA", (c[0], c[1], c[2], 1.0))}


def build(syphon, size, audio_device, palette="synthwave"):
    P = PALETTES[palette]
    b = m.Builder(syphon=syphon, size=size, audio_device=audio_device)

    # --- Globals: one place for every audio-derived value -------------------
    b.glob("Gain", 0.5)                                              # manual 0..1 knob, 0.5 = x2 (consumers use x*Gain*4)
    b.glob("Bass", 0, "audio:Source 0:Freq. Range:20-80 Hz",
           [("Expression", "x*Gain*4"), ("Smooth", 0.35), ("Clamp", 1)])
    b.glob("Highs", 0, "audio:Source 0:Freq. Range:5k-20k Hz",
           [("Expression", "x*Gain*4"), ("Smooth", 0.5), ("Clamp", 1)])
    audio_bank.add_clock(b)                                          # Time, TimeLag, Dt (seconds per frame)
    # Kick: fast attack, 0.12 s decay on any display. y is the previous output; Dt makes the decay per second.
    b.glob("KickRaw", 0, "audio:Source 0:Freq. Range:80-320 Hz", [("Expression", "x*Gain*4")])
    b.glob("Kick", 0, "global:KickRaw", [("Expression", "max(x, y*exp(-Dt/0.12))"), ("Clamp", 1)])
    b.glob("Energy", 0, "audio:Source 0:Volume", [("Expression", "x*Gain*4"), ("Smooth", 0.9), ("Clamp", 1)])
    b.glob("Hue", 0, "calc", [("Increase", 0.01), ("Wrap", 1)])      # slow palette drift 0..1

    # --- Sunset scene ---------------------------------------------------------
    s = b.scene("Sunset")
    sky = s.node("SunsetSky", dict({"Horizon": 0.45, "Stars": 0.6}, **rgba("Sky Top", P["sky_top"]), **rgba("Sky Mid", P["sky_mid"]),
                                   **rgba("Sky Horizon", P["sky_hor"])), isf=isf("SunsetSky"))
    sun = s.node("RetroSun", dict(rgba("Top Color", P["sun_top"]), **rgba("Bottom Color", P["sun_bot"]), **rgba("Glow Color", P["glow"]), **{
        "Sun Pos X": 0.5, "Sun Pos Y": 0.56, "Radius": 0.25, "Bands": 9, "Band Start": 0.6, "Band Speed": 0.1,
        "Glow": ("global:Energy", [("Scale", 1.2), ("Offset", 0.3)], 0.6),
        "Pulse": ("global:Kick", [], 0)}), isf=isf("RetroSun"))
    sky_sun = s.node("Blend", {"Mode": 9}, inputs=[sky, sun])       # 9 = Screen (Mode stores the option index): sun lights the sky
    mountains = s.node("RetroMountains", dict(rgba("Body Color", P["body"]), **rgba("Edge Color", P["edge"]), **{
        "Horizon": 0.45, "Height": 0.13, "Drift": 0.02,
        "Edge Glow": ("global:Highs", [("Scale", 1.5), ("Offset", 0.6)], 1)}), isf=isf("RetroMountains"))
    grid = s.node("SynthGrid", dict(rgba("Line Color", P["line"]), **rgba("Floor Color", P["floor"]), **rgba("Horizon Glow", P["hglow"]), **{
        "Horizon": 0.45, "Density": 8, "Cam Height": 0.3, "Scroll": ("global:Energy", [("Scale", 3), ("Offset", 0.5)], 0.6),
        "Pulse": ("global:Kick", [], 0), "Glow": 0.6}), isf=isf("SynthGrid"))
    s.output(grid, mountains, sky_sun)                                # top pin = front

    # --- Look scene: used as an effect (SceneInput -> Bloom -> CRT) -----------
    lk = b.scene("Look")
    entry = lk.scene_input()
    bloom = lk.node("Bloom", {"BlurAmount": 12, "Intensity": ("global:Kick", [("Scale", 0.6), ("Offset", 0.5)], 0.6)},
                    inputs=[entry])
    crt = lk.node("RetroCRT", {"Scanlines": 0.3, "Curvature": 0.06, "Vignette": 0.45}, inputs=[bloom], isf=isf("RetroCRT"))
    lk.output(crt)

    # --- Main: Sunset through Look ---------------------------------------------
    mn = b.scene("Main")
    sunset_mod = mn.scene_module(s)
    look_mod = mn.scene_module(lk)
    look_mod.inputs.append(sunset_mod)
    mn.output(look_mod)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--syphon", default="RetroSunset")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--palette", default="synthwave", choices=sorted(PALETTES))
    ap.add_argument("--audio-device", default=os.environ.get("MMV_AUDIO_DEVICE"))
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.lower().split("x"))
    b = build(a.syphon, (w, h), a.audio_device, a.palette)
    root = b.build()
    root = m.set_playlist(root, names=["Main"], seconds=600)
    m.write(a.out, root)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
