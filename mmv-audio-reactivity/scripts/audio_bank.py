#!/usr/bin/env python3
"""A standard bank of audio-analysis Globals for Magic scenes, built with mmv-core's Builder.

    import audio_bank
    audio_bank.add_audio_bank(b, source="Source 0")           # b = magicproj.Builder
    # then link params to "global:Bass", "global:Kick", "global:Energy", ...

Globals created (all 0..1 unless noted), in dependency-free order because Magic evaluates every Global
from the previous frame's values:
  Gain        manual knob 0..1, 0.5 = x2 (consumers multiply x*Gain*4); use it as the MIDI/OSC target
  Bass LowMid Mid High Air   five frequency ranges, smoothed, scaled by Gain
  Volume Energy EnergySlow   overall level, fast and slow
  Time        seconds since load (calc + Increase 1, unbounded: wrap before using as angle/hue)
  TimeLag Dt  Dt = frame time in seconds (Time - TimeLag); makes decays frame-rate independent
  KickRaw Kick   kick band follower; Kick is a fast-attack exponential decay envelope (time constant `kick_decay`, default 0.12 s, so about 0.4 s to fade out)
  KickGate KickGateLag KickPulse   Kick above `kick_threshold` as 0/1, that gate one frame later, and KickPulse = 1 for exactly one
                 frame when the gate rises (an edge detector needs the previous INPUT, so it uses a lag Global; `y` would be the
                 previous output and makes a held gate toggle 1,0,1,0)
  Beat4          0,1,2,3,0.. counter that steps on every kick
  Build          slow rise while energy stays high (0..1), for build-ups
Tune `kick_decay` (seconds to reach 1/e) and `kick_threshold` per track.
"""


def add_clock(b):
    """Time (seconds since load, unbounded), TimeLag and Dt (frame time in seconds). Only `calc` Globals lag."""
    g = b.glob
    g("Time", 0, "calc", [("Increase", 1)])
    g("TimeLag", 0, "calc", [("Expression", "Time")])
    g("Dt", 0.016, "calc", [("Expression", "max(0.001, min(0.05, Time - TimeLag))")])
    return b


def add_audio_bank(b, source="Source 0", kick_decay=0.12, kick_threshold=0.6):
    S = "audio:%s:Freq. Range:" % source
    g = b.glob
    g("Gain", 0.5)                      # plain manual 0..1; consumers use x*Gain*4 (0.5 = x2)
    for name, rng in (("Bass", "20-80 Hz"), ("LowMid", "80-320 Hz"), ("Mid", "320-1.2k Hz"),
                      ("High", "1.2k-5k Hz"), ("Air", "5k-20k Hz")):
        g(name, 0, S + rng, [("Expression", "x*Gain*4"), ("Smooth", 0.3), ("Clamp", 1)])
    g("Volume", 0, "audio:%s:Volume" % source, [("Expression", "x*Gain*4"), ("Clamp", 1)])
    g("Energy", 0, "calc", [("Expression", "(Bass*0.5 + LowMid*0.2 + Mid*0.15 + High*0.15)"), ("Smooth", 0.4), ("Clamp", 1)])
    g("EnergySlow", 0, "global:Energy", [("Smooth", 0.97)])
    add_clock(b)
    g("KickRaw", 0, S + "80-320 Hz", [("Expression", "x*Gain*4")])
    g("Kick", 0, "calc", [("Expression", "max(KickRaw, y*exp(-Dt/%g))" % kick_decay), ("Clamp", 1)])
    g("KickGate", 0, "global:Kick", [("Threshold", kick_threshold)])
    g("KickGateLag", 0, "calc", [("Expression", "KickGate")])
    g("KickPulse", 0, "calc", [("Expression", "if (KickGate > 0.5 and KickGateLag < 0.5, 1, 0)")])
    g("Beat4", 0, "global:KickPulse", [("Trigger", 0.5), ("Wrap", 4)])
    g("Build", 0, "global:EnergySlow", [("Expression", "clamp(y + (x - 0.35)*Dt*0.25, 0, 1)")])
    return b
