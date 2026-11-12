# Music X-Ray: what Magic hears, shown live

Three scenes that make the live audio analysis visible, from the audio alone (no DJ software link, no
prior track analysis). Built by `scripts/music_xray_example.py`; shader sources in
`assets/isf/music-xray-src/` (the script expands their `TEXT()` labels and writes `assets/isf/XRay*.fs`).
The browser concept page that came first: `assets/music_xray_concepts.html` (simulated track, seven concepts).

```bash
python3 scripts/music_xray_example.py out.magic --audio-device "BlackHole 2ch"     # live input from DJ software
python3 scripts/music_xray_example.py out.magic --audio-file song.wav              # play a file (Shift+Cmd+Space in Magic)
```

## Scenes (playlist order)

| Scene | Shows |
|---|---|
| Pulse | beat orbit (bar phase, 4 beat markers, lock, bar 1 guess until a drop), kick heart with shock ring, snare burst, hat sparks, sub-bass floor wave, BPM / lock / nudge / bars since drop / hit counters, drop radar (tension gauge, state, three cue meters: sub-bass out, getting brighter, snare roll) |
| Terrain | live FFT as 40 ridgelines flowing to the viewer (auto level per song), over an endless song river: width = loudness, colour = live state, pins for DROP, LIFT, BUILDUP, BREAKDOWN, BEAT IN, INTRO; about 4 minutes wide, no song start or end |
| Tempo | kick hits of the last 3 s with the ms between them, interval histogram (forgets over `Memory` s), every interval as BPM folded into one tempo octave |

## Analysis (Globals)

Every Global reads the previous frame, so edge detectors use lag Globals (`KickGate`/`KickGateLag`).
- Hits: `Kick` (80-320 Hz envelope), `Snare` (1.2-5 kHz) and `Hat` (5-20 kHz) as rises above a 0.15 s average; `*Pulse` one frame per hit, `*Count`.
- Tempo: interval between kick pulses folded into `[TempoLo, 2*TempoLo)`, smoothed; a new tempo is taken only after 3 misses that agree with each other.
- Beat clock `Phase` (0..4 beats): runs on `Bpm`, each kick pulls it 35 % towards the beat, corrected by `Latency` (the kick pulse arrives a few frames after the kick).
- Bar 1: a guess (`DownSlot` 0) until a drop snaps it to the nearest beat.
- Sub-bass relative to its own peak of the last minutes (`BassPeak`), so thresholds fit any song and gain.
- Drop: quarter-beat sub-bass average above `SubHigh` after at least 2 bars below `SubLow`, checked every frame. Lift: crash one beat into a bar, 4 or more bars into a drop.
- States: 0 intro (and silence), 2 buildup, 3 drop, 4 breakdown. No "groove": a steady beat part is named by where it sits. A drop lasts while the kick runs; 16 bars of kick without sub-bass read as the next track's intro.

Tuning knobs (manual Globals): `Gain` (all bands, 0.5 = x2), `SubLow` 0.3, `SubHigh` 0.55, `RiseMin` 0.06, `LiftAir` 1.5, `Quiet` 0.02, `TempoLo` 90, `Latency` 0.04 s, `VisualLead` 0.06 s (moves the drawn kick earlier). Terrain module `Gain` = hill height (0.5).

Timing: the kick heart pulses on the predicted beat while the clock is locked and kicks run (no detection delay); otherwise, and for snare and hat flashes, shader params read the audio band directly (no Global hops).

Thresholds come from an analysis of 189 EDM tracks: at a drop the sub-bass steps from about 0.2 to 0.76 (relative), the kick is gone before a drop in fewer than half, buildups are 1 to 14 bars (8 within one bar in 6 of 10), a second hit about 8 bars into a drop is common (169 of 417), and only 56-64 % of section starts sit on an 8-bar line.

## Dev loop

| Step | Command |
|---|---|
| Model the Globals without Magic | `python3 scripts/music_xray_sim.py` (prints state, drops, lifts per bar on a synthetic track) |
| Test audio | `python3 scripts/music_xray_testtrack.py xray_test.wav` |
| Live: load, play, log the OSC probe, grab frames | `python3 scripts/music_xray_probe.py xray_test.wav Pulse 94 26,70,80` (replaces the open project: ask first) |
| Stream key Globals while tuning | build with `--probe 9300`, read `/xray/<Name>` |

## Verified live (MagicBeta 3.0b6, macOS arm64, synthetic 126 BPM track)

- All three scenes load with no shader errors; persistent buffers and the `audioFFT` input work.
- Drops found one beat after they start (before the per-frame check; the model now puts it at about 0.1 s), the lift 8 bars into the first drop, buildups 1 to 2 bars in, breakdown; tempo 125.5 to 126 BPM.
- On the user's own songs: terrain clipped and flickered (fixed with auto level and slower fall), kick looked late (fixed with the predicted beat), drop was late by half a bar to a bar (fixed with the per-frame check). The fixes after the last live run were checked in the model and compiled, not yet confirmed live by a grab.

Measured pitfalls: GPU `pow(2.0, n)` is inexact (font bits swapped until `floor((g + 0.5) / pow(2.0, n))`); calc Globals load as 0 (guard divisions); `mmv_verify` does not catch unbalanced parentheses in Expressions.
