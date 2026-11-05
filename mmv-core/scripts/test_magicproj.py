"""magicproj tests. Run: python3 -m unittest test_magicproj   (from mmv-core/scripts)

Unit tests use generated projects and Magic's bundled sample projects (skipped
without the app). LiveMagicTests drive the running app; they replace Magic's
current project, so they only run with MAGICPROJ_LIVE=1.
"""
import contextlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import wave
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import magicproj as mp  # noqa: E402
import mmv_verify  # noqa: E402

SAMPLES = sorted(os.path.join(mp.SAMPLES, f) for f in os.listdir(mp.SAMPLES) if f.endswith(".magic")) \
    if os.path.isdir(mp.SAMPLES) else []


def demo(syphon="magicproj-test", hue=0.0):
    b = mp.Builder(syphon=syphon, osc_in=11111, audio_device="Test Mic")
    b.glob("Hue", hue)
    b.glob("Level", 0, "audio:Source 0:Freq. Range:20-80 Hz", [("Expression", "x*Gain*4"), ("Smooth", 0.6)])
    b.glob("Gain", 0.5)
    b.glob("Ext", 0, "osc:/ext/beat")
    b.glob("Width", 0, "internal:Graphics Width")
    s = b.scene("Main")
    poly = s.node("Polygon", {"Sides": 4})
    scale = s.node("Scale", {"X": 4, "Y": 4, "Z": 1, "X For All": 0}, inputs=[poly])
    col = s.node("ColorHSB", {"Hue": ("global:Hue", [], hue), "Saturation": 1, "Brightness": 1, "Alpha": 1, "Override": 1},
                 inputs=[scale], bypass=("global:Level", [("Expression", "if(x > 2, 1, 0)")]))
    osc = s.node("OSCSender", {"IP Addr.": "127.0.0.1", "Port": 9200, "Message": "/vj/level", "Value": ("global:Level",)})
    s.output(col, osc)
    return b.build()


def roundtrip(root):
    return mp.parse(mp.encode(mp.serialize(root)))


class CodecTests(unittest.TestCase):
    @unittest.skipUnless(SAMPLES, "Magic not installed")
    def test_magic_saves_roundtrip_semantically(self):
        for path in SAMPLES:
            with self.subTest(os.path.basename(path)):
                root = mp.read(path)
                self.assertEqual(mp.canonical(roundtrip(root)), mp.canonical(root))

    def test_header_is_ignored_on_decode(self):
        for header in (b"L*h", b"\x00\x00\x00", b"u6m"):
            with self.subTest(header=header):
                data = header + mp.encode(mp.serialize(demo()))[3:]
                self.assertEqual(mp.canonical(mp.parse(data)), mp.canonical(demo()))


class CheckTests(unittest.TestCase):
    @unittest.skipUnless(SAMPLES, "Magic not installed")
    def test_magic_saves_have_no_errors(self):
        for path in SAMPLES:
            with self.subTest(os.path.basename(path)):
                errors = [m for level, m in mp.check(mp.read(path)) if level == "error"]
                self.assertEqual(errors, [])

    def test_built_project_has_no_errors(self):
        self.assertEqual([p for p in mp.check(demo()) if p[0] == "error"], [])

    def test_detects(self):
        def break_link(r):
            mp.find_global(r, "Hue").set("id", "999999")

        def bad_expr(r):
            mp.set_modifiers(mp.find_global(r, "Level"), [("Expression", "x*Gian")])

        def missing_input(r):
            next(r.iter("Child")).set("id", "424242")

        def reserved_name(r):
            mp.find_global(r, "Gain").set("name", "x")

        def dup_global(r):
            mp.find_global(r, "Gain").set("name", "Hue")

        def bad_modifier(r):
            next(r.iter("ValueOperator")).set("type", "99")

        def dup_iv_id(r):
            ivs = list(r.iter("InputValue"))
            ivs[-1].set("id", ivs[-2].get("id"))

        cases = [(break_link, "missing Global id"), (bad_expr, "unknown names ['Gian']"),
                 (missing_input, "is not in the scene"), (reserved_name, "reserved"), (dup_global, "used twice"),
                 (bad_modifier, "unknown modifier type"), (dup_iv_id, "used 2 times")]
        for mutate, expected in cases:
            with self.subTest(mutate.__name__):
                root = demo()
                mutate(root)
                errors = [m for level, m in mp.check(root) if level == "error"]
                self.assertTrue(any(expected in m for m in errors), errors)

    def test_expression_identifiers(self):
        cases = [("x*Gain*4", {"x", "Gain"}), ("max(x, y*exp(-Dt*9))", {"max", "x", "y", "exp", "Dt"}),
                 ("1e-3 + .5*Kick", {"Kick"}), ("var a := Kick; a*2", {"var", "Kick"}), ("'str' + Foo", {"Foo"})]
        for expr, expected in cases:
            with self.subTest(expr):
                self.assertEqual(mp.expression_identifiers(expr), expected)

    def test_scene_module_cycles(self):
        def build(links):
            b = mp.Builder(syphon="t", audio_device="Dev")
            scenes = {n: b.scene(n) for n in "ABC"}
            for src, dst in links:
                scenes[src].output(scenes[src].scene_module(scenes[dst]))
            return b.build()
        cases = [([("A", "B"), ("B", "C")], False), ([("A", "A")], True), ([("A", "B"), ("B", "A")], True),
                 ([("A", "B"), ("B", "C"), ("C", "A")], True)]
        for links, cyclic in cases:
            with self.subTest(links=links):
                errors = [m for level, m in mp.check(build(links)) if level == "error"]
                self.assertEqual(any("cycle" in m for m in errors), cyclic, errors)

    def test_custom_module_dir_is_found_without_the_magic_app(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "Mine.fs"), "w") as f:
                f.write('/*{"INPUTS": [{"NAME": "a", "TYPE": "float", "DEFAULT": 0.5}]}*/\nvoid main() { gl_FragColor = vec4(a); }\n')
            with mock.patch.object(mp, "MAGIC_APP", os.path.join(d, "no-such.app")), \
                    mock.patch.dict(os.environ, {"MMV_MODULE_DIRS": d}):
                mp.custom_module_dirs.cache_clear()
                try:
                    b = mp.Builder(syphon="t", audio_device="Dev")
                    s = b.scene("A")
                    s.output(s.node("Mine", {"A": 0.7, "Typo": 1}))
                    warns = [m for level, m in mp.check(b.build()) if level == "warn"]
                finally:
                    mp.custom_module_dirs.cache_clear()
        self.assertFalse(any("not a Magic 3.0 module" in m for m in warns), warns)
        self.assertTrue(any("params ['Typo'] are not in the ISF header of Mine" in m for m in warns), warns)


class QueryTests(unittest.TestCase):
    def test_describe_source(self):
        table = {g["name"]: g for g in mp.global_table(demo())}
        cases = [("Hue", "manual"), ("Level", "audio:Source 0:Freq. Range:20-80 Hz"), ("Ext", "osc:/ext/beat"),
                 ("Width", "internal:Graphics Width")]
        for name, source in cases:
            with self.subTest(name):
                self.assertEqual(table[name]["source"], source)

    def test_modifier_names(self):
        mods = mp.global_table(demo())[1]["modifiers"]
        self.assertEqual(mods, [("Expression", 0.0, "x*Gain*4", False), ("Smooth", 0.6, None, False)])

    def test_modifier_index_matches_magic(self):
        # Expression = 21 holds every multi-character expression in Magic's samples.
        cases = [("Gate", 0), ("Power", 3), ("Smooth", 4), ("Peak", 12), ("Increase", 16), ("Trigger", 17),
                 ("Expression", 21), ("RandomTrigger", 22)]
        for name, index in cases:
            with self.subTest(name):
                self.assertEqual(mp.MODIFIERS.index(name), index)

    def test_isf_param_names(self):
        # Names as Magic saves them (synthwave_pyramids.magic loads with these).
        cases = [({"NAME": "blurAmount", "TYPE": "float", "DEFAULT": 12.0}, {"BlurAmount": 12.0}),
                 ({"NAME": "mirrorEdges", "LABEL": "Fill Edges", "TYPE": "bool", "DEFAULT": True}, {"Fill Edges": True}),
                 ({"NAME": "center", "TYPE": "point2D", "DEFAULT": [0.5, 0.5]}, {"Center X": 0.5, "Center Y": 0.5}),
                 ({"NAME": "inputImage", "TYPE": "image"}, {}),
                 # God Rays: DEFAULT 10 of VALUES [5, 10, 25] is saved as index 1.
                 ({"NAME": "quality", "TYPE": "long", "VALUES": [5, 10, 25], "LABELS": ["a", "b", "c"], "DEFAULT": 10}, {"Quality": 1}),
                 ({"NAME": "fftImage", "LABEL": "Source", "TYPE": "audioFFT"}, {"Source": -1}),
                 ({"NAME": "waveImage", "LABEL": "Wave", "TYPE": "audio"}, {"Wave": -1, "Overwrite": 1}),
                 ({"NAME": "buffer", "TYPE": "color"}, {"Buffer R": 0, "Buffer G": 0, "Buffer B": 0, "Buffer A": 0})]
        # Magic's own headers have raw newlines in strings and trailing commas (Transparency.fs).
        lenient = '/*{"DESCRIPTION": "two\nlines", "INPUTS": [{"NAME": "amount", "TYPE": "float", "DEFAULT": 0.5},],}*/'
        with self.subTest("lenient"):
            self.assertEqual(mp.isf_params(lenient), {"Amount": 0.5})
        for inp, expected in cases:
            with self.subTest(inp["NAME"]):
                text = '/*{"ISFVSN": "2", "INPUTS": [%s]}*/\nvoid main() {}' % json.dumps(inp)
                self.assertEqual(mp.isf_params(text), expected)

    def test_isf_params_for_time_and_modules(self):
        float_in = {"NAME": "speed", "TYPE": "float", "DEFAULT": 0.3}
        image_in = {"NAME": "inputImage", "TYPE": "image"}
        band_speed = {"NAME": "bandSpeed", "TYPE": "float", "DEFAULT": 2.0}
        cases = [("gl_FragColor = vec4(TIME);", [float_in], False, {"Speed": 0.3, "Speed (M)": 1}),
                 ("gl_FragColor = vec4(TIME);", [], False, {"Speed": 1}),
                 # Magic saves Speed (M) as soon as an input name contains "speed", and TIMEDELTA counts as TIME.
                 ("gl_FragColor = vec4(TIMEDELTA);", [band_speed], False, {"BandSpeed": 2.0, "Speed (M)": 1}),
                 ("/* TIME */ gl_FragColor = vec4(1.0);", [float_in], False, {"Speed": 0.3}),
                 ("gl_FragColor = vec4(1.0);", [], True, {"Power": 1}),
                 ("gl_FragColor = vec4(1.0);", [image_in], True, {"Bypass": 0, "Power": 1})]
        for code, inputs, module, expected in cases:
            with self.subTest(code=code, inputs=[i["NAME"] for i in inputs], module=module):
                text = '/*%s*/\nvoid main() { %s }' % (json.dumps({"ISFVSN": "2", "INPUTS": inputs}), code)
                self.assertEqual(mp.isf_params(text, module=module), expected)

    def test_isf_header_may_follow_comment_lines(self):
        # TurbulentShapes.fs: credit lines before the header, and Magic saves its params.
        text = '// credit\n// more\n\n/*{"INPUTS": [{"NAME": "zoom", "TYPE": "float", "DEFAULT": 20.0},]}*/\nvoid main() {}'
        self.assertEqual(mp.isf_params(text), {"Zoom": 20.0})

    def test_speed_names_are_interchangeable_in_check(self):
        for saved in ("Speed", "Speed (M)"):
            with self.subTest(saved):
                b = mp.Builder(syphon="t", audio_device="Dev")
                s = b.scene("A")
                with tempfile.TemporaryDirectory() as d:
                    fs = os.path.join(d, "Fx.fs")
                    with open(fs, "w") as f:
                        f.write('/*{"INPUTS": []}*/\nvoid main() { gl_FragColor = vec4(TIME); }\n')
                    s.output(s.node("Fx", {saved: 1}, isf=fs))
                    warns = [m for level, m in mp.check(b.build()) if level == "warn"]
                self.assertEqual(warns, [])

    def test_queries_do_not_add_globals(self):
        root = mp.ET.fromstring("<Project><Scenes/></Project>")
        mp.global_names(root)
        mp.global_table(root)
        mp.check(root)
        self.assertIsNone(root.find("Globals"))

    def test_osc_senders(self):
        self.assertEqual([(o["message"], o["ip"], o["port"], o["value_source"]) for o in mp.osc_senders(demo())],
                         [("/vj/level", "127.0.0.1", "9200", "global:Level")])

    def test_summary(self):
        s = mp.summary(demo())
        self.assertEqual((s["syphon"], s["globals"], s["osc_in_ports"], [x["name"] for x in s["scenes"]]),
                         ({"on": True, "name": "magicproj-test", "size": "1920x1080"}, 5, ["11111"], ["Main"]))


class EditTests(unittest.TestCase):
    def test_edits_show_in_diff(self):
        cases = [
            (lambda r: mp.edit_global(r, "Hue", value=0.33), [("global[Hue].value", "0", "0.33")]),
            (lambda r: mp.edit_global(r, "Gain", source="osc:/gain"), [("global[Gain].source", "manual", "osc:/gain")]),
            (lambda r: mp.edit_global(r, "Level", mods=[("Peak", 0.5)]),
             [("global[Level].modifiers", "Expression(x*Gain*4) -> Smooth 0.6", "Peak 0.5")]),
            (lambda r: mp.add_global(r, "New", 2), [("global[New].modifiers", None, ""), ("global[New].source", None, "manual"),
                                                    ("global[New].value", None, "2")]),
            (lambda r: mp.set_syphon(r, False), [("project.videoSharing", "1", "0")]),
            (lambda r: mp.set_osc_target(r, port=9300), [("scene[Main].node[OSCSender#1].Port", "9200", "9300")]),
            (lambda r: mp.set_osc_in(r, 8000), [("source[OSC In]", "Open Sound Control ch 11111", "Open Sound Control ch 8000"),
                                                  ("track[Open Sound Control ch 11111]", "deviceName= isInput=1 isOSC=1", None),
                                                  ("track[Open Sound Control ch 8000]", None, "deviceName= isInput=1 isOSC=1")]),
        ]
        for i, (edit, expected) in enumerate(cases):
            with self.subTest(i):
                before = demo()
                after = edit(before)
                self.assertEqual(mp.diff(before, after), expected)
                self.assertEqual(mp.canonical(before), mp.canonical(demo()), "edits must not mutate their input")

    def test_rename_rewrites_expressions(self):
        root = mp.edit_global(demo(), "Gain", rename="InGain")
        self.assertEqual(mp.global_table(root)[1]["modifiers"][0][2], "x*InGain*4")
        self.assertEqual([p for p in mp.check(root) if p[0] == "error"], [])

    def test_rename_follows_case_insensitive_references(self):
        root = demo()
        mp.set_modifiers(mp.find_global(root, "Level"), [("Expression", "x*gain*4")])
        root = mp.edit_global(root, "Gain", rename="InGain")
        self.assertEqual(mp.global_table(root)[1]["modifiers"][0][2], "x*InGain*4")

    def test_catalog_works_without_magic_samples(self):
        out = io.StringIO()
        with mock.patch.object(mp, "SAMPLES", "/no/such/dir"), contextlib.redirect_stdout(out):
            self.assertEqual(mp.main(["catalog", "--plugin", "^Bloom$"]), 0)
        self.assertIn("Bloom [magic3]", out.getvalue())

    def test_diff_keeps_same_named_sources_apart(self):
        root = demo()
        mp.ET.SubElement(root.find("Layers"), "Layer", name="Source 0", id="9001", trackID="-1", gain="0", gainVisible="0")
        self.assertEqual({k for k in mp.flatten(root) if k.startswith("source[Source 0")}, {"source[Source 0]", "source[Source 0#2]"})

    def test_remove_global_unlinks_params(self):
        root = mp.remove_global(demo(), "Hue")
        hue = next(p for n in mp.node_table(root) for p in n["params"] if p["name"] == "Hue")
        self.assertEqual(hue["source"], "manual")
        self.assertEqual([p for p in mp.check(root) if p[0] == "error"], [])

    def test_add_audio_routes_sources(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "tone.wav")
            for channels in (1, 2):
                with self.subTest(channels=channels):
                    with wave.open(path, "wb") as w:
                        w.setnchannels(channels); w.setsampwidth(2); w.setframerate(44100); w.writeframes(b"\0\0" * channels * 441)
                    root = mp.add_audio(demo(), path)
                    s = mp.summary(root)
                    self.assertEqual(s["audio_files"], [path])
                    self.assertTrue(s["looping"])
                    file_tracks = {t.get("id") for t in root.iter("Track") if t.get("audioFileIndex") == "0"}
                    self.assertEqual(len(file_tracks), channels)
                    self.assertEqual(sum(1 for x in s["sources"] if x["track"] in file_tracks), channels)
                    self.assertEqual([p for p in mp.check(root, d) if p[0] == "error"], [])

    def test_cli_size_keeps_syphon_state(self):
        with tempfile.TemporaryDirectory() as d:
            for syphon, args, expected in ((None, ["--size", "1280x720"], "0"), ("x", ["--size", "1280x720"], "1"),
                                           (None, ["--syphon-name", "out"], "1"), ("x", ["--syphon", "off"], "0")):
                with self.subTest(args=args, syphon=syphon):
                    src, out = os.path.join(d, "p.magic"), os.path.join(d, "o.magic")
                    mp.write(src, demo(syphon=syphon))
                    mp.main(["set", src, "-o", out] + args)
                    root = mp.read(out)
                    self.assertEqual(root.get("videoSharing"), expected)
                    if "--size" in args:
                        self.assertEqual((root.get("videoSharingWidth"), root.get("fixedMagicSize")), ("1280", "1"))

    def test_cli_set_refuses_broken_result(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.magic")
            mp.write(path, demo())
            for args, code in ((["--value", "Hue", "0.5"], 0), (["--mods", "Hue", "x*Nope"], 1)):
                with self.subTest(args=args):
                    self.assertEqual(mp.main(["set", path, "-o", os.path.join(d, "o.magic")] + args), code)


class V3Tests(unittest.TestCase):
    def test_midi_sources(self):
        root = mp.add_midi_in(demo(), "IAC Driver Bus 1", 1, "Keys")
        self.assertEqual(sum(1 for t in root.iter("Track") if t.get("name") == "IAC Driver Bus 1"), 17)
        cases = [("midi:Keys:Control Change:7", "midi:Keys:Control Change:7"), ("midi:Keys:3:1", "midi:Keys:Control Change:1"),
                 ("midi:Keys:Note Velocity:60", "midi:Keys:Note Velocity:60"), ("midi:Keys:Beat Clock:/4", "midi:Keys:Beat Clock:/4"),
                 ("midi:Keys:Program Change", "midi:Keys:Program Change"), ("midi:Keys:Iterator Notes", "midi:Keys:Iterator Notes")]
        for source, shown in cases:
            with self.subTest(source):
                r = mp.edit_global(root, "Hue", source=source)
                self.assertEqual(mp.global_table(r)[0]["source"], shown)
                self.assertEqual([p for p in mp.check(r) if p[0] == "error"], [])

    def test_midi_channel_must_exist(self):
        with self.assertRaises(KeyError):
            mp.add_midi_in(demo(), "IAC Driver Bus 1", 17, "Keys")

    def test_builder_values(self):
        cases = [({"Red": True}, None, "Red", "1"), ({"Green": False}, None, "Green", "0"),
                 ({}, 0, "Power", "0"), ({}, None, "Power", "1"), ({}, 0.5, "Power", "0.5")]
        for values, power, name, expected in cases:
            with self.subTest(values=values, power=power):
                b = mp.Builder(syphon="t", audio_device="Dev")
                s = b.scene("A")
                s.output(s.node("ColorRGB", values, power=power))
                node = next(n for n in b.build().iter("Node") if n.get("pluginName") == "ColorRGB")
                self.assertEqual(mp.param(node, name).get("value"), expected)

    def test_route_source(self):
        cases = [("Source 1", "Built-in Microphone", 0), ("Drums", "USB Interface", 3)]
        for source, device, ch in cases:
            with self.subTest(source):
                root = mp.route_source(demo(), source, device, ch)
                layer = next(l for l in root.iter("Layer") if l.get("name") == source)
                track = next(t for t in root.iter("Track") if t.get("id") == layer.get("trackID"))
                self.assertEqual((track.get("deviceName"), track.get("channel")), (device, str(ch)))
                self.assertEqual([p for p in mp.check(root) if p[0] == "error"], [])

    def test_playlist(self):
        b = mp.Builder()
        for name in ("A", "B", "C"):
            b.scene(name).output()
        root = b.build()
        cases = [(dict(seconds=16, transition=3, style=1), ["0", "1", "2"], ("16", "3", "1")),
                 (dict(names=["C", "A"], seconds=8, style=0), ["2", "0"], ("8", "2", "0"))]
        for kwargs, ids, (secs, trans, style) in cases:
            with self.subTest(kwargs):
                entries = list(mp.set_playlist(root, **kwargs).iterfind("Playlists/Playlist/Scene"))
                self.assertEqual([e.get("id") for e in entries], ids)
                self.assertEqual({(e.get("sceneDuration"), e.get("duration"), e.get("style")) for e in entries}, {(secs, trans, style)})

    def test_playlist_keeps_existing_entry_settings(self):
        b = mp.Builder()
        b.scene("A").output()
        root = b.build()
        next(root.iterfind("Playlists/Playlist/Scene")).set("featureString", "/scene/a")
        entry = next(mp.set_playlist(root, seconds=5).iterfind("Playlists/Playlist/Scene"))
        self.assertEqual((entry.get("featureString"), entry.get("sceneDuration")), ("/scene/a", "5"))

    def test_connect(self):
        root = demo()
        nodes = {n["plugin"]: n["id"] for n in mp.node_table(root)}
        cases = [([nodes["Polygon"]], None), (["999"], KeyError)]
        for ids, error in cases:
            with self.subTest(ids=ids):
                if error:
                    with self.assertRaises(error):
                        mp.connect(root, "Main", nodes["ColorHSB"], ids)
                    continue
                r = mp.connect(root, "Main", nodes["ColorHSB"], ids)
                col = next(n for n in mp.node_table(r) if n["plugin"] == "ColorHSB")
                self.assertEqual(col["inputs"], ids)
                self.assertEqual([p for p in mp.check(r) if p[0] == "error"], [])

    def test_check_flags_pre_v3_and_unknown(self):
        def rename_image(r):
            next(n for n in r.iter("Node") if n.get("pluginName") == "Polygon").set("pluginName", "Image")

        def unknown_param(r):
            col = next(n for n in r.iter("Node") if n.get("pluginName") == "ColorHSB")
            mp.param(col, "Hue").set("name", "Premultiply")

        def unknown_module(r):
            next(n for n in r.iter("Node") if n.get("pluginName") == "Polygon").set("pluginName", "Polygonn")

        def removed_module(r):
            next(n for n in r.iter("Node") if n.get("pluginName") == "Polygon").set("pluginName", "AudioToImage")

        cases = [(rename_image, "pre-3.0 name"), (removed_module, "removed in 3.0"), (unknown_param, "not in Magic 3's ColorHSB"), (unknown_module, "not a Magic 3.0 module")]
        for mutate, expected in cases:
            with self.subTest(mutate.__name__):
                root = demo()
                mutate(root)
                self.assertTrue(any(expected in m for _, m in mp.check(root)))

    def test_bypass_follows_magic(self):
        cases = [("Polygon", False), ("Fractal", False), ("Text", False), ("ColorHSB", True), ("Bloom", True), ("Kaleidoscope", True)]
        for plugin, expected in cases:
            with self.subTest(plugin):
                self.assertEqual(mp.has_bypass(plugin), expected)

    def test_diff_ignores_renumbered_ids(self):
        root = demo()
        renumbered = mp.parse(mp.encode(mp.serialize(root)))
        old = {}
        for e in renumbered.iter():
            if e.tag in ("Node", "InputValue", "Track", "Layer") and e.get("id"):
                old[e.get("id")] = str(int(e.get("id")) + 10000)
        for e in renumbered.iter():
            for k in ("id", "feature", "trackID", "layerID"):
                if e.get(k) in old and (k != "feature" or e.get("layerID") == str(mp.GLOBAL_LAYER)) and \
                        (k != "id" or e.tag in ("Node", "InputValue", "Track", "Layer", "Child")):
                    e.set(k, old[e.get(k)])
        self.assertEqual(mp.diff(root, renumbered), [])


class DriveMagicTests(unittest.TestCase):
    """The osascript layer and mmv_verify's live flow, with Magic and macOS mocked out."""

    def test_magic_windows_reports_denied_access(self):
        cases = [(("", "osascript is not allowed assistive access. (-1719)"), RuntimeError),
                 (("", "timed out after 10s; a macOS prompt may be waiting"), RuntimeError),
                 (("", "Can't get process \"Magic\". (-1728)"), None),
                 (("a, b.magic - Editor\nInput Sources", ""), ["a, b.magic - Editor", "Input Sources"])]
        for result, expected in cases:
            with self.subTest(result=result), mock.patch.object(mp, "_osascript", return_value=result):
                if expected is RuntimeError:
                    with self.assertRaises(RuntimeError):
                        mp.magic_windows()
                else:
                    self.assertEqual(mp.magic_windows(), expected)

    @staticmethod
    def osascript_with_frontmost(front):
        sent = []

        def fake(script, timeout=10):
            sent.append(script)
            return (front, "") if "frontmost" in script else ("", "")
        return fake, sent

    def test_press_only_types_when_magic_is_frontmost(self):
        for front, typed in (("Terminal", False), ("Magic", True), (mp.MAGIC_NAME, True)):
            with self.subTest(front=front):
                fake, sent = self.osascript_with_frontmost(front)
                clock = mock.Mock(time=mock.Mock(side_effect=[0, 0, 1, 2, 3.5]), sleep=mock.Mock())
                with mock.patch.object(mp, "_osascript", side_effect=fake), mock.patch.object(mp, "time", clock):
                    if typed:
                        mp.press("key code 36")
                    else:
                        with self.assertRaises(RuntimeError):
                            mp.press("key code 36")
                self.assertEqual(any("key code 36" in s for s in sent), typed)

    def run_live(self, restore, current, loads, grab_rc=0):
        a = mock.Mock(restore=restore, dismiss=False, file="/tmp/t.magic")
        with mock.patch.object(mmv_verify, "current_project_path", return_value=current), \
                mock.patch.object(mmv_verify.m, "load", side_effect=loads) as load, \
                mock.patch.object(mmv_verify, "grab_live", return_value=grab_rc), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = mmv_verify.live(a, "srv", [])
        return rc, [c.args[0] for c in load.call_args_list]

    def test_restore_refuses_when_the_open_project_is_unknown(self):
        self.assertEqual(self.run_live(True, ("Show.magic", None), []), (2, []))

    def test_restore_runs_after_every_outcome(self):
        editor = ["t.magic - Editor"]
        cases = [("loaded", [(True, editor), (True, [])], 0, 0),
                 ("never named", [(False, []), (True, [])], 0, 2),
                 ("error dialog", [(True, editor + ["ISF Code Errors: X"]), (True, [])], 0, 2),
                 ("black frame", [(True, editor), (True, [])], 2, 2)]
        for name, loads, grab_rc, expected in cases:
            with self.subTest(name):
                rc, opened = self.run_live(True, ("Show.magic", "/shows/Show.magic"), loads, grab_rc)
                self.assertEqual((rc, opened), (expected, ["/tmp/t.magic", "/shows/Show.magic"]))

    def test_editor_title_is_not_an_error_dialog(self):
        rc, _ = self.run_live(False, (None, None), [(True, ["Terror.magic - Editor"])])
        self.assertEqual(rc, 0)


class ListenTests(unittest.TestCase):
    def test_listen_collects_messages(self):
        import socket
        import threading
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()
        packets = [("/vj/beat", [0.5]), ("/vj/beat", [1.0]), ("/vj/level", [0.25])]

        def send():
            time.sleep(0.3)
            tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for addr, args in packets:
                tx.sendto(mmv_verify.osc_packet(addr, args[0]), ("127.0.0.1", port))
            tx.sendto(b"not an osc packet", ("127.0.0.1", port))
            tx.close()
        threading.Thread(target=send).start()
        got = mp.listen(port, 1.0)
        self.assertEqual(got, {"/vj/beat": [0.5, 1.0], "/vj/level": [0.25]})

    def test_parse_packet(self):
        def s(text):
            return text.encode() + b"\0" * (4 - len(text) % 4)
        a = s("/a") + s(",f") + struct.pack(">f", 0.5)
        b = s("/b") + s(",is") + struct.pack(">i", 7) + s("hi")
        bundle = b"#bundle\0" + bytes(8) + struct.pack(">i", len(a)) + a + struct.pack(">i", len(b)) + b
        cases = [(a, [("/a", ",f", [0.5], False)]), (b, [("/b", ",is", [7, "hi"], False)]),
                 (s("/c") + s(",TFN"), [("/c", ",TFN", [True, False, None], False)]),
                 (bundle, [("/a", ",f", [0.5], True), ("/b", ",is", [7, "hi"], True)])]
        for data, expected in cases:
            with self.subTest(expected[0][0], bundled=expected[0][3]):
                self.assertEqual(mp.parse_packet(data), expected)

    def test_osc_packet_is_padded_for_every_address_length(self):
        for n in range(12):
            addr = "/" + "x" * n
            with self.subTest(addr=addr):
                self.assertEqual(mp.parse_packet(mmv_verify.osc_packet(addr, 0.25)), [(addr, ",f", [0.25], False)])

    def test_listen_refuses_reserved_ports(self):
        self.assertEqual(mp.RESERVED_PORTS, set())            # nothing is reserved unless the environment says so
        with mock.patch.object(mp, "RESERVED_PORTS", {9201, 8000}):
            for port in (9201, 8000):
                with self.subTest(port=port), self.assertRaises(ValueError):
                    mp.listen(port, 0.1)


def _osc_id(root):
    return next(n.get("id") for n in root.iter("Node") if n.get("pluginName") == "OSCSender")


@unittest.skipUnless(os.environ.get("MAGICPROJ_LIVE") == "1", "replaces Magic's project; set MAGICPROJ_LIVE=1")
class LiveMagicTests(unittest.TestCase):
    """Builds, loads and edits a project in the running Magic and reads the
    result over Syphon. Reloads MAGICPROJ_RESTORE (if set) afterwards."""

    @classmethod
    def tearDownClass(cls):
        restore = os.environ.get("MAGICPROJ_RESTORE")
        if restore:
            mp.load(restore)

    def grab(self, server):
        out = subprocess.run([mp.SYPHON_PYTHON, os.path.abspath(mp.__file__), "grab", "--server", server, "--wait", "2"],
                             env=dict(os.environ, PYTHONPATH=mp.SYPHON_PATH), capture_output=True, text=True, check=True)
        import json
        return json.loads(out.stdout)

    def test_build_edit_load_grab(self):
        server = "magicproj-e2e"
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "e2e.magic")
            # Hue 0 = red, 1/3 = green; full brightness proves Internals 0 = Graphics Width.
            root = demo(syphon=server)
            root = mp.add_global(root, "Bright", 0, "calc", [("Expression", "if(Width > 1900 and Width < 1940, 1, 0.3)")])
            col = next(n for n in mp.node_table(root) if n["plugin"] == "ColorHSB")
            root = mp.edit_param(root, "Main", col["id"], "Brightness", source="global:Bright")
            for hue, channel in ((0.0, 0), (1 / 3, 1)):
                with self.subTest(hue=hue):
                    mp.write(path, mp.edit_global(root, "Hue", value=hue))
                    ok, wins = mp.load(path)
                    self.assertTrue(ok, wins)
                    stats = self.grab(server)
                    centre = stats["grid"][1][1]
                    self.assertGreater(centre[channel], 200, stats)
                    self.assertLess(sum(centre) - centre[channel], 120, stats)
                time.sleep(0.5)


class MmvExtensions(unittest.TestCase):
    """Additions made in mmv-skills: isf= nodes, scene_input(), layer: sources."""

    def build(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        fs = os.path.join(d, "Mine.fs")
        with open(fs, "w") as f:
            f.write('/*{"ISFVSN":"2.0","INPUTS":[{"NAME":"a","TYPE":"float","DEFAULT":0.5},'
                    '{"NAME":"fftImage","LABEL":"Source","TYPE":"audioFFT"}]}*/\nvoid main(){gl_FragColor=vec4(a);}\n')
        b = mp.Builder(syphon="t", audio_device="Dev")
        look = b.scene("Look")
        e = look.scene_input()
        fx = look.node("Mine", {"A": 0.7, "Source": "layer:Source 0"}, inputs=[e], isf=fs)
        look.output(fx)
        main = b.scene("Main")
        lm = main.scene_module(look)
        main.output(lm)
        return b.build(), fs

    def test_isf_node_and_scene_input(self):
        root, fs = self.build()
        nodes = {n.get("pluginName"): n for n in root.iter("Node")}
        self.assertEqual(nodes["Mine"].get("isfFilename"), fs)
        self.assertEqual(nodes["SceneInput"].get("sceneInputID"), "0")
        self.assertEqual(nodes["Look"].get("sceneID"), "0")
        self.assertEqual([i for l, i in mp.check(root) if l == "error"], [])

    def test_layer_source_resolves_to_layer_id(self):
        root, _ = self.build()
        layer = next(l for l in root.iter("Layer") if l.get("name") == "Source 0")
        node = next(n for n in root.iter("Node") if n.get("pluginName") == "Mine")
        src = next(iv for iv in node.iter("InputValue") if iv.get("name") == "Source")
        self.assertEqual(src.get("value"), layer.get("id"))

    def test_missing_isf_file_warns(self):
        b = mp.Builder(syphon="t", audio_device="Dev")
        s = b.scene("A")
        s.output(s.node("Nope", {}, isf="/nonexistent/Nope.fs"))
        msgs = [m for l, m in mp.check(b.build()) if l == "warn"]
        self.assertTrue(any("isfFilename not found" in m for m in msgs))

    def test_unknown_isf_param_warns(self):
        root, _ = self.build()
        node = next(n for n in root.iter("Node") if n.get("pluginName") == "Mine")
        mp.param(node, "A").set("name", "Typo")
        msgs = [m for l, m in mp.check(root) if l == "warn"]
        self.assertTrue(any("params ['Typo'] are not in the ISF header" in m for m in msgs), msgs)

    def test_isf_bypass_follows_image_input(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        cases = [("Gen", [], False), ("Fx", [{"NAME": "inputImage", "TYPE": "image"}], True)]
        for name, inputs, pin in cases:
            with self.subTest(name):
                fs = os.path.join(d, name + ".fs")
                with open(fs, "w") as f:
                    f.write('/*%s*/\nvoid main(){gl_FragColor=vec4(1.0);}\n' % json.dumps({"ISFVSN": "2.0", "INPUTS": inputs}))
                b = mp.Builder(syphon="t", audio_device="Dev")
                s = b.scene("A")
                s.output(s.node(name, {}, isf=fs))
                node = next(n for n in b.build().iter("Node") if n.get("pluginName") == name)
                self.assertEqual(mp.param(node, "Bypass") is not None, pin)


if __name__ == "__main__":
    unittest.main()
