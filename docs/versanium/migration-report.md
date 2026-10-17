# Versanium migration handoff — 2026-10-18 JST

## Status: synchronization complete; branding branch prepared; rename and original assets blocked

No Actions, build.sh, full Chromium build, production release, or new tag was executed/created.
The inline logo is visible in chat but its original PNG bytes are not available in this workspace.
No generated substitute or hand-traced recreation was used. Actual launcher, repository, social-preview,
fastlane icon/featureGraphic assets therefore remain pending; only their conversion pipeline was prepared.
The build preflight deliberately refuses to build until the original master and complete digest-checked
asset set are present. This is not a completed or device-validated branding migration.

## Repository synchronization

- Previous Primary main: `a70d4abc9fae4277e4b14e5441ace83d9e3e8d7e`.
- Previous Lab main: `29b65f4dad114ce52f6892abe288ea6bd1e223b0`.
- Lab F11 branch: `16d790f05514b483ab27d0a60e5dc15e1a9a6caa`, including the latest certificate-check changes.
- Lab zoom: `469469769d5b02ad9a974b6c96ac91199c77ab23` (device-verified by user).
- Lab version update: `2111f749c735680c91d05eb51dcaf0e749988f38`.
- Lab PiP diagnostics: `33a7f9b3d9e5d72e8df27920d6f99523ace2d963` (separate experimental branch).

Started migration/versanium at Primary main, fast-forwarded Lab main, then made history-preserving
merges of the stable update and latest F11 certificate diagnostics. No conflicts.
Synchronization checkpoint: **`6755ccfd5d5c8a5e8fa3620be6da9ccd4a399aa7`**.
PiP diagnostics are preserved as a separate branch, not silently made part of stable branding.
No history squash, force push, tag deletion, or submodule advancement was used.
GitHub PR/settings enumeration is unavailable through the blocked API; the report covers fetched Git refs,
not a claim to have copied PR discussions or inaccessible GitHub settings.

Operational handoff: both main branches use the stable synchronization checkpoint. The branding work
is pushed as migration/versanium to both repositories, with the same SHA. Branding is not advanced to
main while the actual master assets and rename access are missing. Existing feature histories remain.
Primary received the Lab F11, zoom, update, and PiP branch heads by normal fast-forward/new-ref pushes.
All six corresponding remote branch tips (including main and migration/versanium) were compared and match.
Local default pushes and this migration branch track the Primary remote; explicit backup pushes mirror the same commits.
Existing tags are left unchanged; no new release tag is pushed during migration.

## Repository names and metadata

Actual repositories currently remain:

- https://github.com/Nvoid911/android-titanium-browser
- https://github.com/Nvoid911-Lab/android-titanium-browser

Requested final names (NOT completed):

- Primary/source of truth: https://github.com/Nvoid911/Versanium
- Secondary/backup build: https://github.com/Nvoid911-Lab/Versanium

`gh api repos/Nvoid911-Lab/android-titanium-browser` returns Forbidden. The environment's custom
allowlist was empty and its presets do not contain api.github.com. An additive configuration draft
for **api.github.com** was saved; it requires environment-settings review/save and Publish before
runtime access can be retested. Git operations work; GitHub rename/admin permission is not yet verified.
No Secrets or signing bindings were read, copied, replaced, or created.

`tools/versanium/github_migration.py` defaults to a read-only local plan. Its --apply path requires:
original verified assets; a reviewed branded commit on both main branches; working GitHub API access.
It reads both states first, renames in place, sets the requested description, unions existing topics
with the requested topics, and verifies results. It does not alter default branches, visibility,
Secrets, signing, releases, or tags. Existing topics are not replaced without inspection.
Description/topics are **prepared, not applied**. GitHub social-preview upload is also pending.

After completion, develop on Primary. Mirror exact reviewed Primary refs to Secondary with ordinary
fast-forward pushes; stop on divergence, never force. Secondary's formal-release step is restricted
by repository identity to Primary and is also gated by explicit approval. Both workflows stay manual.

## Changed files and classification

The complete file lists are in [changed-files.tsv](changed-files.tsv), separated into synchronization
and branding changes. [titanium-occurrences.tsv](titanium-occurrences.tsv) classifies every remaining
tracked text match by file, line, and column. This is a repository-source audit, not an APK string dump.
The inventory excludes the generated handoff/audit files themselves to avoid self-referential rows.

A — current-app branding changed/prepared:

- README is exactly the supplied Versanium text, not a renamed Titanium README.
- Issue form targets Versanium and asks device, Android, version, environment, and description.
  Only the Versanium duplicate check is required; no upstream triage is imposed on users.
- fastlane has a new Versanium description preserving supported extension/WebRTC features.
- Workflow display name, artifact/APK names, future release title/body use Versanium.
- Certificate diagnostic console heading uses Versanium; its key/certificate logic is unchanged.
- F11 app label becomes **Versanium**, with the exact same package constant.
- Generated channel app/widget labels and resource message/translation text nodes use Versanium.
  Resource IDs, attributes, comments and paths are not globally replaced. Japanese adjacent text
  is handled without relying on Unicode word boundaries.
- Product FULLNAME/SHORTNAME are Versanium for current-app/About branding. Company, copyright,
  installer identity and bundle identifiers are retained. Resource elements containing legal text,
  external Titanium Extension or upstream links are conservatively retained.
- New icon installation is implemented but not executed for the actual logo. Original artwork
  must be supplied, converted, visually reviewed, and committed before test building.

B — intentionally retained:

- Titanium Browser for Android attribution and jqssun upstream URLs.
- Actual Titanium Extension for Android name and link. .gclient fetches that real upstream CRX;
  no fictitious Versanium Extension was introduced.
- Existing historical build/review/PiP records and their original repository/run references.
  Old own-repository URLs in those historical records are provenance, not active build endpoints;
  GitHub's in-place rename normally preserves redirects. Upstream URLs were not renamed.
- Existing LICENSE and source copyright notices. The new resource transformation leaves comments
  and legal text untouched. The inherited Vanadium→Titanium internal patch process is retained;
  this is not a claim to have audited all generated third-party notices in a built APK.

C — intentionally retained:

- titanium/, res_titanium_base/, package/namespace names, TitaniumConfParser and build hooks.
- io.github.nvoid911.titanium.f11test and its manifest_package-derived authorities/permissions.
- Zoom preferences, storage keys, profile-path identity, migration marker and resource identifiers.
- Old icon-generation files remain as unused internal/historical files; the active old tint/recolor
  calls are removed. No broad Titanium/titanium replacement across repository sources was performed.

## Android identity, signing, upstream

**package/applicationId changed: NO.**
The test path remains io.github.nvoid911.titanium.f11test. The existing normal-build args retain
io.github.jqssun.helium; this migration does not silently unify the two identities.
Manifest authorities, custom permissions, shared-UID rejection and task-affinity validation remain.

**signing configuration changed: NO.**
common.sh, sign_apk/sign_aab, existing Secrets names, certificate checks and expected digest are preserved.
Only a console heading changed in the certificate diagnostic inherited from the latest Lab commit.
No keystore was generated. Primary's actual Secret availability cannot be checked while API access
is blocked; values are neither needed nor requested in chat. In-place rename retains repository IDs.

**LICENSE preserved; upstream attribution preserved.**
.gitmodules and the Vanadium reference remain unchanged from the stable synchronization checkpoint:
8a06a43a04074ab26fa4dc8f8aba915285d56839. Chromium stays 155.0.8059.79 /
a49e2e3d4addfd84e765b52afe230bedb81096db. Fixed-input checks, F11, zoom, async persistence,
lifecycle/reentry protections and native patches are retained. No PiP behavior change was added.

## APK / Actions handoff

- Workflow: **Versanium Build**; workflow_dispatch only.
- Runner default: blacksmith-8vcpu-ubuntu-2404, unchanged.
- Default: test-only arm64, existing F11 identity.
- Artifact: **Versanium-Test**, retention 7 days.
- Exact expected test filename: **Versanium-155.0.8059.79_Test.apk**.
- Exact future production filename: **Versanium-155.0.8059.79_arm64-v8a.apk**.
- Future tag/title: v155.0.8059.79 / Versanium 155.0.8059.79.

The production approval flag is a checked-in false. Non-test dispatch fails preflight before building;
Publish/Attest additionally require non-test + explicit approval + Nvoid911/Versanium. Test artifact
paths never reach Release publish. Production publishing remains unapproved and was not attempted.
The old workflow's automatic latest-Vanadium update/commit/push step is removed so these branding builds
stay on the reviewed source pins. Internal normal-build armeabi/AAB generation/signing is retained,
but future public Release stages only the arm64 APK. That normal build path is not newly validated.

## Validation and remaining work

Executed:

- 10 local migration tests: synthetic image format/densities, source-byte preservation, resource
  references, complete asset hashes and tamper rejection, missing-asset rejection, text-node/Japanese
  branding, retained upstream/legal text, identity template, byte-preserving APK filename staging,
  workflow gates and inline shell. These are not an actual icon review, signed APK, or GitHub run.
- Actual pinned Vanadium channel resource and Chromium BRANDING fields: app/widget names changed;
  existing comments/company/copyright/internal identity retained.
- AAPT2 compile of synthetic-fixture generated icon resources: PASS. Not resource link or actual-logo validation.
- actionlint, YAML parsing, shell syntax, git diff --check.
- Existing zoom Policy 481 assertions, Bridge 31 assertions, Persistence 13 checks; revision gate
  5 metadata-model cases. Bridge Android/JNI are doubles, not renderer/device verification.
- Git comparisons: LICENSE, .gitmodules, args.gn, build.sh, common.sh, zoom Java/native patch and
  signing behavior unchanged by branding, except the explicitly documented label/console changes.

Not executed/confirmed:

- Original-logo conversion and visual checks; real adaptive/monochrome rendering; social-preview upload.
- Full application of all locale resource changes and resource link/GN/Chromium compile.
- APK installation/update, actual Settings/About/permission/notification/share labels, extension UI,
  old screenshots, Samsung DeX keyboard/mouse/window behavior and persisted-data survival.
- GitHub rename, Description/topics, PR/settings enumeration, Secret presence, official Release.

Next prerequisites:

1. Supply the original logo as an actual PNG file attachment. Inline visual context is insufficient
   for byte-preserving conversion; no redesign or generated substitute will be used.
2. Apply/Publish the saved api.github.com network addition in environment settings, then retest access.
   Admin authorization may still need confirmation through the platform; do not paste tokens/keys.
3. Convert/review/commit actual assets; run resource integration checks; advance the fully reviewed
   branding commit to both main branches; execute guarded in-place rename/metadata and verify URLs.
4. Only when build capacity is available, run one manual test build, obtain the Test artifact and
   stop for Galaxy S23/Android 16/One UI 8.5 smartphone and DeX testing. Formal Release and new tags
   remain blocked until explicit user approval.
