# Diagnostic startup-fix APK receipt — 2026-10-29 JST

State: **SIGNED_STARTUP_FIX_APK_READY_FOR_MANUAL_LAUNCH_TEST**.
New APK is built/signed/verified, **not device-launch-tested**.

Start HEAD74460f1d1873073d9c0aef16a8f27ae1bb4ecc75.
Compiled diagnostic fix3ce5aac4c370346ee404a6a65e9b94399b89a16c.
Subject: Guard diagnostic fullscreen permission reads during startup.
Primary/Secondary normal push; branch next-test/156-zoom-transfer-pip.

## Identified cause, not a speculative fix

Exact crashed APK SHA5b89e85e14092894c3ba6f6e5ceec85dfd5731cc95f5f969ed4703f06033928f.
Its embedded library matches fresh stripped libchrome; stripped/unstripped Build ID
6e7fe6dec62a397532653daa08124c566f9f2546. Old mapping preserved before edits/build.

PC0x3b4ff88:
content::MediaWebContentsObserver::IsPictureInPictureAllowedForFullscreenVideo() const,
content/browser/media/media_web_contents_observer.cc:325:3,
CHECK(fullscreen_player_.has_value()), inlined through CheckFailure/ImmediateCrash.
R8 WebContentsImpl.M1 = isPictureInPictureAllowedForFullscreenVideo;
ChromeTabbedActivity.T1 = onStartWithNative; r = finishNativeInitialization.
Exact built-source path proceeds through ChromeActivity.onStartWithNative:1211,
Controller.diagnosticActivity:103, Policy.diagnosticPageFields:94 and existing JNI.
Missing crashpad trampoline is not established as primary cause.

See [symbolication and complete native-read classification](diagnostic-startup-crash.md)
and [old artifact hashes](startup-crash-symbolication.json). Code offsets were not
treated as source line numbers. Supplied crash evidence is a summary, not full tombstone.

## Scope and regression

Only production Policy diagnostic helpers changed: active-fullscreen is sampled
once, the permission JNI getter runs only when true, otherwise unknown. Diagnostic
URL sampling also checks live WC because Tab.getUrl may invoke native getVisibleUrl.
No exception catch to mask a fatal native CHECK. Product eligibility/Owner/videoId/
state/controller/patch/token/media behavior and all C++/JNI/Zoom/F11/pins unchanged.

Updated double starts with no fullscreen player and models the exact native
permission CHECK. Old code fails red via Activity -> diagnosticPageFields; fixed
code **JVM415 PASS**, prior400 +15. Null/not-live WC performs no unsafe native read,
logs unknown, skips attachment; later live content attaches normally. Both valid
permission booleans and mobile/desktop/visibility/media coverage remain observable.
Candidate6 / active-owner24, bundle5, default-off and parse-only5 all PASS.

## Build / signing

Only existing Versanium-Ubuntu fresh workspace phase1-36838 was used.
Source modification was **one Policy Java file** after exact old-content match,
backup and inventory proof; no whole Phase1/patch.sh apply.
Post-build **1316 source entries identical** to post-apply snapshot.
Native stripped/unstripped library SHA256 unchanged; no native code change.
Zoom canonical24 PASS, installed Zoom content unchanged, retired34 absent,
GNI Controller/Policy registration1/1, args SHA d2096bdd18bfb10c2edb46ef950864bf917351dd5c7b059921b51e8b8e335cf8 unchanged.
Fresh controller retains the known Vanadium helper dirty submodule separately
from blob gate; no unexpected changes cleaned/reset.

| Stage | Result | Seconds |
| --- | --- | ---: |
| gn gen out/Default | RC0 PASS | 12.73 |
| autoninja -C out/Default -j6 chrome_java | RC0 PASS | 18.3 |
| autoninja -C out/Default -j6 chrome_public_apk | RC0 PASS | 202.69 |
| aapt2 package / label | io.github.nvoid911.versanium.test / Versanium | |
| zipalign -c -P 16 4 | PASS | |
| apksigner verify --verbose --print-certs | RC0 PASS / V3 / one signer | |

Reviewed Chromium1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775;
patched HEAD e76ab5fc518ef2df24519c82cec55427870f8bd4;
Titanium156.0.8078.47; Vanadium2ae4335402eabcc6e025f3400185fe25094d8521.
Existing ErrorProne=false preserved; ordinary Java build is not NullAway verification.

Existing local device-test key/alias reused, unchanged, no Production signing.
Signer certificate SHA256:
063e982a1c533f32e74a0ddeb47a3b91bfad810de181ef292c8769e276ac8151.
Password used transiently; no key/password repository or Actions storage.
Unsigned build output unchanged by signing; crashed APK kept separately.

Signed SHA256: **6f0c6896ef33048ed53a55bddf332570a31ac31de94c9dafc54dd5babbbc6d13**
Size: **331324511 bytes / 315.98 MiB**

- Diagnostic output: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a-phase1-diagnostic-startup-fix.apk`
- Standard output: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a.apk`
- Windows manual-transfer copy: C:/Users/Nvoid/Documents/ChatGPT/Versanium Build/Versanium-156.0.8078.47-phase1-diagnostic-startup-fix.apk
- Old crashed APK backup: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a-before-startup-fix.apk`

Old R8 mapping remains under evidence/phase1-startup-crash-0cd373e/.
New R8 mapping: `/home/takuma/versanium-fresh/phase1-36838/evidence/phase1-startup-fix-3ce5aac/ChromePublic.startup-fix.apk.mapping`.
New mapping SHA256: 71cf15c440ee58076c8433b2075b8e528242580988e3236acf74760ef6a04667.
The old mapping must be used for the old M1/T1/r crash, not this new mapping.
Full machine-readable build/sign/protection receipts:
[startup-fix-apk-build.json](startup-fix-apk-build.json).

Next: user manual install/launch check, then the four mobile/desktop tab-switch/
Home cases. Original mobile-specific PiP issue is not claimed fixed.
No ADB/install/wireless debugging, saved Run9 access/copy/reset/clean,
Actions, merge/release/tag or Production operation.
