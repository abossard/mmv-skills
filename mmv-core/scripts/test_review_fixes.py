"""One test per fix made after the independent review (review-mmv-skills.md). Run: python3 -m unittest test_review_fixes
(from mmv-core/scripts). Nothing here starts Magic or sends a keystroke."""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "mmv-audio-reactivity", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "mmv-output-mapping", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "mmv-shaders-isf-glsl", "scripts"))
import audio_bank  # noqa: E402
import magicproj as mp  # noqa: E402
import mapping_test_pattern  # noqa: E402
import mmv_verify  # noqa: E402


def read_doc(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def small_project(path):
    b = mp.Builder(syphon="t", audio_device="Dev")
    s = b.scene("A")
    s.output(s.node("Polygon", {"Sides": 4}))
    b.write(path)


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = mp.main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


class VerifySafety(unittest.TestCase):
    """Finding 1, 8: --live is opt-in, nothing is loaded without it; --osc arguments are validated."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)
        self.f = os.path.join(self.d, "p.magic")
        small_project(self.f)

    def verify(self, *args, env=None):
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["mmv_verify.py", self.f] + list(args)), \
                mock.patch.dict(os.environ, env or {}, clear=False), \
                mock.patch.object(mmv_verify.m, "load", side_effect=AssertionError("must not load")) as load, \
                mock.patch.object(mmv_verify.m, "magic_windows", side_effect=AssertionError("must not query Magic")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                rc = mmv_verify.main()
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue(), load

    def test_live_without_yes_does_nothing(self):
        os.environ.pop("MMV_ALLOW_LIVE", None)
        rc, out, load = self.verify("--live")
        self.assertEqual(rc, 2)
        self.assertIn("--yes", out)
        load.assert_not_called()

    def test_live_with_yes_reaches_the_live_path(self):
        with mock.patch.object(mmv_verify, "live", return_value=0) as live:
            rc, _, _ = self.verify("--live", "--yes")
        self.assertEqual(rc, 0)
        live.assert_called_once()

    def test_env_var_also_opts_in(self):
        with mock.patch.object(mmv_verify, "live", return_value=0) as live:
            rc, _, _ = self.verify("--live", env={"MMV_ALLOW_LIVE": "1"})
        self.assertEqual(rc, 0)
        live.assert_called_once()

    def test_unreadable_file_is_a_message(self):
        with open(self.f, "wb") as fh:
            fh.write(b"not a project")
        rc, out, _ = self.verify()
        self.assertEqual(rc, 1)
        self.assertIn("cannot read", out)

    def test_static_only_never_touches_magic(self):
        rc, out, load = self.verify()
        self.assertEqual(rc, 0)
        self.assertIn("static: 0 errors", out)

    def test_osc_needs_a_port_and_a_value(self):
        for args in (["--live", "--yes", "--osc", "/a=1"], ["--osc", "/a"], ["--osc", "/a=x", "--osc-port", "1"]):
            with self.subTest(args=args):
                rc, _, _ = self.verify(*args)
                self.assertEqual(rc, 2)

    def test_mmv_core_skill_says_ask_first(self):
        text = read_doc("mmv-core", "SKILL.md")
        self.assertRegex(text, r"Ask the user first")
        self.assertIn("--yes", text)


class SetCli(unittest.TestCase):
    """Finding 26 and 'set overwrites FILE': no default overwrite, errors are messages not tracebacks."""

    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)
        b = mp.Builder(syphon="t", audio_device="Dev")
        b.glob("Hue", 0.1)
        s = b.scene("A")
        s.output(s.node("Polygon", {"Sides": 4}))
        self.f = os.path.join(self.d, "p.magic")
        b.write(self.f)

    def test_set_needs_out_or_in_place(self):
        with open(self.f, "rb") as fh:
            before = fh.read()
        rc, out, _ = run_cli(["set", self.f, "--value", "Hue", "0.5"])
        self.assertEqual(rc, 2)
        self.assertIn("-o OUT", out)
        with open(self.f, "rb") as fh:
            self.assertEqual(fh.read(), before)

    def test_set_in_place_and_out(self):
        out = os.path.join(self.d, "o.magic")
        self.assertEqual(run_cli(["set", self.f, "-o", out, "--value", "Hue", "0.5"])[0], 0)
        self.assertTrue(os.path.exists(out))
        self.assertEqual(run_cli(["set", self.f, "--in-place", "--value", "Hue", "0.7"])[0], 0)
        self.assertEqual(mp.global_ivs(mp.read(self.f))[0].get("value"), "0.7")

    def test_bad_arguments_give_one_line_errors(self):
        out = os.path.join(self.d, "o.magic")
        cases = {
            "size": ["--size", "12x"],
            "osc target": ["--osc-target", "127.0.0.1"],
            "midi channel": ["--midi-in", "Dev:17"],
            "modifier": ["--mods", "Hue", "Smooth:abc"],
            "source": ["--source", "Hue", "weird:thing"],
            "unknown global": ["--value", "Nope", "1"],
            "unknown scene": ["--playlist-scenes", "Nope"],
        }
        for name, extra in cases.items():
            with self.subTest(name):
                rc, _, err = run_cli(["set", self.f, "-o", out] + extra)
                self.assertEqual(rc, 2)
                self.assertTrue(err.startswith("error: "), err)
                self.assertNotIn("Traceback", err)

    def test_parse_size(self):
        self.assertEqual(mp.parse_size("1920X1080"), (1920, 1080))
        for bad in ("12x", "axb", "0x5", "1920"):
            with self.assertRaises(ValueError):
                mp.parse_size(bad)

    def test_decode_of_garbage_is_a_message(self):
        bad = os.path.join(self.d, "bad.magic")
        with open(bad, "wb") as fh:
            fh.write(b"abcdef")
        rc, _, err = run_cli(["info", bad])
        self.assertEqual(rc, 2)
        self.assertIn("error:", err)


class AudioBankKick(unittest.TestCase):
    """Finding 16: KickPulse fires once per kick (edge of a lagged gate), never from `y`."""

    def bank(self):
        b = mp.Builder(syphon="t", audio_device="Dev")
        audio_bank.add_audio_bank(b)
        s = b.scene("A")
        s.output(s.node("Polygon", {}))
        return b.build()

    def test_structure(self):
        g = {iv.get("name"): iv for iv in mp.global_ivs(self.bank())}
        self.assertIn("KickGate", g)
        self.assertIn("KickGateLag", g)
        pulse = mp.describe_source(g["KickPulse"], self.bank())
        mods = mp.format_mods(mp.modifiers(g["KickPulse"]))
        self.assertIn("KickGateLag", mods)
        self.assertNotRegex(mods, r"\by\b")
        self.assertEqual([i for l, i in mp.check(self.bank()) if l == "error"], [])
        self.assertTrue(pulse)

    def test_one_pulse_per_held_gate(self):
        # Magic reads the previous frame's value of every Global it names, so with gate g[t]:
        #   lag[t] = g[t-1], pulse[t] = 1 if g[t-1] > .5 and lag[t-1] < .5  (= g[t-1] > .5 and g[t-2] < .5)
        gate = [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0]
        pulses = [1 if gate[t - 1] > 0.5 and (gate[t - 2] if t >= 2 else 0) < 0.5 else 0 for t in range(1, len(gate))]
        self.assertEqual(sum(pulses), 2)
        # the old `y` form on the same input toggles while the gate is held
        y, old = 0, []
        for g in gate:
            y = 1 if (g > 0.5 and y < 0.5) else 0
            old.append(y)
        self.assertGreater(sum(old), 2)

    def test_docs_use_the_lag_form(self):
        text = read_doc("mmv-audio-reactivity", "SKILL.md")
        self.assertNotIn("Expression `if (x > 0.5 and y < 0.5, 1, 0)`", text)
        self.assertIn("KickGateLag", text)


class CatalogAndInstall(unittest.TestCase):
    def test_gen_catalog_without_the_app_fails_and_prints_nothing(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "gen_catalog.py")], capture_output=True, text=True,
                           env=dict(os.environ, MAGIC_APP="/nonexistent"))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")
        self.assertIn("MAGIC_APP", r.stderr)

    def test_install_script_leaves_real_folders_alone_and_replaces_links(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        os.makedirs(os.path.join(d, "mmv-core"))
        os.symlink("/nonexistent", os.path.join(d, "mmv-audio-reactivity"))
        r = subprocess.run(["bash", os.path.join(ROOT, "install.sh"), d], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skipped", r.stdout)
        self.assertEqual(os.listdir(os.path.join(d, "mmv-core")), [])          # no nested link inside the real folder
        self.assertEqual(os.path.realpath(os.path.join(d, "mmv-audio-reactivity")), os.path.join(ROOT, "mmv-audio-reactivity"))
        self.assertTrue(os.path.islink(os.path.join(d, "mmv-scene-recipes")))


class MappingPattern(unittest.TestCase):
    def test_centre_cross_bars_have_equal_pixel_thickness(self):
        for w, h in ((1920, 1080), (3840, 1080), (1080, 1080)):
            with self.subTest(size=(w, h)):
                root = mapping_test_pattern.build("t", w, h).build()
                scales = []
                for n in root.iter("Node"):
                    if n.get("pluginName") == "Scale":
                        x, y = (float(mp.param(n, k).get("value")) for k in ("X", "Y"))
                        if 0.12 not in (x, y):          # skip the corner squares
                            scales.append((x, y))
                self.assertEqual(len(scales), 2)
                (vx, vy), (hx, hy) = sorted(scales, key=lambda s: s[0])
                thickness_v, thickness_h = vx * h, hy * h     # a Polygon spans +-1: pixels = 2 * scale * h / 2
                self.assertAlmostEqual(thickness_v, thickness_h)


class SharedIsfHelpers(unittest.TestCase):
    """Finding 25: one ISF header parser and param naming."""

    def test_lint_and_gen_catalog_use_magicproj(self):
        self.assertIn("magicproj.ISF_HEADER", read_doc("mmv-shaders-isf-glsl", "scripts", "isf_lint.py"))
        self.assertIn("magicproj.isf_header", read_doc("mmv-core", "scripts", "gen_catalog.py"))

    def test_param_names_agree(self):
        import isf_lint
        text = ('// comment first\n/*{"INPUTS":[{"NAME":"c","LABEL":"My Col","TYPE":"color"},{"NAME":"p","TYPE":"point2D"},'
                '{"NAME":"fft","TYPE":"audioFFT"}]}*/\nvoid main(){gl_FragColor=vec4(TIME);}\n')
        self.assertEqual(isf_lint.magic_params(text), list(mp.isf_params(text)))
        self.assertEqual(list(mp.isf_params(text)), ["My Col R", "My Col G", "My Col B", "My Col A", "P X", "P Y", "Fft", "Speed"])


class DocConsistency(unittest.TestCase):
    """Findings 11, 12, 13, 18, 24, 27: the docs agree with each other and with the code."""

    def test_midi_clock_is_read_from_channel_zero(self):
        text = read_doc("mmv-midi-osc-control", "SKILL.md")
        self.assertRegex(text, r'channel=0, name="Clock"')
        self.assertIn("midi:Clock:Beat Clock", text)
        self.assertNotIn("midi:DAW:Beat Clock", text)

    def test_strobe_limit_is_the_same_everywhere(self):
        holds = {re.search(r"Hold (0\.\d+)", read_doc(*p)).group(1) for p in (
            ("mmv-effects-color", "references", "effect-recipes.md"), ("mmv-vj-performance", "SKILL.md"))}
        self.assertEqual(holds, {"0.34"})

    def test_bloom_blur_amount_stays_inside_the_module_range(self):
        for path in (("mmv-effects-color", "SKILL.md"), ("mmv-effects-color", "references", "effect-recipes.md"),
                     ("mmv-scene-recipes", "SKILL.md"), ("mmv-scene-recipes", "scripts", "retro_sunset_example.py")):
            for m in re.finditer(r"BlurAmount\W{1,4}(\d+)(?:-(\d+))?", read_doc(*path)):
                self.assertLessEqual(int(m.group(2) or m.group(1)), 12, path)

    def test_retro_example_builds_clean(self):
        sys.path.insert(0, os.path.join(ROOT, "mmv-scene-recipes", "scripts"))
        import retro_sunset_example as ex
        for palette in ex.PALETTES:
            with self.subTest(palette):
                root = ex.build("t", (1280, 720), "Dev", palette).build()
                self.assertEqual([i for l, i in mp.check(root) if l == "error"], [])

    def test_no_dangling_references(self):
        for name in ("magicproj.py", "gen_catalog.py", "mmv_verify.py"):
            src = read_doc("mmv-core", "scripts", name)
            self.assertNotIn("from lab import", src)
            self.assertNotIn("docs/magic-tooling-report.md", src)
        import json
        about = json.loads(read_doc("mmv-core", "scripts", "magic_modules_v3.json"))["_about"]
        self.assertNotIn("swift-vj", about)

    def test_frames_example_names_the_files_it_writes(self):
        text = read_doc("mmv-scene-recipes", "SKILL.md")
        self.assertIn("frame.0.png", text)

    def test_core_doc_does_not_claim_impossible_black_frames(self):
        self.assertNotIn("missing Syphon flag", read_doc("mmv-core", "SKILL.md"))

    def test_module_names_in_docs_exist_in_the_catalog(self):
        catalog = read_doc("mmv-core", "references", "module-catalog.md")
        for name in ("Optical Flow Distort", "Optical Flow Generator", "Multi Pass Gaussian Blur", "Hyperspace", "Median"):
            self.assertIn("**%s**" % name, catalog)
        self.assertNotIn("Displace,", read_doc("mmv-effects-color", "SKILL.md").replace("Edge Distort", ""))

    def test_template_comment_is_accurate(self):
        self.assertIn("option index and value are the same", read_doc("mmv-shaders-isf-glsl", "assets", "templates", "T_Generator.fs"))

    def test_tooling_doc_explains_midi_sources(self):
        self.assertIn("add_midi_in", read_doc("mmv-core", "references", "tooling.md"))

    def test_tests_in_magicproj_run_as_a_script(self):
        src = read_doc("mmv-core", "scripts", "test_magicproj.py")
        self.assertLess(src.index("class MmvExtensions"), src.index('if __name__ == "__main__"'))


class PublicHygiene(unittest.TestCase):
    """The repository is public: no personal paths, machine names, work addresses or copied vendor prose."""

    def files(self):
        for base, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for n in names:
                if n.endswith((".md", ".py", ".sh", ".json", ".fs", ".txt")) or n in ("LICENSE", ".gitignore"):
                    yield os.path.join(base, n)

    def test_no_personal_strings(self):
        pattern = re.compile(r"/Users/|abossard|gmail|microsoft\.com|anbossar|swift-vj|synesthesia-visuals|qlcplus|MacBook Pro Microphone|Scarlett")
        allowed = {os.path.join(ROOT, "mmv-core", "scripts", "test_review_fixes.py"), os.path.join(ROOT, "LICENSE")}
        for f in self.files():
            if f in allowed:
                continue
            with open(f, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    if "abossard/mmv-skills" in line:
                        continue
                    self.assertIsNone(pattern.search(line), "%s:%d: %s" % (f, n, line.strip()[:80]))

    def test_catalog_has_no_shader_description_prose(self):
        text = read_doc("mmv-core", "references", "module-catalog.md")
        for line in text.splitlines():
            if line.startswith("- **"):
                self.assertRegex(line, r"^- \*\*[^*]+\*\* \((pin|no pin)\)$")

    def test_module_table_has_factory_values_only(self):
        import json
        mods = json.loads(read_doc("mmv-core", "scripts", "magic_modules_v3.json"))["modules"]
        self.assertEqual(mods["OSCSender"]["params"]["Port"], "8000")
        self.assertEqual(mods["SyphonClient"]["params"]["Server"], "")
        self.assertFalse(mods["GLSLShader"]["params"]["File"].startswith(("/", "..")))

    def test_license_and_ignore_files_exist(self):
        self.assertIn("MIT License", read_doc("LICENSE"))
        self.assertIn("__pycache__", read_doc(".gitignore"))


class WindowTitles(unittest.TestCase):
    def test_titles_with_commas_survive(self):
        with mock.patch.object(mp, "_osascript", return_value=("Magic - A\nrain, drums.magic - Editor - A\nPlaylist", "")):
            self.assertEqual(mp.magic_windows(), ["Magic - A", "rain, drums.magic - Editor - A", "Playlist"])


if __name__ == "__main__":
    unittest.main()
