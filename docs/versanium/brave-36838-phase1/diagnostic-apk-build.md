# Phase1 diagnostic APK build receipt — 2026-10-28 JST

State: **SIGNED_DIAGNOSTIC_APK_READY_FOR_MANUAL_DEVICE_TEST**.
The new APK has not been installed or device-tested by this task.

Controller source input: `0cd373ea3a086622d9c0ec72af64fa389f1c839e`.
Diagnostic commits: `50eff9ea3f51c7d3ecb352c19273d679be7829c6` and
`0cd373ea3a086622d9c0ec72af64fa389f1c839e`.
Start: `9ef1c26350042cfe8369357d994fcef143a39ca2`.
Branch: next-test/156-zoom-transfer-pip. Primary then Secondary normal pushes.
This receipt/documentation does not change the compiled Java input.

## Build and package

Only existing fresh workspace used:
`/home/takuma/versanium-fresh/phase1-36838`, WSL Versanium-Ubuntu.
Reviewed Chromium base1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775;
patched Chromium HEAD e76ab5fc518ef2df24519c82cec55427870f8bd4.
Titanium156.0.8078.47, Vanadium2ae4335402eabcc6e025f3400185fe25094d8521;
depot_tools8ce91cb0b1b3d28c8a74d84b724a3897e6d8a284.

| Stage | Result | Seconds |
| --- | --- | ---: |
| gn gen out/Default | PASS / RC0 | 9.35 |
| autoninja -C out/Default -j6 chrome_java | PASS / RC0 | 32.44 |
| autoninja -C out/Default -j6 chrome_public_apk | PASS / RC0 | 201.04 |
| aapt2 package / label | io.github.nvoid911.versanium.test / Versanium | |
| zipalign -c -P 16 4 | PASS | |
| apksigner verify --verbose --print-certs | PASS / RC0, V3 true, 1 signer | |

Ordinary Chromium Java compile is not a NullAway run; existing ErrorProne=false
args were preserved. No dependency/environment setup or output clean was performed.

## Signing and outputs

Existing local Galaxy S23 device-test keystore/alias reused. Certificate matches
the previous device-test APK:
`063e982a1c533f32e74a0ddeb47a3b91bfad810de181ef292c8769e276ac8151`.
Not a Production/Release signing identity. Keystore unchanged; no key or password
was stored in the repository, copied to controller keys/, or put in Actions secrets.

Signed SHA256:
`5b89e85e14092894c3ba6f6e5ceec85dfd5731cc95f5f969ed4703f06033928f`.
Size: **331324571 bytes (315.98 MiB)**.

- Standard requested output: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a.apk`
- Diagnostic named copy: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a-phase1-diagnostic.apk`
- Windows manual-transfer copy: C:/Users/Nvoid/Documents/ChatGPT/Versanium Build/Versanium-156.0.8078.47-phase1-diagnostic.apk
- Previous signed APK preserved: `/home/takuma/versanium-fresh/phase1-36838/chromium/src/out/release/156.0.8078.47-arm64-v8a-before-phase1-diagnostic.apk`
- Original build APK out/Default/apks/ChromePublic.apk is unchanged by signing.

All three signed copies have the same SHA256. The actual final dex contains
VSPIP, desktop_site, PAGE_MODE, WC_VISIBILITY, MEDIA_SESSION, TAB_UNSELECTED and
ENTRY_RESULT strings, confirming retained diagnostic code after release dex/R8.
Logcat tag: **cr_VersaniumPiP** (Chromium prefix), payload VSPIP event=... seq=....

## Scope, checks and source protection

Only four fresh Java sources changed: ChromeActivity, upstream fullscreen-video
controller, Phase1 Controller and Policy. Applied two diagnostic-only deltas with
strict anchors and source snapshots; never reapplied full Phase1 or patch.sh.
Existing signed output was backed up before source mutation.

Zoom24 Git blob gate PASS, installed Zoom overlays unchanged, retired34 absent,
Phase1 GNI registration1/1. Initial Zoom integration reverse-check PASS before
logging. Later raw reverse-check encountered logging inserted into a shared
ChromeActivity context; no product mutation was accepted on that failure.
Verified exact prior-diagnostic reverse delta and complete current source inventory
instead, then applied the follow-up. This preserves the initial validated Zoom
content proof without weakening the canonical hash gate.

Post-build source inventory **1316 entries identical** to the approved post-apply
snapshot. args.gn SHA256 unchanged:
`d2096bdd18bfb10c2edb46ef950864bf917351dd5c7b059921b51e8b8e335cf8`.
The known four-line Vanadium patch-error formatting modification remains;
Controller worktree gate reports that submodule dirty state separately from the
passing24-blob gate. No unexpected local changes were reset or cleaned.

Final source tests: JVM400 PASS (candidate6/active24), bundle5 PASS, default-off
PASS, parse-only5 PASS. The bundle anchor-drift test's patch-error output is
expected negative-case evidence. Diagnostic probes have bounded current/previous
page lifetimes, stale identity guards and destruction teardown; no media actions.
Existing product eligibility, ownership, lifecycle and entry/exit decisions remain.

## Device evidence and next step

User reports **same Galaxy S23 / same prior target APK**:
mobile site FAIL (tab switch stops playback, Home no PiP, playback remains stopped);
desktop site PASS (tab switch continues, Home PiP, playback in PiP continues).
This favors YouTube mobile-site-specific visibility/media behavior over generic
Android PiP failure; pause-before-entry remains a hypothesis to verify from logs.

Manually transfer the signed diagnostic APK and compare CASE_MOBILE_TAB_SWITCH,
CASE_MOBILE_HOME, CASE_DESKTOP_TAB_SWITCH, CASE_DESKTOP_HOME. desktop_site,
sourceTab, seq, selected/retainedOutgoing, media signals/session suspension and
entry/state events permit temporal comparison. No case inference is required.
No new APK device PASS is claimed.

Final measured C: free **138136899584 bytes / 128.65 GiB**.
Logs: fresh workspace logs/phase1-diagnostic-{gn,chrome_java,chrome_public_apk}.log.
Evidence: fresh workspace evidence/phase1-diagnostic-0cd373e/.
Machine-readable receipt: [diagnostic-apk-build.json](diagnostic-apk-build.json).
[Logging/API scope and interpretation](diagnostic-logging.md).

No saved Run9 access/reference/copy/reset/clean, ADB connection/install/wireless
debugging, Actions, merge/release/tag or Production operation.
