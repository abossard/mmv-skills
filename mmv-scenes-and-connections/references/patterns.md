# Scene graph patterns

## 1. Layer stack with a shared background

```python
bg   = s.node("SunsetSky", {...}, isf=ISF + "SunsetSky.fs")
sun  = s.node("RetroSun", {...}, isf=ISF + "RetroSun.fs")
sky  = s.node("Blend", {"Mode": 9}, inputs=[bg, sun])
hills = s.node("RetroMountains", {...}, isf=ISF + "RetroMountains.fs")   # alpha 0 outside ridges
floor = s.node("SynthGrid", {...}, isf=ISF + "SynthGrid.fs")             # alpha 0 above horizon
s.output(floor, hills, sky)        # front to back
```

## 2. Scene A / Scene B crossfade driven by a Global

```python
a = b_.scene("A"); bsc = b_.scene("B"); main = b_.scene("Main")
ma, mb = main.scene_module(a), main.scene_module(bsc)
mix = main.node("Mix", {"Amount": ("global:Crossfade", [], 0)}, inputs=[ma, mb])
main.output(mix)
```
Both scenes render while mixed: halve the load by powering one off at the ends (`power=("global:ShowA", [("Threshold", 0.01)])`).

## 3. Effect scene reused as a bus

`Look` scene: `SceneInput -> Bloom -> Chroma Zoom -> RadialBlur -> Kaleidoscope -> Shake`. Each effect `bypass=("global:FxBloom", [("Threshold", 0.01), ("Invert", 1)])` so it switches off at amount 0 (saves GPU). Use `scene_module(look)` in every scene that needs the look.

## 4. Multi-input selector with audio trigger

`InputSelector` with 4 chains, `Input #` = Global `Slot` where `Slot` = source `global:KickPulse` (from `audio_bank`) + `Trigger 0.5` (counts rising edges) + `Wrap 4`; a `calc` source would count nothing, its input is 0. Result: every kick steps to the next chain.

## 5. Scatter with Iterator

`Polygon -> Scale(0.05) -> Translate(X,Y,Z each = Iteration # -> RandomTrigger 0.5 -> Scale 2 -> Offset -1) -> Iterator(60)`. Each iteration gets its own random position.

## 6. Mask a video with a shape

`Mask`: pin 1 = VideoFile chain, pin 2 = `ImageFile circle.png` (alpha) or a Polygon with ColorRGB. `Use Alpha=1` uses the shape's alpha.

## 7. Sources that must never block the output

Syphon clients (`SyphonClient` `Server` = `"<server> - <app>"`) may be absent; they draw nothing. Wrap them in a scene and Mix/LumaKey them over a safe background so a missing server does not leave a black frame.
