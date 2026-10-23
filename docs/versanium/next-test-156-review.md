# Next Test 156 review — 2026-10-23 JST

Status: **candidates implemented; limited local validation; NOT built or device-verified**. Review target is migration/versanium through a feature PR. No Actions dispatch/rerun, production Release/tag or main merge is authorized/performed.

## Source hierarchy and baseline

Read live Primary `Nvoid911-Lab/Versanium` integration `d64b78be40b15dee889c24c67ba689777e090ca7`, PROJECT_STATUS/RULES/ARCHITECTURE/DECISIONS, historical migration and PiP investigations and recovery code. Secondary is `Nvoid911/Versanium`. Its prior integration `8a9c9e9ab37c88c0eedab2f151f96907eabc2583` is an ancestor of Primary, not independent development. Main refs remain out of scope. No accessible Notion/Project Sources tool or local snapshot was available; their contents/agreements have not been invented or marked refreshed.

Run https://github.com/Nvoid911-Lab/Versanium/actions/runs/39765620887 is completed/success. API jobs confirm `Resume preserved IdeaPad Test` and upload succeeded, while normal preflight/Build/staging were skipped. Run controller HEAD is d64b78b; check_resume.py requires original repository `6e7517e6de89e5a1230cebf906470795112466a3`, old Chromium/Vanadium inputs and patched HEAD prefix 8b1224debc. It does not fetch, patch or regenerate GN. Original 6e7517e contains investigation documentation, not the separate diagnostic apply step. `feature/youtube-pip` has diagnostics, not a playback fix. APK bytes were not inspected. Thus this successful 155 APK confirmed persistence of the original problem, NOT failure of an included independent repair candidate.

User device evidence: Galaxy S23 / Android16 / One UI8.5; F11 works; smartphone YouTube home/PiP and tab background playback fail; DeX works; separate zoom settings are in use. New import/export and candidates below have no device result yet.

## Exact upstream inputs

Latest official stable rechecked via release API: **v156.0.8078.47**, published 2026-10-22.

- Titanium release commit: `a3e4b86339a8db237d95d8e8e78248c8f6a1df68` (tag resolved to commit, merged retaining history).
- Vanadium gitlink: `2ae4335402eabcc6e025f3400185fe25094d8521`, exact tag `156.0.8078.47.0`.
- Chromium: `156.0.8078.47`, tag SHA `1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775` (git ls-remote and raw source at exact SHA).
- Since the prior adopted Titanium release 155.0.8059.79, the upstream repository delta is the Vanadium gitlink. No upstream merge conflict occurred. Chromium 156's host zoom UI-thread checks became CHECK_CURRENTLY_ON(...NotFatalUntil::M160); the overlay context was updated to preserve those checks, not restore old DCHECKs.
- Revision validation now requires all new exact refs/version and upstream ancestry. Old saved 155 trees fail; no gate was removed or relaxed.

## PiP: facts, hypotheses, implemented scope

Issue #335 rechecked: open, comments=0. Existing AutoPictureInPictureAndroid and capture feature overrides are already present. Existing patch.sh also disables IsBackgroundMediaSuspendEnabled via its renderer policy edit. These inherited broad policies are retained, not reintroduced as a new fix. They do not establish that YouTube permits PiP or that its page scripts will keep playing.

156's real FullscreenVideoPictureInPictureController still checks active effectively-fullscreen video, video PiP allowance, device PiP feature, Activity state and recent tasks before requesting Android PiP. F11 is not video fullscreen. An inline video can still fail the fullscreen gate. The failure condition on this device is unproven; flags alone do not prove resolution.

Separate chrome://flags experiments (default disabled; enable individually and relaunch):

1. `versanium-youtube-pip-candidate`: normal top-level HTTPS youtube.com/www.youtube.com/m.youtube.com only; on mobile, remove the standard video's disablePictureInPicture suppression. Does not fake fullscreen, bypass Android permission or request autoplay. Repeated site reassertions are bounded to eight adjustments per video. Inline PiP is intentionally NOT claimed solved.
2. `versanium-youtube-background-candidate`: same site/main-document/private restrictions; on mobile only, provide visible/hidden getters and suppress visibilitychange propagation. No play() call, no resume loop, no autoplay/user-activation bypass. Unknown DOM descriptors retain baseline behavior. Changing to DeX turns the visibility override off through the actual Activity display bridge (independent of manual zoom classification); other sites are untouched.
3. `versanium-youtube-diagnostics`: controller decision bools, AppOps PiP mode, recent-task state and API enter true/false/exception; tab load/show/hide/environment stages with fixed booleans for applied candidate, paused/visibility observations. Raw script result strings are never logged. Private tabs are excluded. No URLs, titles, IDs, Cookie or config dump.

Background visibility masking can change YouTube's analytics, quality/resource decisions, battery use and any hidden-page housekeeping. Some page capture listeners may have registered before this load-complete injection; they can still run. Native MediaSession/renderer suspension may also remain a cause. The opt-in diagnostic also delegates the original video.pause method unchanged while noting method calls and user-activation state. A captured method call is evidence of a JS path, including possible user handlers; absence does NOT exclude earlier captured references or prove native suspension. No stack is recorded. More invasive document-start or native/MediaSession work requires evidence; this candidate does not claim those paths are fixed. PiP failure recovery remains Chromium's existing path, unchanged.

Brave source was re-fetched at fixed `46cfe58223924f363192475396dcb196ec29423d` (YouTubeScriptInjectorTabHelper and BraveFullscreenVideoPictureInPictureController). Its main-document controls and asynchronous fullscreen/Activity integration support the hypotheses but are substantially broader. Its files are MPL-2.0; copying them would require preserved notices and covered-source availability. No Brave implementation was copied; these small independent experiments use standard document/video APIs. Existing GPLv2/BSD/upstream notices remain.

## Zoom backup specification

Accessibility adds English/Japanese Export/Import preferences through SAF CreateDocument/OpenDocument. No storage permission was added. UTF-8 JSON format `versanium-environment-zoom`, version=1, unit=`log-base-1.2-exponent`; MOBILE/DEX each contain absolute default and explicit site map. Exponents round-trip as doubles; percent is preview/UI only. A saved value equal to a default stays explicit.

Limit 1MiB, 10,000 combined sites, bounded nonempty host/spec strings; exact schema and numeric type, finite/ranged values (50–300%), duplicate keys, unsupported versions/units, malformed/trailing JSON/UTF-8 and unknown fields are rejected. Legacy storage migration/version=1 and profile key remain unchanged. Old profile migration behavior remains covered by existing policy tests; unrelated export formats are not silently migrated.

Confirmation shows both defaults, total site overrides and display mode. Confirmation replaces both maps, not merges. Display IDs never leave the device: the portable mode maps to the screen used at confirmation; other existing local display overrides remain. This version exports the mode of the exporting screen only, not every display override on the old device; use the desired screen explicitly for that portable mode. New profile-scoped display keys fall back to the existing global display overrides, preserving previous choices.

Import waits for a quiescent existing persistence queue (otherwise safely fails and asks retry), writes the whole snapshot off UI thread with the existing single-file commit, and publishes policy/UI success only on commit success. A failed commit also restores the old SharedPreferences cache/snapshot before publishing failure; active policy remains unchanged. A fixed boolean log reports whether the prior snapshot could also be durably restored; persistent storage failure cannot be represented as a confirmed successful save. Regular changes are blocked during replacement; recreated regular profile handles sharing the persistence receive the committed snapshot. Private stores cannot import/export or be updated by regular import. Cancellation/validation failure never submit a replacement. SAF UI, provider-specific I/O failures and real Android restart/lifecycle still require device verification.

## Fresh build and provenance

This revision rejects `resume_ideapad=true`. The successful old 155 tree and output are not cleaned, moved, reset or repatched. For a new IdeaPad build, checkout/source/output live under a unique `versanium-next-test-<run_id>` child. A pre-check rejects existing directory/symlink; reuse/rerun of that same workspace is not a cache strategy. Normal cloud builds retain their reviewed checkout path.

After fresh pinned fetch/hooks/patches and GN, build-provenance.json records repository and patched Chromium commits, exact upstream pins, actual Java/resource overlays, patch inputs, GN hash, extension index, DEPS and clang binary hash. A separate artifact preserves it. Existing key generation/signing and Test identity stay unchanged. New IdeaPad builds retain the 20-hour IdeaPad timeout and compiles use -j6 initially, with validation of the numeric limit; this is a conservative tuning candidate, not an ETA or proof of current available memory.

Current Windows account, WSL distribution, physical memory/free space and duplicate runner state cannot be inspected from this cloud container. Only the run's actual `versanium-ideapad` label was verified. `tools/versanium/inspect_build_host.sh` is a read-only local inspection helper; it starts/stops no runner. Before authorizing a build, verify host/service ownership, disk capacity for a second full tree, swap pressure and no duplicate listeners/compilers. Current cloud has about 30GiB free; a full Chromium checkout/build was not attempted. Existing successful artifacts remain untouched.

## Validation and limits

Confirmed locally:

- migration tests 13, recovery/fresh-workspace checks 8, revision rejection cases 5 PASS.
- JVM policy 481 assertions (real file roundtrip), bridge 41 assertions (Android/JNI/renderer mocked), persistence 18 (queue/failure/replace), backup 25 (real Android JsonReader/Writer, no SAF UI) PASS.
- YouTube DOM-model checks 22 PASS: host/frame scope, independent flags, manual stop remains stopped, mobile→DeX fallback. This is not an actual YouTube/Chromium test.
- Exact-source selected integration: real 156 files + selected Vanadium hunks + zoom/SAF source/resource copies + F11 anchors + existing renderer policy + PiP hooks/flags PASS. Changed-anchor rejection still fails before writes as intended.
- Actual pinned jni_zero generated HostZoomMapImpl headers/source jar. No C++ body/toolchain compile was performed.
- Limited content-Java type compile against actual Android14/Robolectric API classes and declaration-only projections from pinned Chromium PASS. These projections do NOT establish full Chromium/NullAway type safety; SAF preference UI is excluded.
- actionlint v1.7.7, YAML/inline shell checks, bash -n, git diff --check PASS.
- Real icon digest/density/safe-zone checks, AAPT2 compile of zoom strings and actual icon resources PASS. SeekBar explicit layout/View-ID wiring remains unchanged; no real screen inflation was executed.

Blockers before calling this build-ready:

- Pinned AndroidX binary retrieval at chrome-infra-packages.appspot.com returned proxy CONNECT HTTP403; no credential or network bypass was attempted. Actual SAF screen type/inflation validation is pending. Metadata/source/API correspondence alone is not full UI validation.
- No GN generation, full native compilation, APK link/install or real media/session testing. Features are review candidates, not confirmed fixes.
- Review the inline-video limitation and the background candidate's scope/impact, then gather minimal diagnostics to localize the remaining native-vs-site stop path.
- Windows/WSL host and available capacity still need local evidence. Do not infer them from the prior run or from cloud disk measurements.

## Minimal private diagnostic and device matrix

After review and a user-initiated Test build only, enable diagnostics and compare each candidate separately. In an existing rish shell (`whoami` returns shell), use:

```sh
logcat -v brief -T 1 -s VersaniumPiP:I VersaniumYT:I '*:S' > /sdcard/Download/Versanium-pip-diagnostic.log
```

While collecting, reproduce one controlled case, return to shell and press Ctrl+C. Share only the two named tags for that case plus your case label, with no broad logcat/dumpsys or page contents. Do not capture URLs/titles/accounts. No appOps/permission dump is needed; diagnostic mode is a small integer, and Android PiP permission is checked separately in Settings.

| Case | Smartphone | DeX | Current status |
|---|---|---|---|
| YouTube home→PiP, inline video | compare baseline/PiP candidate | regression compare | new candidate unverified; fullscreen gate remains |
| YouTube home→PiP, video fullscreen | compare attributes/permission/decision/API | regression compare | unverified |
| F11 fullscreen without video fullscreen | distinguish from video fullscreen | keyboard/mouse | baseline F11 device-verified; new156 unverified |
| YouTube tab switch | background flag off/on | regression compare | unverified |
| Manual pause then home/tab switch | must remain paused | must remain paused | model passed; device unverified |
| Screen move/recreation/private tabs | no mixed state or diagnostics in private | same | model/bridge partial; device unverified |
| Twitch home/tab/PiP | unchanged | unchanged | domain model passed; device unverified |
| Zoom export/import/restart | both defaults/maps preserved | same; mode maps current screen only | core tests passed; SAF/device unverified |
| Cancel/invalid file/I/O failure | no partial replacement/success toast | same | core failures tested; real provider UI unverified |

## Branding and durable context

Primary/Secondary metadata both have the expected description/topics and default branch main. Primary main still shows old Titanium README; a separate documentation-only main PR is prepared, never directly merged. Migration README now describes unofficial lineage, Lab source of truth, Test artifacts and unbuilt 156 status without claiming a production Release exists. Issue/fastlane project links point to Lab. LICENSE, upstream URLs, Titanium Extension for Android and internal namespaces/keys/signing/identities are retained. Real approved icons remain unchanged. Inherited fastlane phoneScreenshots are historical illustrations (sample1 shows a LineageOS extension view), not current Galaxy S23/Versanium evidence; actual device captures remain needed before store/production promotion.

PROJECT_STATUS/ARCHITECTURE/DECISIONS are updated on this review branch with success-vs-proposal distinctions. Notion and Project Sources are unmodified because unavailable. Versanium_Project_Context.md is stale for the successful recovery and proposed next milestone; regenerate/replace it only after reviewed integration and Secondary synchronization settle, following RULES rather than presenting an unmerged feature branch as settled technical truth.

## Review delivery and synchronization

- Implementation Draft PR: https://github.com/Nvoid911-Lab/Versanium/pull/5 → migration/versanium.
- Default-main presentation Draft PR: https://github.com/Nvoid911-Lab/Versanium/pull/6 → main (documentation/store metadata only; unmerged).
- Existing reviewed integration d64b78be40b15dee889c24c67ba689777e090ca7 was fast-forwarded from Lab to personal Secondary after ancestry verification. Both migration branches remain at d64b78b until PR review; no prototype was directly merged.
- The next-test feature branch is mirrored without force to Secondary, so the same reviewed commits can be compared there. Its exact final SHA is reported in the PR and delivery message.
- No GitHub Actions run/dispatch/rerun, Release/tag, main merge or runner operation was performed. Current default-main content stays unchanged until the user reviews and merges its separate PR.
