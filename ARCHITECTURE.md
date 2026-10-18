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