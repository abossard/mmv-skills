---
name: mmv-effects-color
description: Effect chains, color and palettes in Magic Music Visuals - ordering post effects (bloom, glow, blur, kaleidoscope, glitch, feedback trails, CRT), ColorRGB/ColorHSB behaviour, additive vs normal blending, blend mode index table, palette drift and gradients, keying, cost per effect, and ready chains per look. Use when styling a scene, building a post-processing bus, picking blend modes, choosing a palette or fixing washed-out, muddy or too-dark output.
---

# Effects and color

Prerequisite: [mmv-core](../mmv-core/SKILL.md). Param names and option lists for every effect: `mmv-core/references/module-catalog.md` (grep the module name).

## Chain order (usual, front-end to output)

1. Sources: generators, Model, video, Syphon.
2. Color: ColorRGB/ColorHSB on 3D or flat sources (they preserve 3D).
3. Compose: Blend, Mask, Mix, MultiMix.
4. Geometry effects: Mirror, Kaleidoscope, Zoom, Shockwave, Twirl, Bump Distortion.
5. Tone: Contrast, HueSaturation, Color Controls, Duotone/Trio Tone, Posterize.
6. Light: Bloom or Glow, God Rays, Chroma Zoom, RadialBlur.
7. Texture: Trails, Echo Trace, Film/VHS, Halftone, scanlines/CRT.
8. Final: Shake/Strobe (performance), Transparency for blackout, Resolution for a cheap pixel look.

Everything after step 4 is 2D, so do depth and 3D first. Put steps 4-8 in one `Look` scene with a SceneInput and reuse it (pattern in mmv-scenes-and-connections).

## Color modules

- ColorRGB `Red Green Blue Alpha`, ColorHSB `Hue Saturation Brightness Alpha`. Hue 0 red, .166 yellow, .333 green, .5 cyan, .666 blue, .833 magenta.
- `Additive` 1 (default): light-like mixing; set 0 for straight alpha. `Override` 1 ignores other color modules upstream in the chain.
- Color modules tint whatever is upstream; a generator that already has color (ISF with color inputs) is not affected unless Override/Additive tints it. For ISF colors set the shader's own `Color R/G/B/A` params.
- Palette drift: ColorHSB `Hue` linked to Global `Hue` (calc + Increase 0.01 + Wrap 1). Keep Saturation 0.7-1, Brightness from `Energy`.
- Retro palettes (HSB): hot pink 0.92/0.9/1, cyan 0.5/0.9/1, violet 0.76/0.8/0.6, sun gold 0.13/0.9/1, deep night 0.72/1/0.12.

## Blend mode index (Blend module `Mode`, stored as the 0-based index; measured)

0 Lighten, 1 Darken, 2 Multiply, 3 Average, 4 Add, 5 Subtract, 6 Difference, 7 Negation, 8 Exclusion, 9 Screen, 10 Overlay, 11 Soft Light, 12 Hard Light, 13 Color Dodge, 14 Color Burn, 15 Linear Dodge, 16 Linear Burn, 17 Linear Light, 18 Vivid Light, 19 Pin Light, 20 Hard Mix, 21 Reflect, 22 Glow, 23 Phoenix, 24 Hue, 25 Saturation, 26 Color, 27 Luminosity.
Verified pixel results for base (0.2, 0.4, 0.6) over (0.5, 0.5, 0.5): Darken (0.2, 0.4, 0.5), Multiply (0.1, 0.2, 0.3), Average (0.35, 0.45, 0.55), Add (0.7, 0.9, 1.0), Exclusion 0.5 gray, Screen (0.6, 0.7, 0.8), Overlay (0.2, 0.4, 0.6). Input order matters for some modes: pin 1 = base, pin 2 = blend.

## Chains per look

| Look | Chain |
|---|---|
| Neon glow | source -> Bloom (BlurAmount 8-12, Intensity from Kick 0.5..1.0) -> Chroma Zoom (small) |
| VHS / CRT | HueSaturation (-0.1) -> VHS Glitch or Bad TV -> RetroCRT (mmv-scene-recipes) |
| Dream trails | source -> Trails (Strength 0.9, Blur on) or Zooming Feedback / `T_Feedback` |
| Club strobe | Strobe module (Color Effect), `Power`/`Bypass` linked to Kick pulse; never full white at > 3 Hz without a master limiter |
| Mirror mandala | Kaleidoscope (Iterations 6-12) or Mirror -> Radial Replicate -> Bloom |
| Glitch drop | Pixel Shifter / Glitch Shifter / FastMosh, Bypass linked to `Drop` |
| Halftone print | CMYK Halftone or Dot Screen, Posterize |
| Video keying | LumaKey (Invert for bright) or ChromaKeyFast (Green/Blue) before compositing |

## Cost (rough, 1080p on Apple silicon; measure with the FPS line)

Cheap: Contrast, HueSaturation, Invert, Posterize, Pixelate, Transparency, Mirror, Zoom, scanlines.
Medium: Bloom/Glow-Fast, RadialBlur, Kaleidoscope, Chroma Zoom, Trails.
Heavy: Multi Pass Gaussian Blur, Optical Flow Distort/Generator, Hyperspace, Median, big Iterators, raymarched generators, Glow (non-fast), Antialias SSAA.
Bypass what is idle: link `Bypass` to `Threshold` of the controlling Global, so effects at amount 0 cost nothing.

## Facts

- Bloom/Gloom: `Intensity` defaults to 0 (a bare Bloom does nothing): set 0.5-1. `BlurAmount` 0..12 (12 is the max).
- Backgrounds: `Solid Color`, `Linear Gradient` (Vertical flag, Start/End Color), `Radial Gradient` (Modules2/Generator), or `SunsetSky.fs`.
- `Bloom(inputs=[fx, bg])` composites both (first = front) and blooms the result; to bloom only the foreground, Bloom first then Blend/stack with the background.

## Common failures

- Washed out: Bloom Intensity too high or Additive color on a bright base. Lower Intensity, Screen -> Add change, Contrast -0.1.
- Muddy: Overlay/Multiply on dark layers; use Screen or Add for glows.
- Black frame after a Mask: wrong pin order (pin 1 = image, pin 2 = mask) or mask alpha 0.
- Trails smear forever: strength 1 plus a static bright source; use <= 0.95 and a floor.
- Banding in gradients: add 1/255 noise in the shader or Posterize off; use FLOAT passes for feedback.
- Alpha: `Transparency Amount` 1 fully transparent. For a global fade-to-black use Brightness (ColorHSB) on the final bus or Blackout Global multiplying.

More: [references/effect-recipes.md](references/effect-recipes.md).
