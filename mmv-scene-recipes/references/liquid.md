# Liquid looks: GPU fluid in one ISF shader, driven by the music

Two looks on one GPU fluid solver (ISF multipass, persistent buffers), each a scene with one shader node. Built by
`scripts/liquid_example.py`; shader sources in `assets/isf/liquid-src/` (the script writes `assets/isf/Liquid<X>.fs`).
The audio analysis is the Music X-Ray Globals bank (`music_xray_example.add_globals`). The reference analysis that
started this: [liquid-analysis.md](liquid-analysis.md).

```bash
python3 scripts/liquid_example.py out.magic                       # scenes Liquid A, Liquid C (live input)
python3 scripts/liquid_example.py out.magic --looks C,A --audio-file song.wav
```

| Look | What it is | Preview |
|---|---|---|
| A, neon ink | two ink jets enter from the frame edges and drift; the kick surges them (with inertia), every 4th kick (about a bar) a velocity puff, a drop fires two opposing splats. Default `Glass` = dye between two glass sheets: smooth colour, glow, no relief | `assets/liquid_ink_preview.png` |
| C, oily fire | burners below the frame inject heat; buoyancy lifts it, vorticity curls it into tongues, cooling heat becomes smoke; a phase field draws dark oil streaks inside the flames. Default `Flat`: hard 1 px temperature bands, soft grey smoke | `assets/liquid_fire_preview.png` |

## Solver (shared, `fluid_common.glsl`)

- One shader, one pass per step: state row (`ctl`: kick/snare/drop/hat onsets, look clock, init marker), forces
  (vorticity confinement, the look's forces, speed limit), divergence, pressure (N passes, two Jacobi iterations each,
  warm start from last frame), projection + velocity advection, dye advection, optional bloom (3 passes), optional
  phase field (Cahn-Hilliard with an Ohta-Kawasaki term, 3 substeps), final pass.
- Velocity grid at 1/4 (A, 480x270 at 1080p) or 1/6 (C); dye at full resolution, advected with a clamped Catmull-Rom
  lookup (sharp, no overshoot) along a cubic B-spline lookup of the coarse velocity (no cell-sized steps).
- Velocity in sim cells per second; forces scale with the grid height, so looks keep their speed at any size.
- `Open Flow` makes the left/right edges open water (pressure 0), with `Pour Force` a slow river through the frame.
- Final pass (shared by all looks): `Zoom`, `Zoom Kick`, `Pixelate` (hard square pixels, thin grid), `Pixel Cloud`
  (pixels as cubes at depth by brightness, `Cloud Spread`, `Cubes` bevel), `Pop`, `HDR`, `Flare` (ghosts in the
  look's own colour), all growing with loudness; `Slow Motion` 1 runs the sim and the looks' clocks at 3 %;
  `Palette`, `Palette Speed`, `Drop Hue` rotate the palette (glides on drops).

## Knobs per look

- A: `Glass` (1 glass, 0 glossy relief), `HDR Pop` (base) + `Pop Auto` (x loudness: energy, kick surge, drop):
  hot cores brighter, fuller saturation, more glow, past-white spots, all before the tone map.
- C: `Flat` (1 hard bands, 0 soft glowing fire), `Fire Edge`, `Burner`, `Lift`, `Hit`, `Gust` (curl-noise gust on hits),
  `Speed Limit` (velocity cap, default 140 for C), `Smoke`, `Smoke Fade`, `Smoke Density`, `Smoke Light`, `Smoke Blur`,
  `Fiber` (oil streak width), `Sheen`, `Variety` (subtle hue per burner).
- Audio params are linked by the script: `Kick`, `Snare`, `Hat`, `Bass` read the audio bands directly (no Global hops),
  `Energy`, `Drop` (DropFlash), `Tension`, `Phase` come from the Globals.

## Harness (`scripts/liquid_harness.py`)

```bash
python3 scripts/liquid_harness.py static                       # build, isf_lint, glslang compile + LINK, buffer checks, project check
python3 scripts/liquid_harness.py live A --yes --manual-play   # load into the running Magic (replaces its project), capture
python3 scripts/liquid_harness.py report A                     # FPS, kick reaction, sheet + 10 fps motion strip vs reference
```

- Work files go to `$LIQUID_WORK` (default `./liquid-work`); the test track is made by `music_xray_testtrack.py`.
- Reference frames: set `LIQUID_VIDEOS` to the folder with the reference videos (not in the repo); the HDR one is tone
  mapped through a generated 3D LUT (PQ BT.2020 to BT.709, this ffmpeg had no zscale).
- `live` grabs Syphon frames continuously (`liquid_capture.py`, syphon-python), reads Internals "Graphics FPS" through
  an OSCSender probe scene, and writes stills plus 2 s at 10 fps. `--manual-play` waits for Play in Magic's Input
  Sources window (the Shift+Cmd+Space keystroke stopped reaching Magic in one session).
- `report`: frame-to-frame change against detected kick times (peak ratio and lag), change per song section, and
  quality numbers for ours vs 2 s of reference (colourfulness, brightness, dark share, detail, change per frame).

## Verified live (MagicBeta 3.0b6, macOS arm64, M1 Max, 1920x1080, synthetic 126 BPM track)

| Look | Graphics FPS | Kick reaction | Notes |
|---|---|---|---|
| A glass + HDR pop | 206-263 | 1.4x frame change, +50 ms | vs fluid_sim reference: colourfulness 68 vs 74, brightness 27 vs 29, detail 8.6 vs 6.0 |
| A (velocity grid 1/6, earlier build) at 3840x2160 | 74-92 | | not re-measured after the grid went to 1/4 |
| C flat fire | 115-120 (soft build); flat build checked as frames only | 1.3x | |

Judged by the user on their own music: A good after the flat/comic detour was removed; C good as soft fire, flat
style requested and delivered. Not verified: C flat style and the palette rotation with music, A at 4K after the
1/4 grid.

## Magic facts found on the way (measured)

- A shader that samples more than 16 buffers draws nothing, no error dialog (16 works, 17 black). The harness counts them.
- A declared but undefined function (link error) also draws black with no dialog; glslang finds it only with `-l`.
- A pass TARGET may appear once (Magic declares a uniform per pass: "may not be redeclared").
- Magic outputs scene 0 (the editor's first tab), not the playlist's first entry: helper scenes go last.
- Persistent buffers start with leftover memory and FRAMEINDEX is no reliable first-frame flag: use a marker texel.
- A lost PERSISTENT flag on the dye showed as flicker, then black; the harness checks `ctl`, `vel`, `dye`.
- `flat` and `half` are reserved words. 64 float inputs and 15 samplers + 50 floats work.
- A Syphon BGRA frame saved as PNG keeps alpha 0 and shows white in viewers: convert with `format=rgb24`.
- The play state (Shift+Cmd+Space) survives project loads, so a blind toggle can pause: check a probed Volume first.

## What the user taught (for the next look)

- Simulate the physics behind the look; patterns drawn over a flow read as fake (acrylic cells and rainbow
  ribbons were dropped for that reason).
- No one-frame events (dye pops, colour jumps): they flicker on dense music. Drive reactions through envelopes.
- Slow, continuous motion; judge with 10 fps strips and on real music, not stills.
