"""Validate, and only with --apply update, four Run9 diagnostic source files.

The default is read-only apart from a new evidence JSON outside the saved tree.
It never compiles, regenerates GN, syncs dependencies, cleans, resets, or signs.
The older three-accessor recovery helper and its conditions are not imported or changed.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True

BASE = "7d9102f4f0e35dec9f69425de44cd889836a88ac"
PRIOR_CONTROLLER = "ebfc81cf6ef4388f0f1b29be86e0eb212bc7bce1"
TARGET_CONTROLLER = "60b00375def663584dfd5c6fd249d25498eeafb2"
PIN = "1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775"
VANADIUM = "2ae4335402eabcc6e025f3400185fe25094d8521"
ARCHIVE_SHA = "101cc6e2b6e0c18d1ca56993b16d9bd5176a02e3451b2ea065842937fdeda0b6"
VERSION = "156.0.8078.47"

CHANGED = {
    "chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java": (
        "ec5d0045359e45462f433271508c1d70ceece918d761f4cc0f8e9a508f91cb88",
        "a75358c25f758ecd385fb8d5148900378af46ad838eb634f165122897a6daa65",
    ),
    "chrome/android/java/src/org/chromium/chrome/browser/tab/TabImpl.java": (
        "c9db6e6999d771cbfd932219754c68a7bca0622af427eead4e7b0f5ee93a9074",
        "10f9dd82ad1939ea214b455dae85198937455f39861eddcd8af72964e222f2e4",
    ),
    "chrome/browser/about_flags.cc": (
        "b12f0b78c697f3c1fda0ddb62d1aeab2641951066e2023d66ed46a2244000fca",
        "ff15f1be73fec10f8cc259cc556b1ea30c5cbb16fb4ac447291607086b9acde1",
    ),
    "content/browser/renderer_host/render_frame_host_impl.cc": (
        "dc1cd0a483221911df155daf88594bd6c9354b67ffc7b3f239bfd0ef08feedf9",
        "48315bb8aad528f8eca6fbd093692a9a656731d2aa5bc2946a2a716a3e6e3ff4",
    ),
}

UNCHANGED_INTEGRATION = {
    "content/browser/renderer_host/versanium_youtube_candidate.h": "0f21bf35573aad1e67ac16cc830cab68ddeba09be0b867fd8738f897bd805753",
    "content/browser/web_contents/web_contents_android.cc": "485ea67f8468c78080425f0df1871eab8f2c01cc3388b0a11cfdcc0ba3e97eeb",
    "content/browser/web_contents/web_contents_android.h": "1aa267c5b2ad6a6d52dc37a02a906fb82bb475f765e9c8399357e556d02bf9e4",
    "content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsImpl.java": "98d03d135bf6128d9324f3c5eff31525ef15d0cd2a643b3da47f11dcc0571484",
    "content/public/android/java/src/org/chromium/content_public/browser/WebContents.java": "7cb95e10b38e55a1b1007e590eb8fd0dbe946f12fb28fb5954a5cae42a30c246",
    "content/browser/BUILD.gn": "7242bd860e255c600996413d12bdd494cca9c192e7dee285c8e7ebeb6f77b193",
    "chrome/browser/flag-metadata.json": "293f70fc5fb06168611389d93af5f99f70a3adcb77d9cea3d432a4de2d5f199c",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args, text=True):
    return subprocess.check_output(["git", "-C", str(root), *args], text=text).strip()


def git_blob(root, revision, name):
    return subprocess.check_output(["git", "-C", str(root), "show", revision + ":" + name])


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def replace_once(data, old, new, label):
    require(data.count(old) == 1, "Unexpected pre-update source for " + label)
    return data.replace(old, new, 1)


def update_bytes(path, data):
    if path.endswith("FullscreenVideoPictureInPictureController.java"):
        data = replace_once(
            data,
            b'''                || !LibraryLoader.getInstance().isInitialized()) return;
        Tab tab = mActivityTabProvider.get();''',
            b'''                || !LibraryLoader.getInstance().isInitialized()) return;
        if (mActivity.isDestroyed() || mActivity.isFinishing()) return;
        Tab tab = mActivityTabProvider.get();''',
            path,
        )
        old = b'''        android.app.AppOpsManager appOps = mActivity.getSystemService(android.app.AppOpsManager.class);
        int appOp = appOps == null ? -1 : appOps.checkOpNoThrow(
                android.app.AppOpsManager.OPSTR_PICTURE_IN_PICTURE,
                android.os.Process.myUid(), mActivity.getPackageName());
        String record = stage
                + " full=" + contents.hasActiveEffectivelyFullscreenVideo()
                + " videoAllows=" + contents.isPictureInPictureAllowedForFullscreenVideo()
                + " devicePip=" + mActivity.getPackageManager().hasSystemFeature(
                        PackageManager.FEATURE_PICTURE_IN_PICTURE)
                + " appOp=" + appOp
                + " recentTaskAllowed=" + canStartPipBasedOnRecentTasks()
                + " inPip=" + mActivity.isInPictureInPictureMode()
                + " changing=" + mActivity.isChangingConfigurations()
                + " finishing=" + mActivity.isFinishing();'''
        new = b'''        String record = stage
                + " inPip=" + mActivity.isInPictureInPictureMode()
                + " changing=" + mActivity.isChangingConfigurations();'''
        return replace_once(data, old, new, path)
    if path.endswith("TabImpl.java"):
        old = b'''        boolean diagnostics = command.hasSwitch("versanium-youtube-diagnostics");
        if (!pip && !background && !diagnostics) return;'''
        new = b'''        if (!pip && !background) return;'''
        data = replace_once(data, old, new, path)
        start = b'''        if (diagnostics) Log.i("VersaniumYT", "stage=%s injection_requested mobile=%b", stage,mobile);
        contents.applyVersaniumYoutubeCandidate(mobile, result -> {'''
        begin = data.find(start)
        require(begin >= 0, "Missing old diagnostic callback in " + path)
        end_marker = b'''        });
        java.lang.ref.WeakReference<TabImpl> owner'''
        end = data.find(end_marker, begin)
        require(end >= 0, "Unbounded old diagnostic callback in " + path)
        replacement = b'''        // Diagnostics never authorizes injection or owns a script-result callback.
        contents.applyVersaniumYoutubeCandidate(mobile, null);
        java.lang.ref.WeakReference<TabImpl> owner'''
        return data[:begin] + replacement + data[end + len(b"        });\n        java.lang.ref.WeakReference<TabImpl> owner"):]
    if path.endswith("about_flags.cc"):
        return replace_once(
            data,
            b"Log only PiP decision booleans for normal YouTube tabs. Does not change playback. Disable after testing.",
            b"Log existing PiP decision stages for normal YouTube tabs; no script injection or fullscreen permission probes. Disable after testing.",
            path,
        )
    if path.endswith("render_frame_host_impl.cc"):
        data = replace_once(
            data,
            b'  options += command->HasSwitch("versanium-youtube-diagnostics") ? u"true" : u"false";',
            b'  options += u"false";  // Diagnostics is passive Java event logging only.',
            path,
        )
        return replace_once(
            data,
            b'''  return candidate_command->HasSwitch("versanium-youtube-pip-candidate") ||
         candidate_command->HasSwitch("versanium-youtube-background-candidate") ||
         candidate_command->HasSwitch("versanium-youtube-diagnostics");''',
            b'''  return candidate_command->HasSwitch("versanium-youtube-pip-candidate") ||
         candidate_command->HasSwitch("versanium-youtube-background-candidate");''',
            path,
        )
    raise RuntimeError("No reviewed transformation for " + path)


def original_manifest(archive):
    require(file_sha(archive) == ARCHIVE_SHA, "Original Run9 provenance ZIP digest mismatch")
    with zipfile.ZipFile(archive) as zipped:
        names = [name for name in zipped.namelist() if name.endswith("build-provenance.json")]
        require(len(names) == 1, "Expected exactly one original build-provenance.json")
        require(zipped.getinfo(names[0]).file_size < 1024 * 1024, "Unexpected original provenance size")
        return json.loads(zipped.read(names[0]))


def comparable_to_original(current, original):
    left = dict(current)
    right = dict(original)
    left.pop("tracked_source_diff_sha256", None)
    right.pop("tracked_source_diff_sha256", None)
    return left == right


def ninja_lines(path):
    pending = None
    with path.open("rb") as stream:
        for physical in stream:
            line = physical.removesuffix(b"\n").removesuffix(b"\r")
            if pending is None and line.lstrip(b" \t").startswith(b"#"):
                continue
            if pending is not None:
                line = pending + line.lstrip(b" \t")
                pending = None
            dollars = len(line) - len(line.rstrip(b"$"))
            if physical.endswith(b"\n") and dollars % 2:
                pending = line[:-1]
                continue
            yield line, True
    if pending is not None:
        yield pending, False


def object_for_source(output, source, expected=None):
    explicit = ("../../" + source).encode("ascii")
    matches = []
    for graph in output.rglob("*.ninja"):
        for line, complete in ninja_lines(graph):
            match = re.match(rb"^build[ \t]+([^:]+):[ \t]+([^ \t]+)[ \t]+(.*)$", line)
            if not match:
                continue
            inputs = []
            for token in match[3].split():
                if token in (b"|", b"||", b"|@"):
                    break
                inputs.append(token)
            outputs = match[1].split()
            if explicit in inputs:
                if expected and expected.encode("ascii") not in outputs:
                    continue
                if not expected and not any(item.startswith(b"obj/") for item in outputs):
                    continue
                matches.append((graph, outputs, match[2], inputs, complete))
    require(len(matches) == 1, "Expected one object edge for " + source + "; found " + str(len(matches)))
    graph, outputs, rule, inputs, complete = matches[0]
    require(complete and rule == b"cxx" and inputs == [explicit] and len(outputs) == 1,
            "Unexpected native edge shape for " + source + " in " + str(graph))
    target = outputs[0].decode("ascii")
    if expected:
        require(target == expected, "Logged RFH object target changed: " + target)
    return target


def has_exact_output(output, target):
    wanted = target.encode("ascii")
    count = 0
    for graph in output.rglob("*.ninja"):
        for line, complete in ninja_lines(graph):
            match = re.match(rb"^build[ \t]+([^:]+):", line)
            if match and complete and wanted in match[1].split():
                count += 1
    return count


def output_state(output):
    names = {"args.gn", "build.ninja", ".ninja_log", ".siso_deps"}
    names.update(str(path.relative_to(output)) for path in output.rglob("*.ninja"))
    names.update(name for name in [".ninja_deps", ".siso_log"] if (output / name).is_file())
    return {name: file_sha(output / name) for name in sorted(names)}


def validate(workspace, control, archive, prior_evidence, current, expected_hashes):
    require(workspace.name == "versanium-next-test-39951209951", "Not the saved Run9 workspace")
    require(workspace.absolute() == workspace.resolve(), "Symlinked workspace refused")
    source = workspace / "chromium/src"
    output = source / "out/Default"
    require(source.resolve() == source and output.resolve() == output, "Source/output alias refused")
    require(control != workspace and workspace not in control.parents, "Controller must be separate")
    require(git(workspace, "rev-parse", "HEAD") == BASE, "Saved repository HEAD changed")
    require(not git(control, "status", "--porcelain"), "Controller must be clean")
    subprocess.run(["git", "-C", str(control), "merge-base", "--is-ancestor", TARGET_CONTROLLER, "HEAD"], check=True)
    allowed = {"PROJECT_STATUS.md", "ARCHITECTURE.md", "DECISIONS.md", "RULES.md",
               "tools/versanium/prepare_diagnostic_update.py"}
    for name in git(control, "diff", "--name-only", TARGET_CONTROLLER, "HEAD").splitlines():
        require(name in allowed or name.startswith(("docs/", "tools/versanium/tests/test_diagnostic_update")),
                "Post-target build input changed: " + name)
    for name in ["tools/apply_youtube_candidates.py", "tools/youtube_pip/diagnostics.patch",
                 "tools/youtube_pip/execution_scope.patch", "tools/youtube_pip/candidate.js"]:
        require((control / name).read_bytes() == git_blob(control, TARGET_CONTROLLER, name),
                "Target build input drifted: " + name)

    original = original_manifest(archive)
    require(original["repository_commit"] == BASE and original["chromium_input"] == PIN
            and original["vanadium_input"] == VANADIUM and original["version"] == VERSION,
            "Wrong original provenance")
    prior = json.loads(prior_evidence.read_text())
    require(prior.get("applied") is True and prior.get("controller_commit") == PRIOR_CONTROLLER,
            "Wrong prior three-accessor evidence")
    require(prior.get("original_provenance") == original and prior.get("corrected_native_sha256") == CHANGED[
        "content/browser/renderer_host/render_frame_host_impl.cc"][0], "Prior correction chain mismatch")
    require(comparable_to_original(current, original), "Current provenance differs beyond source diff")

    old_recorder = workspace / "tools/versanium/write_build_provenance.py"
    require(old_recorder.read_bytes() == git_blob(control, BASE, "tools/versanium/write_build_provenance.py"),
            "Original recorder changed")
    os.environ["DEPOT_TOOLS_UPDATE"] = "0"
    os.environ["PATH"] = str(workspace / "depot_tools") + os.pathsep + os.environ["PATH"]
    require((source / "buildtools/linux64/gn").is_file(), "Preserved GN missing")
    spec = importlib.util.spec_from_file_location("run9_original_record", old_recorder)
    recorder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder)
    require(not git(workspace / "depot_tools", "status", "--porcelain", "--untracked-files=no"),
            "Tracked depot_tools changes found")
    actual = recorder.record(workspace, source)
    require(actual == current, "Current source/GN/toolchain provenance does not match saved record")
    require(file_sha(source / "third_party/llvm-build/Release+Asserts/bin/clang++")
            == current["inputs_sha256"]["clang_binary"], "clang++ differs from recorded toolchain")
    args = (output / "args.gn").read_text()
    require(re.search(r'^target_cpu\s*=\s*"arm64"', args, re.M), "Not arm64")
    require('chrome_public_manifest_package = "io.github.nvoid911.versanium.test"' in args,
            "Not isolated Versanium Test identity")
    for name in ["build.ninja", ".ninja_log", ".siso_deps"]:
        require((output / name).is_file(), "Missing saved output state: " + name)
    for name, pair in CHANGED.items():
        require(file_sha(source / name) == pair[expected_hashes], "Changed-file baseline mismatch: " + name)
    for name, digest in UNCHANGED_INTEGRATION.items():
        require(file_sha(source / name) == digest, "Unchanged integration file drifted: " + name)
    rfh = object_for_source(output, "content/browser/renderer_host/render_frame_host_impl.cc",
                            "obj/content/browser/browser/render_frame_host_impl.o")
    flags = object_for_source(output, "chrome/browser/about_flags.cc")
    require(has_exact_output(output, "chrome_java") == 1, "Expected one chrome_java target in saved graph")
    return source, output, original, current, recorder, {"rfh": rfh, "about_flags": flags, "java": "chrome_java"}


def prepare(args):
    evidence = args.evidence.parent.resolve() / args.evidence.name
    require(not evidence.exists(), "Evidence already exists; never overwrite")
    require(args.workspace not in evidence.parents, "Evidence must be outside saved workspace")
    source, output, original, current, recorder, targets = validate(
        args.workspace, args.control, args.provenance_zip, args.prior_evidence,
        json.loads(args.current_provenance.read_text()), 0)
    before = {name: file_sha(source / name) for name in CHANGED}
    after_bytes = {name: update_bytes(name, (source / name).read_bytes()) for name in CHANGED}
    for name, data in after_bytes.items():
        require(sha(data) == CHANGED[name][1], "Reviewed post-update hash mismatch: " + name)
    state = output_state(output)
    result = {"format": 1, "run_id": 39951209951, "target_controller": TARGET_CONTROLLER,
              "preparation_controller": git(args.control, "rev-parse", "HEAD"),
              "original_repository_commit": BASE, "chromium_pin": PIN, "vanadium": VANADIUM,
              "workspace": str(args.workspace), "source": str(source), "output": str(output),
              "original_provenance": original, "pre_update_provenance": current,
              "pre_update_source_sha256": before,
              "post_update_source_sha256": {name: sha(data) for name, data in after_bytes.items()},
              "unchanged_integration_sha256": UNCHANGED_INTEGRATION,
              "pre_update_output_state_sha256": state, "compile_targets": targets,
              "applied": False, "compilation": "NOT RUN"}
    if not args.apply:
        with evidence.open("x") as stream:
            json.dump(result, stream, indent=2)
        print("READ-ONLY diagnostic update preflight PASS; saved source/output unchanged")
    else:
        for process in ["Runner.Worker", "clang++", "ninja", "siso"]:
            status = subprocess.run(["pgrep", "-x", process], stdout=subprocess.DEVNULL).returncode
            require(status == 1, "Builder/runner process present, or pgrep unavailable: " + process)
        backup = evidence.with_suffix(".source-before")
        backup.mkdir()
        for name in CHANGED:
            destination = backup / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((source / name).read_bytes())
        result["source_backup"] = str(backup)
        with evidence.open("x") as stream:
            json.dump(result, stream, indent=2)
        for name, data in after_bytes.items():
            require(file_sha(source / name) == before[name], "Source changed during apply: " + name)
            (source / name).write_bytes(data)
        require(output_state(output) == state, "Generated output changed during source apply; stop")
        post = recorder.record(args.workspace, source)
        require(comparable_to_original(post, original), "Post-update provenance changed outside source diff")
        for name, pair in CHANGED.items():
            require(file_sha(source / name) == pair[1], "Post-update source mismatch: " + name)
        result["post_update_provenance"] = post
        result["applied"] = True
        evidence.write_text(json.dumps(result, indent=2) + "\n")
        print("APPLIED four reviewed diagnostic source updates; no compilation/output mutation")
    print("Targets from saved graph:", json.dumps(targets, sort_keys=True))
    print("Evidence:", evidence)


def verify_applied(args):
    recorded = json.loads(args.evidence.read_text())
    require(recorded.get("applied") is True and recorded.get("compilation") == "NOT RUN",
            "Evidence does not describe an uncompiled applied update")
    source, output, original, _, _, targets = validate(
        args.workspace, args.control, args.provenance_zip, args.prior_evidence,
        recorded["post_update_provenance"], 1)
    require(recorded["target_controller"] == TARGET_CONTROLLER
            and recorded["preparation_controller"] == git(args.control, "rev-parse", "HEAD"),
            "Applied evidence/controller mismatch")
    require(recorded["pre_update_output_state_sha256"] == output_state(output),
            "Output state changed since apply; stop before compilation")
    require(recorded["compile_targets"] == targets, "Saved build graph target changed")
    print("Applied source/provenance/GN/toolchain/output recheck PASS; no compilation or writes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--provenance-zip", type=Path, required=True)
    parser.add_argument("--prior-evidence", type=Path, required=True)
    parser.add_argument("--current-provenance", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--apply", action="store_true")
    actions.add_argument("--verify-applied", action="store_true")
    options = parser.parse_args()
    options.workspace = options.workspace.absolute()
    options.control = options.control.resolve()
    options.provenance_zip = options.provenance_zip.resolve()
    options.prior_evidence = options.prior_evidence.resolve()
    options.evidence = options.evidence.absolute()
    if options.verify_applied:
        verify_applied(options)
    else:
        require(options.current_provenance is not None, "Preflight/apply needs --current-provenance")
        options.current_provenance = options.current_provenance.resolve()
        prepare(options)
