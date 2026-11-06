# MMV skills (Magic Music Visuals)

Claude Code skills that generate, edit and verify Magic Music Visuals scenes (`.magic`). Built on 2026-11-04 against MagicBeta 3.0b6 on macOS arm64.

## Skills

| Skill | Covers |
|---|---|
| [mmv-core](mmv-core) | Entry point. The .magic format, the `magicproj.py` CLI and `Builder`, `mmv_verify.py` (static check, live load, Syphon grab), a catalog of all 222 modules, the verification protocol |
| [mmv-scenes-and-connections](mmv-scenes-and-connections) | Scene graph, pin order, compositing (Blend, Mask, Mix, MultiMix, InputSelector), scene modules, SceneInput, post buses, Iterator, groups, playlist structure |
| [mmv-audio-reactivity](mmv-audio-reactivity) | Inputs, features, modifier cookbook, the Globals bank in `audio_bank.py` (bands, Kick, Dt, Beat4, Build), tuning |
| [mmv-midi-osc-control](mmv-midi-osc-control) | MIDI and OSC sources and features, OSC in and out, Learn, MIDI clock, Ableton workflow, what Magic lacks (Link, NDI, DMX) and bridges |
| [mmv-shaders-isf-glsl](mmv-shaders-isf-glsl) | ISF 2.0 authoring, GLSLShader, loading custom `.fs` files, `isf_lint.py`, five verified templates, a measured GLSL compatibility table |
| [mmv-3d-geometry](mmv-3d-geometry) | Measured camera and coordinates, transform order, Model, Iterator grids, DepthTest, MSAA, the flattening rule |
| [mmv-effects-color](mmv-effects-color) | Effect order, color modules, blend index table, palettes, chains per look, cost per effect |
| [mmv-output-mapping](mmv-output-mapping) | Syphon out, resolution, mapping-app workflow, calibration scene generator, fullscreen, NDI bridging, export |
| [mmv-vj-performance](mmv-vj-performance) | Set structure, playlist, live editing, frame budget, safety, pre-show checklist |
| [mmv-scene-recipes](mmv-scene-recipes) | Recipe index, a full retro sunset generator (5 palettes, 5 original ISF shaders), sketches for more looks |

## Install

With [`npx skills`](https://github.com/vercel-labs/skills), into the current project's `.claude/skills`:

```bash
npx skills add abossard/mmv-skills -a claude-code
npx skills add abossard/mmv-skills -a claude-code -g   # user-wide (~/.claude/skills)
npx skills add abossard/mmv-skills --list              # list the skills without installing
```

- Install all 10. The skills call each other's scripts as siblings (`../mmv-core/scripts/...`) and `mmv-core` holds the shared tooling. Installing a subset with `--skill` breaks those paths.
- Remove with `npx skills remove`, update with `npx skills update`.

Or clone and link:

```bash
git clone https://github.com/abossard/mmv-skills && cd mmv-skills
./install.sh                            # links every mmv-* folder into ~/.claude/skills
./install.sh ./project/.claude/skills   # or into a project
```

`install.sh` replaces existing links and skips a real folder of the same name. Uninstall by deleting the links.

## Requirements

- macOS, Magic 3.0b6 in `/Applications` (`MagicBeta.app`, else `Magic.app`, or set `MAGIC_APP`), Python 3.9+.
- The Builder, `check`, `diff`, `catalog` and `isf_lint` need nothing else. `gen_catalog.py` needs the app.
- `magicproj.py load|play` and `mmv_verify.py --live` drive Magic through System Events. Allow your terminal under System Settings > Privacy & Security > Accessibility and Automation, or they stop with a message.
- `magicproj.py grab` and `--live` need `syphon-python` importable by `python3.13`. Install it with `python3.13 -m pip install --user syphon-python`. Set `SYPHON_PYTHON` or `SYPHON_PYTHONPATH` if it lives elsewhere (default `~/.local/lib/python3.13/site-packages`).

## Tools

- `python3 mmv-core/scripts/magicproj.py <cmd>`: commands are in `mmv-core/references/tooling.md`. `set` needs `-o OUT` or `--in-place`.
- `python3 mmv-core/scripts/mmv_verify.py FILE`: static check. `--live --yes` loads the file into Magic (see Limits).
- `python3 mmv-shaders-isf-glsl/scripts/isf_lint.py [--params] [--strict] X.fs`: shader lint.
- Regenerate the catalog (needs the app). Write to a temp file first, because a failed run with a plain `>` would empty the catalog:

  ```bash
  cd mmv-core/scripts && python3 gen_catalog.py > catalog.tmp && mv catalog.tmp ../references/module-catalog.md
  ```
- Environment: `MMV_AUDIO_DEVICE` (or `--audio-device`) sets the audio input of `retro_sunset_example.py`. `MMV_MODULE_DIRS` adds ISF folders for `check` and `catalog`. `MMV_ALLOW_LIVE=1` replaces `--yes`.

## Retro sunset quick start

```bash
python3 mmv-scene-recipes/scripts/retro_sunset_example.py ~/Desktop/sunset.magic --palette synthwave --size 1920x1080
python3 mmv-core/scripts/mmv_verify.py ~/Desktop/sunset.magic          # static check
open -a MagicBeta ~/Desktop/sunset.magic                                # or mmv_verify.py --live --yes --restore
```

`--live` replaces the project open in Magic. Ask first: `--yes` confirms you did. Preview image: `mmv-scene-recipes/assets/retro_sunset_preview.png`.

## How it was verified

Every row ran against the real app (MagicBeta 3.0b6, macOS arm64). The references tag any claim that comes only from the docs.

| Claim | Evidence |
|---|---|
| Format: 3 ignored header bytes, then zlib XML, with all element and attribute names | Decoded 36 bundled samples and 11 other projects, read strings of the `Magic` binary, loaded generated files with a made-up header |
| Builder output opens without dialogs and renders | Live Syphon grabs of an orange square test, the sunset, bars, templates, 3D |
| Custom ISF loads through `isfFilename` | 10+ shaders compile and render |
| Broken shaders and unknown modules are detectable | `mmv_verify.py` reports the `ISF Code Errors: <name>` and `Warning...` windows |
| `long` params store the option index | Blend modes measured pixel-exact, God Rays and Diagonal Blur defaults |
| 20 GLSL constructs compile on 3.0b6 | Battery shader grid, all red |
| Audio Globals react, and `Dt`, `Kick`, `Beat4` behave | Looping 124 BPM WAV, bar chart read from PNGs |
| OSC input drives a param | UDP packets to a custom port, red channel 143 against 0 |
| Scene module, SceneInput, Bloom, custom CRT | Sunset render |
| 3D: Iterator, Model, DepthTest, MSAA, camera distance about 2.4 | Cube field and 3-cube depth probe |
| Calibration scene | Render check |
| A fresh session can use the skills | A new agent with only these skills built a 12-square audio-reactive ring with Bloom. The static check passed and the live load rendered it. The doc gaps it found are fixed |
| Magic has no Link, NDI, Art-Net or MTC | String search of the binary |

Tests never start Magic unless `MAGICPROJ_LIVE=1`. Tests that read Magic's sample projects skip without the app.

```bash
cd mmv-core/scripts && python3 -m unittest test_magicproj test_review_fixes
python3 mmv-shaders-isf-glsl/scripts/test_isf_lint.py
```

`test_review_fixes.py` has one test per fix from the independent review.

## Findings that differ from common assumptions

- Magic saves ISF `long` values (Blend `Mode`, quality menus) as the 0-based option index. The ISF header lists 1-based values, so Blend Screen saves as 9, not 10.
- Magic 3.0b6 on macOS compiles GLSL 1.30 constructs that older GLSL 1.20 guidance forbids (see `mmv-shaders-isf-glsl/references/glsl-compat.md`). The old forbidden list stays as a portability lint.
- A lag Global with source `global:Time` gave `Dt` = 0. Defined as `calc` with Expression `Time`, it gave the real frame time (about 8.7 ms on a 120 Hz display). `audio_bank.py` uses the `calc` form.

## Lineage

The format research, the `magicproj` CLI and `Builder`, and the module parameter table come from the author's earlier, unpublished scene tooling. This repository extends them with `isf=` nodes, `scene_input()`, `layer:` sources, `MMV_MODULE_DIRS`, `mmv_verify.py` and the catalog generator. The shaders and scene code are original. This repository ships nothing from Magic's application bundle.

## Licence

- Code, shaders, templates and docs: MIT, see `LICENSE`.
- Magic Music Visuals is a product of Color & Music, LLC. This project is independent and not affiliated with or endorsed by them.
- It includes no file from Magic's application bundle (modules, shaders, sample projects, User's Guide, help text). `mmv-core/scripts/magic_modules_v3.json` and `mmv-core/references/module-catalog.md` list parameter names, defaults, option lists and ranges as interoperability data. Shader description text is not copied.
- The tests and `gen_catalog.py` read Magic's sample projects and shader headers from your own installation at run time.
- The five retro shaders and the templates are original. ISF is an open specification by Vidvox. Shaders you copy from community collections carry their own licences (many are CC-BY-NC-SA).
- `.magic` files are not committed (see `.gitignore`). Generate them with the scripts.

## Limits

- Live verification replaces the project open in the single running Magic. `--live` refuses to run without `--yes` or `MMV_ALLOW_LIVE=1`. `--restore` reopens the project afterwards, but only if it is a saved project with a file name that is unique among Magic's recent files. Otherwise `--live --restore` refuses to start. Ask whoever is using Magic first, and run it only when nobody is performing.
- Observations about display refresh, ports and controllers come from one MacBook running MagicBeta 3.0b6 and may differ on yours.
- Not tested on Windows. Spout and DirectShow modules are documented from the guide only.
- Not tested: MIDI hardware, MIDI clock from Live, mapping-app ingest (Millumin, MadMapper), the ISF AI window, movie export, password protection.
- `isf_lint.py` is static. Magic does the real ISF compile.
