---
name: mmv-3d-geometry
description: 3D and geometry in Magic Music Visuals - coordinate system and camera distance, Translate/Scale/RotateAxis/RotateVector order, Model files (OBJ/3DS via Assimp) with lighting and wireframe, Polygon/SineWave/Spectrum/Waveform/Lissajous/Starfield, Iterator-driven grids and tunnels, DepthTest, MSAA Antialias, and the 2D-flattening rule for effects. Use when building 3D scenes, spinning/repeating geometry, tunnels, cube fields, wireframes, or when depth, clipping or draw order looks wrong.
---

# 3D and geometry

Prerequisite: [mmv-core](../mmv-core/SKILL.md), [mmv-scenes-and-connections](../mmv-scenes-and-connections/SKILL.md).

## Space (measured on 3.0b6)

- Right-handed x right, y up, z toward the viewer. y spans -1..1 at z = 0 whatever the resolution; x edge = aspect ratio.
- Perspective camera on the +z axis about 2.4 units from the origin, looking at -z. A 0.3 cube looks 83 px wide at z = 0 and 45 px at z = -2 (540 px frame); at z = +2 or more it is clipped or behind the camera. Keep z in about -20..+1.5.
- No camera module: move the world. To fly forward, Translate Z of the whole scene +, or animate it with `Increase`.
- Rotations are in turns (1 = 360 degrees): `RotateAxis(Axis "X-Axis"|"Y-Axis"|"Z-Axis", Angle)`, `RotateVector(Angle, X, Y, Z)`.

## Transform order

Modules apply to everything upstream of them. `Model -> Scale -> RotateAxis -> Translate` = scale first, then spin about the origin, then move. Spin in place: Translate must come after RotateAxis. Orbit: Translate before RotateAxis. Per-axis scale by linking `X`, `Y`, `Z` separately; `X For All` copies X.

## Drawing order and depth

- Default: pin order, first = front, no depth buffer between inputs.
- `DepthTest` after the inputs makes them intersect and occlude correctly. Put it after the transforms of each object, before 2D effects.
- `Antialias` `Quality`: SSAA 2x or MSAA 2x-16x (index in the catalog; verified MSAA 4 on a cube field). MSAA keeps 3D; SSAA needs output size <= half the GPU max.
- Every Effects2D / ISF / GLSLShader / Media module flattens to a plane. After one of them the geometry has no depth anymore. Draw 3D first, then effects.

## Modules

| Module | Notes |
|---|---|
| Polygon `Sides`, `Fit` | filled n-gon; sides 100 = circle; 4 = square at Scale 1 as tall as the frame |
| Model `File`, `Center`, `Scale`, `Colorize`, `Wireframe`, `3-Light`, `Global Light`, `L. Azimuth`, `L. Elevation`, `L. Intensity` | Assimp; bundled samples use `.obj` and `.3ds`; `Colorize` applies ColorRGB/HSB, otherwise original colours; Wireframe overrides fills |
| SineWave, Waveform, Spectrum, Lissajous | audio drawn as geometry (`Source` = Layer id; MIDI/OSC sources draw nothing) |
| Starfield | `Speed Size Circles Stars/sec Distance Spread`, max 5000; an input becomes the star sprite |
| Iterator | repeat N times, params link to `Iteration #` |
| Trails | needs alpha; hides behind opaque full-frame inputs |

## Facts for generated files

- `RotateAxis` `Axis` is stored as the string `"X-Axis"`, `"Y-Axis"` or `"Z-Axis"` (saved samples and live render). `Angle` is in turns and not limited to 0..1.
- `Iteration #` is the raw 0-based integer (0..N-1, plus `Offset`), `Total Iterations` the count (Internals feature 8; `"internal:Total Iterations"`).
- The ISF module `Rotate` (Geometry Adjustment) is a flat 2D rotation with Angle 0..1; use `RotateAxis` for geometry.

## Recipes

- Ring / orbit (verified by a fresh session): `Polygon -> Scale 0.06 -> ColorHSB -> Translate X (r) -> RotateAxis Z (Angle = Iteration #/N) -> Iterator N`. Translate BEFORE RotateAxis so the rotation orbits; link `r` to `Bass` for a pulsing radius.
- Cube field: `Model(cube.obj) -> Scale 0.25 -> RotateAxis Y (Angle = Iteration # * 0.1) -> Translate X (Iteration # * 0.3 - 1.2) -> Iterator 9 -> RotateAxis X 0.12 -> DepthTest -> Antialias 4`. Verified frame: nine lit, tilted cubes.
- Flythrough: `Polygon(Sides 100) -> Scale 0.05 -> Translate (X, Y from RandomTrigger per Iteration #, Z = -Iteration # * 0.5) -> Iterator 40`, then Translate Z of the whole scene by `Increase`/`Wrap` for forward motion. Magic's `Starfield` does this natively and cheaper. (Recipe not rendered in testing; check with a grab.)
- Spectrum bars in 3D: `Iterator(N, Freq. Range Iterator Freqs.)`: Polygon scaled in Y by audio `Freq. Range` sub 6, Translate X by `Iteration #`. See `IteratorSpectrumExamples.magic`.
- Wireframe pyramids / grid floor: use `Model` with `Wireframe 1` for meshes, or draw a perspective floor in a shader (`mmv-scene-recipes/assets/isf/SynthGrid.fs`) which is cheaper and sharper than geometry.
- Beat-synced spin: `Angle` = `Beat4` Global with `Smooth` (spins a quarter turn per kick) or `Increase` for continuous motion.
- Many instances with variation: Iterator + `RandomTrigger 0.5 -> Scale 2 -> Offset -1` for x/y/z of Translate (`IteratorCubeExamples`).

## Pitfalls

- A cube that "disappears": z beyond the camera, or Scale 0.
- Model colours: `Colorize 0` keeps the file's colours (the bundled cube renders grey); `Colorize 1` takes ColorRGB/HSB (verified: orange, red cubes). Dark result: raise `L. Intensity` or enable `3-Light`.
- Effects before 3D transforms rotate a flat picture, not geometry.
- Iterator with 3D models is GPU heavy: keep draws under ~200 at 60 fps; lower Antialias.
- File params: absolute path works; relative resolves against the project; samples live in the app bundle `SampleProjects/` (`cube.obj`, `balls.3DS`, `grid.3ds`).

Samples worth opening: `ModelExamples`, `DepthTestExample`, `IteratorCubeExamples`, `3DSpectrums`, `DancingRobot` (app bundle, Help > Open Sample Project).
