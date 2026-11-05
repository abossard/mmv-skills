# MMV skills (Magic Music Visuals)

Claude Code skills for generating, editing and verifying Magic Music Visuals scenes (`.magic`). Built 2026-11-04 against MagicBeta 3.0b6 on macOS arm64 and the bundled docs, samples and modules.

## Skills

| Skill | Covers |
|---|---|
| [mmv-core](mmv-core) | entry point; .magic format, `magicproj.py` CLI + `Builder`, `mmv_verify.py` (static + live load + Syphon grab), module catalog of all 222 modules, verification protocol |
| [mmv-scenes-and-connections](mmv-scenes-and-connections) | scene graph, pin order, compositing (Blend/Mask/Mix/MultiMix/InputSelector), scene modules, SceneInput, post buses, Iterator, groups, playlist structure |
| [mmv-audio-reactivity](mmv-audio-reactivity) | inputs, features, modifier cookbook, Globals bank (`audio_bank.py`: bands, Kick, Dt, Beat4, Build), semantics and tuning |
| [mmv-midi-osc-control](mmv-midi-osc-control) | MIDI/OSC sources and features, OSC in/out, Learn, MIDI clock, Ableton workflow, what Magic lacks (Link, NDI, DMX) and bridges |
| [mmv-shaders-isf-glsl](mmv-shaders-isf-glsl) | ISF 2.0 authoring, GLSLShader, loading custom `.fs`, `isf_lint.py`, five verified templates, measured GLSL compatibility table |
| [mmv-3d-geometry](mmv-3d-geometry) | measured camera/coordinates, transform order, Model, Iterator grids, DepthTest, MSAA, flattening rule |
| [mmv-effects-color](mmv-effects-color) | effect order, color modules, blend index table, palettes, chains per look, cost list |
| [mmv-output-mapping](mmv-output-mapping) | Syphon out, resolution choice, mapping-app workflow, calibration scene generator, fullscreen, NDI bridging, export |
| [mmv-vj-performance](mmv-vj-performance) | set structure, playlist, live editing, frame budget, safety, pre-show checklist |
| [mmv-scene-recipes](mmv-scene-recipes) | recipe index; full retro sunset generator (5 palettes) with five original ISF shaders; sketches for more looks |

## Requirements

- macOS with Magic 3.0b6 in `/Applications` (`MagicBeta.app`, else `Magic.app`, or set `MAGIC_APP`) and Python 3.9+ (`ET.indent`). The Builder, `check`, `diff`, `catalog` and `isf_lint` need nothing else; `gen_catalog.py` needs the app.
- `magicproj.py load|play` and `mmv_verify.py --live` drive Magic through System Events: allow your terminal under System Settings > Privacy & Security > Accessibility and Automation. Without it they stop with a message.
- `magicproj.py grab` (and `--live`) needs `syphon-python` importable by `python3.13` (`SYPHON_PYTHON`, packages in `~/.local/lib/python3.13/site-packages`, override with `SYPHON_PYTHONPATH`). Install it with `python3.13 -m pip install --user syphon-python`.
- Tools:
  - `python3 mmv-core/scripts/magicproj.py <cmd>` (commands: `mmv-core/references/tooling.md`; `set` needs `-o OUT` or `--in-place`).
  - `python3 mmv-core/scripts/mmv_verify.py FILE` static check; `--live --yes` loads it into Magic (see Limits).
  - `cd mmv-core/scripts && python3 gen_catalog.py > catalog.tmp && mv catalog.tmp ../references/module-catalog.md` regenerates the catalog (needs the app; with a plain `>` into the catalog a failed run would empty it, so go through the temp file).
  - `python3 mmv-shaders-isf-glsl/scripts/isf_lint.py [--params] [--strict] X.fs` lints a shader.
  - `MMV_AUDIO_DEVICE` (or `--audio-device`) sets the audio input of `retro_sunset_example.py`; `MMV_MODULE_DIRS` adds ISF folders for `check`/`catalog`; `MMV_ALLOW_LIVE=1` is the env form of `--yes`.

Get the skills: `git clone https://github.com/abossard/mmv-skills && cd mmv-skills`. Install into Claude Code (symlinks, keeps sibling paths working; existing links are replaced, a real folder of the same name is skipped, uninstall by deleting the links):

```bash
./install.sh            # links every mmv-* folder into ~/.claude/skills
./install.sh ./project/.claude/skills   # or into a project
```

## Retro sunset quick start

```bash
python3 mmv-scene-recipes/scripts/retro_sunset_example.py ~/Desktop/sunset.magic --palette synthwave --size 1920x1080
python3 mmv-core/scripts/mmv_verify.py ~/Desktop/sunset.magic          # static check
open -a MagicBeta ~/Desktop/sunset.magic                                # or mmv_verify.py --live --yes --restore (replaces the open project: ask first, `--yes` confirms you did)
```
Preview: `mmv-scene-recipes/assets/retro_sunset_preview.png`.

## How it was verified

Everything below ran against the real app (MagicBeta 3.0b6, macOS arm64); nothing is only "from docs" unless tagged in the references.

| Claim | Evidence |
|---|---|
| Format: 3 ignored header bytes + zlib XML, all element/attribute names | decoded 36 bundled samples + 11 user projects; strings of the `Magic` binary; generated files with a made-up header load |
| Builder output opens without dialogs and renders | live Syphon grabs: orange square test, sunset, bars, templates, 3D |
| Custom ISF through `isfFilename` | 10+ shaders compile and render |
| Broken shader and unknown module are detectable | `ISF Code Errors: <name>` and `Warning...` windows reported by `mmv_verify.py` |
| `long` params store the option index | Blend modes measured pixel-exact; God Rays/Diagonal Blur defaults |
| 20 GLSL constructs compile on 3.0b6 | battery shader grid, all red |
| Audio Globals react; `Dt`, `Kick`, `Beat4` behave | looping 124 BPM WAV, bar chart read from PNGs |
| OSC input drives a param | UDP packets to a custom port, red 143 vs 0 |
| Scene module, SceneInput, Bloom, custom CRT | sunset render |
| 3D: Iterator + Model + DepthTest + MSAA; camera distance about 2.4 | cube field and 3-cube depth probe |
| Calibration scene | render check |
| Fresh-session test | a new agent with only these skills built a 12-square audio-reactive ring + Bloom; static check passed, live load rendered it (doc gaps it found are fixed) |
| Magic lacks Link/NDI/Art-Net/MTC | string search of the binary |

Unit tests (none of them starts Magic unless `MAGICPROJ_LIVE=1`): from `mmv-core/scripts` run `python3 -m unittest test_magicproj test_review_fixes` (also work as `python3 test_magicproj.py`); `python3 mmv-shaders-isf-glsl/scripts/test_isf_lint.py`. Tests that read Magic's sample projects skip without the app. `test_review_fixes.py` holds one test per fix from the independent review.

## Findings that differ from common assumptions

- ISF `long` values (Blend `Mode`, quality menus) are stored as the 0-based option index; the ISF header lists 1-based VALUES, but Blend Screen is stored as 9, not 10.
- Magic 3.0b6 on macOS compiles GLSL 1.30 style constructs that older GLSL 1.20 guidance forbids (see `mmv-shaders-isf-glsl/references/glsl-compat.md`); the forbidden list is kept as a portability lint.
- Frame time `Dt`: a lag Global defined as source `global:Time` gave Dt = 0 in testing; defined as `calc` + Expression `Time` it gave the real frame time (about 8.7 ms on a 120 Hz display). `audio_bank.py` uses the `calc` form.

## Lineage and credit

The format research, the `magicproj` CLI/`Builder` and the module parameter table grew out of the author's earlier, unpublished scene tooling and are extended here: `isf=` nodes, `scene_input()`, `layer:` sources, `MMV_MODULE_DIRS`, `mmv_verify.py`, the catalog generator. Ideas, shaders and scene code in this repository are original; nothing from Magic's application bundle is redistributed (see Licence).

## Licence and third-party material

- Code, shaders, templates and docs in this repository: MIT, see `LICENSE`.
- Magic Music Visuals is a product of Color & Music, LLC. This project is independent and not affiliated with or endorsed by them. No file from Magic's application bundle (modules, shaders, sample projects, User's Guide, help text) is included. `mmv-core/scripts/magic_modules_v3.json` and `mmv-core/references/module-catalog.md` list parameter names, defaults, option lists and ranges as interoperability data; shader description prose is not copied.
- Tests and `gen_catalog.py` read Magic's bundled sample projects and shader headers from your own installation at run time when it is present.
- The five retro shaders and the templates are original work. ISF is an open specification by Vidvox; shaders you copy from community collections carry their own licences (many are CC-BY-NC-SA).
- `.magic` files are not committed (`.gitignore`); generate them with the scripts.

## Limits

- Live verification replaces the project open in the single running Magic. `--live` refuses to run without `--yes` (or `MMV_ALLOW_LIVE=1`). `--restore` reopens it afterwards, but only a saved project whose file name is unique among Magic's recent files; otherwise `--live --restore` refuses to start. Ask whoever is using Magic first and run it only when nobody is performing.
- Machine-specific observations (display refresh, ports, controllers) come from one MacBook running MagicBeta 3.0b6 and may differ on yours.
- No Windows testing; Spout and DirectShow modules are documented from the guide only.
- Not tested: MIDI hardware, MIDI clock from Live, mapping-app ingest (Millumin, MadMapper), ISF AI window, movie export, password protection.
- ISF is compiled by Magic; `isf_lint.py` is static.
