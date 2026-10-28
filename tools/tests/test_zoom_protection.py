"""Repository-only ledger tests with disposable Git repositories; no Zoom execution."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "zoom_protection.py"
spec = importlib.util.spec_from_file_location("zoom_protection", SCRIPT)
zoom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zoom)


class LedgerTests(unittest.TestCase):
    def git(self, *args, repo=None, data=None):
        return subprocess.check_output(["git", "-C", str(repo or self.repo), *args],
                                       input=data, stderr=subprocess.PIPE)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        template = self.root / "empty-template"
        template.mkdir()
        self.git("init", "--template=" + str(template))
        self.git("config", "user.name", "Ledger test")
        self.git("config", "user.email", "ledger@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "commit.gpgsign", "false")
        for path in zoom.PROTECTED_PATHS:
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(("synthetic fixture: " + path + "\nsecond line\n").encode())
        self.commit()
        self.baseline = self.git("rev-parse", "HEAD").decode().strip()
        self.ledger = self.root / "ledger.json"
        self.value = zoom.generate(self.repo, "HEAD")
        self.write_ledger()

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-m", "fixture")

    def write_ledger(self):
        self.ledger.write_text(json.dumps(self.value), encoding="utf-8")

    def validate(self, ref="HEAD", repo=None):
        return zoom.validate(repo or self.repo, self.ledger, ref)

    def assert_fail(self, ref="HEAD", repo=None):
        with self.assertRaises(zoom.LedgerError):
            self.validate(ref, repo)

    def test_lf_checkout(self):
        clone = self.root / "lf"
        subprocess.check_output(["git", "-c", "core.autocrlf=false", "clone", "--no-local",
                                 str(self.repo), str(clone)], stderr=subprocess.PIPE)
        for path in zoom.PROTECTED_PATHS:
            self.assertNotIn(b"\r\n", (clone / path).read_bytes())
        self.assertEqual(self.validate(repo=clone)["worktree_gate"], "PASS")

    def test_crlf_checkout(self):
        clone = self.root / "crlf"
        subprocess.check_output(["git", "-c", "core.autocrlf=true", "clone", "--no-local",
                                 str(self.repo), str(clone)], stderr=subprocess.PIPE)
        # Persist matching checkout configuration for the separate dirty-state check.
        self.git("config", "core.autocrlf", "true", repo=clone)
        for path in zoom.PROTECTED_PATHS:
            self.assertIn(b"\r\n", (clone / path).read_bytes())
        result = self.validate(repo=clone)
        self.assertEqual(result["blob_gate"], "PASS")
        self.assertEqual(result["worktree_gate"], "PASS")

    def test_changed_blob_one_byte(self):
        path = self.repo / zoom.PROTECTED_PATHS[0]
        data = path.read_bytes()
        path.write_bytes(b"X" + data[1:])
        self.commit()
        self.assert_fail()
        self.assertEqual(self.validate(self.baseline)["blob_gate"], "PASS")

    def test_dirty_worktree_and_cli_are_separate(self):
        (self.repo / zoom.PROTECTED_PATHS[0]).write_bytes(b"worktree-only change\n")
        result = self.validate()
        self.assertEqual(result["blob_gate"], "PASS")
        self.assertEqual(result["worktree_gate"], "FAIL")
        self.assertTrue(result["dirty"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = zoom.main(["validate", "--repo", str(self.repo),
                              "--ledger", str(self.ledger), "--ref", "HEAD"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["blob_gate"], "PASS")

    def test_missing_path(self):
        (self.repo / zoom.PROTECTED_PATHS[0]).unlink()
        self.commit()
        self.assert_fail()

    def test_wrong_hash(self):
        self.value["files"][zoom.PROTECTED_PATHS[0]] = "0" * 64
        self.write_ledger()
        self.assert_fail()

    def test_unknown_target_ref(self):
        self.assert_fail("refs/heads/no-such-ledger-test")
        self.assert_fail("--bad-option")

    def test_unknown_reviewed_ref(self):
        self.value["ref"] = "0" * 40
        self.write_ledger()
        self.assert_fail()

    def test_attributes_and_autocrlf_variation(self):
        expected = zoom.blob_hashes(self.repo, self.baseline)[1]
        for eol, autocrlf in (("crlf", "true"), ("lf", "input"), ("lf", "false")):
            self.git("config", "core.autocrlf", autocrlf)
            (self.repo / ".gitattributes").write_bytes(
                ("* text eol=" + eol + "\n# autocrlf=" + autocrlf + "\n").encode())
            self.git("add", ".gitattributes")
            self.git("commit", "-m", "attributes " + autocrlf)
            self.assertEqual(zoom.blob_hashes(self.repo, "HEAD")[1], expected)
            self.assertEqual(self.validate()["blob_gate"], "PASS")

    def test_duplicate_json_path(self):
        raw = self.ledger.read_text()
        path = zoom.PROTECTED_PATHS[0]
        raw = raw.replace('"files": {', '"files": {' + json.dumps(path) + ': "' + "0" * 64 + '",')
        self.ledger.write_text(raw, encoding="utf-8")
        self.assert_fail()

    def test_missing_ledger_entry(self):
        del self.value["files"][zoom.PROTECTED_PATHS[0]]
        self.write_ledger()
        self.assert_fail()

    def test_extra_ledger_entry(self):
        self.value["files"]["tools/environment_zoom/unreviewed"] = "0" * 64
        self.write_ledger()
        self.assert_fail()

    def test_extra_protected_tree_path(self):
        (self.repo / "tools/environment_zoom/unreviewed").write_bytes(b"unexpected\n")
        self.commit()
        self.assert_fail()

    def test_symlink_mode(self):
        oid = self.git("hash-object", "-w", "--stdin", data=b"some-target").decode().strip()
        self.git("update-index", "--cacheinfo", "120000," + oid + "," + zoom.PROTECTED_PATHS[0])
        self.git("commit", "-m", "symlink in index")
        self.assert_fail()

    def test_submodule_mode(self):
        self.git("update-index", "--cacheinfo", "160000," + self.baseline + "," + zoom.PROTECTED_PATHS[0])
        self.git("commit", "-m", "submodule in index")
        self.assert_fail()

    def test_executable_mode(self):
        self.git("update-index", "--chmod=+x", zoom.PROTECTED_PATHS[0])
        self.git("commit", "-m", "unexpected mode")
        self.assert_fail()

    def test_missing_blob(self):
        oid = self.git("rev-parse", "HEAD:" + zoom.PROTECTED_PATHS[0]).decode().strip()
        blob = self.repo / ".git/objects" / oid[:2] / oid[2:]
        blob.chmod(0o600)  # Git objects are read-only on Windows, too.
        blob.unlink()
        self.assert_fail()

    def test_invalid_schema_and_digest(self):
        self.value["content_source"] = "worktree"
        self.write_ledger()
        self.assert_fail()
        self.value["content_source"] = "git-blob"
        self.value["files"][zoom.PROTECTED_PATHS[0]] = "not-a-sha256"
        self.write_ledger()
        self.assert_fail()


if __name__ == "__main__":
    unittest.main()
