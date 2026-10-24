# Video fullscreen zoom — 2026-10-24 JST

User checkpoint reports Diagnostic APK SHA256
`d01c7633cef628154ac752db4c4c9781e5ac15e9157c3368978f0c872fb20be2` built,
signed with the same certificate and installed. Diagnosis-only playback and
restart on smartphone/DeX no longer crashed in the reported tests. This supersedes
earlier unbuilt diagnostic-correction status; original Actions Run9 remains failed.
PiP stage results for that APK remain unavailable. Video fullscreen size follows
page zoom with diagnosis both OFF/ON, and the user corrected the initial old-APK
comparison: Titanium F11 Test also reproduces it. Neither upstream origin nor a
diagnostic-specific regression is established.

## Source evidence and correction

Pinned Chromium `1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775`:

- Blink `core/frame/fullscreen_controller.cc::DidEnterFullscreen` resets page
  scale to1 and fullscreen scale constraints; this is distinct from browser page
  zoom. The fullscreen CSS uses 100% width/height and object-fit contain. We do
  not change CSS, crop/stretch video, or modify saved percentages.
- Our HostZoomMapImpl lookup returned environment values before upstream
  temporary zoom; its setter saved temporary changes before reaching upstream's
  temporary branch. Both now defer to an existing temporary entry. JNI zoom
  setter updates an existing temporary entry and returns without saving or
  erasing it. Normal explicit environment/site storage remains unchanged.
- Rendering-only `WebContentsImpl::GetPendingZoomLevel` now checks temporary
  zoom first. For an outermost main frame in actual DOM fullscreen with a media
  fullscreen-player ID, it renders exponent0 (100%) without calling a setter.
  F11/browser fullscreen alone has no media-player ID and retains page zoom.
  Paused video retains this ID: this deliberately avoids the active-playing
  getter, which would undo sizing on manual pause.
- `MediaWebContentsObserver::OnMediaEffectivelyFullscreenChanged` sets/resets
  fullscreen_player_ before calling WebContentsImpl. Its public getter returns
  an optional without the unsafe PiP permission CHECK. WebContents now calls
  UpdateZoom on both entry and exit; clearing the ID restores the *current*
  environment/site value, without a captured stale zoom or persistence writes.
  Existing Java display/settings refresh also enters this rendering decision.

This fixes concrete temporary-zoom priority/persistence defects and supplies a
scoped fullscreen-rendering candidate. No device trace proves those defects
caused the reported video-size symptom; actual visual resolution is pending.
Temporary zoom wins even during video fullscreen. A pending main-frame
navigation uses the same scoped rendering decision; after its old video ID is
cleared, the pending environment lookup is restored by existing navigation.
Iframe-driven video is not independently normalized; the outer page render path
must be checked on device. A missing/late media ID or native fullscreen state
delays the override. Geometry feedback across effective-fullscreen thresholds,
rotation and exit ordering remains a device risk.

## Validation

Selected exact156 + Vanadium/F11/zoom/SAF/PiP patch application PASS, including
negative anchor rejection. Added C++ test compiles the actual applied rendering
decision with doubles:67 MODEL checks for below/equal/above100%, repeated
entry/exit, F11-only, existing temporary priority, in-fullscreen settings/display
change, restoration and other contents. Applied source checks cover getter,
setter/JNI non-persistence and both entry/exit refresh. These do NOT establish
Chromium C++ API/ABI integration, layout, Android or media lifecycle behavior.

Existing policy481 (real persistence/migration), bridge41 MOCK, persistence18,
backup67 (actual Android JSON) checks PASS. Migration/recovery/preparation47
tests PASS; actionlint and diff checks PASS. No real Chromium compile, Actions,
saved Run9 apply, GN regeneration, key, identity, backup-schema or Release change.

## Next acceptance and build boundary

Do not reuse or relax the four-file diagnostic apply helper: this change modifies
host_zoom_map_impl.cc and web_contents_impl.cc and needs a new reviewed build
path plus information-source checkpoint before any later authorized build.
Actual native compilation of both changed translation units and dependent
Java/native integration/linking remain required.

On a future reviewed APK: record initial mobile/DeX default/site values; compare
below100%,100%,above100% normal→video fullscreen→exit three times; verify saved
values and export bytes are unchanged absent user edits. Test aspect-ratio
letterboxing (expected), inline/DOM fullscreen vs F11-only, pause (no automatic
resume), rotation, same-tab mobile→DeX→mobile, settings changes while fullscreen,
tab switch, reload/navigation and private/other-site/Twitch behavior. Exit should
use the current environment's saved value. Do not declare layout/fullscreen
restoration successful based on these models alone. PiP/background playback
remain separate unresolved acceptance items.
