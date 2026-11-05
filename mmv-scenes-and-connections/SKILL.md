---
name: mmv-scenes-and-connections
description: Build and edit the structure of Magic Music Visuals scenes - modules, pin order, layering and compositing (Blend/Mask/Mix/MultiMix/InputSelector), scene modules, SceneInput effects, post-processing scenes, Iterator repeats, scene groups and tabs. Use when wiring modules together, deciding what draws in front, splitting a project into reusable scenes, or generating a scene graph with the Builder.
---

# Scenes, modules, connections

Prerequisite: [mmv-core](../mmv-core/SKILL.md) (Builder, check, verify). Exact param names: `mmv-core/references/module-catalog.md`.

## Model

- A scene = modules connected, left to right, into the `Magic` root. Anything not reaching Magic is not drawn and not evaluated.
- Output pin (right) can feed many inputs: the module is computed once, drawn once per path.
- Input pins are ordered. First child = top pin = drawn in front. Ordinary modules composite all their inputs into one image first, then apply themselves (so `Scale` after three inputs scales all three).
- Layers modules (Blend, Mask, Mix, MultiMix, InputSelector) and most ISF effects with two images treat inputs independently: pin 1 = first image, pin 2 = second.
- Everything is 3D space. Effects2D, ISF, GLSLShader, Media output a flat plane; the plane can still be scaled, rotated, translated.

## Builder patterns

```python
s = b.scene("Main")
gen = s.node("RetroSun", {...}, isf="/abs/RetroSun.fs")        # generator, no input pin
fx  = s.node("Bloom", {"BlurAmount": 14}, inputs=[gen])         # effect, input pin 0
mix = s.node("Blend", {"Mode": 9}, inputs=[a, b])               # a = base, b = overlay, Mode index 9 = Screen
s.output(fx, bg)                                                # root children: fx in front of bg
```

- Chain: `s.chain(gen, color, scale)` then `s.output(scale)`.
- Fan-in to one effect: `inputs=[a, b, c]` (composited, a on top).
- Fan-out: reuse the same node object in several `inputs`.
- Effect over foreground + background: `bloom = s.node("Bloom", {...}, inputs=[fg, bg])` blooms the composite; to bloom only the foreground bloom `fg` first and stack it over `bg` at the root.
- Reusable component: build scene `Part`, then `m1 = main.scene_module(part)` as a module in other scenes (Translate it to place copies). Scene modules cannot reference themselves.
- Scene as effect: in scene `Look`, `e = look.scene_input()` then chain effects from `e`; in the user scene `lm = main.scene_module(look); lm.inputs.append(source)`. Several SceneInputs = several pins in creation order.
- Post-processing for every scene: GUI command Scene > Add/Update Post-Processing Scene. In code: make one `Look` scene with a SceneInput and add it as a scene module before `Magic` in each scene (`isPostProcessing` stays 0 in files made by Builder; only the GUI command sets it).
- Always-on modules (OSCSender, Syphon senders): put them in their own scene and draw it as a scene module from every shown scene. A module only runs while something draws it.

## Compositing recipes

| Goal | Build |
|---|---|
| Glow sun over a sky | `Blend` Mode 9 Screen, pin 1 sky, pin 2 sun |
| Add light | Blend Mode 4 Add |
| Darken / multiply a texture | Blend Mode 2 Multiply |
| Cut a shape out of a layer | `Mask` pin 1 = layer, pin 2 = shape (Use Alpha 1, or 0 to use luma) |
| Crossfade two looks | `Mix` Amount 0..1, or `MultiMix Index` for N inputs |
| Switch between looks | `InputSelector` `Input #` (0 = top pin) |
| Foreground over background with alpha | give the ISF alpha 0 where empty and stack as pins (front first) |
| Key out black / white | `LumaKey` (Strength, Falloff, Invert) |

Full blend mode index list: [mmv-effects-color](../mmv-effects-color/SKILL.md).

## Iterator (repeat with per-copy variation)

`Iterator(Iterations, Offset)` draws its input chain N times. Params below it link to internal `Iteration #` (`"internal:Iteration #"`) with modifiers: `[("Scale", 0.3), ("Offset", -1.2)]` spreads copies along X. Verified: 9 cubes, each rotated by `Iteration # * 0.1`. Details and 3D use: [mmv-3d-geometry](../mmv-3d-geometry/SKILL.md). Iterator Freqs. (audio `Freq. Range` sub 6) splits the spectrum across the iterations.

## Scene groups, tabs, playlist

- `SceneTreeItems` are organisation only; ids of groups and scenes are separate spaces.
- `Tabs/Tab` hold editor x,y per node; Builder lays nodes out by depth. Missing entries still load.
- Playlist entries decide what the Magic window shows (see [mmv-vj-performance](../mmv-vj-performance/SKILL.md)).
- Keep scene count low: every scene uses VRAM (`keepInGfxMem`, Load All Scenes Into Graphics Memory).

## Checks before saying done

- `magicproj check` clean; every scene has at least one output; every ISF file exists.
- Draw order matches intent: open the grabbed frame, not the node graph.
- Power/Bypass: a powered-off module disables everything feeding it; bypass only itself. Link `Bypass`/`Power` to a Global for performance switches (`bypassParamUsed`/`powerParamUsed` are set by Builder when linked).

More patterns and a full multi-scene example: [references/patterns.md](references/patterns.md).
