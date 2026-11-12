# Liquid looks: what is in the two reference videos

Sources (not in this repository; the user's own copies): `fluid_sim.webm` (2560x1440, 29.97 fps, 7:22, AV1 8-bit SDR) and `magic_fluid.webm`
(3840x2160, 60 fps, 2:39, AV1 10-bit HDR PQ, "Magic Fluids" by Roman De Giuli: real paint filmed in macro).
Contact sheets were made with ffmpeg (16 frames per video) plus 4 full-detail crops each. The HDR frames were
not tone mapped (this ffmpeg has no zscale), so they look greyer than the real video.

## Liquid types

| # | Type | Seen in | What makes it look right |
|---|---|---|---|
| A | Neon ink jets in dark water | fluid_sim, whole video | 2D incompressible flow with strong vorticity (curls at every edge), dye emitted as jets from screen edges, saturated neon dyes on black, white-hot cores where dye piles up, soft glow (bloom), dye fades over seconds, colours mix where they meet. Fast: big changes within 0.5 s |
| B | Acrylic pour cells | magic_fluid 0:50-1:05, 1:40 | white or pastel base with oval cells, each cell rimmed by a thin dark line and an iridescent (gold to violet) fringe, small satellite droplets, cells stretched along a slow laminar flow |
| C | Oil-slick marbling | magic_fluid 1:30, 2:00-2:15 | long parallel bands of pastel thin-film colours (rainbow order), fibrous lacy edges, laminar shear flow, specular sheen |
| D | Ink bloom in water | magic_fluid 1:20 | soft translucent tendrils feathering outward (fingering), volumetric haze, dark background |
| E | Radial burst | magic_fluid 2:20 | pigment explodes outward from a centre in radial streaks, rainbow mix, fine streak texture |
| F | Membrane dome | magic_fluid 1:10, 1:50 | a dark dome with a bright iridescent rim, like a soap film, slow breathing |

Common to the macro footage: very fine detail at 4K, thin-film (iridescent) colour bands, specular
highlights that make the surface read as wet and glossy, slow motion, black surround.

## Plan for Magic

- One GPU fluid solver in ISF with persistent buffers: velocity, dye, pressure (Jacobi passes), curl
  (vorticity confinement). The simulation grid is low resolution (e.g. 256 high) and the dye is high
  resolution, which is how real-time fluid sims keep 60+ fps.
- Each look is a render style over the same solver: A = neon dye + bloom; B = cells (threshold of a
  second scalar field advected by the flow, rim from its gradient) + thin film; C = thin film from dye
  "thickness" + shear emitters; D = soft dye + feathering noise; E = radial burst emitter; F = ring
  emitter + rim light. Wet look on all: normal from the dye gradient, specular, thin-film by angle.
- Audio: kick = splat (impulse + dye), sub-bass = emitter strength, snare = swirl kick (vorticity boost),
  highs = sparkle/specular, drop = colour change and burst, buildup = rising force. Driven by the
  Music X-Ray analysis Globals (`../scripts/music_xray_example.py`).

## Harness (dev loop under Claude's control)

1. Build: generator script writes the .fs and the .magic (Builder, as in `../scripts/music_xray_example.py`).
2. Static: `isf_lint.py`, glslangValidator compile (GLSL 1.20 wrapper), `mmv_verify.py` static check.
3. Live: load into the running Magic, play a test track, grab Syphon frames over time (`magicproj.py grab`),
   read FPS from Magic's Internals "Graphics FPS" via an OSCSender probe (as in the X-Ray probe).
4. Judge: side-by-side sheets of our frames next to the reference frames of the same look, frame-to-frame
   change against kick times (audio reaction), FPS at 1920x1080 and 4K.
Loading into Magic replaces the open project: only when the user is not using Magic.
