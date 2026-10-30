# Diagnostic startup crash: symbolicated root cause and minimal fix — 2026-10-29 JST

Start Controller74460f1d1873073d9c0aef16a8f27ae1bb4ecc75; crashing diagnostic input
0cd373ea3a086622d9c0ec72af64fa389f1c839e. User reports Galaxy S23/Android16,
about2s uptime, native SIGTRAP, not a Java exception. Prior non-diagnostic APK boots.
Current state: SIGNED_STARTUP_FIX_APK_READY_FOR_MANUAL_LAUNCH_TEST.
[Completed build/sign receipt](startup-fix-apk-build.md).

## Exact artifact symbolication BEFORE source edits

Delivered crashed APK SHA256:
5b89e85e14092894c3ba6f6e5ceec85dfd5731cc95f5f969ed4703f06033928f.
Same fresh out/Default unsigned APK SHA256:
1eb7c602c3e6726e7af0116a5159284069438276f87986d3d1ab844a904905e9.
APK-embedded libchrome.so content matches the stripped build library.
Stripped/unstripped native Build ID: **6e7fe6dec62a397532653daa08124c566f9f2546**.
Unstripped SHA25646f0104ff149a7f083ab65e8c84d24731e6a003c3be1b5cb7889ad6147d307a2.
R8 mapping SHA2562b1ee55126b88869b8cf7be76358bbcdc8424c84f29e42aef9690f97444613e0.
Old mapping copied before rebuild; exact hashes and paths:
[startup-crash-symbolication.json](startup-crash-symbolication.json).

llvm-symbolizer --obj=out/Default/lib.unstripped/libchrome.so --inlines --demangle 0x3b4ff88:

```text
base::ImmediateCrash() — base/immediate_crash.h:184:3
logging::CheckFailure() — base/check.h:258:3
content::MediaWebContentsObserver::IsPictureInPictureAllowedForFullscreenVideo() const
  content/browser/media/media_web_contents_observer.cc:325:3
```

The failing native condition is **CHECK(fullscreen_player_.has_value())**.
The next check requires picture_in_picture_allowed_in_fullscreen_.has_value().
A live/native-initialized WebContents without a fullscreen player is insufficient.

R8 names from this exact old mapping:
- WebContentsImpl.M1 = isPictureInPictureAllowedForFullscreenVideo (Java1012–1014).
- ChromeTabbedActivity.T1 = onStartWithNative; super call at source1838.
- ChromeTabbedActivity.r = finishNativeInitialization.
- ChromeActivity -> xg2; xg2.T1 = onStartWithNative; diagnostic hook at1211.
- Controller -> s2i; s2i.g = diagnosticActivity; page-field call at103.
- Policy -> v2i; v2i.c = diagnosticPageFields; unsafe getter at94.

Exact source/mapping call path:
ChromeTabbedActivity.finishNativeInitialization -> onStartWithNative ->
ChromeActivity.onStartWithNative -> Controller.diagnosticActivity ->
Policy.diagnosticPageFields -> WebContentsImpl.isPictureInPictureAllowedForFullscreenVideo ->
existing JNI -> WebContentsAndroid -> MediaWebContentsObserver CHECK at325.

The supplied +20/+76/+154 are code offsets, not R8/source line numbers; no false
line interpretation was used. Intermediate diagnostic names resolve from mapping
and the exact built source; the user supplied a crash summary, not the full tombstone.
Missing crashpad-handler trampoline is not established as cause: PC resolves to
the fullscreen CHECK, matching the newly added unconditional diagnostic getter.

## Review of every diagnostic native-backed read / initialization

All call sites are existing UI-thread lifecycle/tab/WC/media callbacks. No native
failure is caught to suppress CHECKs. Backend contracts were read in fixed source.

| Read/initialization | Classification / contract | Diagnostic handling |
| --- | --- | --- |
| Activity finishing/destroyed/config/PiP flags | Android Activity state; no Chromium WC/native-init requirement | Retained |
| Tab.getId/getWebContents/getUserAgent/isDestroyed | Cached Java values; non-null Tab only | Null/destroyed guards |
| Tab.getUrl | TabImpl checks initialization; may call WC.getVisibleUrl JNI | Diagnostic-only URI helper now requires live WC; otherwise empty URI/unknown |
| Uri parsing and field formatting | Pure Java/Android data; safe before Chromium native init | Retained, no URL query/UA logging |
| WC.isDestroyed | Zero pointer short-circuits in Java; otherwise native isBeingDestroyed on existing WC | Used as liveness guard, not proof of fullscreen |
| WC.getNavigationController | Cached Java wrapper | Access only after live WC guard |
| NavigationController.getUseDesktopUserAgent | JNI when navigation pointer nonzero; implementation returns false for zero | Live WC/UI guard retained |
| WC.getVisibility | checkNotDestroyed + JNI; live native WC required, no fullscreen condition | Live WC/UI guard retained |
| WC.hasActiveEffectivelyFullscreenVideo | UI/live WC; native returns false when no active fullscreen player | Sample once as permission precondition |
| WC.isPictureInPictureAllowedForFullscreenVideo | Live WC is insufficient; CHECK requires fullscreen player/permission optional | **Call only if prior active-fullscreen result true**, otherwise unknown |
| new WebContentsObserver(wc) / observe(wc) | WC addObserver requires nonzero native pointer and may initialize JNI proxy | Existing null/isDestroyed guard in diagnosticObserve; defer when not live |
| MediaSession.fromWebContents | Existing JNI lookup; live WC required | Only inside live guarded DiagnosticPage construction |
| new MediaSessionObserver(session) | Java addObserver may synchronously call state/metadata callbacks | Fields initialized; emit rechecks live source and uses guarded snapshot |
| MediaSession callback controllable/suspended | Supplied booleans; no new getter | Retained; no active-state inference |
| observer removal / stopObserving | Existing Java unregister/detach, no media command | Retained on close/identity change/destruction |

Deferring all observation until fullscreen would hide the mobile-page sequence.
Instead retain passive page/media/visibility observation for live inline pages,
and represent only the unavailable fullscreen permission as unknown.
Native initialization alone is not a sufficient fix: a later live nonfullscreen
page would still hit the same CHECK.

## Minimal diagnostic-only fix

Only Policy production Java changes:
1. Cache hasActiveEffectivelyFullscreenVideo once; short-circuit the fullscreen-only
   permission getter exactly as existing upstream canDoPictureInPicture does.
2. Return fullscreenPipAllowed=unknown when no fullscreen video.
3. Guard diagnostic-only Tab URL sampling with the same live-WC checks.

Product capture/eligibility/videoId/Owner/state/entry/media/token logic is untouched.
Controller, integration patch, source registration, Zoom, JNI/C++ and pins unchanged.
No generic try/catch, permission widening, resume, fallback or media actions.
All useful mobile/desktop and outgoing-page observation remains.

## Regression/gates

The old stub defaulted fullscreenVideo=true and omitted the native CHECK contract,
masking this regression. The updated WC double starts with no fullscreen player
and throws on the exact forbidden getter; guarded native reads also reject a
not-yet-live WC. The unmodified production diagnostic fails red through the same
Activity -> Policy path. With the fix **JVM415 PASS**, previous400 retained +15:
- null Tab / null WC / not-native-backed WC report unknown;
- no unsafe permission, URL or other diagnostic native reads while not live;
- passive observer attachment defers until later live content;
- live nonfullscreen page retains desktop/visibility logs without permission JNI;
- fullscreen false/true permission is sampled once only when valid;
- owner/media/state remain unchanged; observers detach normally.
Candidate6 / active-owner24 remain PASS. Bundle5 / default-off / parse-only5,
Zoom24 and retired34 are required before the authorized fresh incremental build.

Exact crash artifacts were resolved and preserved before this fix or push.
New APK launch success remains unverified until the user's next device test.
No Run9, ADB/install, merge/release/tag or Production operation.
