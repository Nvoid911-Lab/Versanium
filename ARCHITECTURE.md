# Versanium Architecture

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
