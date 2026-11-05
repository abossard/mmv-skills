# GLSL compatibility table

Measured on MagicBeta 3.0b6, macOS arm64, 2026-11-04: every construct below compiled. A shader `T_x.fs` computed `float t = <expr>` and drew red when it compiled; 20 of 20 drew red. Three deliberately broken shaders raised `ISF Code Errors` dialogs.

Source of the "forbidden" list: older GLSL 1.20 guidance (errors seen with earlier builds). Use it as a portability checklist, not as truth for 3.0b6.

| Construct | 3.0b6 arm64 | Portable replacement |
|---|---|---|
| `tanh`, `sinh`, `cosh` | compiles | polyfill `_tanh(x) = (e-1)/(e+1)` with `e = exp(2.0*clamp(x,-20.,20.))` |
| `2.0f` suffix | compiles | `2.0` |
| `round`, `trunc` | compiles | `floor(x + 0.5)`, `floor` or `sign(x)*floor(abs(x))` |
| `int` overloads `max/min/clamp/abs` | compiles | cast to float |
| `uint`, `uvec*` | compiles | `int` or `float` |
| `<<`, `>>`, `&`, `\|`, `^` | compiles | `floor`/`mod` arithmetic, `fract(sin(dot()))` hash |
| `int % int` | compiles | `mod(float(a), float(b))` |
| `isnan`, `isinf` | compiles | `x != x`, `abs(x) > 1e37` |
| `float[N](...)` constructor | compiles | assign elements inside a function |
| `precision highp float;` | compiles | remove |
| `#version 120` | compiles | remove (ISF manages it) |
| non-constant `for` bound | compiles | fixed bound plus `if (i > n) break;` |
| `const float K = sin(1.0);` | compiles | `#define` or literal |
| `texture()` | not tested | `texture2D` or `IMG_NORM_PIXEL` |
| `ivec2` in `IMG_PIXEL` | not tested | `vec2` |
| `fwidth` | compiles | none needed |

Other rules from that guidance that hold regardless:
- Final alpha must be set; black output with alpha 0 can read as empty.
- Divide safely: `x / max(d, 0.001)`.
- Do not redeclare ISF-managed uniforms or input NAMEs; buffer names must not also appear in IMPORTED.
- Black screen: alpha 0, or a gate on a dead uniform; add a floor like `max(v, 0.05)` while debugging.
- Licences: bareimage/rhythmic-visions are CC-BY-NC-SA, keep CREDIT.

## Error dialog quick reference

| Message | Cause |
|---|---|
| `Use of undeclared identifier 'X'` | cascading from an earlier error, a misspelled input NAME, or a redeclared uniform |
| `Invalid call of undeclared identifier 'f'` | function not available or defined after use |
| `Incompatible types in initialization` | `vec3 t = 1.0;` style mismatch |
| `syntax error` | stray `f` suffix, missing `;`, GLSL 1.30 syntax |
