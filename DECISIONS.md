# Versanium Decision Log

> Append-only record of material project decisions. Correct mistakes with a new decision entry; do not silently rewrite history except to fix formatting or factual transcription errors.

## 2026-10-19 — Establish durable cross-chat project control plane

**Decision:** Use GitHub, Notion, and ChatGPT Project Sources together rather than relying on chat-to-chat memory.

**Authority model:**

1. live GitHub state in Primary;
2. four authoritative GitHub documents;
3. ChatGPT Project Sources;
4. Notion planning/history;
5. Memory;
6. older individual chats/handoffs.

**Reason:** Separate ChatGPT conversations do not reliably carry the entire detailed state of every other conversation. Durable project sources reduce stale assumptions and make conflicts auditable.

**Operational consequence:** Any material state/policy change must update the appropriate GitHub control document. Notion and Project Sources are then refreshed as needed.

## 2026-10-18 — Correct repository roles

**Decision:** `Nvoid911-Lab/Versanium` is Primary / Source of Truth. `Nvoid911/Versanium` is Secondary / backup.

**Supersedes:** Earlier migration documentation that described `Nvoid911/Versanium` as Primary and the Lab repository as Secondary.

**Synchronization direction:** Primary → Secondary.

**Long-term intent:** After migration validation, the Personal Secondary repository may be archived.

**Reason:** The user explicitly corrected the earlier Primary/Secondary assumption and selected the Lab repository as the main authoritative repository.

## 2026-10-18 — CircleCI retired

**Decision:** CircleCI is no longer part of the intended Versanium CI/build architecture. GitHub Actions is the supported automated build path.

**Consequence:** Do not reintroduce CircleCI configuration without a new explicit decision.

## 2026-10-18 — Test-first release gating

**Decision:** Migration work must be validated through Test builds before production release. Production release is not implied by successful local tests or successful Test builds.

**Current gate:** `VERSANIUM_RELEASE_APPROVED` remains false until explicit user approval.

**Production repository:** Production stage/publish/attest is restricted to `Nvoid911-Lab/Versanium` under the current corrected repository-role model.

## 2026-10-18 — Preserve compatibility-sensitive inherited identity

**Decision:** Versanium is the user-facing project/product identity, but inherited package/application IDs, signing configuration, internal Titanium identifiers, upstream attribution, storage/resource identifiers, and other compatibility-sensitive values are not globally renamed.

**Reason:** Branding and technical identity are different layers. Broad replacement risks breaking updates, stored data, permissions, signing, extensions, build logic, or provenance.

**Consequence:** Identity changes require scoped migration design and validation.

## 2026-10-18 — Preserve feature histories separately until integration is intentional

**Decision:** DeX/mobile zoom, F11 toolbar/certificate work, Titanium version-update work, and YouTube PiP diagnostics may exist as separate branch histories. Branch presence does not mean automatic integration into stable/main.

**Specific note:** YouTube PiP diagnostic work remains experimental unless explicitly integrated after review.

## 2026-10-18 — Runner configuration evolved; current workflow wins

**Historical state:** Commit `a8098ae78f82b91b1a8dc48a54d4bcc514177207` implemented a fixed repository→runner mapping.

**Current reviewed Primary state:** Later migration commits changed the workflow to a constrained `runner_provider` choice (`blacksmith` or `sengi`) while keeping an allowlist of the two Versanium repositories and preventing arbitrary runner labels.

**Decision:** Treat the current Primary workflow as authoritative. Do not resurrect the older fixed repository→runner mapping solely because it appears in historical documentation or Memory.

## 2026-10-19 — Synchronization discrepancy discovered during control-plane setup

**Observation:** At the start of this documentation pass, Primary `migration/versanium` was at `7a3beb16851ce22989018ac609a7c98693231fc9`, while Secondary `migration/versanium` was still at older commit `a8098ae78f82b91b1a8dc48a54d4bcc514177207`. Primary and Secondary `main` also did not share the same tip.

**Decision:** Do not reinterpret this as a role reversal. Primary remains authoritative. Synchronize reviewed migration refs Primary → Secondary without force when ancestry permits. Main synchronization remains a separate consequential operation and is not performed merely as part of documentation setup.

## 2026-10-19 — Complete Primary → Secondary migration branch synchronization

**Decision:** Fast-forward Secondary `Nvoid911/Versanium` branch `migration/versanium` to the reviewed Primary documentation head.

**Previous Secondary head:** `a8098ae78f82b91b1a8dc48a54d4bcc514177207`

**Synchronized head:** `b40976ec3c209c805fba5326f2326e8324fc64d2`

**Transfer:** 15 commits, Primary → Secondary.

**Safety:** The Secondary head was verified as an ancestor of the Primary head before push. A normal fast-forward push was used; no force or force-with-lease operation was used.

**Verification:** After push, Primary and Secondary `migration/versanium` resolved to the same SHA, and the synchronized commit was independently retrievable from both repositories.

**Consequence:** The migration-branch discrepancy recorded earlier on 2026-10-19 is resolved. The two `main` branches remain outside this synchronization decision and must not be changed merely to make their tips match.

## Decision-entry template

For future material decisions append:

```text
## YYYY-MM-DD — Decision title

Decision:
Supersedes (if any):
Reason:
Consequences:
Verification / evidence:
```


## 2026-10-22 — Propose in-place recovery of IdeaPad Run #5

**Decision proposed for review:** Resume the preserved source/output in place via a dedicated opt-in mode in the existing manual workflow. Checkout the controller into a separate child directory and reject ordinary IdeaPad checkout when the old workspace exists. Do not move, clean, reset, sync, or reapply patches to the interrupted tree.

**Reason:** The initial IdeaPad job reached C++ compilation but was cancelled after approximately six hours. The user confirmed 14GB of output and Ninja/Siso state remain. Moving paths or repeating the original non-idempotent setup could discard useful work.

**Scope:** Primary-only arm64 Test recovery at original repository commit 6e7517e6de89e5a1230cebf906470795112466a3, unchanged GN arguments and default parallelism, 1200-minute recovery timeout, vmstat telemetry, temporary signing files, no production authorization. Mismatches fail closed without a full-build fallback.

**Validation/status:** Local checks only; review and real IdeaPad recovery remain pending. This does not declare a permanent persistent-workspace implementation or authorize dispatch. Old Run #5 reruns remain unsafe because workflow changes do not retroactively alter them.


## 2026-10-22 — Propose six local jobs for IdeaPad recovery

**Supersedes:** Retaining default recovery parallelism in the earlier Run #5 recovery decision.

**Reason:** User-supplied long-duration vmstat measurements show recurring memory pressure and swap traffic on the 12GB WSL instance. The default execution had twelve concurrent clang++ processes and very slow progress.

**Proposed change:** Use autoninja -j 6 for chrome_java and chrome_public_apk in recovery only. Scheduling is changed without changing GN inputs or cleaning incremental state. Six is an initial measured tuning candidate, not a promise of six-hour completion. Keep telemetry for comparison. Production remains blocked; Run 39624481319 is cancelled and a new Test dispatch requires user selection.

## 2026-10-23 — Propose 156 Test with explicit candidate and recovery separation

**Evidence:** Primary d64b78b and successful recovery Run39765620887 reuse the 155 tree from original source6e7517e. User confirmed F11 and persistent smartphone YouTube problems with working DeX. This was not a test of newly applied independent playback fixes. Official latest stable at work start is v156.0.8078.47.

**Review proposal:** Preserve upstream merge history/exact pins; adapt the zoom overlay's context to retain Chromium's newer CHECK. Add confirmed SAF backup/restore of absolute zoom values, retaining internal keys/migration marker and profile privacy. Add separately switchable, bounded YouTube-only PiP-attribute/background-visibility candidates and minimal non-content diagnostics. Keep these statuses distinct from build/device success.

**Build boundary:** Reject old resume mode on the new revision. Use an isolated fresh IdeaPad directory and explicit source/GN/toolchain provenance. Keep six local jobs as an initial conservative cap, with the 20-hour IdeaPad timeout and a required local host-capacity check. Do not clean/relabel/repatch the prior tree or dispatch a build. All production/main/tag gates remain unchanged.

**Remaining review blockers:** AndroidX package access and real preference UI/type validation, whole native/GN/renderer integration, inline PiP fullscreen limitations, native-vs-page pause diagnosis and actual Windows/WSL capacity. Notion/Project Sources need a verified refresh after reviewed integration, not before. A separate main documentation PR does not authorize code promotion or Release.

**Pre-build correction to the October23 proposal:** Real-source review identified the WebUI-only JavaScript API gate. The draft must not be built with an unadapted normal-page call. A separate shared native scope predicate and marked-payload guard replace that invalid assumption, with no process-global injection enablement or test-only API. The 17 policy-model cases pass; actual Chromium C++ compilation/security review is still required.


## 2026-10-23 — PR5 review: archive compatibility and fixed-payload native route

**Supersedes:** The pre-build correction's original marked-payload/frame-wide CHECK exception, not upstream JavaScript restrictions. Keep generic JavaScript APIs byte-for-byte at the pinned Chromium implementation. Add a separate JNI route with no script argument, using only a compiled reviewed payload and natively checked flags/frame/profile/domain scope. A script marker is not authentication. Limited tests/JNI generation do not constitute a native build or security audit.

**Legacy zoom:** Preserve all finite stored exponents in the archive; do not use slider limits as storage/schema limits. Before SAF replacement, reject an entire numerically unsafe restore explicitly while preserving its source file/current data. Do not silently clamp/delete entries. Slider summaries distinguish stored out-of-range defaults from its bounded thumb; renderer limits remain upstream behavior. Literal old-key fixtures and the pre-v1 migration path cover lossless double round trips without collecting user data.

**Environment movement:** Restore only the candidate-owned PiP attribute; observed intervening site mutations revoke ownership even when the final value is again false. Restore still-owned detached elements before releasing references. Retain bounded attempts and opt-in/mobile-only changes.

**Readiness:** Cloud CIPD CONNECT403 and runner-list API authorization403 are separate failures, neither evidence of host capacity or actual build-host dependency failure. Exact156 AndroidX snapshot metadata and local inspection/manual-ref steps are recorded in docs/versanium/next-test-156-review.md. No build, main merge, tag or Release is authorized by these changes; PR6 remains separate.


## Run9 — Correct real GURL API and retain a strictly bounded156 recovery path

**Correction:** At fixed Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775, GURL has std::string_view host() const, no host_piece(). Prior model success did not establish API compatibility; our earlier source review missed this. Replace only three calls and require real-header digest/declaration comparison before model tests. Actual failed-object compilation remains the next validation gate.

**Recovery decision:** Do not rerun normal fresh-build logic, relax155 recovery, regenerate GN, resync/repatch/reset/clean/move the saved Run9 tree. Prepare a new156-specific manual validation/apply/recheck helper, pinned to Run39951209951/repository7d9102f and its original provenance artifact digest. Only after host validation and separate authorization may the real failed object be requested using the preserved Ninja/Siso graph; a subsequent full APK target requires a separate decision. Retain original provenance plus correction controller/diff/hash evidence. No cache-count/time promises.

**Evidence limits:** Run metadata/provenance-artifact metadata are readable; log/artifact bytes are blocked in this cloud. GN/chrome_java success comes from the user's log. Actual host object compilation/APK/runtime remain unverified. Update information-source files before resumption; preserve PR6, signing/Secrets/package isolation/runner policies and main/migration refs. No Actions or build is authorized in this work unit.

### Run9 — Match the logged object without requiring UTF-8 graph files

**Evidence:** Read-only host preflight on controller093f787 stopped on non-UTF-8 bytes in an unrelated rust lib.ninja before mutation/compilation. Other toolchains define objects with the same basename. The user confirms the original log's failed target is obj/content/browser/browser/render_frame_host_impl.o.

**Correction:** Parse ASCII build syntax as bytes, including Ninja continuation handling; do not silently delete undecodable characters or re-encode graph files. Require exactly one definition of the full logged target, rule cxx and its exact explicit .cc input. Do not conflate different toolchain prefixes or deduplicate repeated exact definitions. Retain all provenance and preserved-state gates. Retry only read-only preflight from the separate corrected controller with new evidence; this helper correction does not authorize apply, build or Actions. Fixture tests do not establish real host preflight/native success.

## 2026-10-24 — Remove unsafe diagnostic probes; separate PiP exit investigation

Context v1.9 records successful manual156 build/sign/install and diagnostic-only crash loops. Real pinned MediaWebContentsObserver requires fullscreen_player_ and picture_in_picture_allowed_in_fullscreen_ for the permission getter; our unconditional diagnostic query violated that contract. Remove the probe rather than weakening CHECKs. No stack means user root cause remains unconfirmed. Make diagnostics passive Java stage logging, exclude it from both candidate gates and always disable page diagnostic instrumentation. Retain candidate DOM behavior that improved tab playback. Do not alter PiP dismissal/MediaSession without event-order evidence. Persisted diagnosis should no longer reach this hazard after a future compatible update; no data-deletion/reproduction request or tested recovery claim. Keep saved Run9 untouched; its narrow recovery gate must reject this wider change.

## 2026-10-24 — Prepare a separate evidence-gated reuse path for target60b0037

The completed Run9 output contains useful real156 work but predates four applied source changes. Do not relax or repurpose `prepare_run9.py`. Add a distinct read-only-first controller which authenticates the original ZIP, ebfc correction evidence, saved post-build provenance, exact source hashes, unchanged generated/JNI/GN inputs, toolchain and current graph. A future apply needs separate authorization and may alter only the four reviewed files with external backups/evidence. Require chrome_java and the two graph-derived native objects before any separately approved APK continuation. Saved output implies neither reuse nor completion. The next APK tests diagnostic crash removal and collects PiP event order; it is not a PiP-fix APK.

### Correct flag-metadata expectation from the actual patch order

The b401856 host preflight exposed that selected-source testing had omitted the 11 patch.sh expiry edits before adding the three candidate records. Reject the resulting candidate-only293f hash as a pipeline expectation. Reproduce fixed HEADc155 → expiry-only47f → candidatesdc5 with exact patch.sh names/order and candidate formatting, then compare saved bytes directly. The reported real hash equals reproduceddc5, but cloud-side direct comparison is unavailable without the host file. Do not treat a newly observed digest as an allowlist or bypass provenance. The stopped preflight made no source/output change and does not authorize apply/build.

## 2026-10-24 — Video fullscreen rendering candidate (unbuilt)

Keep persisted default/site/environment values and backup formats. Restore upstream temporary zoom priority before environment lookup/save; temporary JNI adjustments must not persist. Render exponent0 only for outermost DOM fullscreen with a media fullscreen-player ID, preserving existing temporary entries. Re-evaluate on media fullscreen entry/exit and existing refresh. F11 alone is excluded and pause does not remove the override. Actual visual resolution/root cause and rotation/media ordering remain unverified; see docs/versanium/video-fullscreen-zoom-review.md. Prior diagnostic APK is user-confirmed working in diagnosis-only tests. Do not reuse/relax the four-file apply controller for this wider native change.

## 2026-10-24 — Preserve both PiP comparison outcomes; instrument existing branches

Candidate OFF is a blocked-entry observation; ON confirms entry then exit. The latter demonstrates a conditional eligibility/transition difference, superseding blanket "ineffective" interpretations. At +88ms the fixed50ms dismissal grace has elapsed, but old dismiss/stop logs precede real branch actions. Add actual branch and suspend-completion diagnostics, preserving getter counts/short circuit and all playback/exit rules. Do not ignore fullscreen6/7 or disable onStop based only on timing. Trace persistent-video, browser fullscreen origins and renderer effective state as hypotheses; no causal stack is present. Retain video zoom work and report its not-yet-built status separately.

## 2026-10-24 — Correct common selected-source pipeline coverage for A/B

Host provenance matched but three manifest files exposed six omitted inherited patch.sh operations. Reproduce exact commands and require reported host hashes from fixed inputs, rather than skipping files or accepting alternatives. Apply corrected coverage tooling to installed/A/B, regenerate B native hash/diff, and test omission of each operation plus order equivalence. Selected fixture PASS is not real-host40/40 or Chromium success. Old helpers remain strict and unchanged; corrected read-only comparison precedes any later authorization.

## 2026-10-24 — Prepare executable A-only transaction after reported host40/40

User confirms b341 host40/40 and applied/after-apk/current provenance match without apply/compile. Add an independent one-Java-file controller with default read-only, explicit apply, and precompile verify. Reconstruct fixed-source installed→A bytes via exact historical patches, retain external backup/intent/provenance/full Ninja-Siso-generated-output hashes, reject drift/repetition and preserve partial evidence without automatic rollback. No old helper relaxation or B application. Next narrow build gate is chrome_java before separately authorized APK/signing; A device evidence precedes B.

## 2026-10-24 — ConfigA confirms actual exit; trace request origins before changing policy

User A logs establish OFF video permission denial and ON reason6 move success/cleanup, later inactive7, returned SYSTEM suspend then media stop/framework exit. Update old execution uncertainty for this A trial only. Existing PiP guard is conditional multiwindow behavior, not a global protection. Add fixed same-tab safe labels at actual Base handler request/dispatch sites to identify the first caller; preserve condition evaluation/getter counts and all exit/stop rules. No grace-only fix or blanket suppression without a transition/user-intent distinction. Do not treat persistent-video call return as renderer completion or new A logs as evidence for unapplied B. Restart/current display/candidate settings for new posts remain instructed rather than fully re-reported.

## 2026-10-24 — Prepare AOrigin against completed A, without B

Add a new41-file selection (A40 plus Base) and independent explicit two-file apply controller. Require A applied.updated_provenance and after-apk equality/current reconstruction, not pre-A diagnostic inputs. Preserve original A helpers/manifests and B exclusion. Test fixed-source recipes, repeated/mismatched state and second-file failure without automatic rollback. Real chrome_java/NullAway then APK/signing remain later authorization gates, with a distinct ConfigAOrigin artifact and retained A distributions. Filtered origin-log absence never proves absence of the underlying event.

## 2026-10-24 — AOrigin② external exit remains unproven

Preserve user-visible failure and framework-entry evidence together. Do not infer
multiwindow causality from callback alone or from missing filtered request logs.
Trace the fixed156 native/Java delegate forwarding gap; propose branch-local
labels before changing behavior. Recorded STOPPED/hidden follow first accepted
exit; do not bypass all fullscreen exits/onStop or extend grace as a substitute.
No product/apply-manifest changes; no B or host operations are authorized.

## 2026-10-24 — Implement Java forwarding diagnosis on AOrigin baseline

Adopt only fixed wrapper/selected Activity-branch labels and scoped tab reporter.
Preserve feature reads, eligibility, manager calls and lifecycle behavior. Use
built AOrigin evidence LfbK0s and43-input before/after manifest, never A/installed.
Keep old apply helpers unchanged. Native origin remains unresolved; defer native
implementation until a scoped lifetime-safe JNI bridge is reviewed. No B/apply/build.

## 2026-10-24 — Prepare AOriginForward independent three-file transaction

Require completed AOrigin LfbK0s evidence, not A/installed; reconstruct pinned
before/after bytes and check43 inputs. Preserve other40/B exclusion and output
inventory. Default read-only, explicit apply with external backups/intent,
post-verify before compilation. Partial failure retains evidence without rollback.
Plan real Java/NullAway then APK/same-key signing to distinct ConfigAOriginForward
filename; do not execute. Java forwarding only; native requester remains unknown.

## 2026-10-25 — Forward② narrows route to EAM, not initial cause

Preserve full log and brief-visible-PiP/audio-stop/no-crash/restart report.
Observed ExclusiveAccess forwarding before Base acceptance narrows Java route;
it does not establish JNI/native guard or first caller. Fixed source admits EAM
reentry and context→FullscreenManager output. Do not infer independent requests
from repetitions, renderer completion from persistent return, or no downstream
FullscreenManager from absent normal Activity label. Defer behavior changes;
document safe scoped native ingress/guard/context diagnostics and lifetime/JNI/
GN gates. No feature force-off, blanket exit suppression or grace-only fix.

## 2026-10-25 — Adopt bounded EAM native diagnostics, defer content ingress

Instrument actual EAM exit JNI and existing controller branches/context output,
with fixed enums/current scoped contents and TLS depth. Preserve all original
conditions/getter counts/CHECKs; WeakPtr callbacks suppress destroyed owners.
JNI generator private-callback error corrected via package-private method, no
generator relaxation. Root content renderer/browser/security remains unmeasured:
do not introduce content→chrome dependency or infer original cause from EAM entry.
Keep all43 Forward inputs/B unmodified; new50/51 selection needs a new reviewed
transaction/GN plan before any host apply/build. Old helper gates remain unchanged.

## 2026-10-25 — Separate native source apply from graph regeneration

Require completed Forward lnxJen evidence and exact installed-distribution APK
hash. Add standalone source-only transaction and post-GN byte/metadata audit,
without importing any historical preflight/apply helper. Preserve50 inputs/new
header absence and51 outputs/Forward43/B exclusion; external graph and histories
backup precedes writes, partial failure retains evidence without rollback.
Modified BUILD.gn requires GN gen with saved binary/args; no implicit regeneration
via autoninja. Resolve actual objects by loaded source/rule/toolchain, not names.
All actual host apply/GN/compile remain outside current authorization.

## 2026-10-25 — Repair escaped Ninja tokens, retain source controller evidence

User-host source/GN success does not imply compile success; parser failure is
separate. Decode $:/space/dollar and continuations as bytes; inspect decoded
explicit/implicit output duplicates, reject unknown variable syntax. Keep source/
rule/toolchain and old/new object identity gates. Permit old source-record SHA
only via trusted ancestor and audit/test/Markdown-only delta plus product/manifest/
source-helper invariance. Record proof under fresh re-audit evidence, never rewrite
original controller or reapply/regenerate the saved tree to solve an audit bug.

## 2026-10-25 — Separate Native early media stop from Forward onStop suspend

Preserve full log and visible result/restart; do not invent signed Native APK SHA.
Native media stop precedes onStop and stop_not_playing excludes this branch's
SYSTEM suspend. Existing Forward suspend evidence remains a separate trial.
Observed d3/d4 are nested cycles consistent with loss/Base WebContents call-outs,
not multiple roots; first content ingress still unknown. No safe blanket EAM/
fullscreen/PiP cleanup fix is established. Prioritize ingress + persistent-false
dispatch only if another diagnostic is needed, with actual scoped content observer
JNI and lifetime review. Keep B/video zoom separate; do not build or modify host.

## 2026-10-25 — Implement narrow content ingress and false-dispatch diagnosis

Use existing content observer/Android JNI boundary, actual receiver/current tab
and fixed enum labels. No Chrome TLS/dependency in content. Bracket actual API/
wrapper/dispatch calls and selected security/navigation/gone branches; generic
arrival alone remains unknown. Observe cleanup false, existing equal-state/no-player
returns and actual Mojo call begin/returned, never renderer completion. No pause/
MediaSession diagnostics or exit behavior change. Preserve old manifests/helpers;
new58 source-only product selection is not saved-host apply authorization.

## 2026-10-25: Native58 content-origin preparation only

Accept only user-confirmed Native source/graph/after-apk/sign record and actual
APK through exact hashes and ancestry proof. No retroactive graph reference is
inserted into signature records. New independent helper defaults read-only;
explicit source apply and separate graph audit retain external backups/evidence,
stop without rollback. Actual graph/JNI closure and generator depfile determine
GN need; no BUILD diff alone is insufficient. Saved ErrorProne=false cannot be
reported as NullAway success. No product/old helper changes or host/build execution.

## 2026-10-25: Correct JNI discovery without loosening graph identity

Use fixed156 jni_zero Android root_build_dir/gen/jni_headers layout, not a
basename fallback. Since Android JNI outputs may be shared across toolchains,
require exact content_jni_headers arm64 action in toolchain.ninja plus actual
Java input, recipe, uniqueness and dependency closure. Keep old evidence/product/
selection/helpers immutable. Host Java/NullAway was not reached; rerun read-only
with new controller and external evidence, no apply or build authorized.

## 2026-10-25: Java production membership is GN action identity

Remove Ninja file-stem family inference. Exact content/chrome compile rules,
default arm64, direct Java inputs, template-derived jars/info/optional compliment
and JNI dependencies determine membership. Separate ErrorProne/stamp/shard and
validation scan determines analysis availability; ordinary compiler NullAway flag
absence is not a proxy for analysis absence. Reject ambiguous/unproven membership.
Preserve product/selection/old helpers/evidence; retry read-only in new evidence.

## 2026-10-25: Plan isolated real-source NullAway validation

User host TQNw0X read-only completed; source apply/GN/compile not done. Saved
ErrorProne=false and no separate actions mean NullAway remains NOT_PROVEN. Plan
fresh verification-only output, exactly ErrorProne=true/static_analysis="on"/
warnings-as-errors=true overrides, after content candidate source-only apply and
verify. No output generated now. Audit real graph/shards/source lists/processor/
classpaths and capacity before executing family-wide analysis; no jar/fragment
substitutes, no cross-output packaging/signing. Old helper gate and Default remain
unchanged; a reviewed matching execution receipt is needed before product build.

## 2026-10-26: Applied candidate and bounded acquisition provenance audit

Accept user-reported candidate10 apply/verify PASS under7b60873 as latest host
state; no reapply. Processor hashes identify observed bytes, not standalone proof
of immutable CIPD instance membership. Package-local .cipd absence is inconclusive;
inspect actual saved gclient root/tool revision and centrally indexed package
metadata once, without executing bootstrap clients or acquiring dependencies.
If binding evidence is absent, report unproven, not mismatch or waived provenance.
Keep Default/args and original apply controller/evidence; prepare only docs-only
compatibility proof, isolated-output3-override/GN/audit stages. C physical capacity
and measured dependency growth govern future review, not WSL virtual capacity.

## 2026-10-26: Separate large apply receipts from small metadata

The first CIPD batch failed before jars because1MiB metadata cap was applied to
normal generated-output inventory. Preserve old batch/evidence. New external
collector uses bounded256MiB receipt parsing after size/estimated memory check,
strict required schema/config/controller/pins and stable-file checks. Keep small
package caps and original disk inventory unchanged; no unconditional limit waiver.
Documented function regressions cover normal>1MiB inventory and invalid inputs.
Changes remain Markdown only, preserving original applying controller7b60873 and
its verification/provenance rules. No host collection/build execution authorized.

## 2026-10-26: Confirm CIPD file digest encoding, preserve trust boundary

LUCI primary iid.go plus caspb SHA256=2 confirms supplied manifest file hashes
as digest+algorithm rawURLBase64;3 positive/2 negative checks PASS. Prepare new
external live size/hash/package/subdir/instance receipt, explicitly local-record
consistency only. Host metadata-location uncertainty is resolved by v2-5N3hJj
user report, not fabricated host access. Keep original apply controller7b and
Default unchanged; future separate3-override output/GN stops for graph/capacity
review before analysis. No packages or runtime verification executed now.

## 2026-10-27 — Reconcile dead diagnostic labels in the current generator

Remove only the unused private stage parameter and four literal arguments;
do not restore callback/logging or introduce stage-based behavior. Retain the
current content/PiP native route and passive authorization boundaries. Current
generator output must match the reviewed host post-fix TabImpl bytes. Suppression
and warnings-as-errors relaxation are not acceptable alternatives.

Historical source-apply controllers remain pinned and strict: the preparation
history test uses its own immutable7b60873 snapshot for the positive case and
explicitly rejects the new no-arg generator under the old product gate. Do not
rewrite old manifests/hashes or auto-approve old controllers for the new product.
User-reported host NullAway outcomes are recorded separately from locally run
models/source-generation tests; neither proves a new native/APK/device build.
The existing local shard2 fix and host preparation helpers are preserved but
not silently swept into this narrowly scoped reconciliation commit.

## 2026-10-27 — Publish reviewed context-menu constant-expression correction

Formalize the preserved one-line patch.sh fix, not a new alternative: remove
the short-circuited desktop-UA expression and generate MOUSE || LONG_PRESS.
Retain prior Versanium empty-space menu behavior and no UA-getter evaluation.
Do not revert to Chromium's desktop-UA-dependent long press, add suppression,
change compiler options, or broaden DevTools enablement. Source regression tests
execute only the actual selected command in a temporary fixed156 tree, compare
all surrounding bytes, and reject old/false-constant/missing-condition output.

Keep b69195c stage hooks and current content/PiP route intact; do not include
untracked host helpers/evidence. Exact generated source matches host post-fix,
but distinct whole patch.sh hashes are not interchangeable without host-byte
review. Preserve historical host pins. Successful reconciliation permits the
next saved integration review, not a Test Build, release or host re-analysis.

## 2026-10-27 — Close saved integration review; hold explicit Test Build gate

Accept the user-supplied completed saved integration/graph/Siso evidence for
reviewed product d1e3261690917bb29d75947c3e9d6bf89c44f728. Saved Default reuse
PASS, GN regeneration NOT REQUIRED; gn clean FORBIDDEN for the recorded saved
workspace. Changed sources still require incremental recompilation. Whole-file
patch.sh comparison is reported resolved to the reviewed shard2 one-line fix;
retain distinct historical hashes. Never re-execute the old saved patch.sh or
old saved tools/apply_youtube_candidates.py. Preserve current source, graph/args,
Siso v1.6.3 / ProdCIPD=true binary and saved state, evidence and untracked files.
Exact binary/state identity, paths/hashes and freshness facts are appended in
[stage reconciliation](docs/versanium/post-nullaway-stage-reconciliation.md#2026-10-27-jst--completed-saved-integration-review--current-state).
This records provided host evidence, not new host verification/build success.

### Test Build Gate

Test Build NOT APPROVED; require explicit user approval in a later step.
Candidate only after approval: saved out/Default via Siso/autoninja incremental
chrome_public_apk using reviewed current source, without old patch/generator or
GN gen/clean. Refresh/present Context and check live host capacity/concurrency
before execution. This docs-only checkpoint authorizes normal commit/push, not
build execution. Actions/APK/merge/release/tag/Production remain NOT APPROVED;
keep PR5 Draft/Open/unmerged. No PR body change is needed for this checkpoint;
its historical entries remain historical. Next gate:
WAITING_FOR_EXPLICIT_TEST_BUILD_APPROVAL.


## 2026-10-28: Retire independent YouTube candidates; preserve Zoom

> Current policy — 2026-10-28 JST: the former Versanium YouTube PiP,
> Diagnostics/unsafe diagnostics and Background candidates are **retired / superseded**.
> Their generators, runtime plumbing, dedicated apply controllers and tests are removed.
> Earlier candidate descriptions below and existing docs/versanium reports/manifests/logs
> are historical evidence, not current functionality or executable instructions.
> Zoom (phone/DeX, transfer, persistence, policy, backup), F11/display, branding,
> Chromium156 pins and non-PiP features remain unchanged. Saved generated source
> and existing APKs are untouched and still reflect their historical configuration.
> Future PiP work is limited to Brave #36838 (YouTube PiP lifecycle/dismiss),
> #33522 (background playback), #39765 (Chromium153+ screen-lock/onStop).
> No Brave code is ported here. Build/GN/Actions/APK/merge/release/tag/Production
> are prohibited in this cleanup phase; PR5 stays Draft/Open/unmerged, body unchanged.
> See [retirement plan and integrity ledger](docs/versanium/pip-candidate-retirement-2026-10-28/plan.md).
> Next: `READY_FOR_BRAVE_36838_33522_39765_READONLY_PORT_ANALYSIS`.

User device trials did not resolve the PiP lifecycle failure. Stop the old three-candidate approach and remove its product/experiment/apply paths, while retaining historical evidence and all Zoom bytes. This supersedes prior candidate-development and recovery directions; earlier decisions remain historical. The three Brave references define future read-only analysis scope, not a verified or implemented port.


## 2026-10-28: Implement restricted Brave #36838 Phase 1; require prebuild review

> Current checkpoint — 2026-10-28 JST: Brave #36838 Phase 1 source implementation
> is complete. **Phase 1 implemented but NOT compiled/built/device-verified.**
> Next: `READY_FOR_36838_PHASE1_PREBUILD_REVIEW`. A separate Source-of-Truth gate
> is required before GN/build. Java-only, Chrome-only, exact HTTPS mobile YouTube
> watch/fullscreen scope; #33522/#39765 remain unimplemented; old candidates stay
> retired. Zoom inputs and existing lifecycle statements are unchanged.
> This supersedes the retirement-only/current-no-port notices below, which remain
> historical. No saved Run9 access/change, GN/build/Actions/APK/merge/release/tag/
> Production operation or PR body edit occurred.
> See [implementation, verification and limits](docs/versanium/brave-36838-phase1/implementation.md).

Adopt the approved design with seven commits and a single default-off gate in commits1–6. The final source integration enables the gate. Persistent-video leave callbacks are detached before DOM/UI teardown to prevent reentrant task dismissal; all protection is already off in EXITING. This ordering refinement and API-double/parse-only validation limits are recorded in the implementation report. Entry does not resume media, media never falls back to a new current tab, config change ends the session, and screen lock follows ordinary stop. No build or device result is implied.


## 2026-10-28: Diagnose Phase1 device failure without changing behavior

Fresh Phase1 integration, GN, chrome_java and chrome_public_apk succeeded in the
specified phase1-36838 workspace (existing logs verified). User reports Galaxy S23
launch/playback PASS, tab switch stops playback, Home no PiP, playback stays stopped.
Add Java-only VersaniumPiP structured logs at existing policy/controller/upstream
entry/lifecycle/tab-switch hooks. No eligibility widening, forced resume, fallback,
JS/C++/JNI, #33522/#39765, Zoom/F11/branding or identity/signing changes.
The user explicitly authorizes commit/normal push (Primary then Secondary), fresh
incremental GN -> chrome_java -j6 -> chrome_public_apk -j6, and reuse of the existing
local device-test key. No previous Run9 access, ADB/install, Actions or release.
[Diagnostic events, limits and tests](docs/versanium/brave-36838-phase1/diagnostic-logging.md).


## 2026-10-28: Compare mobile/desktop visibility and media without changing PiP

Additional user evidence on the same Galaxy S23 / same target APK: mobile site
fails tab-switch playback and Home PiP; desktop site continues playback and enters
PiP successfully. This favors mobile-site-specific visibility/background handling
over generic Android PiP API failure, but pause-before-entry remains a hypothesis.
Add desktop_site/Tab UA mode and source-correlated seq logs, existing tab shown/
hidden/selection callbacks, and at most two passive WC/MediaSession observers to
retain outgoing asynchronous media/visibility events after tab observer cleanup.
Use only existing Java APIs; report unsupported active/custom-UA state as unknown.
Diagnostic www/bare YouTube observation does not broaden product eligibility.
No media action, ownership policy, observer decision, JS/C++/JNI or branding change.
