# Verification protocol

## Levels

1. Static: `mmv_verify.py FILE` (dangling child ids, duplicate ids, scene-module cycles, missing Globals, unknown expression names, unknown modules, ISF param names that the shader does not declare, missing files). Exit 1 on errors.
2. Opens: `--live` loads the project in the running Magic, waits for the editor title, flags dialog windows. Measured: an unknown module opens `Warning...` ("The following module(s) could not be loaded: Name"); a shader that fails to compile opens `ISF Code Errors: <Module>` with lines like `ERROR: 0:2: Use of undeclared identifier 't'` (line numbers count from the line after the JSON header). Dialogs expose no AX buttons; `--dismiss` presses Return (brings Magic to the front first and stops if it cannot, so the key never reaches another app).
3. Renders: `--live` grabs a Syphon frame (needs `videoSharing="1"`; Builder `syphon="Name"`) and prints mean RGB and lit fraction. Always open the PNG and look.
4. Reacts: `--osc /addr=0.8 --osc-port N` (project needs `osc_in=N`), or `--play` with `magicproj.add_audio(root, wav)`. Compare two grabs.

## Test audio

Synthetic kick (sine sweep 160 to 50 Hz, exp decay) plus noise hats at 124 BPM, 16 s, 44.1 kHz stereo: any `wave`-module script. `add_audio(root, path, source="Source 0", loop=True)` routes Source 0/1 to the file; `--play` toggles Shift+Cmd+Space playback (brings Magic to the front, stops if it cannot).

## Pitfalls seen

- Syphon server list shows other apps first; pass `--server` with the project's `videoSharingName`.
- `open -n -a` and direct launch of the binary do not give a second instance (it exits). Only the running instance can be used.
- `--restore` prints `restored` only when the editor names the old project again; when it says it could not confirm, check Magic's window list.
- Magic is driven through System Events. The terminal needs Accessibility and Automation permission (System Settings > Privacy & Security); `mmv_verify.py --live` and `magicproj.py load|play` stop with a message when macOS denies it.
- `Blend Mode`, quality menus: index not value (see format.md).
- Opaque full-frame ISF generators hide everything beneath them; combine with Blend (Screen 9, Add 4) or give the shader alpha 0 where it should be empty.
- A scene only runs while something draws it. Put always-on modules (OSCSender) in their own scene used as a scene module from every shown scene.
- The expression `y*0.93` decays per frame, not per second; frame rate changes the feel. Prefer a `Dt` Global (Increase clock difference) for fixed-seconds decays.
- Never run `--live` while the user is performing. Ask first; the script refuses without `--yes` (or `MMV_ALLOW_LIVE=1`) and prints that reason without loading anything.

## What was tested live while writing these skills

| Test | Result |
|---|---|
| Builder project: Solid Color + Polygon + ColorRGB + Scale | opens, orange square on navy, exact |
| Custom ISF via `isfFilename` (5 shaders) | compile and render |
| Blend modes 1,2,3,4,5,8,9,10 on solid colors | index semantics measured to 0.01 |
| Scene module + SceneInput + Bloom + custom CRT | renders |
| Audio-driven Globals (looping WAV) | frame mean varies with beat |
| OSC in on custom port | red channel 143 at 1.0, 0 at 0.0 |
| Iterator + Model + DepthTest + Antialias MSAA 4 | nine lit cubes |
| 20 GLSL constructs (tanh, 2.0f, round, uint, shifts, int %, arrays, precision, #version 120, dynamic loop bound, const with function, ...) | all compile on 3.0b6 macOS arm64 |
| 3 broken shaders (syntax, undeclared, type error) | `ISF Code Errors` dialogs, detected |
| Unknown module name | `Warning...` dialog, detected |
| GLSLShader with bundled plasma6.txt | renders |
