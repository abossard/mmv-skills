---
name: mmv-scene-recipes
description: Ready scene recipes for Magic Music Visuals with generator scripts and shaders - retro sunset / synthwave (sun, perspective grid, mountains, stars, bloom, CRT; five palettes), calibration pattern, Music X-Ray (live audio analysis made visible: beat, drops, spectrum, tempo), audio spectrum, 3D cube field, kaleidoscope, glitch drop, feedback trails, lyrics overlay, Syphon compositing. Use when asked to build a specific look quickly, when starting the VJ Retro Sunset scene, or when you need a worked end-to-end example of Builder + ISF + audio Globals.
---

# Scene recipes

Prerequisites: [mmv-core](../mmv-core/SKILL.md), [mmv-audio-reactivity](../mmv-audio-reactivity/SKILL.md), [mmv-shaders-isf-glsl](../mmv-shaders-isf-glsl/SKILL.md).

## Recipe index

| Recipe | Status | Where |
|---|---|---|
| Retro sunset / synthwave (5 palettes) | generated, opens, renders, audio-reactive (verified live) | `scripts/retro_sunset_example.py`, `assets/isf/*.fs`, preview `assets/retro_sunset_preview.png` |
| Music X-Ray: live analysis made visible (beat orbit, drop radar, spectral terrain, song river, tempo lens) | verified live, tuned on real songs | `scripts/music_xray_example.py`, [references/music-xray.md](references/music-xray.md) |
| Liquid looks: GPU fluid (neon ink jets, oily fire with smoke), audio driven, with dev harness | verified live, 1080p 200+ fps | `scripts/liquid_example.py`, [references/liquid.md](references/liquid.md), analysis [references/liquid-analysis.md](references/liquid-analysis.md) |
| Mapping calibration pattern | verified live | `mmv-output-mapping/scripts/mapping_test_pattern.py` |
| Audio spectrum bars (ISF FFT + native Spectrum) | verified live | `mmv-shaders-isf-glsl/assets/templates/T_AudioFFT.fs` |
| 3D cube field (Iterator + Model + DepthTest + MSAA) | verified live | `mmv-3d-geometry` |
| Feedback trails | template verified | `T_Feedback.fs`, or module `Zooming Feedback`, `Trails` |
| Kaleidoscope mandala | design sketch | below |
| Glitch drop | design sketch | below |
| Lyrics / text overlay | design sketch | below |
| Syphon compositing (external renderer + FX) | common pattern | mmv-vj-performance |

## Retro sunset (start here for the VJ Retro Sunset scene)

Run:
```bash
python3 scripts/retro_sunset_example.py out.magic --palette synthwave --size 1920x1080 --syphon "Retro Sunset"
python3 ../mmv-core/scripts/mmv_verify.py out.magic --live --yes --restore --out frame.png --frames 4 --play   # --play only with an audio file
```
The second command replaces the project open in Magic: ask the user first. With `--frames 4` the frames are `frame.0.png` to `frame.3.png`; the brightest one is named in the output. `--audio-device NAME` (default `$MMV_AUDIO_DEVICE`, else the device Magic is set to) picks the audio input.
Palettes: `synthwave miami vapor tron sunset`. Output: scenes `Sunset` (picture), `Look` (SceneInput -> Bloom -> RetroCRT), `Main` (Sunset through Look), playlist = Main only.

Layer stack (front to back): `SynthGrid` (alpha 0 above horizon) > `RetroMountains` (alpha 0 outside ridges) > `Blend Screen(9)` of `SunsetSky` and `RetroSun`. Look bus on top.

Audio wiring (Globals from the file): `Gain` (manual sensitivity), `Highs`, `KickRaw`/`Kick` (0.12 s decay through `Dt`, the same on any display), `Energy`. `Bass` and `Hue` (a 0..1 drift) are spare controls that nothing is linked to yet. Sun `Pulse` and grid `Pulse` = `Kick`; grid `Scroll` = `Energy*3 + 0.5`; mountain `Edge Glow` = `Highs*1.5 + 0.6`; sun `Glow` = `Energy*1.2 + 0.3`; Bloom `Intensity` = `Kick*0.6 + 0.5`.
`Time`, `TimeLag` and `Dt` come from `audio_bank.add_clock`. The full `audio_bank.add_audio_bank` defines Gain, Bass, KickRaw, Kick and Energy again, so use it instead of the script's own Globals, not in addition.

Shader knobs worth linking (names as Magic shows them):
- `RetroSun`: `Sun Pos X/Y`, `Radius`, `Bands`, `Band Start`, `Band Speed`, `Glow`, `Pulse`, `Top/Bottom/Glow Color R..A`.
- `SynthGrid`: `Horizon`, `Cam Height`, `Density`, `Scroll`, `Line Width`, `Horizon Fade`, `Glow`, `Pulse`, `Line/Floor/Horizon Glow Color`.
- `SunsetSky`: `Horizon`, `Sky Top/Mid/Horizon`, `Stars`, `Twinkle`.
- `RetroMountains`: `Horizon`, `Height`, `Ridge Scale`, `Drift`, `Seed`, `Edge Glow`, `Body/Edge Color`.
- `RetroCRT`: `Scanlines`, `Line Count`, `RGB Split`, `Curvature`, `Vignette`, `Flicker`.
Keep every `Horizon` equal: `SunsetSky`, `RetroMountains` and `SynthGrid` each have one (the script sets 0.45 on all three). To move the horizon, add one Global `Horizon` and link the three.

Ideas to push it further (each is a small Builder change; verify with a grab):
1. Lower horizon to 0.35 and raise Sun Pos Y to 0.5 so more sun bands show above the ridges; `Band Start` 0.65.
2. Night Global (0..1): sun Y down by `Night*0.25`, Sky Top/Mid darker, `Stars` up, Hue untouched. One Global drives four params.
3. Drop: `Drop` Global flashes `Glow` to 2 and `RGB Split` to 0.01 for 0.3 s (`max(DropEvt, y - Dt/0.3)`).
4. Spectrum on the horizon: `T_AudioFFT` scaled (Scale Y 0.1) and translated to y = horizon, Blend Add.
5. Grid reflection: mirror the sun into the floor with `Flip V` + Transparency 0.7 below the horizon.
6. Palette morph: ColorHSB over the whole Sunset scene with `Hue` Global small range (0..0.08) for subtle drift.
7. Camera sway: Translate X on `SynthGrid` input via a scene wrapper, `Sine 0.05` modifier, tiny amplitude.
8. Moon: second `RetroSun` with Radius 0.08, Bands 0, pale colors, upper left.
9. VHS finish: add `VHS Glitch` or `Bad TV` before `RetroCRT`, `Bypass` linked to Drop.
10. 4K: `--size 3840x2160`; the shaders are resolution independent (Bloom `BlurAmount` is capped at 12).

Performance (Apple silicon, measured loosely): five shaders + Bloom + CRT held display rate at 1920x1080 on a MacBook (no dropped frames noticed in grabs); raise cost only with `BlurAmount` and 4K.

Known limits: sun bands are hidden by ridges when Horizon is high; mountains are 2 noise layers (not parallax); stars are static cells with twinkle; no moon/clouds yet.

## Design sketches (not rendered in testing)

- Kaleidoscope mandala: `SunsetSky` or `Fractal` -> `Kaleidoscope (Iterations from Beat4 * 2 + 4, Rotation = Increase 0.02)` -> `Bloom`. Fractal `Real/Imaginary` from `Energy` with Smooth 0.8.
- Glitch drop: `Pixel Shifter` / `Glitch Shifter` with `Bypass` = Invert of `Drop`; `Shake Magnitude` = `Drop` for 0.4 s.
- Lyrics overlay: `Text` (Size 8, Bold) or SyphonClient of a lyrics app -> LumaKey -> top pin of Master; `Text Line #` stepped by an OSC value.
- Spectrum wall: `Iterator 32` + `Polygon` scaled in Y by `Freq. Range Iterator Freqs.`, hue from `Iteration #`.

## Build checklist for any new recipe

1. Pick modules from the catalog; write a Builder script in the project; `--palette`-style options for colour variants.
2. All moving params linked to Globals (never to raw audio).
3. `mmv_verify.py` static, then `--live --yes --restore --out frame.png` (after asking the user); view the PNG; fix alpha/order issues.
4. For audio: `add_audio` loop + `--play --frames 4`, or OSC drive.
5. Record in the project README which Globals are the performance controls.
