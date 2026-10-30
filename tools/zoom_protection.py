"""Exact Zoom protection against reviewed Git blob bytes; no checkout normalization."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

LEDGER = "docs/versanium/brave-36838-phase1/zoom-protection-ledger.json"
# Reviewed scope, independent of ledger entries: omissions cannot shrink protection.
PROTECTED_PATHS = (
    "tools/apply_environment_zoom.py",
    "tools/check_environment_zoom_revision.py",
    "tools/environment_zoom/chromium.patch",
    "tools/environment_zoom/java/org/chromium/components/browser_ui/accessibility/EnvironmentZoomSettings.java",
    "tools/environment_zoom/java/org/chromium/components/browser_ui/accessibility/EnvironmentZoomTransfer.java",
    "tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoom.java",
    "tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomBackup.java",
    "tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomPersistence.java",
    "tools/environment_zoom/java/org/chromium/content_public/browser/EnvironmentZoomPolicy.java",
    "tools/environment_zoom/res/values-ja/titanium_zoom_strings.xml",
    "tools/environment_zoom/res/values/titanium_zoom_strings.xml",
    "tools/environment_zoom/tests/EnvironmentZoomBackupTest.java",
    "tools/environment_zoom/tests/EnvironmentZoomBridgeTest.java",
    "tools/environment_zoom/tests/EnvironmentZoomPersistenceTest.java",
    "tools/environment_zoom/tests/EnvironmentZoomPolicyTest.java",
    "tools/environment_zoom/tests/ParseJavaSources.java",
    "tools/environment_zoom/tests/check_android_api.py",
    "tools/environment_zoom/tests/check_build_pin.py",
    "tools/environment_zoom/tests/check_jni_abi.py",
    "tools/environment_zoom/tests/check_patch.py",
    "tools/environment_zoom/tests/check_settings_resources.py",
    "tools/environment_zoom/tests/check_video_fullscreen.py",
    "tools/environment_zoom/tests/fixtures/legacy-zoom-v1.properties",
    "tools/environment_zoom/tests/run_local_tests.py",
)
SCOPE = ("tools/apply_environment_zoom.py", "tools/check_environment_zoom_revision.py",
         "tools/environment_zoom")


class LedgerError(ValueError):
    pass


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise LedgerError("git " + args[0] + ": " + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def resolve_commit(repo, ref):
    if not isinstance(ref, str) or not ref or "\0" in ref:
        raise LedgerError("invalid ref")
    return git(repo, "rev-parse", "--verify", "--end-of-options",
               ref + "^{commit}").decode("ascii").strip()


def blob_hashes(repo, ref):
    commit = resolve_commit(repo, ref)
    entries = {}
    for record in git(repo, "ls-tree", "-r", "-z", commit, "--", *SCOPE).split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split()
        path = path.decode("utf-8")
        if path in entries:
            raise LedgerError("duplicate tree path: " + path)
        if mode != "100644" or kind != "blob":
            raise LedgerError("unexpected file type/mode: " + path)
        entries[path] = oid
    expected = set(PROTECTED_PATHS)
    if set(entries) != expected:
        raise LedgerError("protected scope mismatch; missing=" +
                          repr(sorted(expected - set(entries))) + "; extra=" +
                          repr(sorted(set(entries) - expected)))
    # Read binary stdout directly: no text decoding, filters, EOL conversion or fallback.
    hashes = {path: hashlib.sha256(git(repo, "cat-file", "blob", entries[path])).hexdigest()
              for path in PROTECTED_PATHS}
    return commit, hashes


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise LedgerError("duplicate ledger key: " + key)
        value[key] = item
    return value


def read_ledger(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise LedgerError("cannot read ledger: " + str(error)) from error
    required = {"schema_version", "hash_algorithm", "content_source", "ref", "files"}
    if not isinstance(value, dict) or set(value) != required:
        raise LedgerError("invalid ledger fields")
    if (type(value["schema_version"]) is not int or value["schema_version"] != 2
            or value["hash_algorithm"] != "sha256" or value["content_source"] != "git-blob"):
        raise LedgerError("unsupported canonical hash schema")
    if not isinstance(value["ref"], str) or not re.fullmatch(r"[0-9a-f]{40}", value["ref"]):
        raise LedgerError("ledger ref must be a full reviewed commit SHA")
    files = value["files"]
    if not isinstance(files, dict) or set(files) != set(PROTECTED_PATHS):
        raise LedgerError("ledger must contain exactly the reviewed 24 paths")
    if any(not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
           for digest in files.values()):
        raise LedgerError("invalid sha256")
    return value


def generate(repo, ref):
    commit, hashes = blob_hashes(repo, ref)
    return {"schema_version": 2, "hash_algorithm": "sha256",
            "content_source": "git-blob", "ref": commit, "files": hashes}


def validate(repo, ledger_path, ref):
    ledger = read_ledger(ledger_path)
    baseline, reviewed = blob_hashes(repo, ledger["ref"])
    if baseline != ledger["ref"] or reviewed != ledger["files"]:
        raise LedgerError("ledger does not match its reviewed commit")
    commit, actual = blob_hashes(repo, ref)
    mismatches = [path for path in PROTECTED_PATHS if actual[path] != ledger["files"][path]]
    if mismatches:
        raise LedgerError("Git blob SHA256 mismatch: " + repr(mismatches))
    # Separate from blob validation; dirty state never selects a different byte source.
    status = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    return {"blob_gate": "PASS", "reviewed_ref": baseline, "target_ref": commit,
            "files_verified": len(actual), "worktree_gate": "FAIL" if status else "PASS",
            "dirty": bool(status),
            "worktree_status": status.decode("utf-8", "replace").split("\0")[:-1]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "validate"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ref", required=True, help="Explicit commit/ref to read from Git")
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            result = generate(args.repo, args.ref)
            code = 0
        else:
            result = validate(args.repo, args.ledger or args.repo / LEDGER, args.ref)
            code = 2 if result["dirty"] else 0
        print(json.dumps(result, indent=2))
        return code
    except (LedgerError, OSError, UnicodeError) as error:
        print(json.dumps({"blob_gate": "FAIL", "error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
