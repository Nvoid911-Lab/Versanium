# Native → content-origin host preparation (2026-10-25 JST)

Product pin: `415f6df9bb70d1e3c062c398c05ebebc997772ee`. This independent
helper does not import/modify historical apply helpers or manifests. It prepares
first content ingress and persistent-false diagnostics, NOT a PiP fix. B/video
fullscreen zoom remains excluded. No host operation or build was performed here.

## Confirmed baseline and evidence linkage

Use built/signed **AOriginForwardNative**, never Forward/A/installed60b.
User confirmed signing record, actual host APK and previous certificate match,
installation and restart; this is NOT extraction/verification of the device APK.

- signed Native APK SHA256: `fba3cbd639abdb0c00d9e7c1d4621e61580efde1fb9126ce8545437261923bc7`
- certificate: `2e79f4e6597f7ea320b32c4889405c8d93081774a0fd8db4a040def0d54ad120`
- source-applied SHA256: `5934cc6dd0074b66d95cd6ae8f94236de7977e453b93a5db910cdcfe23c920d4`
- after-apk-provenance SHA256: `7331a3d310403149b05d705ffa5f07b699db4138969936a602e597b3699a03b3`

`source-applied.json` is in native-diagnostic-evidence-NQzDtk. Graph, APK
provenance and signed record are in its graph-reaudit-ZFshuZ directory. The
signature record has NO graph reference. The helper derives a new evidence link:
sign record→actual source/provenance hashes; graph→same source hash/provenance;
current loaded graph→historically audited graph hashes; actual signed/unsigned
APK→recorded hashes. This is a read-only consistency proof, not a retroactive
cryptographic compiler attestation. Old records are never edited or re-signed.

Recorded source controller→graph audit controller ancestry and exact historical
audit-only delta are checked against stored proof. Product415 and new preparation
are checked as separate descendant stages; only enumerated product/preparation
paths and documentation are accepted. Native product/manifest/helper and content
product/selection bytes are invariant. Old controller fields are never rewritten.

## First operation: read-only, separate controller only

Replace CONTROLLER_SHA with the final reviewed preparation commit in PR5.
This checkout is ONLY in the separate controller; never checkout/reset saved Run9.

```sh
(
  set -eu
  CONTENT_CONTROL=/home/takuma/versanium/run9-control-093f787-3k3yO1
  test -z "$(git -C "$CONTENT_CONTROL" status --porcelain)"
  git -C "$CONTENT_CONTROL" fetch --no-tags https://github.com/Nvoid911-Lab/Versanium.git next-test/156-zoom-transfer-pip
  git -C "$CONTENT_CONTROL" checkout --detach CONTROLLER_SHA
  CONTENT_EVIDENCE=$(mktemp -d /home/takuma/versanium/content-origin-evidence-XXXXXX)
  printf 'Evidence: %s\n' "$CONTENT_EVIDENCE"
  PYTHONDONTWRITEBYTECODE=1 python3 "$CONTENT_CONTROL/tools/versanium/prepare_content_diagnostic.py" \
    --workspace /home/takuma/versanium/actions-runner/_work/Versanium/Versanium/versanium-next-test-39951209951 \
    --control "$CONTENT_CONTROL" \
    --native-source-record /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/source-applied.json \
    --build-evidence /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/graph-reaudit-ZFshuZ \
    --signed-apk /home/takuma/versanium/native-diagnostic-evidence-NQzDtk/signed-test/Versanium-156.0.8078.47_Test_ConfigAOriginForwardNative.apk \
    --evidence "$CONTENT_EVIDENCE/read-only.json"
)
```

This hashes the COMPLETE saved output tree (potentially substantial disk I/O,
no dependency downloads). Keep builders/runner idle throughout. It checks58 inputs
(Native51 plus7), exactly10 changes, no B. Ten before/after files are reproduced
from fixed Chromium HEAD and selected historical patches/transforms in temporary
space, including the reviewed common patch.sh WebContents sed; patch.sh itself
is never executed. The58-input selection is unchanged from product415.

Tracked nonselection source diff, untracked-name census, tool binaries, saved
args and signing/identity sources are checked. This is not a byte census of all
ignored/untracked source files; do not externally edit those. All generated output
files are inventoried including Ninja/Siso logs/deps. No saved source/output writes.
Unknown/indirect graph syntax, missing action, ambiguous target, nonliteral path,
wrong baseline, output/source drift, unsupported depfile: STOP for review.

## Future source-only apply (NOT authorized in this task)

Repeat identical arguments with NEW external `--evidence .../applied.json --apply`.
After reviewing read-only evidence, do not reuse read-only.json as apply record.
Before10 writes: copy original files, four historical evidence files, Native
unsigned APK and all loaded graph/state files externally; record intent, original
provenance and full output inventory. Native signed APK remains untouched.
After:58 after hashes, only intended source provenance delta, other sources,
args/toolchain/signing and entire generated output inventory must match.
Then repeat same arguments with `--evidence .../applied.json --verify` **before
any GN/compile**. Duplicate apply, mismatch or partial failure stops, retains
false/partial intent and backups, never automatic rollback/reset. Do not manually
resume partial writes. Existing old helper conditions are unchanged.

## GN decision: real graph first, separate stage

No BUILD.gn product difference is insufficient evidence. Read-only inspects actual
content JNI Java input/header output/generator script, native dependency closure,
content_full_java/chrome_java compile actions and JNI closure. Actual default
cxx object definitions must uniquely match source/rule/default arm64 scope; other
toolchains do not substitute. Targets are recorded from actual graph, never guessed.
GN memberships and toolchain hashes are cross-checked. Generator edges AND their
actual depfiles determine whether changed files participate in GN regeneration.
Absent/unsupported depfile gives REVIEW_REQUIRED, not implicit permission.
NO_REGEN_INDICATED requires literal complete evidence; SEPARATE_GN_UPDATE_REQUIRED
means a separately authorized graph step. No implicit Ninja regeneration allowed.

If separately approved, source-only verify first, retain pre-GN graph backups;
use unchanged saved args/depot/toolchain, from the same chromium/src:

```sh
# FUTURE ONLY, after explicit authorization; use new external log/status paths.
export DEPOT_TOOLS_UPDATE=0
export PATH="$CONTENT_WORKSPACE/chromium/src/buildtools/linux64:$CONTENT_WORKSPACE/depot_tools:$PATH"
(
  cd "$CONTENT_WORKSPACE/chromium/src" || exit 1
  if (set -o noclobber; ./buildtools/linux64/gn gen out/Default > "$CONTENT_EVIDENCE/gn.log" 2>&1); then
    printf '0\n' > "$CONTENT_EVIDENCE/gn.status"
  else
    CONTENT_GN_STATUS=$?
    printf '%s\n' "$CONTENT_GN_STATUS" > "$CONTENT_EVIDENCE/gn.status"
    exit "$CONTENT_GN_STATUS"
  fi
)
```

Then same helper/base args with NEW `--evidence .../after-gn.json
--audit-after-gn --application-record .../applied.json --gn-log .../gn.log
--gn-status .../gn.status`. This never runs GN. It requires a fresh generated
graph timestamp, status0, actual source58/provenance and all object/JNI/Java action
recipes/dependencies unchanged. Only graph/depfile/stamp output changes accepted;
args, objects, jars, APK, Ninja/Siso history changes STOP. Retain new graph copies.
Unexpected legitimate graph changes still require review, not blanket acceptance.

## Subsequent compile/sign gates (not run)

|Order|Actual target selection / requirement|
|---|---|
|1|Content JNI action from graph_plan.jni.target; verify generated observer proxy signature against native use. A file left on disk is insufficient.|
|2|Actual graph_plan.java targets for content_full_java (observer/proxy) then chrome_java (controller), real Java integration.|
|3|Actual ErrorProne/NullAway action targets with --enable-nullaway, dependency/validation closure verified; execute and retain results separately.|
|4|Four graph_plan.objects: RFH, WebContentsImpl, MediaWebContentsObserver, Android observer proxy. Source/cxx/default arm64 toolchain must match before execution.|
|5|Actual saved graph chrome_public_apk alias and dependency closure, full APK integration including public observer/header users. No rebuild/time guarantee.|
|6|Check Test manifest/version156.0.8078.47/arm64, sign by existing approved key/flow; new APK below, compare certificate above. No key/Secrets logged.|

Use saved autoninja/depot with DEPOT_TOOLS_UPDATE=0, same out/Default; use recorded
actual targets, do not paste speculative object names. Record each command/status,
updated provenance and output inventory. Stop on implicit GN rerun, source/args/
tool/config drift or failure. Precompile --verify cannot be used as postcompile
proof because output changes are expected then. No build.sh, patch.sh, sync/clean.

**NullAway blocker:** repository args.gn sets use_errorprone_java_compiler=false.
Read the actual saved argument and action graph; ordinary Java success is NOT
NullAway success. Helper records actual flag/action evidence. Missing/disabled
NullAway remains an unresolved gate; do not change saved args behind the user.
A separately reviewed verification configuration is needed if absent.

New external signed name:
`Versanium-156.0.8078.47_Test_ConfigNativeContentOrigin.apk`.
Preserve Native and all older signed/unsigned distributions. Signed record must
link new source, graph, after-apk hashes explicitly; do not modify old records.
No release/upload, main/migration merge, tag, Actions or B follows.

## Validation boundary

New7 tests cover fixed reconstruction, exact record links/config/APK mismatch,
read/apply/verify/partial transaction fixtures, controller-history proof, bytes
Ninja escaping/scopes/duplicates/JNI dependencies, GN depfile decision and
separate post-GN rejection. Fixtures are NOT real-host evidence. Real Native58,
actual Ninja/JNI/action discovery, GN decision, Java/NullAway/C++/APK integration
and new APK device trial remain unverified until user executes reviewed stages.

Local result:93 unittest tests PASS (7 new); actionlint PASS; documented shell
syntax PASS; git diff --check PASS. No actual host evidence files, graph or APK
were accessible in this environment. These results do not verify actual host
preflight, JNI generation, Java/NullAway/native compilation, signing or device behavior.

## JNI path correction after host read-only stop (2026-10-25)

Controller630a64b stopped at JNI action discovery in user evidence
`/home/takuma/versanium/content-origin-evidence-oj2Q3e`; no apply/GN/compile.
The expected path omitted `jni_headers/`. Fixed Chromium1d17's
`third_party/jni_zero/jni_zero.gni` lines35–40 sets Android
`jni_headers_dir = "$root_build_dir/gen/jni_headers"`; lines476–477 combines
that with target_gen_dir relative to root_gen_dir and the target name.
Thus the exact output is:
`gen/jni_headers/content/public/android/content_jni_headers/WebContentsObserverProxy_jni.h`.
This agrees with the user's actual graph report: direct proxy Java input and
jni_zero.py recipe, rule
`__content_public_android_content_jni_headers__action___build_toolchain_android_android_clang_arm64__rule`
in `toolchain.ninja`. The helper now checks all these together, unique candidate,
recorded default arm64 and native/Java dependency closure. Basename-only matching
is never used. Another toolchain can share Android's root JNI directory, so the
exact action/toolchain identity is essential, in addition to output path.

Reviewed remaining path assumptions: cpp outputs are discovered by actual source,
cxx rule and default obj scope; Java outputs by actual compiler/source/family;
GN membership uses source-relative paths. No other hardcoded generated JNI path
was found in the dedicated helper. C++ include paths without gen/jni_headers are
include-relative and must not be rewritten as filesystem paths. Existing product,
selection and old helpers/manifests remain unchanged.

Regression fixture now uses actual output layout/action and toolchain.ninja;
rejects old layout, other toolchain/action, Java-input mismatch, wrong generator,
ambiguous candidates, duplicate decoded outputs, missing native/Java dependency
closure. These are fixture proofs, not an actual-host graph replay. All93 local
tests PASS; Java/NullAway stages were NOT reached by the real host preflight.

Restart from a new external content-origin-evidence-XXXXXX using the first
command above with the NEW controller SHA from PR5. Do not reuse or overwrite
oj2Q3e. Existing source/signature/graph records are read-only and unchanged.

## Java action membership correction after NDSMal (2026-10-25)

Host b85fc37 passed JNI discovery and stopped at Java action discovery in
`/home/takuma/versanium/content-origin-evidence-NDSMal`. No apply/GN/compile.
Host reports exact rule
`__content_public_android_content_full_java__compile_java___build_toolchain_android_android_clang_arm64__rule`
in toolchain.ninja, direct Proxy.java input, compile_java.py recipe and outputs
obj/content/public/android/content_full_java.javac.jar, its .info and
content_full_java.compliment.jar. Compiler action errorprone.py and
--enable-nullaway are false. That alone says NOTHING about separate analysis
actions. Java/NullAway graph inspection did not complete; neither was executed.

Fixed Chromium1d17 build/config/android/internal_rules.gni was retrieved and
matched against the previously inspected fixed template:
- compile_java (2968 onwards) selects compile_java.py, turbine.py or errorprone.py;
  normal compiler outputs output_jar_path and .info; filtered classes optionally
  add exact family.compliment.jar. ErrorProne outputs target_out_dir/target.stamp.
- android_library (3624,4142–4170) uses family.javac.jar and helper names
  family__compile_java / family__errorprone, with compile validation dependency.
- 4198–4255: sharded analysis uses family__errorprone_shardN, each own .sources,
  direct subset inputs and stamp, with an aggregate validation group.
- 3169 onwards: the separate ErrorProne recipe supplies --enable-nullaway;
  its presence in a graph is still not successful analysis execution.

The new scanner uses exact GN label-derived default-arm64 rules, never a Ninja
file stem. Both content_full_java observer/proxy and chrome_java controller must
have exactly one production compile action, direct source membership, exact
family/path outputs and compile_java recipe (not turbine/ErrorProne), and actual
JNI dependency closure. Only the primary .javac.jar is selected as compile target;
all outputs including .info/optional compliment are recorded, not independently
invented targets. Other toolchain/test/similar labels cannot substitute. Storage
in toolchain.ninja or another loaded file does not change Java membership.

Analysis is scanned independently across all loaded graph files by exact family
and default toolchain. Unsharded/sharded rule and stamp, errorprone recipe and
validation closure must match. Duplicate source membership or mixed shard modes
stop; a detected family with unproven direct target-source membership stops.
Compiler_nullaway_flag_observed is distinct from each analysis action's
nullaway_flag_observed. No matching actions means no proven exact-family action,
not a conclusion drawn from a compile action flag. The NullAway gate remains
NOT_PROVEN unless all target sources have the requisite separate action, and
then still requires actual execution. Unsupported indirect inputs require review.

Other naming assumptions reviewed together: JNI full output/action is now based
on fixed template and observed rule; native object paths remain discovered from
actual source/cxx/default obj scope; no concrete object name is guessed. Recorded
Native graph/default toolchain and fixed GN source membership remain checked.
Exact GN generator edge/depfile checks may still stop on unsupported syntax;
that is not a passed GN decision. No additional file-stem family assumptions
remain in the dedicated graph scanner. Real host chrome action/analysis/shards
and later GN checks remain unverified until a fresh read-only run succeeds.

Fixture now stores content and chrome compiler actions in toolchain.ninja using
real rule/output layout. Tests cover both families, all three Java inputs, other
toolchain/test/similar labels, extra distractors, wrong outputs/recipe, ambiguous
production actions, missing JNI dependencies, separate unsharded/sharded analysis,
NullAway flag present/absent, missing validation and source membership. Renaming
the fixture's Java storage file does not alter membership. These are NOT actual
host graph replay or Java/NullAway compilation. New evidence must retain NDSMal.

Local validation after Java correction:95 tests PASS (two additional test methods,
expanded shared actual-layout fixture), actionlint PASS, documented shell syntax
PASS and git diff --check PASS. All host/compilation limitations above remain.


## Completed host read-only and isolated analysis follow-up

User reports controller7b60873 completed TQNw0X/read-only.json: READ_ONLY_COMPLETE,
NO_REGEN_INDICATED_BY_GRAPH_AND_DEPFILE, saved ErrorProne=false, separate analysis
records0, NullAway NOT_PROVEN_REQUIRES_SEPARATE_REVIEW_ARGS_UNCHANGED. No apply/GN/
compile. This is the latest host result; previous discovery stops are historical.
The records were not locally reread here.

See [isolated NullAway plan](nullaway-isolated-output-plan.md) for fixed156
configuration, source coverage, separate output/args, real graph/shard/processor
checks, capacity/stop conditions and source-apply→analysis→product build order.
Existing helper gate and Default args/output remain unchanged. Creating a graph
or finding flags alone does not satisfy the gate; separate actual execution
evidence must match the final candidate. No output generation or build performed.
