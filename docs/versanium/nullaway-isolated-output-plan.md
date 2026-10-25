# Fixed156 isolated NullAway verification plan — preparation only

Product:415f6df; preparation baseline:7b608732d56f3885d5c950715d10709405695e70.
NO commands below that generate args/graphs or compile were executed in this task.
They require separate user authorization. This is not permission to apply/build.
The existing prepare_content_diagnostic.py gate is UNCHANGED, not bypassed.

## Actual host result (user report, not locally reread)

`/home/takuma/versanium/content-origin-evidence-TQNw0X/read-only.json`:
READ_ONLY_COMPLETE; GN decision NO_REGEN_INDICATED_BY_GRAPH_AND_DEPFILE;
saved_errorprone_assignment=false; NullAway gate
NOT_PROVEN_REQUIRES_SEPARATE_REVIEW_ARGS_UNCHANGED. content_full_java/chrome_java
normal compiler actions have no NullAway flag; separate analysis records:0.
No source apply/GN/compile. This completes the previously failing graph discovery,
NOT NullAway verification. Old evidence remains immutable. Analysis availability
is established independently of compiler flag absence in this completed scan.

## Fixed-source basis / proposed configuration

Reviewed at Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775:

- build/config/android/config.gni: android_static_analysis="on" waits for static
  analysis; "build_server" does not block for results. Official builds normally
  resolve "default" to "off". use_errorprone_java_compiler defaults from that
  setting, but saved args explicitly override it to false.
- build/config/android/internal_rules.gni:3960–3970 selects Chromium Java targets
  with sources, filters generated root_gen_dir Java from ErrorProne; invoker
  enable_errorprone may override defaults. 4142–4255 creates exact family analysis
  targets/shards, compile validations, intra-target turbine headers, and excludes
  generated srcjars from direct ErrorProne analysis. 3067 records actual sources
  and .sources as inputs. 3170 adds nullaway.jar and --enable-nullaway.
- build/android/gyp/errorprone.py: uses actual javac+ErrorProne+NullAway, not a
  jar inspection. OnlyNullMarked/JSpecifyMode, restrictive annotations, generated
  warning exclusions and existing suppressions limit coverage. It converts errors
  to warnings; treat_warnings_as_errors=true is needed for fail-on-warning.
  ERRORPRONE_CHECKS_TO_APPLY is empty at this pin: no in-place source fixes.
  It stops after FLOW (no normal code generation); stamp is not a production jar.
- server_utils.py: MaybeRunCommand only queues work when use_build_server is true;
  the proposed "on" mode must NOT emit --use-build-server in any selected action.

New verification-only out directory under SAME pinned chromium/src, e.g.
`out/NullAwayContent-415f6df-<unique>`. Never reuse/copy/symlink Default's graph,
jars, generated headers, .siso_deps, .ninja_log or other outputs. Dependencies must
be regenerated/resolved for this configuration; an unchanged compiler cache may
be used by the existing tools but is not a coverage proof. No download/sync/hooks.

Exactly three permitted argument replacements/additions in the NEW args:

|Argument|Verification value|Reason|
|---|---|---|
|use_errorprone_java_compiler|true|Generate analysis actions despite saved false|
|android_static_analysis|"on"|Synchronous results, no deferred build-server completion|
|treat_warnings_as_errors|true|Do not accept successful exit with analysis warnings|

All other saved arguments remain unchanged, including identity, arm64, official/
component, optimization, Java/toolchain, signing, Siso/remote options. The saved
Default/args.gn is never written. android_static_analysis="on" can introduce
extra lint/validation dependencies; it is not a promise of only two cheap actions.
Do not remove those dependencies or weaken checks to make the graph smaller.
Explicit target enable_errorprone=false may still prevent coverage: STOP on absent
expected actions. No feature flag or product source modification is proposed.

### Pinned processor dependencies (no packages downloaded)

Fixed156 DEPS lists these immutable CIPD instances (not Maven versions):

|Package under chromium/third_party/android_build_tools/|Instance ID|
|---|---|
|error_prone|TP-iwhtizFRV0x62m6MtiWtm4Wh9cYsTCOTYQM0zIiYC|
|error_prone_javac|7EcHxlEXEaLRWEyHIAxf0ouPjkmN1Od6jkutuo0sfBIC|
|nullaway|ds9Vm6LkQNc9O9nuG0_FbrsNQ5VoGPpFIWKur53l3wUC|

Their DEPS condition is checkout_android and non_git_source. Check actual saved
CIPD installation records and jar hashes; a DEPS pin alone does not prove jars
are present/correct. Do not run cipd ensure/gclient sync if absent. Chromium's
plugin is built from tools/android/errorprone_plugin at this source pin, not an
unrelated downloaded plugin. Exact resulting plugin/classpath hashes belong in
the future execution receipt. No installed jar hash is known from this task.

## Execution order / boundaries

1. **Now:** preparation/review only; retain TQNw0X. No new output or args yet.
2. **After separate authorization:** rerun the current Native baseline read-only;
   source-only content apply + --verify through the existing reviewed helper in
   new external evidence. This is required BEFORE candidate NullAway validation:
   current unapplied Native sources would validate Native, not the new diagnostic.
   Source58-after/changed10 and updated provenance are the common candidate basis.
   Product Default output remains byte/mode/mtime unchanged during source apply.
3. Snapshot candidate sources, tools, processor scripts and Default output state;
   create a fresh verification output/args and generate only its GN graph.
4. Audit real GN/Ninja/response files/dependencies; assess capacity and planned
   target closure. Stop for review BEFORE compilation if unexpected/large/unknown.
5. If separately authorized, run only the two families' complete ErrorProne
   groups/all shards with dependencies; preserve logs/status/new-output inventory.
   No chrome_public_apk target, packaging, signing or distribution from this out.
6. Record separate NullAway verification receipt. Recheck candidate58/provenance,
   all analyzed source hashes and old Default/tool hashes unchanged. An actual
   successful matched receipt can satisfy the *separate review* gate; it does not
   change the saved graph's factual NOT_PROVEN status or rewrite old JSON.
7. Only later, after reviewing that receipt: real contentJNI, content/chrome Java,
   actual native objects and APK integration in **Default**, existing key signing
   to the separately named Test APK. Preserve Default args=false. Ordinary Java
   and separate NullAway results must be reported individually. If candidate
   inputs change, invalidate receipt and review rerun scope. No timing guarantee.

## Future prechecks and args/graph generation (DO NOT RUN NOW)

Record df -h/df -i, free -h, du -sh Default and any existing verification dirs,
process/runner idle status on the HOST. This cloud environment cannot determine
host free space, memory or elapsed time. Source checkout/depot/tools must match
recorded pins and binaries. Check required JDK/Android jars, nullaway.jar,
ErrorProne compiler/plugin, Python/build tools and CIPD artifacts locally; retain
hashes. Missing/403 dependency stops; no automatic large fetch, resync or rebuild.

Below variables must refer to reviewed external evidence and a clean controller;
CONTENT_SOURCE must be the existing saved chromium/src, never a moved tree.
First take full Default snapshot (the existing helper's state function can read
it) and candidate hash/provenance records into external evidence. Compare them
again after every phase, not only at the end. Budget includes these read-only
full-output hash passes. Do not log raw args/API keys or environment contents.

Future args creation example, AFTER source-only verification and authorization:

```sh
# FUTURE ONLY. Set CONTENT_SOURCE and CONTENT_EVIDENCE explicitly first.
# Evidence is external to saved workspace; directory must be NEW.
export CONTENT_SOURCE CONTENT_EVIDENCE
python3 - <<'PY'
import hashlib,json,os,re
from pathlib import Path
s=Path(os.environ['CONTENT_SOURCE']).resolve()
e=Path(os.environ['CONTENT_EVIDENCE']).resolve()
assert not e.is_relative_to(s) and e.is_dir()
old=s/'out/Default/args.gn';raw=old.read_bytes();text=raw.decode('utf-8')
# Fail closed on conditional/imported/complex settings, never append overrides blindly.
assert not re.search(r'^\s*(import\s*\(|if\s*\(|declare_args\s*\(|[{}])',text,re.M)
values={'use_errorprone_java_compiler':'true','android_static_analysis':'"on"','treat_warnings_as_errors':'true'}
for key,value in values.items():
    pattern=r'(?m)^([ \t]*)'+key+r'[ \t]*=[ \t]*(true|false|"[^"\n]*")[ \t]*(#[^\n]*)?$'
    n=len(re.findall(pattern,text));assert n<=1,(key,'duplicate')
    assignments=re.findall(r'(?m)^\s*'+key+r'\s*=',text);assert len(assignments)==n,(key,'unsupported expression')
    if n:text=re.sub(pattern,lambda m:m[1]+key+' = '+value+(' '+m[3] if m[3] else ''),text)
    else:text+=('' if text.endswith('\n') else '\n')+key+' = '+value+'\n'
out=Path(__import__('tempfile').mkdtemp(prefix='NullAwayContent-415f6df-',dir=s/'out'))
(out/'args.gn').write_bytes(text.encode('utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
record={'purpose':'NULLAWAY_ONLY_NO_APK_NO_SIGNING','source':str(s),'output':str(out),'saved_args_sha256':sha(raw),'verification_args_sha256':sha((out/'args.gn').read_bytes()),'overrides':values}
with (e/'verification-config.json').open('x') as f:json.dump(record,f,indent=2)
assert old.read_bytes()==raw
print('Verification output:',out)
PY
```

Review the exact args delta privately: only the above three settings permitted;
no package/signing values need to be shared. Record original/candidate args
hashes and source/provenance/tool hashes. Example is future setup, not evidence
that args or GN were generated in this task.

Then set CONTENT_VERIFY_OUT to the printed absolute path, retain exact value,
reject any alias/symlink and assert it is distinct from Default. Use saved GN2578
and frozen depot, exact same source. Capture exit status without tee masking:

```sh
# FUTURE ONLY, separate authorization required.
export DEPOT_TOOLS_UPDATE=0
export PATH="$CONTENT_SOURCE/buildtools/linux64:$CONTENT_SOURCE/../../depot_tools:$PATH"
(
  cd "$CONTENT_SOURCE" || exit 1
  if (set -o noclobber; ./buildtools/linux64/gn gen "$CONTENT_VERIFY_OUT" > "$CONTENT_EVIDENCE/nullaway-gn.log" 2>&1); then
    printf '0\n' > "$CONTENT_EVIDENCE/nullaway-gn.status"
  else
    CONTENT_GN_STATUS=$?
    printf '%s\n' "$CONTENT_GN_STATUS" > "$CONTENT_EVIDENCE/nullaway-gn.status"
    exit "$CONTENT_GN_STATUS"
  fi
)
```

No GN command targets Default. Do not run build.sh or source-mutating patch/hook
scripts. GN output may include many targets; generating a graph is not compiling
all of them. Verify source and Default state unchanged immediately after GN.

## Required graph audit before analysis execution

GN read-only queries from the saved source, with NEW output only:

```sh
# FUTURE ONLY, after verification GN generation.
./buildtools/linux64/gn ls "$CONTENT_VERIFY_OUT" '//content/public/android:content_full_java__errorprone*'
./buildtools/linux64/gn ls "$CONTENT_VERIFY_OUT" '//chrome/android:chrome_java__errorprone*'
# Use each ACTUAL returned label, including the aggregate group/shards.
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" --format=json
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" deps --all
./buildtools/linux64/gn desc "$CONTENT_VERIFY_OUT" "$CONTENT_ANALYSIS_LABEL" outputs
```

Retain JSON/text externally, verify default toolchain android_clang_arm64. Use
existing literal graph scanner on the NEW output only as an additional audit;
never call the Native transaction helper with this output or substitute its
records for Native provenance. The scanner proves membership for the three
changed Java sources, NOT complete family source coverage by itself.

For **each** family content_full_java and chrome_java:

- Resolve exact __compile_java and __errorprone[_shardN] rule, action input/script,
  stamp outputs, dependencies/validations and actual `.sources` response file.
  Record complete compiler/analysis command metadata (private), source/processor/
  script hashes, all input/output paths. No basename or guessed object matching.
- Verify real errorprone.py command contains --enable-nullaway, processorpath
  nullaway.jar and Chromium ErrorProne plugin; referenced @FileArg build configs
  must resolve to actual existing/generated dependency jars from THIS output.
  Validate no --use-build-server, NullAway:OFF, checker downgrades or in-place
  patch flags; verify saved errorprone.py has empty CHECKS_TO_APPLY and expected
  OnlyNullMarked/JSpecifyMode. Effective treat_warnings_as_errors must be true
  and action --warnings-as-errors observed. Absence is STOP, not a warning waiver.
- Read generated .sources as lists without executing them. Resolve every entry
  relative to NEW output, record hashes. For a family, the disjoint union of all
  actual ErrorProne shard source lists must equal the compile family's real Java
  sources minus generated root_gen_dir Java (and Kotlin). Cross-check each list
  against direct action inputs. No duplicate/missing source, especially Proxy,
  WebContentsObserver and PIP controller; no stale Native source hashes. Mixed
  sharded/unsharded or unsupported indirect response syntax: STOP for review.
- The three edited classes are @NullMarked in the reviewed fixed source; recheck
  candidate bytes, nested @NullUnmarked / existing suppressions and checker flags.
  NullAway invocation does not mean every method/type is checked: package/class
  null-marking, generated exclusions and suppressions remain explicit limits.
- JNI/srcjar/header/turbine classpath producers, JDK/Android SDK/annotations,
  NullAway/plugin jars/build configs must have dependency closure. Generated Java
  is resolved through header jars (and normal producer generation), not directly
  checked by NullAway here. No copying existing Default jars as a shortcut.

All family analysis shards, not just the shard containing an edited file, are
recommended to preserve target-wide context. Actual labels/output stamps may be
selected only after the above audit. The analysis group may be a phony aggregate;
use actual queried output alias/stamp(s). Do not invent a Ninja object/alias.

## Future analysis execution and acceptance

First query the saved build frontend's help and dry-run only actual graph-derived
analysis targets in NEW output; capture dependency closure/task estimate without
executing producers. Audit closure for unexpected native compile/APK/signing,
network fetching, source/Default paths written, uncontrolled remote runner use or
large/unknown generation. Stop rather than dropping dependencies. Saved Siso may
have its own cache/shared state: account for this explicitly; no manual cache
reset, no change to saved Siso config, no graph/history copying across outputs.
The actual command uses saved autoninja -C "$CONTENT_VERIFY_OUT" with reviewed
actual group/outputs, DEPOT_TOOLS_UPDATE=0 and logged exit status. No invocation
is authorized now. If dry-run frontend semantics are unclear, inspect/query the
graph and stop; do not experiment by accidentally building.

Record available disk/inodes/RAM before, projected graph closure and observed
growth after each step. No measured host capacity or reliable byte/time estimate
is available yet. A new output can regenerate a substantial Java dependency graph,
resources/JNI/srcjars, header jars, plugins and tools; it is NOT an incremental
reuse guarantee. Ask the user to review the dry-run plan/capacity before execution;
stop if free resources cannot cover estimated dependency outputs plus protected
Default/backups, if estimate is unavailable, or memory/disk pressure appears.
No timed claim is inferred from prior Ninja counts or previous APK duration.

Accept only fresh successful synchronous actions for every audited family shard,
status0, matching new stamps/logs, actual NullAway flags/processor hashes and
source coverage, no remaining NullAway warnings/errors hidden by filters. No
'nothing to do' accepted without an earlier complete same-config execution
receipt. Preserve logs before summarizing; do not use grep absence as sole proof.
Warnings-as-errors may stop on unrelated upstream checks: preserve and report
separately; do not suppress or downgrade them and call NullAway PASS.

Receipt must include candidate58-after and full analysis source hash maps, tool/
script/jar hashes, exact args delta/new output, GN/action/shard/source-list records,
command/log/status/stamp hashes and unchanged Default+source inventories. No
cert/key material needed. Match receipt to subsequent Default candidate at build
review; no auto-clear of historical helper gate. The separately configured output
must never feed APK packaging/signing or be renamed/symlinked to Default.
Existing jars/fragment/model tests are NOT equivalent to this real-source run.

## Current validation / remaining uncertainty

This task reviewed fixed config.gni/internal_rules.gni/errorprone.py/server_utils.py
and static_analysis.md; no missing dependencies were fetched and no verification
output was generated. Source-template findings and documented command syntax are
preparation only. Actual graph/shard/source-list/classpath audit, disk/closure
estimate, analysis execution and product integration remain UNVERIFIED. No
NullAway PASS is claimed. Product/default args/old helper gate remain unchanged.

Local preparation checks:95 existing tests PASS, actionlint PASS, documented
Bash and embedded Python syntax PASS, git diff --check PASS. AST inspection of
fixed errorprone.py confirms empty in-place-fix list; no processor/Java execution
is implied. No product code/helper/gate/selection or saved host file changed.
