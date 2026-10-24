"""Tests for Run9 diagnostic-update preparation; no saved host or compiler is used."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "diagnostic_update", ROOT / "tools/versanium/prepare_diagnostic_update.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
OLD = Path("/tmp/versanium156/run9-host-fix")
NEW = Path("/tmp/versanium156/passive-diagnostics-final")


class DiagnosticUpdateTests(unittest.TestCase):
    def test_exact_four_transformations_match_selected_156(self):
        if not OLD.is_dir() or not NEW.is_dir():
            self.skipTest("selected pinned156 comparison trees unavailable")
        for name, (before, after) in d.CHANGED.items():
            with self.subTest(name=name):
                original = (OLD / name).read_bytes()
                expected = (NEW / name).read_bytes()
                self.assertEqual(d.sha(original), before)
                self.assertEqual(d.sha(expected), after)
                self.assertEqual(d.update_bytes(name, original), expected)

    def test_changed_file_rejects_repeat_and_drift(self):
        if not OLD.is_dir() or not NEW.is_dir():
            self.skipTest("selected pinned156 comparison trees unavailable")
        for name in d.CHANGED:
            with self.subTest(name=name):
                with self.assertRaises(RuntimeError):
                    d.update_bytes(name, (NEW / name).read_bytes())
                old = (OLD / name).read_bytes() + b"\n// unrelated drift\n"
                transformed = d.update_bytes(name, old)
                self.assertNotEqual(d.sha(transformed), d.CHANGED[name][1])

    def test_unchanged_jni_gn_payload_hashes(self):
        if not OLD.is_dir() or not NEW.is_dir():
            self.skipTest("selected pinned156 comparison trees unavailable")
        for name, digest in d.UNCHANGED_INTEGRATION.items():
            if name == "chrome/browser/flag-metadata.json":
                continue
            with self.subTest(name=name):
                self.assertEqual(d.file_sha(OLD / name), digest)
                self.assertEqual(d.file_sha(NEW / name), digest)

    def test_flag_metadata_exact_pipeline(self):
        from tools.versanium import flag_metadata_pipeline as pipeline
        head = Path("/tmp/versanium156/source/chrome/browser/flag-metadata.json")
        if not head.is_file():
            self.skipTest("fixed Chromium156 metadata unavailable")
        data = head.read_bytes()
        expiry, final = pipeline.reproduce(data)
        self.assertEqual(d.sha(data), d.FLAG_HEAD_SHA)
        self.assertEqual(d.sha(pipeline.apply_candidate_entries(data)), d.FLAG_CANDIDATE_ONLY_SHA)
        self.assertEqual(d.sha(expiry), d.FLAG_EXPIRY_SHA)
        self.assertEqual(d.sha(final), d.FLAG_FINAL_SHA)
        self.assertEqual(pipeline.patch_sh_flags((ROOT / "patch.sh").read_text()), pipeline.EXPIRY_FLAGS)
        for name in pipeline.EXPIRY_FLAGS:
            start = final.index(('"name": "' + name + '"').encode())
            self.assertIn(b'"expiry_milestone": -1', final[start:final.index(b"}", start)])
        for name in pipeline.CANDIDATE_FLAGS:
            self.assertEqual(final.count(('"name": "' + name + '"').encode()), 1)

    def test_native_edges_and_other_toolchain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = "content/browser/renderer_host/render_frame_host_impl.cc"
            edge = ("build obj/content/browser/browser/render_frame_host_impl.o: cxx ../../"
                    + source + "\n").encode()
            (root / "browser.ninja").write_bytes(edge)
            other = root / "android_clang_arm/browser.ninja"
            other.parent.mkdir()
            other.write_bytes(edge.replace(b"build obj/", b"build android_clang_arm/obj/"))
            self.assertEqual(d.object_for_source(
                root, source, "obj/content/browser/browser/render_frame_host_impl.o"),
                "obj/content/browser/browser/render_frame_host_impl.o")

    def test_native_edge_rejects_duplicate_wrong_rule_or_implicit_source(self):
        source = "chrome/browser/about_flags.cc"
        good = ("build obj/chrome/browser/browser/about_flags.o: cxx ../../" + source + "\n").encode()
        cases = [good + good, good.replace(b": cxx ", b": cc "),
                 good.replace(("../../" + source).encode(), b"other.cc | ../../" + source.encode())]
        for content in cases:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "browser.ninja").write_bytes(content)
                with self.assertRaises(RuntimeError):
                    d.object_for_source(root, source)

    def test_chrome_java_exact_output_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build.ninja").write_bytes(b"build chrome_java: phony obj/chrome_java.stamp\n")
            self.assertEqual(d.has_exact_output(root, "chrome_java"), 1)
            (root / "duplicate.ninja").write_bytes(b"build chrome_java: phony other\n")
            self.assertEqual(d.has_exact_output(root, "chrome_java"), 2)

    def test_only_source_diff_may_change_in_provenance(self):
        original = {"repository_commit": d.BASE, "gn_version": "2578",
                    "tracked_source_diff_sha256": "old", "inputs_sha256": {"clang_binary": "x"}}
        current = json.loads(json.dumps(original))
        current["tracked_source_diff_sha256"] = "host-corrected"
        self.assertTrue(d.comparable_to_original(current, original))
        current["gn_version"] = "changed"
        self.assertFalse(d.comparable_to_original(current, original))


if __name__ == "__main__":
    unittest.main()
