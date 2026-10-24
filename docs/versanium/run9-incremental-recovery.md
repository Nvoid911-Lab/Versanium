# Run9: limited GURL correction and preserved156 recovery

## Facts and scope

Run9 https://github.com/Nvoid911-Lab/Versanium/actions/runs/39951209951 ran `next-test/156-zoom-transfer-pip` at **7d9102f4f0e35dec9f69425de44cd889836a88ac**, completed/failure. API step records confirm the Build failure and successful provenance upload. The user's build log reports GN generation and chrome_java success, followed by APK compilation failure at the three `candidate_url.host_piece()` calls. It reports43763 done/1 failed/21902 remaining. Those counts are NOT a time estimate or a guarantee that a particular number of tasks can be reused.

Pinned Chromium **1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775** url/gurl.h has `std::string_view host() const LIFETIME_BOUND`, no host_piece(). Exact raw header SHA256: **64379fac91a7d4949e7b0c2da12e26952f36ed98dbbd5506fc4480bf8c3f88aa**. The prior model invented host_piece(), and our source review missed it. That model pass was not a real API compile. The fix changes ONLY these three accessor calls in execution_scope.patch. HTTPS, exact youtube.com/www.youtube.com/m.youtube.com matching, live/active/outermost frame, regular non-shutdown profile and explicit native experiment-flag restrictions are unchanged. Generic JavaScript restrictions stay unchanged.

The model now uses host(), with its actual string_view return shape, and requires the real pinned header digest/declaration before running. This remains source comparison plus model compilation, NOT compilation against the real GURL header or RFH native body. The selected-source integration checker now includes the real url/gurl.h input.

## Current evidence and limits

Original provenance artifact: **12524821969**, `Versanium-build-provenance`,1668 bytes, reported archive digest **101cc6e2b6e0c18d1ca56993b16d9bd5176a02e3451b2ea065842937fdeda0b6**. API reported not expired at the initial review. This cloud could read metadata but failed to retrieve the run log and artifact payload at their result-storage destinations. Absolute host paths, patched source HEAD, GN args/toolchain hashes and archive bytes are NOT independently inspected here. The user has since confirmed the exact failed target from the original Run9 log: **obj/content/browser/browser/render_frame_host_impl.o**. The helper requires the exact downloaded archive and its API digest; a mismatch or unavailable original archive is a STOP condition, not permission to use a new self-generated baseline.

GN/chrome_java success is evidence from the user's Run9 log, not this cloud compiling them. No Java changes are part of this correction. The old cloud AndroidX CONNECT403 was not a demonstrated build-host failure; Run9's Java compilation provides more relevant host evidence. Actual SAF screen inflation/lifecycle and device media behavior are still unverified. Full native/APK success remains unverified. No stored Run9 source/output exists in this cloud for a real incremental test.

## Reviewable helper (no compiler or Actions calls)

`tools/versanium/prepare_run9.py` is a NEW156-specific, default-read-only validator. It does not reuse/modify old155 resume_ideapad or its gates. No Workflow edits are needed or provided for this manual route. Do NOT rerun Run9 or dispatch the normal fresh-build Workflow: its workspace guard/resume rejection is intentional and does not target this saved tree.

The helper requires:

- Original Run9 directory ending `versanium-next-test-39951209951`; original repository HEAD remains7d9102f. Source stays at its existing chromium/src, output stays out/Default, with no symlink/path relocation.
- Separate clean reviewed controller descended from7d9102f, with changes restricted to this correction, recovery helpers/tests and information-source documents. Existing args/build/signing/Workflow/identity/icon inputs cannot change through this route.
- Exact original provenance archive hash and one original build-provenance.json. The preserved original recorder itself must match7d9102f. It recomputes the original record (no gn gen) and requires exact equality: repository/patched Chromium commits, Chromium pin/tag ancestry, Vanadium **2ae4335402eabcc6e025f3400185fe25094d8521**, version156.0.8078.47, GN args hash/version, depot_tools commit, clang hash, DEPS, source diff, overlay/patch/payload inputs. Tracked depot_tools changes reject; actual clang++ must match the recorded clang binary hash. DEPOT_TOOLS_UPDATE=0 is set; missing preserved GN binary rejects instead of bootstrapping.
- Existing arm64 Test GN args with io.github.nvoid911.versanium.test, plus build.ninja/.ninja_log/.siso_deps. Source url/gurl.h must match the real pinned header hash.
- Native helper matches the exact original scope body. The controller patch must equal the original patch with precisely three host_piece→host substitutions. A repeated fix or any changed predicate rejects.
- Exactly one definition of the log-confirmed **obj/content/browser/browser/render_frame_host_impl.o** in the existing .ninja files, with rule exactly `cxx` and the sole explicit input exactly `../../content/browser/renderer_host/render_frame_host_impl.cc` (relative to unchanged out/Default). Other toolchain-prefixed outputs are different targets and do not create ambiguity. Missing/duplicate exact-target definitions, wrong rules/sources, and unsupported output shapes reject. The helper reads ASCII build syntax as bytes, supports Ninja `$` newline continuations, and distinguishes explicit input from implicit/order-only/validation dependencies. It never requires whole-file UTF-8 decoding, uses no `errors="ignore"`, and does not modify any .ninja file. Variable/escaped candidate paths are not normalized into a match; unreviewed candidate forms stop instead of guessing.

The original provenance did not record all Ninja/Siso state or the GN binary hash. The helper captures their CURRENT hashes for before/after preservation and future traceability; that cannot retroactively authenticate all generated graph files as original Run9 bytes. It rejects known provenance drift and requires the operator to preserve/inspect the original workspace. It does not promise cache-hit counts or ETA.

## Host steps — preparation only until separately authorized

Use the same Windows account/WSL distro and saved workspace as Run9. Check it is idle, with no Runner.Worker, compiler, ninja or siso process; the helper conservatively refuses active builder processes on apply. Process-name checks alone cannot prevent a concurrent job starting: coordinate an idle maintenance window locally. It does not stop/kill services or change runner configuration. Do not clean/reset/fetch Chromium, sync dependencies, run hooks/GN/patch.sh/build.sh, relocate the tree, delete outputs, or rerun old155 recovery.

Obtain the original provenance ZIP through Run9's artifact UI (or an authorized download client). Keep it outside the saved tree. Use a separately checked-out reviewed controller; do not pull/checkout new code inside the preserved Run9 directory. Replace the following absolute placeholders locally, with canonical existing paths:

```sh
RUN9_WORKSPACE='/absolute/saved/workspace/versanium-next-test-39951209951'
RUN9_CONTROL='/absolute/separate/reviewed-controller'
RUN9_PROVENANCE_ZIP='/absolute/download/Versanium-build-provenance.zip'
RUN9_EVIDENCE_ROOT='/absolute/new/evidence-run9'
mkdir -p "$RUN9_EVIDENCE_ROOT"
sha256sum "$RUN9_PROVENANCE_ZIP"

python3 "$RUN9_CONTROL/tools/versanium/prepare_run9.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_PROVENANCE_ZIP" \
  --evidence "$RUN9_EVIDENCE_ROOT/preflight.json"
```

Default preflight writes only the new external evidence file; it never changes the saved source/output. It checks the original provenance against current bytes. STOP on any mismatch, record the reason, and inspect; do not reset state or relax guards to pass. Repeated preflight needs a new evidence filename, never overwrites existing evidence.

### Retrying the read-only preflight after controller093f787

The user reports that controller `093f787e560a8288e83906f11c6f7bde59a010bc` stopped before applying any change: UTF-8 decoding failed at byte1319 of `android_clang_arm/obj/third_party/rust/lazy_static/v1/lib.ninja`. The saved graph also contains RFH objects for multiple toolchains. The previous parser incorrectly required UTF-8 for every file and uniqueness across all toolchains; `set(matches)` could additionally hide duplicate definitions of the same target. These were helper defects, not evidence of corrupt build outputs. The user confirms saved source/output were unchanged and compilation has not started.

Use the new reviewed controller commit recorded in PR5, updating only the separate controller checkout. Leave RUN9_WORKSPACE at its original7d9102f checkout. Do not edit, re-encode or regenerate lib.ninja or other saved graph files. With the variables above pointing to the original workspace/archive and the separate updated controller, rerun **read-only** validation using a new evidence name:

```sh
git -C "$RUN9_CONTROL" rev-parse HEAD
python3 "$RUN9_CONTROL/tools/versanium/prepare_run9.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_PROVENANCE_ZIP" \
  --evidence "$RUN9_EVIDENCE_ROOT/preflight-target-fix.json"
```

No `--apply` or compiler command is part of this retry. A successful result must name exactly `obj/content/browser/browser/render_frame_host_impl.o`. All provenance, original SHA, GN, toolchain, native-scope and preserved-output checks still apply. Actual successful host preflight with this parser remains unverified here; stop on any new mismatch rather than bypassing checks.

After the source documents/controller commit and preflight are reviewed, the following explicit apply is available; **Codex has not run it on Run9**:

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_run9.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_PROVENANCE_ZIP" \
  --evidence "$RUN9_EVIDENCE_ROOT/applied.json" --apply
```

Apply reruns validation. It saves an exact native-source backup outside the tree, records intent, then changes ONLY the three calls in the existing .cc. It hashes all existing .ninja files, args.gn and available Ninja/Siso state before/after, requiring equality. No existing output is deleted/recreated and no GN regeneration or build runs. Original JSON/provenance and original repository HEAD remain untouched. Applied evidence records original/controller commits, source/output paths, pins, exact native diff and before/after native/diff hashes, GN binary hash, object target and original provenance. If a write/concurrent-state check fails, STOP with evidence retained; do not compile or automatically roll back/reset.

## First build validation — actual failed object only, future authorization required

Immediately before a later object compile, recheck the applied correction without writing or compiling:

```sh
python3 "$RUN9_CONTROL/tools/versanium/prepare_run9.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --provenance-zip "$RUN9_PROVENANCE_ZIP" \
  --evidence "$RUN9_EVIDENCE_ROOT/applied.json" --verify-applied
```

This permits only the recorded corrected source-diff hash relative to the original provenance and rechecks all other fields, native/GN hashes and unchanged output state. Run it BEFORE object compilation; afterward normal build log/state changes intentionally prevent this precompile-state check from passing again. Stop on drift.

Only after explicit authorization to compile on that host, use the exact log-confirmed target validated against the saved graph and recorded in applied.json. Do NOT start with chrome_public_apk, chrome_java, build.sh or a normal Actions rerun. The following is a future manual command, NOT executed by this work:

```sh
if (
  set -uo pipefail
  export DEPOT_TOOLS_UPDATE=0
  export PATH="$RUN9_WORKSPACE/depot_tools:$PATH"
  cd "$RUN9_WORKSPACE/chromium/src" || exit 1
  RUN9_OBJECT=$(python3 - "$RUN9_EVIDENCE_ROOT/applied.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
assert p['applied'] and p['object_compile']=='NOT RUN'
print(p['object_target'])
PY
  ) || exit 1
  test ! -e "$RUN9_EVIDENCE_ROOT/object-compile.log" || exit 1
  autoninja -C out/Default -j 1 "$RUN9_OBJECT" 2>&1 | tee "$RUN9_EVIDENCE_ROOT/object-compile.log"
); then RUN9_OBJECT_STATUS=0; else RUN9_OBJECT_STATUS=$?; fi
( set -C; printf '%s\n' "$RUN9_OBJECT_STATUS" > "$RUN9_EVIDENCE_ROOT/object-compile.exit-code" )
test "$RUN9_OBJECT_STATUS" -eq 0
```

This targets the real failed translation unit with its actual generated headers, includes/defines, Android toolchain and retained GN graph. The graph may schedule prerequisites; the requested target is one object, not an assurance of exactly one compiler invocation. On any failure, STOP and retain logs/state; do not continue to APK or reapply patches. Success establishes compilation of that object/configuration only, not full native linkage, security or device behavior.

Record a fresh non-overwriting provenance file after the object attempt using the ORIGINAL recorder, with the existing source and frozen depot_tools PATH:

```sh
(
  set -eu
  export DEPOT_TOOLS_UPDATE=0
  export PATH="$RUN9_WORKSPACE/depot_tools:$PATH"
  cd "$RUN9_WORKSPACE/chromium/src"
  test ! -e "$RUN9_EVIDENCE_ROOT/after-object-provenance.json"
  python3 "$RUN9_WORKSPACE/tools/versanium/write_build_provenance.py" \
    --repository "$RUN9_WORKSPACE" --source "$PWD" \
    --output "$RUN9_EVIDENCE_ROOT/after-object-provenance.json"
)
sha256sum "$RUN9_EVIDENCE_ROOT/object-compile.log" \
  "$RUN9_EVIDENCE_ROOT/object-compile.exit-code" \
  "$RUN9_EVIDENCE_ROOT/applied.json" \
  "$RUN9_EVIDENCE_ROOT/after-object-provenance.json"
```

The original recorder deliberately still reports repository7d9102f; applied.json links the new correction-controller SHA and corrected source diff/native hash. Keep BOTH, the original archive, source backup and object result/exit status. Never present a new record alone as if it were Run9's original provenance. A later reviewed manual `autoninja -C out/Default -j 6 chrome_public_apk` can incrementally resume from that SAME directory only after object success and separate build authorization. Ninja/Siso determines reuse/invalidation; source/output retention guarantees neither cache reuse nor build completion. This preparation does not add signing/packaging or upload/Release operations; any later signed Test delivery must use a separately reviewed existing signing path, with no new keys/Secrets.

## Validation performed here

- Fixed raw GURL header SHA256/declaration: source-checked; no real-header/native compilation.
- Selected exact156/Vanadium/zoom/F11/PiP source patch application and generic JavaScript restrictions retained: PASS. Intentional changed-anchor rejection emits an expected patch error.
- Scope predicate17 MODEL cases: PASS using corrected API shape; not Chromium API compilation.
- Initial recovery10 tests passed but did not cover real graph encoding/multiple-toolchain conditions; they did not establish successful host preflight.
- After the parser correction: recovery18 tests PASS, including invalid UTF-8 at byte1319 in the reported unrelated path, multiple toolchains, exact-target absence/duplicates, wrong rule/source/output, implicit-only deceptive source, LF/CRLF continuations, literal/comment dollars and incomplete continuations. A temporary-fixture dry-run/apply/recheck now uses the real graph parser and verifies graph/output bytes stay unchanged; host provenance validation remains mocked. These are NOT an execution on the saved build host.
- Current migration13 + old recovery8 + recovery18 =39 tests, actionlint, shell/YAML/documented-command syntax and git diff checks: PASS. No actual object/full build or Actions run occurred here.

PR5 contains this correction and preparation; PR6 stays separate. Source information files PROJECT_STATUS/ARCHITECTURE/DECISIONS and the next-Test report are updated BEFORE any future host restart. Notion/Project Sources are unavailable here and are not claimed updated. main/migration branches, signature/Secrets/Test identity/runner choices are unchanged.
