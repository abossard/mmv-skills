---
name: mmv-shaders-isf-glsl
description: Write, port, lint and debug shaders for Magic Music Visuals - ISF 2.0 generators and effects, audio FFT shaders, multi-pass and persistent-buffer feedback, GLSLShader (Shadertoy/GLSL Sandbox style) files, custom module folders, and the ISF AI Prompt window. Use when creating a new look in GLSL, porting a Shadertoy shader, fixing an "ISF Code Errors" dialog, or deciding how a custom .fs gets loaded into a generated project.
---

# Shaders for Magic (ISF, GLSL)

Prerequisite: [mmv-core](../mmv-core/SKILL.md). Shader work flow: write `.fs`, `python3 scripts/isf_lint.py --params X.fs`, put it in a module folder or reference it by `isf=`, `mmv_verify.py --live`, look at the frame.

## Which route

| Need | Route |
|---|---|
| Generator or effect with sliders, colors, audio | ISF `.fs` (this skill) |
| Quick Shadertoy / GLSL Sandbox paste | `GLSLShader` module with a `.txt` file; uniforms `time`, `resolution`, `mouse` (X/Y/Z/W Param) |
| Native speed, no shader | built-in modules |
| Let an LLM write it | Window > ISF AI Prompt Window (Shift+Cmd+U, needs a key), then lint the result |

## Getting a custom `.fs` into a project

1. `isfFilename`: `s.node("MyShader", {...}, isf="/abs/MyShader.fs")` (verified live; no Additional Module Folder needed). The path is absolute; move the project and the shader together or regenerate.
2. Additional Module Folder (Help > Additional Module Folders, restart Magic): shader appears in the menu and projects reference it by name only. Preferences belong to whoever uses Magic: ask before changing them.
3. `ISFShader` module + `File` param (GUI route).

The node's `pluginName` is the module name (file stem). Param names Magic shows/saves: `LABEL` else `NAME` capitalised; `point2D` -> `Name X`/`Name Y`; `color` -> `Name R/G/B/A`; `TIME` use adds `Speed` (saved as `Speed (M)` when an input's NAME or LABEL contains "speed"); an `audio`/`audioFFT` input is a param named after its LABEL (`Source`, `FFT`, `Wave`) and an `audio` input also adds `Overwrite`. `isf_lint.py --params` prints them. `long` params store the option INDEX. For an `audio`/`audioFFT` input set the param to `"layer:Source 0"` in Builder values (resolves to the Layer id; verified with `Source`).

## ISF 2.0 skeleton

```glsl
/*{
  "DESCRIPTION": "...", "CREDIT": "...", "ISFVSN": "2.0", "CATEGORIES": ["Generator"],
  "INPUTS": [
    {"NAME": "inputImage", "TYPE": "image"},                      // pin = effect. Omit for generators.
    {"NAME": "amount", "LABEL": "Amount", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
    {"NAME": "tint", "TYPE": "color", "DEFAULT": [1.0, 0.3, 0.7, 1.0]}
  ]
}*/
void main() { vec2 uv = isf_FragNormCoord; gl_FragColor = vec4(uv, amount, 1.0); }
```

Auto-declared (never redeclare): `TIME TIMEDELTA RENDERSIZE PASSINDEX FRAMEINDEX DATE isf_FragNormCoord`, macros `IMG_PIXEL IMG_NORM_PIXEL IMG_SIZE`. Input NAME is the GLSL variable. Templates in `assets/templates/` (all verified to compile and render in Magic 3.0b6): `T_Generator`, `T_Effect`, `T_TwoInputs`, `T_AudioFFT`, `T_Feedback`.

Rules that matter for looks:
- Output alpha: opaque `1.0` for backgrounds; alpha 0 where a layer should be empty so stacking works. Opaque generators need Blend Screen(9)/Add(4) to combine.
- Coordinates: `uv` 0..1; multiply x by `RENDERSIZE.x / RENDERSIZE.y` for round shapes.
- Anti-alias with `1.5 / RENDERSIZE.y` smoothstep widths; `fwidth()` works.
- Audio-driven params: expose floats (`pulse`, `level`) and link them to Globals in Magic; do not read audio inside the shader unless you need the spectrum.
- Time: use `TIME` plus Magic's `Speed` param (it scales time per module), not hard-coded rates.
- Multi-pass/feedback: `"PASSES": [{"TARGET": "buf", "PERSISTENT": true, "FLOAT": true}, {}]`; reset with `FRAMEINDEX == 0`; lower pass size for speed (`"WIDTH": "$WIDTH/2"`).
- Performance: stay at 60 fps at the project resolution; raymarch <= 64-128 steps live; cache texture reads.

## Compatibility (measured, not assumed)

Magic 3.0b6 macOS arm64 compiled all 20 tested constructs: `tanh`, `2.0f`, `round`, `trunc`, `sinh`, `uint`, shifts, bit-and, `int % int`, `isnan`, array constructors, `precision`, `#version 120`, `fwidth`, non-constant loop bound, `const` with a function call, int `max`. Real errors (syntax, undeclared identifier, type mismatch) open `ISF Code Errors: <Module>` with GL log lines (`ERROR: 0:2: ...`, line numbers count from the line after the JSON header) and the module draws nothing.

Older guidance (GLSL 1.20 profile, written against Magic 2.5 and earlier builds) lists these constructs as forbidden. Keep new shaders clean of them when they must also run in Magic 2.5; `isf_lint.py --strict` enforces it. Details and the full rule table: [references/glsl-compat.md](references/glsl-compat.md).

## Debug loop

1. `isf_lint.py` (structure, forbidden constructs, param names).
2. `mmv_verify.py proj.magic --live --yes --dismiss --out f.png`: reports `ISF Code Errors` windows by module name.
3. Black module but no dialog: alpha 0, wrong `Source`, image input unconnected, or output below horizon of your own math. Output a debug color first (`gl_FragColor = vec4(uv, 0.0, 1.0)`).
4. Compare with a bundled shader of the same kind: `Modules/` and `Modules2/` in the app bundle (`FFT Filled Waveform`, `Bloom`, `Mirror`...).

## Reuse before writing

- 187 bundled ISF modules in 189 `.fs` files (Kaleidoscope and Posterize also exist in `Modules2/Stylize`; list in `mmv-core/references/module-catalog.md`).
- Community ISF collections (editor.isf.video and others): check each shader's licence (many are CC-BY-NC-SA, non-commercial) and keep its CREDIT line.
- Retro shaders written for these skills: `mmv-scene-recipes/assets/isf/` (RetroSun, SynthGrid, SunsetSky, RetroMountains, RetroCRT).
- ISF spec and editor: isf.video, editor.isf.video. Shadertoy ports: replace `iTime` -> `TIME`, `iResolution` -> `RENDERSIZE`, `fragCoord` -> `isf_FragNormCoord * RENDERSIZE.xy`, `mainImage` -> `main` writing `gl_FragColor`; channels become `image` inputs.
