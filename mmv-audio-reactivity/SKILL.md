---
name: mmv-audio-reactivity
description: Make Magic Music Visuals scenes react to audio - input sources and channels, audio features (Volume, Freq. Range, Best Pitch, Tone), modifier chains, Globals as a shared analysis bank, kick/hat envelopes, beat counters, energy and build-up trackers, and gain staging. Use when linking visuals to sound, tuning responsiveness, fixing jittery or stuck envelopes, routing BlackHole/Loopback or audio files, or generating a standard audio Global bank.
---

# Audio reactivity

Prerequisite: [mmv-core](../mmv-core/SKILL.md).

## Inputs

- A `Track` is a device channel (stereo mic = 2 tracks), a `Layer` ("Source 0") points at a track. Params link to Layers, so re-routing a source never breaks links.
- Builder creates `Source 0/1` on the device Magic is currently set to (often the built-in mic). For DJ/DAW audio always pass `audio_device="BlackHole 2ch"` (or the interface name); the static check cannot tell. Magic 3 can read several devices at once; give each Track its own `deviceName`.
- Audio files: `magicproj.add_audio(root, "loop.wav", source="Source 0", loop=True)`; they only drive visuals while playing (Shift+Cmd+Space). Live devices always run.
- For DJ or DAW audio on a Mac: loopback driver (BlackHole 2ch) as Magic's input; do not use the built-in mic.
- Per-source gain slider: `Layer gain` (dB, up to +/-24).

## Features (all 0..1)

| Feature | Use |
|---|---|
| Volume | overall level |
| Freq. Range | 5 presets, 2 octaves each: 20-80, 80-320, 320-1.2k, 1.2k-5k, 5k-20k Hz; Custom Freq. (low/high cutoffs); Iterator Freqs. (spectrum split over an Iterator) |
| Best Pitch | monophonic pitch 40..2560 Hz, log |
| Tone | brightness, 40..20480 Hz, log |

## Pattern: analysis in Globals, visuals read Globals

1. One Global per concept (`Bass`, `Kick`, `Energy`), linked to audio with a short modifier chain.
2. Every visual param links to a Global, never to the raw source. Then the source can become MIDI/OSC, a file, or a visualizer app (for example Synesthesia over OSC) without touching scenes, and sensitivity lives in one `Gain` Global.
3. Gain: keep `Gain` a plain manual Global (0.5 = x2) and multiply in the consumer: Expression `x*Gain*4`.

`scripts/audio_bank.py` adds the standard bank (verified live with a 124 BPM test loop: Dt, Kick decay, Beat4 counting):

```python
sys.path += ["<skills>/mmv-audio-reactivity/scripts"]
import audio_bank; audio_bank.add_audio_bank(b, source="Source 0", kick_decay=0.12)
```

Globals: Gain, Bass, LowMid, Mid, High, Air, Volume, Energy, EnergySlow, Time, TimeLag, Dt, KickRaw, Kick, KickGate, KickGateLag, KickPulse, Beat4, Build. `audio_bank.add_clock(b)` adds only `Time`, `TimeLag` and `Dt`.

## Modifier cookbook (applied top to bottom)

| Goal | Chain |
|---|---|
| Responsive level | Expression `x*Gain*4` -> Smooth 0.3 -> Clamp 1 |
| Drum envelope (fast attack, timed decay) | source Freq. Range -> Expression `max(x, y*exp(-Dt/0.12))`; `y` is the previous output; needs Global `Dt` |
| Do not use Peak for drums | it holds too long; use the exp decay above |
| Pulse on each kick (one frame) | `Gate` = Kick -> Threshold 0.6; `GateLag` = calc + Expression `Gate`; `Pulse` = calc + Expression `if (Gate > 0.5 and GateLag < 0.5, 1, 0)`. Do not use `y` for this: it is the previous output, so a held gate toggles 1,0,1,0 |
| Count beats mod 4 | on the pulse: Trigger 0.5 -> Wrap 4 |
| Slow build-up | Expression `clamp(y + (x - 0.35)*Dt*0.25, 0, 1)` on a slow energy Global |
| Constant oscillation | source `calc`, Sine 0.25 (input ignored) |
| Hue drift | source `calc`, Increase 0.01 -> Wrap 1 |
| Frame-rate independent time | `Time` = calc + Increase 1; `TimeLag` = calc + Expression `Time`; `Dt` = calc + Expression `max(0.001, min(0.05, Time - TimeLag))`. Works only through `calc` Globals (a `global:Time` source did not lag, measured) |
| Randomize on beat | on KickPulse: RandomTrigger 0.5 |
| Square wave / gate | Threshold p |

## Expression functions

ExprTk: `abs clamp min max floor ceil frac exp log pow sqrt sin cos tan atan2 avg sgn round trunc if/else and or not` plus `x`, `y`, `pi`. There is no `fmod`; for modulo use `frac(x/n)*n` or `x - n*floor(x/n)` (`mmv_verify` rejects unknown names). Global names are variables (case-insensitive). `Time` (audio_bank) is seconds since load and unbounded: wrap it (`frac(Time*0.02)`) before using it as an angle or hue.

## Semantics to remember

- Every Global/param reads the previous frame's value of Globals it names. N hops = N frames latency; keep chains shallow for tight sync.
- Params clamp silently to their range even if the modifier output is larger.
- `calc` Globals start at 0 at load; feedback expressions (`y`) need that in mind.
- Expression names are case-insensitive. Global names used in expressions: no spaces, not `x`/`y`, not a function name.
- Manual (unlinked) Globals are plain values: do not rely on modifiers there, put the maths in the consumer.
- Measured: Magic drove frame time at about 8.7 ms on a 120 Hz display, so per-frame decays (`y*0.93`) differ by display. Use `Dt`.
- Movie export ignores live audio links; only audio files drive exports.

## Tuning checklist

1. Play the loudest part of the track; `Gain` so `Bass` peaks near 0.8-1.
2. Kick: `kick_decay` 0.08 (tight techno) to 0.2 (big room). Threshold 0.5-0.7.
3. If visuals jitter: raise Smooth (0.3 to 0.6). If they lag: lower Smooth, shorten chain.
4. Show the Globals: a bar scene (Polygon scaled by Global, as used in `mmv-core/references/verification.md`) makes tuning visible.

Worked analysis chains (onset follower with refractory time, beat clock, build/breakdown detector) are longer than `audio_bank.py`; build them from the cookbook above and test with a looping WAV.
