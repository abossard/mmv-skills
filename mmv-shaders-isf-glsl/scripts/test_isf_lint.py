import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import isf_lint  # noqa: E402

HEAD = '/*{"ISFVSN":"2.0","INPUTS":[{"NAME":"amt","TYPE":"float","DEFAULT":0.5}]}*/\n'


def lint_src(body, head=HEAD, strict=True):
    with tempfile.NamedTemporaryFile("w", suffix=".fs", delete=False) as f:
        f.write(head + body)
    try:
        return isf_lint.lint(f.name, strict)
    finally:
        os.unlink(f.name)


class Lint(unittest.TestCase):
    def test_clean(self):
        errs, _, _ = lint_src("void main(){ gl_FragColor = vec4(amt, 0.0, 0.0, 1.0); }")
        self.assertEqual(errs, [])

    def test_forbidden_constructs(self):
        cases = {
            "tanh": "float f = tanh(1.0);",
            "round": "float f = round(1.4);",
            "float suffix": "float f = 2.0f;",
            "texture": "vec4 c = texture(inputImage, vec2(0.0));",
            "bitwise": "int a = 1 << 2;",
            "int modulo": "int a = 5 % 2;",
            "uint": "uint a = 1u;",
            "isnan": "bool b = isnan(1.0);",
            "int max": "int a = max(1, 2);",
            "array ctor": "float a[2] = float[2](1.0, 2.0);",
            "auto uniform": "uniform float TIME;",
            "input uniform": "uniform float amt;",
        }
        for name, line in cases.items():
            with self.subTest(name):
                errs, _, _ = lint_src("void main(){ %s gl_FragColor = vec4(1.0); }" % line)
                self.assertTrue(errs, name)

    def test_header_errors(self):
        errs, _, _ = lint_src("void main(){ gl_FragColor = vec4(1.0); }", head='/*{ not json }*/\n')
        self.assertTrue(errs)
        errs, _, _ = lint_src("void main(){ gl_FragColor = vec4(1.0); }",
                              head='/*{"INPUTS":[{"NAME":"a","TYPE":"float"},{"NAME":"a","TYPE":"float"}]}*/\n')
        self.assertTrue(any("duplicate" in m for _, m in errs))

    def test_params(self):
        text = ('/*{"INPUTS":[{"NAME":"c","LABEL":"My Col","TYPE":"color"},{"NAME":"p","TYPE":"point2D"}]}*/\n'
                'void main(){ gl_FragColor = vec4(TIME); }')
        self.assertEqual(isf_lint.magic_params(text), ["My Col R", "My Col G", "My Col B", "My Col A", "P X", "P Y", "Speed"])

    def test_portability_rules(self):
        cases = [("int modulo without spaces", "int f(int a) { return a%2; }", True),
                 ("in/out function parameters", "float f(in vec3 p, out vec3 q) { q = p; return p.x; }", False),
                 ("global in", "in vec2 uv;", True),
                 ("global out", "out vec4 fragColor;", True),
                 ("local named fragColor", "vec4 f() { vec4 fragColor = vec4(1.0); return fragColor; }", False)]
        for name, code, flagged in cases:
            with self.subTest(name):
                errs, _, _ = lint_src(code + "\nvoid main(){ gl_FragColor = vec4(1.0); }")
                self.assertEqual(bool(errs), flagged, errs)

    def test_header_may_follow_comment_lines(self):
        errs, _, header = lint_src("void main(){ gl_FragColor = vec4(amt); }", head="// credit\n" + HEAD)
        self.assertEqual((errs, header["ISFVSN"]), ([], "2.0"))

    def test_void_main_with_extra_space(self):
        errs, _, _ = lint_src("void  main(){ gl_FragColor = vec4(1.0); }")
        self.assertEqual(errs, [])

    def test_loop_bounds(self):
        def loop(name, bound):
            return "float %s(int n) { float t = 0.0; for (int i = 0; i < %s; i++) { t += 1.0; } return t; }\n" % (name, bound)
        main = "void main(){ gl_FragColor = vec4(1.0); }"
        cases = [(loop("f", "n"), True), (loop("f", "4"), False), ("#define N 4\n" + loop("f", "N"), False),
                 (loop("f", "4") + loop("g", "n"), True)]
        for code, warned in cases:
            with self.subTest(code=code):
                _, warns, _ = lint_src(code + main, strict=False)
                self.assertEqual(any("non-constant" in m for _, m in warns), warned, warns)


if __name__ == "__main__":
    unittest.main()
