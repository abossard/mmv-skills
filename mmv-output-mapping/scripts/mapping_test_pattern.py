#!/usr/bin/env python3
"""Calibration scene for projectors, LED walls and mapping apps (MadMapper, Millumin, Resolume).

    python3 mapping_test_pattern.py OUT.magic [--size 1920x1080] [--name "Mapping Test"]

Draws: checkerboard (square cells), colour test grid, 4 corner squares in different colours (orientation),
centre cross and a Text line with the output size. Syphon server = --name. Verified to open and render in Magic 3.0b6.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mmv-core", "scripts"))
import magicproj as m  # noqa: E402


def build(name, w, h):
    b = m.Builder(syphon=name, size=(w, h))
    s = b.scene("Test")
    grid = s.node("Color Test Grid", {"Grid Columns": 16, "Grid Rows": 9})
    chk = s.node("Checkerboard", {"Width": 0.03125})
    mix = s.node("Mix", {"Amount": 0.35}, inputs=[grid, chk])
    outs = []
    aspect = w / h
    corners = [(-1, 1, (1, 0, 0)), (1, 1, (0, 1, 0)), (-1, -1, (0, 0, 1)), (1, -1, (1, 1, 0))]
    for sx, sy, (r, g, bl) in corners:
        sq = s.node("Polygon", {"Sides": 4})
        col = s.node("ColorRGB", {"Red": r, "Green": g, "Blue": bl, "Alpha": 1}, inputs=[sq])
        sc = s.node("Scale", {"X": 0.12, "Y": 0.12, "Z": 1}, inputs=[col])
        tr = s.node("Translate", {"X": sx * (aspect - 0.12), "Y": sy * 0.88, "Z": 0}, inputs=[sc])
        outs.append(tr)
    for sx, sy in ((0.004, 1.0), (aspect, 0.004)):                    # centre cross, both bars the same thickness in pixels
        bar = s.node("Polygon", {"Sides": 4})
        col = s.node("ColorRGB", {"Red": 1, "Green": 1, "Blue": 1, "Alpha": 1}, inputs=[bar])
        sc = s.node("Scale", {"X": sx, "Y": sy, "Z": 1}, inputs=[col])
        outs.append(sc)
    txt = s.node("Text", {"Text": "%s  %dx%d" % (name, w, h), "Font": "Arial", "Size": 6, "Bold": 1})
    outs.append(txt)
    s.output(*outs, mix)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--name", default="Mapping Test")
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.lower().split("x"))
    build(a.name, w, h).write(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
