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
2. `versanium-youtube-background-candidate`: same site/main-document/private restrictions; on mobile only while a video is already playing, provide visible/hidden getters and suppress visibilitychange propagation. Paused/ended video returns the real visibility and is never resumed. No play() call, no resume loop, no autoplay/user-activation bypass. Unknown DOM descriptors retain baseline behavior. Changing to DeX turns the visibility override off through the actual Activity display bridge (independent of manual zoom classification); other sites are untouched.
3. `versanium-youtube-diagnostics`: controller decision bools, AppOps PiP mode, recent-task state and API enter true/false/exception; tab load/show/hide/environment stages with fixed booleans for applied candidate, paused/visibility observations. Raw script result strings are never logged. Private tabs are excluded. No URLs, titles, IDs, Cookie or config dump.

Background visibility masking can change YouTube's analytics, quality/resource decisions, battery use and any hidden-page housekeeping. Some page capture listeners may have registered before this load-complete injection; they can still run. Native MediaSession/renderer suspension may also remain a cause. The opt-in diagnostic also delegates the original video.pause method unchanged while noting method calls and user-activation state. A captured method call is evidence of a JS path, including possible user handlers; absence does NOT exclude earlier captured references or prove native suspension. No stack is recorded. More invasive document-start or native/MediaSession work requires evidence; this candidate does not claim those paths are fixed. PiP failure recovery remains Chromium's existing path, unchanged.

Brave source was re-fetched at fixed `46cfe58223924f363192475396dcb196ec29423d` (YouTubeScriptInjectorTabHelper and BraveFullscreenVideoPictureInPictureController). Its main-document controls and asynchronous fullscreen/Activity integration support the hypotheses but are substantially broader. Its files are MPL-2.0; copying them would require preserved notices and covered-source availability. No Brave implementation was copied; these small independent experiments use standard document/video APIs. Existing GPLv2/BSD/upstream notices remain.

### Dedicated native execution boundary (supersedes the original frame-scoped exception)

The original 752eda5 review head permitted generic ExecuteJavaScript on eligible frames, including with diagnostics alone. That exception is removed. ExecuteJavaScript, CanExecuteJavaScript and WebContentsAndroid::EvaluateJavaScript bodies now match pristine pinned156 byte-for-byte; ExecuteJavaScriptMethod is untouched. The early marker check is also removed. A marker is neither authentication nor a permission mechanism.

The only new route is TabImpl.applyVersaniumYoutubeCandidate → WebContents.applyVersaniumYoutubeCandidate(boolean mobile, callback) → WebContentsImpl @NativeMethods → WebContentsAndroid::ApplyVersaniumYoutubeCandidate → RenderFrameHostImpl::ExecuteVersaniumYoutubeCandidate. Neither Java/JNI nor the native executor accepts script text. A generated, UTF16 fixed payload from the reviewed candidate.js is included by the Android RFH target, listed in content/browser/BUILD.gn, and hashed in provenance. Native code constructs only four boolean options; experiment switches are read natively, not taken from Java. Existing WebContentsImpl content_java / content_jni_headers sources already contain the modified Java file, so no additional JNI target or dependency cycle is introduced. The interface's default no-op keeps other implementations/test fakes compatible; the real WebContentsImpl overrides it.

Both entry and executor check a live, active, outermost normal-profile HTTPS youtube.com/www.youtube.com/m.youtube.com frame, initialized command line, non-shutdown profile and at least one explicit experiment flag. No frame initialization, process-wide JS permission, test API, user activation, autoplay exemption or arbitrary script parameter is used. Diagnostics alone runs only this same fixed diagnostic payload; it does not grant generic callers access. A detached/navigated/private/disabled request is dropped without invoking the generic CHECK. The script independently checks current top-document/host and does not play or force fullscreen. UI-thread execution and frame-specific IPC retain Chromium navigation semantics; actual navigation races/device behavior remain unverified.

JNI was generated with the pinned jni_zero implementation: the generated method passes long native pointer, bool mobile, and typed JavaScriptCallback JavaRef, matching the existing object's callback conversion pattern. No new JNI script string exists. Actual Chromium/Android-toolchain native body compilation and independent security review remain required. Seventeen predicate MODEL cases, actual generated-header output and source comparisons do NOT establish security correctness or full ABI/link correctness.

### PiP attribute ownership on a same-document screen move

While playing on mobile, the candidate records the exact original reflected attribute before clearing it. On DeX or PiP-option disable it restores that exact value ONLY if the element still has the candidate's false/absent result and no intervening attribute mutation was observed. MutationObserver records, including pending true→false site writes before callback delivery, revoke ownership. Own writes drain only their own records. A later site-owned value is never restored from an older snapshot. Still-owned removed nodes are restored before their ownership references are released; attempt counts remain bounded per video/document. Missing observer or an element-specific property override causes safe no-op. A no-op site assignment that produces no DOM mutation expresses no observable value change; the candidate cannot infer that site's intention.

The same document mobile→DeX→mobile, site-owned true→false/changed attribute, option disable and detached element paths pass DOM-model tests. Actual video attributes, MutationObserver timing, PiP eligibility and Samsung Activity/display movement still require device comparison. This is a reversible suppression-attribute experiment, not an established repair for the original155 failure.

## Zoom backup specification

Accessibility adds English/Japanese Export/Import preferences through SAF CreateDocument/OpenDocument. No storage permission was added. UTF-8 JSON format `versanium-environment-zoom`, version=1, unit=`log-base-1.2-exponent`; MOBILE/DEX each contain absolute default and explicit site map. Exponents round-trip as doubles; confirmation and site lists use exact 1.2^exponent notation, avoiding integer-percent overflow. A saved value equal to a default stays explicit.

Limit 1MiB, 10,000 combined sites, bounded nonempty host/spec strings; exact schema and numeric type, finite exponent values (the archive domain matches Policy storage, not the 50–300% slider), duplicate keys, unsupported versions/units, malformed/trailing JSON/UTF-8 and unknown fields are rejected. Legacy storage migration/version=1 and profile key remain unchanged. Old profile migration behavior remains covered by existing policy tests; unrelated export formats are not silently migrated.

Confirmation shows both defaults, total site overrides and display mode. Confirmation replaces both maps, not merges. Display IDs never leave the device: the portable mode maps to the screen used at confirmation; other existing local display overrides remain. This version exports the mode of the exporting screen only, not every display override on the old device; use the desired screen explicitly for that portable mode. New profile-scoped display keys fall back to the existing global display overrides, preserving previous choices.

Legacy compatibility: archive encode/decode accepts every finite IEEE754 double, including values outside50–300%, subnormal exponents, signed zero and extreme finite values. NaN/infinity, invalid JSON and size/count/schema violations still reject the whole archive. No value is rounded, dropped or silently migrated. The existing storage marker/profile keys/explicit equal-default site values are unchanged. Before SAF restoration, validateForRestore rejects the ENTIRE replacement if pow(1.2,exponent)×2 is non-finite or ×0.85 is below Double.MIN_NORMAL. These are numerical overflow/underflow guards accounting for Chromium's documented Android font envelope; the original file and current settings remain intact. Extreme finite archives are still exportable/readable, even if not safe to apply. No element is selectively removed or clamped to make import pass.

This is archive compatibility and numerical safety, not a guarantee of every requested rendering ratio. Pinned Blink page_zoom.cc documents Android rendering bounds0.425–6.0 and WebViewImpl::ClampZoomLevel applies renderer bounds. Existing legitimate legacy25%,400%,450%/fractional examples are preserved exactly in storage/backup; Blink may constrain actual rendering as before. Confirmation explicitly warns about that. Slider remains50–300%; out-of-range defaults show the exact saved exponent and an explicit preserved-until-edited warning. Only the thumb position is bounded, without changing Policy. Backup tests load a literal old-v1 properties fixture (real storage key/value shape) and the actual pre-v1 migration constructor, then export/import/reopen and compare double bits. They use deterministic legacy examples, NOT a user's S23 settings dump. Android SharedPreferences/SAF/renderer behavior is not established by that JVM fixture.

Import waits for a quiescent existing persistence queue (otherwise safely fails and asks retry), writes the whole snapshot off UI thread with the existing single-file commit, and publishes policy/UI success only on commit success. A failed commit also restores the old SharedPreferences cache/snapshot before publishing failure; active policy remains unchanged. A fixed boolean log reports whether the prior snapshot could also be durably restored; persistent storage failure cannot be represented as a confirmed successful save. Regular changes are blocked during replacement; recreated regular profile handles sharing the persistence receive the committed snapshot. Private stores cannot import/export or be updated by regular import. Cancellation/validation failure never submit a replacement. SAF UI, provider-specific I/O failures and real Android restart/lifecycle still require device verification.

## Fresh build and provenance

This revision rejects `resume_ideapad=true`. The successful old 155 tree and output are not cleaned, moved, reset or repatched. For a new IdeaPad build, checkout/source/output live under a unique `versanium-next-test-<run_id>` child. A pre-check rejects existing directory/symlink; reuse/rerun of that same workspace is not a cache strategy. Normal cloud builds retain their reviewed checkout path.

After fresh pinned fetch/hooks/patches and GN, build-provenance.json records repository and patched Chromium commits, exact upstream pins, actual Java/resource overlays, patch inputs, GN hash, extension index, DEPS, frozen depot_tools commit, GN version and clang binary hash. Depot self-update is disabled after dependency hooks and before GN/compilation. A separate artifact preserves it. Existing key generation/signing and Test identity stay unchanged. New IdeaPad builds retain the 20-hour IdeaPad timeout and compiles use -j6 initially, with validation of the numeric limit; this is a conservative tuning candidate, not an ETA or proof of current available memory.

Current Windows account, WSL distribution, physical memory/free space and duplicate runner state cannot be inspected from this cloud container. Only the run's actual `versanium-ideapad` label was verified. GET /repos/Nvoid911-Lab/Versanium/actions/runners returned GitHub HTTP403 Resource not accessible by integration, so current runner online/busy/duplicate registration state is also unverified; no auth changes or alternate access were attempted. `tools/versanium/inspect_build_host.sh` is a read-only local inspection helper; it starts/stops no runner. Before authorizing a build, verify host/service ownership, disk capacity for a second full tree, swap pressure and no duplicate listeners/compilers. Current cloud has about 30GiB free; a full Chromium checkout/build was not attempted. Existing successful artifacts remain untouched.

## Validation and limits

Confirmed locally:

- migration tests 13, recovery/fresh-workspace checks 8, revision rejection cases 5 PASS.
- JVM policy 481 assertions (real file roundtrip), bridge 41 assertions (Android/JNI/renderer mocked), persistence 18 (queue/failure/replace), backup 67 (real Android JsonReader/Writer, no SAF UI) PASS.
- Native execution scope 17 model cases PASS (actual predicate body, model API objects; not Chromium typing/ABI).
- YouTube DOM-model checks 37 PASS: host/frame scope, independent flags, manual stop remains stopped, mobile→DeX fallback. This is not an actual YouTube/Chromium test.
- Exact-source selected integration: real 156 files + selected Vanadium hunks + zoom/SAF source/resource copies + F11 anchors + existing renderer policy + PiP hooks/flags PASS. Changed-anchor rejection still fails before writes as intended.
- Actual pinned jni_zero generated HostZoomMapImpl and the new WebContentsImpl dedicated route headers/source jars. The generated fixed UTF16 payload header also compiles with host g++, which is not RFH/WebContents body compilation. No C++ body/toolchain compile was performed.
- Limited content-Java type compile against actual Android14/Robolectric API classes and declaration-only projections from pinned Chromium PASS. These projections do NOT establish full Chromium/NullAway type safety; SAF preference UI is excluded.
- actionlint v1.7.7, YAML/inline shell checks, bash -n, git diff --check PASS.
- Real icon digest/density/safe-zone checks, AAPT2 compile of zoom strings and actual icon resources PASS. SeekBar explicit layout/View-ID wiring remains unchanged; no real screen inflation was executed.

Blockers before calling this build-ready:

- 155 and156 use different AndroidX CIPD instance IDs (155 NxGqadT06DkHEQp5MD5TiHG2eSAfSkZ-oJ5vFL1gnzMC; 156 BPpMyM0SWd-E1wUl8rg83DvakkDwYKkwEfy561BXtXkC), so an old cached155 AAR cannot be assumed exact. Pinned AndroidX binary retrieval at chrome-infra-packages.appspot.com returned proxy CONNECT HTTP403; no credential or network bypass was attempted. Actual SAF screen type/inflation validation is pending. Metadata/source/API correspondence alone is not full UI validation.
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

## Reproduction inputs and manual dispatch UI caveat

Local JVM checks used JDK21, ECJ3.40.0 and Android14 `org.robolectric:android-all:14-robolectric-10818077`. Published Maven digests were checked (ECJ SHA1, android-all SHA512). The JSON test jar contains the unchanged android/util/Json*.class, android/util/MalformedJsonException.class and com/android/internal/util/StringPool.class extracted from that actual jar; excluding Android's java.lang shadow classes avoids boot-classpath conflicts. Run:

```
python tools/environment_zoom/tests/run_local_tests.py --ecj /path/to/ecj.jar --android-json /path/to/android-json.jar
python tools/youtube_pip/tests/check_source_integration.py --source-tree /path/to/pristine-pinned-selected-files --output-dir /new/output/path
node tools/youtube_pip/tests/test_candidate.cjs
python tools/versanium/tests/test_migration.py
python tools/versanium/tests/test_resume.py
```

The selected-files checker explicitly lists its extra files in addition to the overlay's patch paths. All input files must come from the exact Chromium SHA above. The checker mutates only a new output directory. Its intentional changed-anchor negative test emits a git-apply error before the positive test passes; that output is not an ignored integration failure.

Current default-main Workflow still exposes legacy `runner` input, whereas the review/migration definition uses `runner_provider` and `resume_ideapad`. PR6 deliberately does not promote Workflow/app code. The actual authenticated GitHub web-form behavior for a selected non-default ref was not verified here. Before any later UI-only dispatch, select the reviewed ref and confirm the correct provider/Test/fresh-mode fields; if they are unavailable, stop and prepare a separate reviewed default-branch dispatch-interface alignment. Do not guess the values or start a main/old-run build to test the form. No dispatch was used to probe this behavior.

## PR5 follow-up: AndroidX, SAF and build authorization checklist

### Exact dependency and HTTP403 evidence

The affected machine is THIS Codex Linux cloud container, not the IdeaPad/Blacksmith/Sengi machine. HEAD to
`https://chrome-infra-packages.appspot.com/dl/chromium/third_party/androidx/+/BPpMyM0SWd-E1wUl8rg83DvakkDwYKkwEfy561BXtXkC`
again returned `CONNECT tunnel failed, response403` (Envoy), before TLS reached CIPD. No artifact/authentication response from CIPD was obtained; this is a cloud egress/proxy failure, not evidence of package permission failure or build-host failure. No network/credential workaround was used. The exact Chromium DEPS condition is checkout_android && non_git_source, package chromium/third_party/androidx, instance BPpMyM0SWd-E1wUl8rg83DvakkDwYKkwEfy561BXtXkC. The old155 instance is different and cannot validate this156 snapshot.

Pinned Chromium committed README.chromium files resolve these precise artifacts (Apache2.0):

| Component | Version | Exact upstream artifact under https://androidx.dev/snapshots/builds/16459101/artifacts/repository/ |
|---|---|---|
| Activity | 1.14.0-SNAPSHOT | androidx/activity/activity/1.14.0-SNAPSHOT/activity-1.14.0-20260928.125204-1.aar |
| Fragment | 1.10.0-SNAPSHOT | androidx/fragment/fragment/1.10.0-SNAPSHOT/fragment-1.10.0-20260928.125204-1.aar |
| Preference | 1.3.0-SNAPSHOT | androidx/preference/preference/1.3.0-SNAPSHOT/preference-1.3.0-20260928.125204-1.aar |

These versions come from exact156 source metadata, not downloaded/inspected AAR bytecode. Source paths: third_party/androidx/committed/libs/androidx_{activity_activity,fragment_fragment,preference_preference}/README.chromium. BUILD.gn maps each to its CIPD libs/.../*.aar and committed .info. The accessibility Java target directly depends on Activity for ActivityResultLauncher/ActivityResultContracts and already depends on Fragment/Preference. There is no SAF storage-permission dependency; framework ContentResolver and Android document-provider UI perform I/O. Exact AAR typing/inflation is still blocked here; substituting a released/stale AAR is not a validation of this snapshot.

### Actual application lifecycle audit (source-level, NOT screen execution)

AccessibilitySettings.onCreatePreferences builds the existing XML and calls EnvironmentZoomSettings.add, which calls Transfer.add once. It registers CreateDocument/OpenDocument in deterministic order during preference creation (Fragment's early onCreate phase), before STARTED. This is the intended ActivityResult registration lifecycle, not a registration inside a click/late callback. Clicks launch only when attached, non-finishing, regular-profile and not replacing; picker absence/security rejection is specifically handled. A null/cancel result never submits a mutation. Result callbacks recheck fragment/activity and profile native pointer/private state; worker I/O then posts confirmation to main and rechecks again at confirmation and positive action.

Rotation while the picker is open relies on ActivityResultRegistry's recreated registration/order. Rotation during the worker read intentionally discards confirmation targeting the old fragment, requiring retry; it does not import silently. Rotation after a confirmed committed replacement is handled by the existing shared persistence observer; a replacement is not cancelled by an old UI disappearing. Process-death result delivery, registration/lifecycle behavior of these exact snapshot binaries, picker/theme/layout inflation and content-provider failures remain APK tests. No persistable URI permission is taken: the returned grant is used immediately for this operation; there is no later URI reopen after process death. Export encodes the callback-time snapshot, not click-time state. Streams are closed on the worker, and only successful close/write is reported as successful. A failed output can leave a partial user-selected export file; regular zoom settings are not changed by export. A failed/cancelled import never partially replaces settings.

### Read-only build-host checks (user runs locally; no runner starts/stops)

From the checkout of the reviewed ref, in the intended WSL distro/account:

```sh
bash tools/versanium/inspect_build_host.sh
systemctl list-units 'actions.runner.*' --type=service --all --no-pager
pgrep -xc Runner.Worker || true
```

Also inspect the intended NEW workspace filesystem with `df -h /path/to/intended/workspace`, and measure the preserved old checkout/output with `du -sh /path/to/old/check-out`. Replace placeholder paths locally; do not paste full environment/service configuration or credential files. Allow space for a SECOND fresh source+dependency+output tree plus headroom; do not treat the cloud's30GiB as the host's free space or assume old output can be deleted. No exact capacity requirement can be certified without old tree measurements/target settings. Confirm one intended listener/service, zero active worker/compiler before a future build, correct Windows/WSL account and label; process-count checks alone are not proof of runner readiness. GitHub Settings→Actions→Runners must also show the intended runner online/idle.

A read-only cloud GET /repos/Nvoid911-Lab/Versanium/actions/runners again returned403 Resource not accessible by integration. That API permission failure is distinct from the CIPD CONNECT403 and leaves actual host online/busy/duplicate state unknown. Do not infer it from an old successful run. To compare networking locally without fetching a dependency or starting a runner, run the following public read-only request:

```sh
curl --head --max-time 20 --silent --show-error \
  'https://chrome-infra-packages.appspot.com/dl/chromium/third_party/androidx/+/BPpMyM0SWd-E1wUl8rg83DvakkDwYKkwEfy561BXtXkC'
```

 A200/redirect shows route reachability only; a local403/error needs its own diagnosis. Do not disable TLS, change dependency pins, or bypass authentication.

### Ref and inputs for a later, separately authorized manual Test build

No dispatch is authorized now. After review, select Primary Nvoid911-Lab/Versanium → Versanium Build → ref `next-test/156-zoom-transfer-pip` at the reviewed final SHA. Do NOT select unchanged migration/versanium or main and expect these156 changes. For the prepared IdeaPad path use runner_provider=ideapad, resume_ideapad=false, f11_test_build=true. Label remains versanium-ideapad, Test identity remains io.github.nvoid911.versanium.test. If using an explicitly chosen cloud provider instead, choose its existing constrained provider label only after capacity/authorization checks; no fallback is automatic. VERSANIUM_RELEASE_APPROVED remains false; production remains Lab-only. The legacy default-main form caveat above still applies: if the selected-ref screen does not expose these exact inputs, STOP; do not dispatch to test it or edit runner labels ad hoc.

All candidate flags default off. After a future APK, compare baseline, diagnostics-only, PiP-only and background-only with browser restart; explicitly test mobile→DeX→mobile in one live document, site/manual pause, navigation/private tabs and Twitch. A single candidate-bearing APK can compare flags off/on; no candidate is a confirmed original-cause fix. Expected future artifact Versanium-Test / Versanium-156.0.8078.47_Test.apk is NOT generated here.

### Follow-up evidence classification

Confirmed local: backup67 using actual Android JSON classes (includes legacy literal fixture/migration and unsafe-restore rejection); policy481; bridge41/persistence18 models; DOM37 models; scope17 models; selected exact156+Vanadium patch application with generic JS bodies unchanged; actual dedicated JNI generation; generated fixed payload header host compilation; Java syntax only; migration13/recovery8; actionlint/YAML/shell/XML/AAPT2/diff checks. A changed-anchor negative test intentionally emits a patch-apply error before the positive integration check.

Source comparison only: JNI/member argument shapes, existing GN/JNI target membership and Android guards; direct AndroidX dependency graph and precise snapshot metadata; SAF registration/result/profile/lifecycle guards; renderer zoom bounds. Unverified: real snapshot SAF UI typing/inflation and rotation/process death, full GN generation/Chromium Java/NullAway/C++ native object/link compile, independent security review, APK/device behavior, host capacity/runner status. No Actions/full build/Release/tag/main merge occurred. PR6 remains separate presentation-only work.
