#!/usr/bin/env python3
"""Lint ISF (.fs) shaders for Magic Music Visuals (GLSL 1.20 profile, ISF 2.0 JSON header).

    python3 isf_lint.py FILE.fs [FILE.fs ...]       exit 1 if any error
    python3 isf_lint.py --params FILE.fs            also print the param names Magic will show/save

Portability rules (GLSL 1.30+ constructs) are WARNINGS by default: Magic 3.0b6 on macOS arm64 compiled all
20 constructs tested (tanh, 2.0f, round, uint, shifts, int %, arrays, precision, #version 120, ...). They are
errors with --strict, for projects that must also run in Magic 2.5 or other builds. Static only: it cannot compile GLSL. Final proof is loading the shader in Magic (see mmv-core
verification) and reading the error dialog, whose line numbers refer to the .fs file without the
JSON header. Rules come from real Magic compile errors from older GLSL 1.20 guidance.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mmv-core", "scripts"))
import magicproj  # noqa: E402

AUTO_UNIFORMS = ("TIME", "TIMEDELTA", "RENDERSIZE", "PASSINDEX", "FRAMEINDEX", "DATE", "isf_FragNormCoord", "isf_FragCoord")
TYPES = {"event", "bool", "long", "float", "point2D", "color", "image", "audio", "audioFFT", "text"}

# (regex, message). Applied to code with comments and strings removed.
RULES = [
    (r"\b(max|min)\s*\(\s*-?\d+\s*,\s*-?\d+\s*\)", "int overload of max/min does not exist in GLSL 1.20; use floats"),
    (r"\bclamp\s*\(\s*-?\d+\s*,", "int overload of clamp does not exist; use floats"),
    (r"\btanh\s*\(", "tanh() is GLSL 1.30+; add a _tanh polyfill"),
    (r"\b(sinh|cosh|asinh|acosh|atanh)\s*\(", "hyperbolic functions are GLSL 1.30+"),
    (r"\bu(int|vec[234])\b", "unsigned types are not available"),
    (r"<<|>>", "bit shifts are not available"),
    (r"(?<![&])&(?![&])|(?<![|])\|(?![|])|\^", "bitwise operators are not available (^ is not xor in GLSL anyway)"),
    (r"\bround\s*\(", "round() is GLSL 1.30+; use floor(x + 0.5)"),
    (r"\b(trunc|roundEven)\s*\(", "trunc/roundEven are GLSL 1.30+"),
    (r"\b\d+\.\d*f\b|\b\d+f\b", "C-style float suffix (2.0f) is invalid"),
    (r"^\s*precision\b", "precision qualifiers are not needed and fail in desktop GLSL 1.20"),
    (r"^\s*#version\b", "#version must be removed, ISF manages it"),
    (r"\btexture\s*\(", "texture() is GLSL 1.30+; use texture2D() or IMG_NORM_PIXEL"),
    (r"\b(isnan|isinf)\s*\(", "isnan/isinf are GLSL 1.30+; use (x != x) and (abs(x) > 1e37)"),
    (r"\b(float|vec[234]|int|ivec[234])\s*\[\s*\w*\s*\]\s*\(", "array constructors are GLSL 1.30+"),
    (r"^\s*#ifdef\s+GL_ES", "GL_ES blocks are not needed (desktop host)"),
    (r"\bIMG_(NORM_)?PIXEL\s*\([^;]*\bivec2\b", "IMG_PIXEL expects vec2, not ivec2"),
    (r"%", "% is not available in GLSL 1.20, not even for ints; use mod(float(a), float(b))"),
    (r"^\s*(?:flat\s+|smooth\s+)?(?:in|out)\s+\w+\s+\w+\s*;|\blayout\s*\(", "GLSL 1.30+ in/out/layout declaration; use varying and gl_FragColor"),
]


def strip_comments_strings(src):
    src = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    return re.sub(r'"[^"\n]*"', '""', src)


def parse_header(text):
    m = magicproj.ISF_HEADER.search(text)
    if not m:
        return None, None, "no /*{ ... }*/ JSON header"
    try:
        return magicproj.isf_header(text)[0], m.end(), None
    except ValueError as e:
        return None, m.end(), "header is not valid JSON: %s" % e


def magic_params(text):
    """Param names Magic shows and saves for the shader source `text` (shared with magicproj.isf_params)."""
    return list(magicproj.isf_params(text))


def lint(path, strict=False):
    errs, warns = [], []
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    header, end, herr = parse_header(text)
    if herr:
        errs.append((1, herr))
        return errs, warns, None
    if str(header.get("ISFVSN", "2")).split(".")[0] != "2":
        warns.append((1, "ISFVSN is not 2.x; Magic expects ISF 2.0"))
    names = set()
    has_image = False
    for i in header.get("INPUTS", []):
        n, t = i.get("NAME"), i.get("TYPE")
        if not n:
            errs.append((1, "an INPUT has no NAME"))
            continue
        if n in names:
            errs.append((1, "duplicate input NAME %r" % n))
        names.add(n)
        if t not in TYPES:
            errs.append((1, "input %r: unknown TYPE %r" % (n, t)))
        if t == "image":
            has_image = True
        if n in AUTO_UNIFORMS:
            errs.append((1, "input NAME %r clashes with an auto-declared uniform" % n))
        if t == "long":
            v, l = i.get("VALUES"), i.get("LABELS")
            if not v:
                pass        # a plain integer (MIN/MAX) is valid
            elif l and len(l) != len(v):
                errs.append((1, "long input %r: LABELS and VALUES differ in length" % n))
            elif isinstance(i.get("DEFAULT"), (int, float)) and v and i["DEFAULT"] not in v:
                warns.append((1, "long input %r: DEFAULT %r is not in VALUES (Magic stores the option INDEX)" % (n, i["DEFAULT"])))
        if t in ("float", "point2D") and "MIN" in i and "MAX" in i and isinstance(i["MIN"], (int, float)) and i["MIN"] > i["MAX"]:
            errs.append((1, "input %r: MIN > MAX" % n))
        if t == "color" and not (isinstance(i.get("DEFAULT"), list) and len(i["DEFAULT"]) == 4):
            warns.append((1, "color input %r should have a 4 element DEFAULT" % n))
    code_all = text[end:]
    base_line = text[:end].count("\n")
    code = strip_comments_strings(code_all)
    lines = code.split("\n")
    for rx, msg in RULES:
        for ln, line in enumerate(lines, 1):
            if re.search(rx, line):
                (errs if strict else warns).append((base_line + ln, "portability: " + msg))
    for ln, line in enumerate(lines, 1):
        m = re.search(r"\buniform\s+\w+\s+(\w+)", line)
        if m and (m.group(1) in AUTO_UNIFORMS or m.group(1) in names):
            errs.append((base_line + ln, "uniform %s is declared by ISF; remove the declaration" % m.group(1)))
    if not re.search(r"\bvoid\s+main\b", code):
        errs.append((base_line + 1, "no void main()"))
    if "gl_FragColor" not in code:
        errs.append((base_line + 1, "never writes gl_FragColor"))
    for loop in re.finditer(r"for\s*\([^;]*;[^;]*<=?\s*([A-Za-z_]\w*)\s*;", code):
        bound = loop.group(1)
        if not re.search(r"#define\s+%s\b|\bconst\s+\w+\s+%s\b" % (bound, bound), code):
            warns.append((base_line + code.count("\n", 0, loop.start()) + 1,
                          "for-loop bound %s looks non-constant; GLSL 1.20 needs compile-time bounds (use a fixed bound and break)" % bound))
    if has_image and "IMG_" not in code and "texture2D" not in code and "inputImage" in code:
        warns.append((base_line + 1, "has an image input but never samples it with IMG_NORM_PIXEL/IMG_PIXEL"))
    return errs, warns, header


def main(argv):
    show = "--params" in argv
    strict = "--strict" in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    bad = 0
    for f in files:
        errs, warns, header = lint(f, strict)
        for ln, msg in errs:
            print("%s:%s: error: %s" % (os.path.basename(f), ln, msg))
        for ln, msg in warns:
            print("%s:%s: warn: %s" % (os.path.basename(f), ln, msg))
        if show and header:
            with open(f, encoding="utf-8", errors="replace") as fh:
                print("%s params: %s" % (os.path.basename(f), ", ".join(magic_params(fh.read()))))
        print("%s: %d errors, %d warnings" % (os.path.basename(f), len(errs), len(warns)))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
