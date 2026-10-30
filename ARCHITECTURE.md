# Versanium Architecture

> Zoom fullscreen diagnostic boundary — 2026-10-29 JST: independent generated-source
> overlay after existing Zoom/Phase1/Versanium transforms; canonical protected24
> inputs/ledger unchanged. Dedicated command-line gate is OFF by default and
> forwarded to children. No new JNI or source registration. Renderer received
> grant and previous stored grant are distinct; paint-root/CSS/device units are
> never treated as interchangeable. Fullscreen correction is observed, not moved
> ahead of the no-pending return. Source of Truth v1.25 and causal uncertainty remain.
> [Evidence contract and future installation boundary](tools/zoom_fullscreen_diagnostics/README.md).

> Current checkpoint — 2026-10-29 JST: correlated native diagnostics implemented, NOT built.
> Producer attribute/status + browser cache + first pause ingress/policy/session paths.
> Frame token/player -> native RFH/WC main ID -> Java sourceTab/desktop-site correlation.
> Product permission/transport/storage/entry/pause/visibility unchanged; old CHECK guard retained.
> JVM427 (+12), candidate6/active24, bundle5, native structural5, gate-off and parse5 PASS.
> Attribute setter and first pause root cause UNCONFIRMED until future S23 evidence.
> Previous PHASE1_BUILD=PASS; mobile device FAIL; desktop control PASS remain historical.
> No fresh apply/GN/build/APK/signing/ADB/Actions/Run9/merge/release/tag operation.
> NEXT=WAIT_FOR_CHATGPT_REVIEW, then separately reviewed diagnostic APK stage.
> See [instrumentation, correlation and limits](docs/versanium/brave-36838-phase1/correlated-diagnostics.md).

> Current checkpoint — 2026-10-29 JST: source trace completed; no product change.
> PHASE1_BUILD=PASS (previous); MOBILE_DEVICE_TEST=FAIL; DESKTOP_CONTROL_TEST=PASS.
> User same-device/same-APK comparison: mobile fullscreen=true/allowed=false/upstream=false;
> desktop fullscreen=true/allowed=true/upstream=true/frameworkPiP=true.
> Blink video disablepictureinpicture presence -> fullscreen status enum -> browser
> per-player cached optional bool -> JNI -> upstream canDo -> entry is confirmed.
> Exact page writer/timing and first tab-switch pause remain UNCONFIRMED.
> NEXT: review producer/first-pause diagnostic plan; no instrumentation/build authorized here.
> Brave36838 assumes complementary page support omitted by approved Phase1 scope.
> No new GN/build/APK/Actions/Run9/device/merge/release/tag operation.
> See [producer, consumers, Q1–Q7 and evidence limits](docs/versanium/brave-36838-phase1/fullscreen-pip-source-trace.md).

> Current checkpoint — 2026-10-29 JST: symbolicated diagnostic startup fix built/signed.
> State: `SIGNED_STARTUP_FIX_APK_READY_FOR_MANUAL_LAUNCH_TEST` (device launch unverified).
> Compiled fix3ce5aac guards fullscreen-only JNI read; native CHECK was resolved before edits/push.
> Fresh GN/chrome_java/APK RC0, package/alignment/same local-key verify PASS.
> JVM415 (+15) / bundle5 / default-off / parse-only5 PASS; candidate6/active24 retained.
> Source inventory1316, native library hashes, Zoom24, retired34, args and GNI1/1 verified.
> Product PiP behavior unchanged. No Run9, ADB/install, Actions or merge/release/tag.
> See [exact symbols, fix and signed artifact receipt](docs/versanium/brave-36838-phase1/startup-fix-apk-build.md).

> Current checkpoint — 2026-10-28 JST: diagnostic APK built and signed for manual S23 test.
> State: `SIGNED_DIAGNOSTIC_APK_READY_FOR_MANUAL_DEVICE_TEST`.
> Compiled diagnostic controller0cd373e (initial logging50eff9e + mobile/desktop follow-up).
> Fresh GN/chrome_java/chrome_public_apk RC0; Test package and same local-key verify PASS.
> JVM400 / bundle5 / default-off / parse-only5 PASS; Zoom blob24 PASS; retired34 absent.
> Source inventory1316 unchanged after build; args and registration1/1 preserved.
> User's same-device/same-prior-APK report: mobile FAIL, desktop PASS. New APK untested.
> No product behavior fix, ADB/install, saved Run9, Actions, merge/release/tag or Production.
> See [artifact hashes, paths and complete build receipt](docs/versanium/brave-36838-phase1/diagnostic-apk-build.md).

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


Content diagnostic transport is scoped WebContentsImpl→new default no-op native
observer callback→existing Android proxy→generated (I)V JNI→Java observer→current
actual WebContents PiP observer→unchanged scoped logger. No Chrome dependency or
Chrome TLS in content, no global origin state, no async pointer retention.
WeakPtr/destruction guards preserve original decisions; actual false send branches
do not re-evaluate eligibility. Product selection is separate from host transaction.

Native trial constrains EAM branch/reentry, not upstream initiator. Loss clears
exclusive tab then exits WebContents; context output enters Base, whose stored
WebContents exit can reenter again. PiP reason6 move/cleanup runs persistent-false
callbacks before framework exit; renderer delivery/application is unmeasured.
Media-stopped Java callback drops native reason/player context and cannot identify
pause origin. This trial onStop sees mIsPlaying=false and makes no SYSTEM suspend.
Next diagnosis, if separately approved, should identify content ingress and
actual persistent-false dispatch via content observer/JNI, not repeat EAM labels.

Post-GN edge lexer uses bytes tokens: escaped colon/space/dollar are path bytes,
unescaped colon/group operators are syntax. Duplicate checks cover decoded
explicit+implicit outputs. Controller compatibility is a constrained ancestor/
audit-test-Markdown diff proof with product/manifest/source-helper byte invariants,
stored alongside unchanged original source-record hash; never edit that record.

Native preparation is independent of old helpers: Forward50/source-only51 with
unchanged generated outputs, external source+graph/state backup and provenance.
Graph regeneration is a separate manual authorization/command; post-GN read-only
audit allows only graph byte differences and resolves actual default-toolchain
cxx objects from loaded Ninja edges and GN metadata. Non-UTF8 irrelevant Ninja
bytes are preserved, never errors-ignore decoded. No old gate relaxation.

Native diagnostic uses a default no-op ExclusiveAccessContext hook overridden
only by Android, through existing Java context generated JNI. Actual contents
identity is checked before routing to unchanged current-tab scoped logger.
WeakPtr branch callback and pre-call contents snapshots avoid added post-destroy
dereferences; trivial TLS RAII depth captures synchronous instrumented reentry
without owner pointers/async attribution. Content imports no chrome dependency.
New common header is listed in GN; a future graph-change review is required.

Fixed156 EAM path: Java native-pointer gate→ExclusiveAccessManagerAndroid JNI→
FullscreenController→Android NotifyTabExclusiveAccessLost (clears exclusive tab
then WebContents exit)→context native/Java→FullscreenManager.onExitFullscreen.
Base cleanup can call WebContents.exitFullscreen again. Repeated forwarding can
be reentry/chain, not independent root requests. PiP persistent screen-state
preserves fullscreen; Base multiwindow PiP guard is disabled when EAM enabled.
No blanket bypass follows from these facts. Native scope/JNI/dependency/lifetime
review is documented in docs/versanium/config-a-origin-forward2-review.md.

AOriginForward transaction is separate from historical apply controllers:
require built AOrigin updated provenance == after-apk == current recorder;
43 selected hashes, scratch reconstruction of3 Java from fixed source/pinned
transforms; retain other40 and all generated output. Verify is precompile-only.
No old helper gate changes, automatic rollback or build execution.

AOriginForward uses existing UI-thread PiP controller registry/current Tab
identity to route fixed forwarding labels into the existing scoped logger.
It introduces no window-to-Activity inference, retained native pointer or JNI.
Wrapper entry and existing Activity delegate branches distinguish Java routes;
native renderer/browser/security origin remains a separate unimplemented bridge.

AOrigin② source trace: native WebContentsDelegateAndroid can forward through
TabWebContentsDelegateAndroidImpl and ActivityTabWebContentsDelegateAndroid
directly to FullscreenManager.onExitFullscreen, without Base-local request labels.
Missing labels are inconclusive due to scope filters. See
docs/versanium/config-a-origin2-review.md for fixed-source edges and proposed
branch-local diagnostics; no exit/lifecycle behavior is changed.

> High-level technical and repository architecture. This document describes boundaries and responsibilities, not every implementation detail.

Last reviewed: 2026-10-19 JST

## System overview

Versanium is an Android browser derived from Titanium Browser for Android, which in turn carries Chromium/Vanadium-derived build and patch infrastructure. Versanium adds project-specific UX, large-screen/DeX behavior, build/release controls, branding, and selected fixes while retaining compatibility-sensitive inherited internals.

```text
Chromium / Vanadium lineage
          ↓
Titanium Browser for Android upstream
          ↓
Versanium Primary: Nvoid911-Lab/Versanium
          ↓ reviewed synchronization
Versanium Secondary: Nvoid911/Versanium
          ↓
GitHub Actions → Test APK → Galaxy S23 / Android 16 / One UI 8.5 validation
          ↓ explicit approval only
Production Release
```

## Repository topology

### Primary

`Nvoid911-Lab/Versanium`

- authoritative repository;
- source for new reviewed changes;
- production release repository;
- authoritative copy of project documentation.

### Secondary

`Nvoid911/Versanium`

- backup/sub repository during migration;
- receives reviewed Primary refs;
- not a competing source of truth;
- intended for archive after migration validation unless a later decision changes that plan.

### Upstream

`jqssun/android-titanium-browser`

Used as the Titanium upstream reference. Upstream changes should be reviewed deliberately rather than blindly merged into Versanium.

## Key repository areas

- `.github/workflows/` — GitHub Actions build/sign/release orchestration.
- `build.sh`, `common.sh`, `patch.sh` — inherited/custom build and patch pipeline.
- `args.gn` and Vanadium/Chromium inputs — Chromium build configuration and pinned source inputs.
- `tools/versanium/` — Versanium migration/branding/package validation tooling and tests.
- `docs/versanium/` — migration reports and technical audit material; historical documents here may describe superseded repository roles.
- `docs/` — feature investigations/reviews including zoom, Titanium updates, accessibility, and YouTube PiP investigation.
- `res/`, generated resources, fastlane assets — user-facing resources/metadata subject to the branding and compatibility rules.

## Build architecture

The current reviewed Primary migration workflow is `Versanium Build` and is manual-only (`workflow_dispatch`). It restricts execution to the two Versanium repositories and restricts runner selection to reviewed providers/labels.

Current runner provider choices:

| Provider | Runner label |
|---|---|
| Blacksmith | `blacksmith-8vcpu-ubuntu-2404` |
| Sengi | `sengi-standard-8-ubuntu-2404` |
| IdeaPad (self-hosted WSL2) | `versanium-ideapad` |

The provider is selected at dispatch time in the current Primary workflow. Arbitrary runner labels are not accepted.

Build flow, conceptually:

```text
Manual dispatch
  → repository guard
  → reviewed runner selection
  → checkout + submodules
  → Test/release preflight
  → Versanium asset/environment checks
  → Chromium/Titanium build pipeline
  → APK staging
  → Test artifact upload
  → [production path only when explicitly approved]
       release staging → GitHub Release → provenance attestation
```

Production stage/publish/attest is gated by all of the following:

- non-Test invocation;
- `VERSANIUM_RELEASE_APPROVED == 'true'`;
- execution from `Nvoid911-Lab/Versanium`.

The checked-in approval flag is currently false.

## Product identity layers

Versanium intentionally separates user-facing identity from compatibility-sensitive inherited identity.

### User-facing Versanium layer

Includes, where validated:

- app/product display name;
- APK/artifact/release naming;
- repository-facing descriptions and documentation;
- selected app/widget/resource labels;
- Versanium-specific assets when original approved source assets are available.

### Retained inherited layer

May include:

- Titanium/Vanadium/Chromium source directories and patch machinery;
- upstream URLs and attribution;
- package/namespace values needed for compatibility;
- signing configuration;
- storage keys/profile identity;
- authorities/custom permissions;
- resource IDs and internal class/config names;
- historical documentation and provenance references.

These are not branding defects by default. Change them only through an explicit migration decision.

## Test and release separation

The project follows a Test-first migration model. Test artifacts must be safe to validate without accidentally becoming an approved production release. Release publishing remains a separate gated path.

Real-device validation target currently includes:

- Galaxy S23;
- Android 16;
- One UI 8.5;
- smartphone display behavior;
- Samsung DeX external-display behavior;
- keyboard/mouse interactions;
- persistence and upgrade behavior relevant to retained identity;
- YouTube PiP regression awareness.

## Feature/history boundaries

Important feature histories are deliberately separable:

- `feature/dex-mobile-zoom` — environment/zoom behavior; previously device-verified work is preserved.
- `feature/f11-toolbar` — F11/toolbar and certificate-diagnostic lineage.
- `feature/youtube-pip` — PiP diagnostic/experimental history; do not treat it as stable integration merely because the branch exists.
- `update/titanium-155.0.8059.79` — Titanium version update history.

Branch existence is not equivalent to inclusion in the current stable/main state.

## Documentation architecture

The four root documents form the project control plane:

- `PROJECT_STATUS.md` — current changing state and blockers.
- `RULES.md` — stable operating rules and source hierarchy.
- `ARCHITECTURE.md` — technical/repository boundaries.
- `DECISIONS.md` — append-only material decision log.

Notion provides the human planning/history layer. ChatGPT Project Sources provide a compact shared entry point across project chats. Neither should supersede live GitHub state.
## IdeaPad recovery boundary (2026-10-22 proposal)

The manual Versanium Build workflow has an opt-in resume_ideapad mode solely for the preserved Run #5 arm64 Test tree. The controller lives in `$GITHUB_WORKSPACE/versanium-recovery-control`; the original `$GITHUB_WORKSPACE/chromium` and depot_tools stay at their original absolute paths. Only the controller directory is cleaned by checkout. A shared workflow concurrency group and a recovery flock protect against overlapping current jobs; they cannot protect against manually launched processes or old workflow revisions.

Recovery does not fetch Chromium, sync dependencies, run hooks, install packages, regenerate GN, or reapply patches. Ninja/Siso still decides which actions are valid for reuse. The controller validates original repository HEAD, reviewed Chromium/Vanadium ancestry and version, expected patched HEAD, exact generated GN arguments, and required state files. These checks establish the reported prepared-tree provenance, not a full cryptographic attestation of all modified source files. Local source modifications are expected from the original patch pipeline.

Signed output and staging live only under the fresh controller checkout. Signing material uses a private RUNNER_TEMP directory, removed on normal exit and handled termination; force-kill/power loss can leave residue there. No production publishing path is added. Dependencies and toolchain are reused as already provisioned. General persistent source storage outside the checkout remains a later migration, after recovery validation.

## 2026-10-23 proposed next-Test boundaries

The review branch upgrades exact Titanium/Vanadium/Chromium inputs to 156.0.8078.47 with the original ancestry/ref gates retained. Current successful 155 recovery remains historical and cannot supply a new156/candidate APK.

Zoom portable data uses a separate versioned UTF-8 JSON protocol; internal version=1 preferences/profile identifiers remain unchanged. SAF grants per-document access. The import replaces both environment maps after validation/confirmation and an off-thread single-file commit, without re-migration or default/site pruning. A portable display mode maps to the current local display ID; no foreign IDs are restored. Local per-profile display overrides fall back to previous global overrides. A shared persistence transaction flag protects recreated regular handles; private stores are excluded. Screen generation/provider I/O still needs Android validation.

YouTube candidates are separate opt-in flags for standard PiP suppression and background document visibility. HTTPS main-document host allowlist, normal-profile gating and actual display classification limit execution. No play()/autoplay relaxation is added. Existing native PiP/fullscreen gates remain. Pause/visibility diagnostics do not prove a native suspension cause. A weak tab listener updates candidates outside native zoom callbacks, avoiding JNI→zoom→script recursion and strong lifecycle retention.

Fresh IdeaPad source/output uses a unique run-ID child directory, never the retained 155 tree. The same reviewed provider labels/concurrency and manual-only policy remain. Fresh IdeaPad uses an initial six-job cap and 20-hour timeout; cloud paths keep existing defaults. Build provenance includes actual overlays, source commits/patch diff, GN, extension index and toolchain hashes. Real Windows/WSL resource availability remains a local verification prerequisite. See docs/versanium/next-test-156-review.md for experimental limitations and required device tests.

The PR5 follow-up supersedes the original frame-scoped JavaScript CHECK exception. Generic ExecuteJavaScript/CanExecuteJavaScript/WebContentsAndroid::EvaluateJavaScript remain pinned upstream behavior. A dedicated boolean+callback WebContents JNI route runs only a compiled fixed candidate payload, with native flags and live/active/outermost/normal-profile/HTTPS YouTube checks. No script parameter or marker grants permission. Its generated UTF16 header is in the existing Android native target and provenance; the Java owner is already a content JNI source. Actual native body compilation, device behavior and independent security review remain unverified.

Zoom archives preserve every finite double exponent, matching legacy storage; SAF restore explicitly rejects numerical overflow/underflow for the Android font envelope before submitting any replacement. Existing values are never rounded/dropped to force an import through. This differs from the50–300% slider UI and Blink rendering bounds; an exact legacy-value warning distinguishes the saved default from the bounded thumb. The PiP candidate owns only its own reflected attribute change and revokes that ownership on subsequent site mutations; it restores before DeX/option disable or releasing a detached video. Same-document movement remains model-tested only. See the PR5 report for exact artifact pins and the SAF/runner readiness checklist.

### Run9 incremental correction boundary

Run9's real native build exposed the invalid host_piece() accessor. Only host() is present in the fixed GURL header. The patch/model now use host(); the model checks the exact pinned header hash first, without claiming to compile that header. HTTPS/exact-host/profile/frame/native-flag predicates and the fixed-payload route remain intact.

A separate156-only manual controller can validate the preserved Run9 repository7d9102f, authenticated-by-API-digest original provenance ZIP, pin/ancestry, exact old recorder/inputs/source diff, GN args/version, depot commit, clang/clang++ and output state. It records before/after hashes plus a separate source backup, makes only the three-call correction, and rechecks applied state before any separately authorized object compile. It does not touch old155 recovery, Workflow/signing, GN generation, dependency sync or existing outputs. Existing Ninja files are read as bytes to require a single definition of the log-confirmed obj/content/browser/browser/render_frame_host_impl.o, rule cxx and exact explicit source; different toolchain prefixes remain distinct and duplicate exact targets reject. No guessed target or all-APK-first retry is used. Current graph/GN-binary hashes cannot retroactively authenticate graph files absent from the original record. Updated host validation/compilation is still pending after the reported read-only parser failure; see the dedicated Run9 report.

### 2026-10-24 — Passive diagnosis boundary

Diagnostics only observes existing PiP controller stages in regular live HTTPS YouTube tabs and live Activity; no fullscreen permission/AppOps/recent-task probing, candidate authorization, JS pause wrapping or script-result callback. Both Java and native candidate entry require a PiP/background candidate flag. Native options force diagnostics=false. Fixed-payload JNI and generic JavaScript restrictions remain. Background/PiP DOM behavior is unchanged. User reports the prior156 manual APK works except diagnosis/PiP issues; the new correction still requires integration/device validation.

### Preserved Run9 diagnostic-update boundary

The APK-completed saved Run9 tree may only be considered for reuse through the new diagnostic-update helper, not by weakening the historical three-accessor helper. The new chain requires original provenance, prior applied evidence, saved post-correction provenance, exact four-file pre/post hashes, unchanged JNI/GN/payload hashes, existing arm64 Test GN/toolchain and byte-parsed saved targets. Its default is external-evidence-only. A future explicit apply may write those four sources while proving output bytes unchanged. Java and both native objects are separate compile gates before any APK target. GN regeneration, sync, patch/build scripts, cleaning and path movement are stop conditions, not recovery actions.

Flag metadata is authenticated as a derivation, not an observed-hash exception: fixed Chromium HEAD bytes → the exact 11-name patch.sh expiry loop in order → the exact three candidate entries and formatting. HEAD, intermediate and final hashes are pinned, and the saved final bytes must equal the reproduced bytes. This corrects the earlier candidate-only fixture while retaining fail-closed behavior.

Video fullscreen rendering now proposes a scoped exponent0 override in GetPendingZoomLevel after upstream temporary zoom priority. It requires native DOM fullscreen and a media fullscreen-player ID, leaving F11-only and stored environment/site values intact. Media fullscreen notifications refresh both entry and exit; current environment values are looked up on exit rather than replaying a cached value. Getter/setter/JNI temporary paths cannot enter environment persistence. Full native and device layout validation remains pending.

PiP diagnosis additionally observes existing decision/dismiss branches and persistent-video call boundaries without duplicate permission/eligibility queries. stop_suspend remains pre-call; stop_suspend_called follows actual invocation. No exit/stop policy changes are made. Entry callbacks, app session activity, fullscreen observers, Activity stopping and actual MediaSession suspension are distinct evidence boundaries. Video zoom and PiP remain separate candidates with an unverified layout interaction.

Configuration A transaction is independent of previous apply controllers. Its inputs are the user-validated diagnostic applied record and after-apk provenance, plus exact b341 installed/A40-file manifest. It reconstructs A Java from fixed HEAD and pinned patch selection, writes only that file after external backup/intent/full output inventory, and records a new source-diff provenance. Verify is pre-compilation-only; generated output changes after real builds require a new after-build provenance comparison. No B path is exposed.

Origin diagnostic candidate adds fixed logging calls inside FullscreenHtmlApiHandlerBase's existing request/dispatch branches, routed via the existing PiP controller with same-tab/live/normal-profile/YouTube checks. Both classes are existing chrome_java sources. Conditions, getter counts and exit policy remain unchanged. A actual logs establish move/suspend execution but not the request origin. Old apply paths are not valid for this expanded two-file selection; B remains separately deferred.

AOrigin has a separate41-file manifest and transaction controller. It reuses only immutable utility functions of the A helper, not its validation/apply conditions, and requires the actual completed A record plus after-apk provenance. Two fixed-source-reproduced Java files can be written only after external backup/intent/full output snapshot. AOrigin41, other source/tool/output and updated provenance are verified afterward; partial failure is retained for review. No B path exists in this controller.

Native→content diagnostic host preparation is isolated in prepare_content_diagnostic.py
and content_diagnostic_graph.py. Product415/old helpers/manifests remain immutable.
Signed source/provenance and actual graph are linked by new external evidence,
not edits to old signature/controller records. Source apply, GN, compilation and
signing are separate gates; saved NullAway flag/actions must be proven. See
docs/versanium/content-diagnostic-host-preparation.md.

Isolated NullAway validation is a separate verification-only output using the
SAME reviewed candidate source, never Default output artifacts or APK/signing.
Source-only apply/verify precedes candidate analysis; separate receipt binds full
source coverage, processor/tool/args/graph/actions and actual successful execution.
Default's disabled ErrorProne gate is preserved as historical fact, not auto-cleared.
See docs/versanium/nullaway-isolated-output-plan.md.

Processor acquisition evidence belongs to gclient's actual management root and
client revision, not presumed package-local .cipd files. Separate requested DEPS
pin, observed jar bytes/version and recorded installed instance/file manifests.
Original7b60873 apply receipt remains bound to that controller for verification;
docs-only review compatibility is separate evidence, not a record rewrite.

CIPD collection separates inventory-bearing apply receipt parsing from small
package metadata: bounded file size, MemAvailable heuristic, schema/hash checks;
only needed fields retained for collection. This does not replace original58-input
helper verification or change on-disk receipts. See cipd-collector-large-record-review.md.
