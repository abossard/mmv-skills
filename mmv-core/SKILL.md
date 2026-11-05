---
name: mmv-core
description: Entry point for Magic Music Visuals (MMV, "Magic", .magic projects, MagicBeta.app). Use first for any task that reads, generates, edits, validates or live-tests a .magic scene. Covers the file format (3 header bytes + zlib XML), the Python Builder and magicproj CLI, the module catalog, static checks and the load-and-grab verification loop. Routes to the other mmv-* skills for audio, MIDI/OSC, shaders, 3D, effects, output and performance.
---

# MMV core: format, tools, verification

A `.magic` file = 3 ignored header bytes + zlib-compressed XML. Never hand-edit with sed. Generate with `magicproj.Builder`, edit with its library functions, then verify.

## Which skill

| Task | Skill |
|---|---|
| Scenes, modules, connections, layering, scene modules, Iterator | mmv-scenes-and-connections |
| Audio inputs, Globals, kick/beat/energy chains, modifiers | mmv-audio-reactivity |
| MIDI, OSC, MIDI clock, Ableton, controllers, playlist control | mmv-midi-osc-control |
| Write or debug ISF/GLSL shaders, custom modules | mmv-shaders-isf-glsl |
| 3D models, transforms, depth, MSAA, coordinates | mmv-3d-geometry |
| Effect chains, color, palettes, blend modes, post look | mmv-effects-color |
| Syphon out, projection mapping apps, fullscreen, export | mmv-output-mapping |
| Playlist, transitions, live editing, show checklist, perf | mmv-vj-performance |
| Ready scene recipes (retro sunset, tunnel, spectrum...) | mmv-scene-recipes |

## Tools (stdlib Python 3, in `scripts/` next to this file)

- `magicproj.py` CLI: `info`, `nodes`, `globals`, `check`, `diff`, `catalog`, `decode`, `encode`, `set`, `load`, `grab`, `play`, `listen`. Full list: [references/tooling.md](references/tooling.md).
- `magicproj.Builder`: generate a project in code (Globals, scenes, nodes, links, modifiers, ISF files, scene modules, SceneInput).
- `mmv_verify.py FILE [--live --yes] [--restore]`: static check, then load into the running Magic, detect error dialogs, grab a Syphon frame, report mean colour and lit fraction.
- `gen_catalog.py`: regenerates [references/module-catalog.md](references/module-catalog.md) (all 222 modules, exact param names, defaults, option lists).

## Workflow for a new scene

1. Pick modules and exact param names from the catalog (`python3 scripts/magicproj.py catalog --plugin REGEX`). Names are case and space sensitive.
2. Write a short Python script with `Builder` (pattern in [mmv-scenes-and-connections](../mmv-scenes-and-connections/SKILL.md)). Keep it in the project so the scene is regenerated, not patched.
3. `python3 scripts/mmv_verify.py out.magic` (static). Fix every error; read warnings.
4. Ask the user first and never run this while they perform: `python3 scripts/mmv_verify.py out.magic --live --yes --restore --out frame.png`; it refuses without `--yes`, so add that only after the user agreed replaces the project open in Magic. Then look at `frame.png`. A black frame with 0 errors usually means an opaque layer on top, a generator below the horizon of its own shader, or a playlist showing another scene (with Syphon off `mmv_verify` stops before the grab).
5. If audio matters: add a looping test WAV (`magicproj.add_audio`) and `--play`, or drive the Globals by OSC (`--osc /addr=0.8 --osc-port N`).

## Hard facts (verified in Magic 3.0b6, macOS arm64)

- Magic is a single-instance app. `--live` replaces the open project. `--restore` reopens the previous one, but only a saved project whose file name is unique among Magic's recent files; otherwise `--live --restore` refuses to start. The test never writes the user's files.
- Missing params are filled with defaults, so generated files list only the params they set.
- ISF `long` params (Blend Mode, quality menus) store the 0-based option INDEX, not the VALUES entry. Blend: 0 Lighten, 1 Darken, 2 Multiply, 4 Add, 9 Screen, 10 Overlay.
- Custom ISF outside Additional Module Folders works with `isfFilename="/abs/path.fs"` on the node (Builder: `node(name, isf=path)`).
- Magic has no Ableton Link, NDI, Art-Net/sACN/DMX or MTC. See mmv-midi-osc-control and mmv-output-mapping for bridges.
- Coordinates: y is -1..1 (bottom to top), x edge = aspect ratio. Scale 1 square = frame height.

## Where the facts come from

App bundle docs (User's Guide, VersionHistory, 36 sample projects, module `.fs` files), strings in the `Magic` binary, saved projects from real use, and live frames (Syphon grabs of generated projects). Format detail: [references/format.md](references/format.md). Verification protocol and pitfalls: [references/verification.md](references/verification.md).
