# Post-GN escape parser correction / read-only re-audit — 2026-10-25 JST

User-host evidence: `/home/takuma/versanium/native-diagnostic-evidence-NQzDtk`.
User confirms source-only apply/verify PASS, direct GN gen exit0, both GN targets
use `//build/toolchain/android:android_clang_arm64`; compilation NOT performed.
These are user-host reports, not independently reproduced here. Preserve existing
source-applied.json, baseline evidence, GN logs/JSON/output and graph backups.

## Confirmed audit defect and correction

Old partition(b':') split the escaped colon in `$:all_rust` / `$:blink_python_tests`
/ `$:blink_tests`, producing the false repeated output `$`. This was an audit
parser failure, not source/GN compile failure. No source reapply or GN rerun is
needed to correct this parser issue.

New bytes lexer distinguishes unescaped colon/pipes from literal `$:`/`$ `/`$$`;
logical lines handle `$` newline/CRLF continuation, indentation and literal final
dollars. Explicit and implicit outputs both enter decoded-name duplicate checks.
Explicit inputs are tokenized independently of implicit/order-only/validation
groups. Include/subninja paths use the same decoding. cxx must have one explicit
source, matching actual resolved source/rule/GN toolchain. No full UTF-8 decoding,
errors-ignore, dollar-line exclusion or removal of duplicate detection.

Unresolved `$name`/`${name}`, unknown escapes, extra separators, invalid/empty
groups, inline comment/control ambiguities or unresolved paths STOP with explicit
error. Variable definitions/rule commands are not expanded or executed; only
literal graph paths/build edges are supported. If a further valid-but-unsupported
construct appears, preserve it for parser review rather than dropping its edge.

Old/new source/rule/toolchain/object identity, non-graph output/args/Ninja/Siso
state, tool/signing/source provenance and selected51 checks remain unchanged.

## Controller compatibility, not evidence editing

The source-only record still contains its original controller SHA. New audit
requires a clean controller and proves:

1. recorded SHA is a real ancestor descending from trusted830fef60…;
2. current HEAD descends from recorded SHA;
3. diff is limited to audit_native_graph.py, test_native_preparation.py,
   root PROJECT_STATUS/ARCHITECTURE/DECISIONS and docs/*.md;
4. native manifest, native product transform and prepare_native_diagnostic.py
   bytes are identical at old commit, new commit and current disk. Other product
   or JSON/manifest changes are refused by the path restriction.

The original source-only environment validator remains unchanged. The new result
stores controller_compatibility with old/new SHA, changed paths and binary-diff
SHA256, plus source_record_sha256. No rewriting of record.controller or its
provenance. A non-ancestor, unknown older controller, dirty tree, product drift
or manifest change is STOP, never an unconditional mismatch exception.

## Re-audit command (after updating ONLY separate controller)

Use the final reviewed repair SHA in the separate controller. Do not checkout,
pull, apply, touch or regenerate anything in saved Run9. Confirm existing file
paths below; if previous logs/description/APK have another preserved name, point
to the actual file without recreating or changing it.

```sh
RUN9_WORKSPACE='/home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951'
RUN9_CONTROL='/home/takuma/versanium/run9-control-093f787-3k3yO1'
RUN9_FORWARD_BASE='/home/takuma/versanium/config-a-origin-forward-evidence-lnxJen'
RUN9_FORWARD_APK="$RUN9_FORWARD_BASE/signed-test/Versanium-156.0.8078.47_Test_ConfigAOriginForward.apk"
RUN9_NATIVE_EVIDENCE='/home/takuma/versanium/native-diagnostic-evidence-NQzDtk'
RUN9_REAUDIT=$(mktemp -d "$RUN9_NATIVE_EVIDENCE/graph-reaudit-XXXXXX")
python3 "$RUN9_CONTROL/tools/versanium/audit_native_graph.py" \
  --workspace "$RUN9_WORKSPACE" --control "$RUN9_CONTROL" \
  --forward-applied "$RUN9_FORWARD_BASE/applied.json" \
  --after-apk "$RUN9_FORWARD_BASE/after-apk-provenance.json" \
  --forward-apk "$RUN9_FORWARD_APK" \
  --source-record "$RUN9_NATIVE_EVIDENCE/source-applied.json" \
  --gn-log "$RUN9_NATIVE_EVIDENCE/gn-gen.log" \
  --gn-status "$RUN9_NATIVE_EVIDENCE/gn-gen.status" \
  --gn-desc "$RUN9_NATIVE_EVIDENCE/common-target.json" \
  --gn-desc "$RUN9_NATIVE_EVIDENCE/android-target.json" \
  --toolchain '//build/toolchain/android:android_clang_arm64' \
  --evidence "$RUN9_REAUDIT/graph-audited.json"
```

Only NEW external re-audit evidence and graph copies are written. No build or GN
command is invoked. Never reuse the failed audit's output name or remove partial
evidence. Further errors mean STOP and preserve source/output/evidence.

## Verification boundary

Regression fixtures include the exact three reported escaped-colon edges,
dollars/spaces/colons/continuations, implicit .o output, decoded duplicate output,
binary non-UTF8 comments, multiple toolchains and unsupported variables. Controller
proof tests accept audit/docs-only delta and reject product/manifest/helper drift.
This is not a new successful host graph audit or a Chromium integration compile.
Compiler and PiP result remain unverified. No saved-source/GN change, build,
Actions/B/clean/reset/sync/merge/Release/tag operation occurred in this task.

Executed locally:80 tests PASS (3 new parser/controller regression tests),
actionlint, documented shell syntax and diff checks PASS. Existing product,
native manifest and source-only helper have no diff from830fef60. Repaired
real-host post-GN audit has NOT been run; do not treat fixture PASS as host PASS.
