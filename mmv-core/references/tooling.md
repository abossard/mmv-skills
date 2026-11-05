# Tooling reference

All commands: `python3 <skills>/mmv-core/scripts/magicproj.py <cmd>`. Standard library only, except `grab` (needs syphon-python; it re-runs itself under `python3.13` with `PYTHONPATH=~/.local/lib/python3.13/site-packages`, override `SYPHON_PYTHON`, `SYPHON_PYTHONPATH`).

| Need | Command |
|---|---|
| Overview: scenes, playlist, Syphon, audio, sources | `info FILE` |
| Every Global: source, value, modifier chain | `globals FILE [--name REGEX]` |
| Modules per scene with params and links | `nodes FILE [--scene NAME] [--plugin REGEX]` |
| OSCSender addresses and targets | `osc FILE` |
| Validate (exit 1 on errors) | `check FILE` |
| Semantic diff | `diff A B` |
| Param names and defaults | `catalog [--plugin REGEX] [FILES]` |
| Raw XML | `decode FILE [-o X.xml]`, `encode X.xml -o FILE` |
| Edit | `set FILE -o OUT ...` (or `--in-place`; there is no default overwrite) |
| Open in running Magic (replaces project) | `load FILE` |
| One Syphon frame, stats, PNG | `grab --server NAME --out f.png --wait 5` |
| Play/pause audio files | `play` |
| Log OSC Magic sends | `listen PORT --seconds 3` |

Environment: `MAGIC_APP` (default MagicBeta.app, else Magic.app), `MMV_MODULE_DIRS` (extra ISF folders for `check`/`catalog`, `:` separated), `MAGICPROJ_RESERVED_PORTS`.

## Builder

```python
import sys; sys.path.insert(0, "<skills>/mmv-core/scripts")
import magicproj as m

b = m.Builder(syphon="MyScene", size=(1920, 1080), fps=60, audio_device=None, osc_in=None)
b.glob("Bass", 0, "audio:Source 0:Freq. Range:20-80 Hz", [("Expression", "x*3"), ("Smooth", 0.4), ("Clamp", 1)])
s = b.scene("Main")
poly = s.node("Polygon", {"Sides": 6})
col = s.node("ColorHSB", {"Hue": ("global:Bass", [("Scale", 0.3)], 0), "Saturation": 1, "Brightness": 1}, inputs=[poly])
s.output(col)                       # first output = top pin = drawn in front
root = b.build()
root = m.set_playlist(root, names=["Main"], seconds=600)
m.write("out.magic", root)
```

- Param value: constant, or `(source, [modifiers], manual_value)`. `bypass=` and `power=` take the same.
- Sources: `None` manual, `calc` (input 0, modifiers compute), `global:Name`, `internal:Iteration #`, `audio:<Source name>:<Volume|Freq. Range|Best Pitch|Tone>[:<20-80 Hz|80-320 Hz|320-1.2k Hz|1.2k-5k Hz|5k-20k Hz|Custom Freq.|Iterator Freqs.>]`, `midi:<Source>:<feature>[:<sub>]` (only on a built root that already has the MIDI source: `add_midi_in`, then `add_global`/`edit_param`; `Builder.glob` cannot resolve it), `osc:/address` (needs `Builder(osc_in=PORT)`).
- Modifiers: `(name, number)` with names Gate Scale Offset Power Smooth Wrap Random Ramp Sine Triangle Threshold Average Peak Exponent Clamp Step Increase Trigger Invert Hold Delay Expression RandomTrigger; `("Expression", "x*Gain")`.
- `s.node(plugin, values, inputs=[...], isf=None)`: `inputs` order = pin order (first = top pin). `isf="/abs/file.fs"` for shaders outside the Additional Module Folders.
- `s.scene_module(other_scene)`: draws another scene as a module. `s.scene_input()`: SceneInput module (the scene becomes an effect; one pin per SceneInput on the scene module).
- `s.chain(a, b, c)`: b gets a as input, c gets b.
- Library edits return copies: `edit_global`, `edit_param`, `add_global`, `remove_global`, `connect`, `set_syphon`, `set_osc_target`, `add_midi_in`, `route_source`, `set_playlist`, `set_osc_in`, `add_audio`.
- `b.write("out.magic")` writes a Builder project directly; use `root = b.build()` + `m.write(path, root)` only when you post-process (`set_playlist`, `add_midi_in`, `add_audio`).
- `m.check(root, base_dir)` returns `[(level, msg)]`. Source `Source` params: pass `"layer:Source 0"` as the value.

## Edit an existing project

```bash
python3 magicproj.py set in.magic -o out.magic --value Gain 0.7 --syphon on --syphon-name Main --size 1920x1080
python3 magicproj.py set in.magic -o out.magic --source Bass 'audio:Source 0:Freq. Range:20-80 Hz' --mods Bass 'Smooth:0.4; x*Gain*3; Clamp:1'
python3 magicproj.py set in.magic -o out.magic --param Main/12/Hue @global:Bass     # SCENE/NODE_ID/PARAM; node ids come from `nodes`
```
