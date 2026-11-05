# Effect recipes with Builder snippets

Names below exist in Magic 3.0b6 (see module-catalog.md). `"global:X"` links need Globals from `mmv-audio-reactivity/scripts/audio_bank.py`.

## Post bus (reusable Look scene)

```python
lk = b.scene("Look")
e = lk.scene_input()
bloom = lk.node("Bloom", {"BlurAmount": 12, "Intensity": ("global:Kick", [("Scale", 0.6), ("Offset", 0.5)], 0.6)}, inputs=[e])
cz = lk.node("Chroma Zoom", {"Master_zoom": 1, "Red_zoom": 1.0, "Blue_zoom": ("global:Kick", [("Scale", 0.02), ("Offset", 1)], 1)}, inputs=[bloom])
crt = lk.node("RetroCRT", {"Scanlines": 0.3}, inputs=[cz], isf=ISF + "RetroCRT.fs")
lk.output(crt)
```

## Switch an effect off at zero (saves GPU)

```python
fx = s.node("RadialBlur", {"Distance": ("global:FxBlur", [], 0), "Density": 0.5},
            inputs=[src], bypass=("global:FxBlur", [("Threshold", 0.01), ("Invert", 1)], 0))
```
Bypass = 1 when FxBlur < 0.01.

## Palette cycling

Global `Hue` = calc, Increase 0.01, Wrap 1. ColorHSB `Hue`: `("global:Hue", [], 0)`. Two-tone: second ColorHSB with Hue = `Hue` + 0.5 via Offset 0.5, Wrap 1.

## Beat strobe with limiter

Global `Strobe` = global:KickPulse, Scale 1. Transparency or Brightness linked to `Strobe`, but cap: Global `StrobeSafe` = Expression `min(Strobe, 0.6)` and a Hold 0.34 so it cannot fire faster than 3 Hz (the limit in mmv-vj-performance). Keep a manual `Blackout` Global that multiplies the final bus.

## Gradient background without a shader

`Linear Gradient` / `Radial Gradient` from Modules2/Generator (colors as `Color R..A` params). Link both colors' Hue by converting in Expressions, or use `SunsetSky.fs` for a three-stop sunset.

## Keying a Syphon source over a background

`SyphonClient (Server "name - App") -> LumaKey (Strength 0.5, Falloff 0.5) -> pin 1`, background generator on pin 2 of the root.
