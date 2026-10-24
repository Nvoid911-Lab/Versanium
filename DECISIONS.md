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
