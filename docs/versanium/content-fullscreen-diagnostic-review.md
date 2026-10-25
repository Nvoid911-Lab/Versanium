# Content ingress / persistent-false diagnostic product — 2026-10-25 JST

Scope is ONLY first content ingress and persistent-false request/dispatch. No
renderer pause, broad MediaSession, playback/exit policy or B changes. Prior
Native device evidence/full log remains in native-diagnostic-device-review-2026-10-25.md.
Signed Native APK hash remains unreported. This product selection is not a host
transaction or permission to apply/build. Existing helpers/manifests are unchanged.

## Product route and fixed events

New apply_content_fullscreen_origin.py transforms10 existing files. Content
WebContentsImpl exposes a scoped reporter and notifies a new default no-op
WebContentsObserver callback. Existing Android WebContentsObserverProxy passes
one fixed int through generated JNI; Java proxy forwards to its observers.
The existing PiP observer matches its actual super.getWebContents() to the
controller's current WebContents before the unchanged scoped logger. No content
include/dependency on chrome or the Chrome TLS header is introduced.

|Fixed content_diag_ event|Meaning / limit|
|---|---|
|renderer_api_enter / renderer_api_return|Actual RenderFrameHostImpl::ExitFullscreen ingress/return, scoped to current active primary frame. Does not identify the JS function/user intent.|
|browser_exit_enter / browser_exit_return|WebContentsImpl::ExitFullscreen wrapper, also used by cleanup/reentry. ALONE does not prove a browser-origin root request.|
|dispatch_enter / dispatch_return|Generic ExitFullscreenMode call. ALONE cannot determine origin.|
|navigation_exit|Existing should_exit_fullscreen branch selected. Main vs descendant-navigation operand is not re-queried.|
|security_downstream_exit / security_opener_exit|Actual selected ForSecurityDropFullscreen call-out to that receiver. Do not suppress security exit.|
|renderer_gone_exit|Existing current-renderer-gone fullscreen cleanup branch selected, only if scope still live/active. Missing event does not exclude renderer loss.|
|cleanup_false_request / cleanup_false_returned|Stored PiP leave callback called setHasPersistentVideo(false) for current live contents. Return is not renderer completion.|
|persistent_false_unchanged|Inside ORIGINAL equal-state early return: native flag was already false, so no new player request on that invocation.|
|persistent_false_no_player|Inside ORIGINAL no-fullscreen_player branch, no SetPersistentState send on that invocation.|
|persistent_false_send_begin / persistent_false_send_returned|Immediately around actual SetPersistentState(false) call. The latter proves call returned locally; Mojo disconnect/renderer handling is NOT acknowledged.|

All stage→label mapping is fixed in source; JNI transports only int, not arbitrary
string, URL/title/account, frame/player id or native stack. Existing EAM depth
labels remain separate. Enter/return brackets indicate synchronous boundaries,
not async parentage or a count of independent external requests. No global
last-caller field or new shared TLS attribution is introduced.

## Scope / lifetime / JNI review

- Native reporter: Android only, actual UI thread, not being destroyed,
  diagnostic switch, normal non-shutdown BrowserContext, live active primary
  main frame and HTTPS exact youtube.com/www.youtube.com/m.youtube.com.
  These are privacy/liveness scope checks, not PiP permission/eligibility.
- Renderer API entry additionally requires actual originating frame active and
  primary; return checks that frame and contents still exist and remain current.
  Child/inactive/deleted-frame requests are intentionally not attributed by that
  marker. Generic dispatch may still be observed, leaving origin unknown.
- Actual receiver WebContents carries the native event. Security call-outs use
  their actual receiver's WeakPtr, never substitute the initiating tab. Java
  observer identity plus existing logger enforce current tab, normal profile,
  live Activity/WebContents, HTTPS YouTube/diagnosis/native-library gates.
- Native call sites retain WeakPtrs before emitting and guard against destruction
  before original work or return-only reporting. No post-call raw-owner access
  is added. Existing weak guards and CHECKs are unchanged. New early returns are
  destruction-only safety guards, not changes to valid exit decisions.
- New observer callback contract forbids mutation/page execution/task pumping;
  only new implementation forwards fixed diagnosis and other observers default
  to no-op. Existing observer iteration/handleObserverCall/finishObserverCall
  conventions are preserved. No task, raw pointer, frame or reference survives
  asynchronously. Existing PiP cleanup keeps its original captured WebContents;
  additional logging occurs only for matching live current contents.
- New Android proxy callback uses a dedicated nullable Java-proxy lookup and
  returns if detached/native pointer zero. The existing lookup calls assertNonNull,
  so it is NOT reused here. Neither it nor GetJavaObjectChecked/CHECK is changed.
  The new static JNI lookup takes actual WebContents* const& and returns a nullable
  local object reference; Java reads only its existing proxy field. Missing mapping can drop
  events, never imply the content event did not occur.
- Generated function:
  Java_WebContentsObserverProxy_versaniumContentFullscreenDiagnostic(JNIEnv*,
  JavaRef<jobject> obj, JniIntWrapper stage), Java signature **(I)V**, void return.
  Actual WebContents identity comes from observer registration, not an inferred
  Activity, pointer supplied by Java or URL match alone.

Persistent true behavior is uninstrumented. False no-player/equal-state labels
sit inside already selected original branches. Original equality/fullscreen-player
checks and SetPersistentState calls still occur once; permission getters and
CHECKs are not added/repeated/relaxed. Send-return checks only a previously
captured contents WeakPtr; no source object member access after possible teardown.
Profile shutdown/teardown can suppress a late return event.

## What another APK would decide, before requesting it

|Observed first scoped path|Limited fix to evaluate|What must stay intact|
|---|---|---|
|renderer_api_enter before dispatch/EAM|Trace the renderer/fullscreen transition or site-request handling; possibly a caller-specific candidate adjustment|Cannot generally reject genuine page/user exit or bypass permission|
|navigation_exit before wrapper/dispatch|Check actual navigation/fullscreen ownership; if transition is erroneous, fix that branch|Real navigation still exits fullscreen|
|security_* before wrapper/dispatch|Investigate the triggering browser UI/transition rather than suppressing security drop|All security fullscreen escapes remain|
|renderer_gone_exit|Investigate renderer termination/teardown; app no-crash does not mean renderer survived|Never retain dead WebContents/player or relax CHECK|
|browser_exit only or dispatch only|Still insufficient origin evidence; identify another specific caller if needed|Do not label generic arrival as proven root|
|cleanup false→send begin→send returned before stopped|False dispatch ordering confirmed, not renderer application or pause cause|No force-play/blanket late-cleanup change without cause|
|cleanup false→no player or unchanged|That invocation sent no new false IPC|Do not blame that absent send or pick a stale player to force delivery|

This should avoid rebuilding for already known EAM branches alone. It cannot
identify exact JS code, player-specific pause reason, renderer application time,
audio-focus origin or asynchronous causal links. Missing markers may be scope
filtering, no observer, inactive frame, destroyed receiver or an uninstrumented
caller. Renderer pause/Mojo/media-session instrumentation is NOT part of this
candidate and should not be inferred from stopped notifications.

## Selected-source verification, not saved-host apply preparation

New content-fullscreen-diagnostic-selection.json describes10 before/after file
hashes and48 preserved Native baseline inputs (58 checked files total). Native51
was reconstructed/verified first; seven previously unselected observer/header/
media inputs come from fixed156. Both native zoom files retain baseline bytes:
B is NOT in this selection. Original Native51/Forward43/A manifests remain intact.
Fresh full branch pipeline composition also includes unbuilt B in scratch;
that pipeline must NOT be run on saved Native. No existing apply helper accepts
these changes, and no new saved-host apply controller is provided here.

## Build dependencies and unverified integration

Fixed GN already lists modified existing sources/headers: native implementations
in //content/browser:browser (Android proxy under Android condition); Java
WebContentsObserver and Proxy in //content/public/android:content_full_java;
Proxy in existing //content/public/android:content_jni_headers; controller in
//chrome/android:chrome_java. Existing native proxy includes that JNI header.
No new source/header file, BUILD.gn edit, resource or dependency edge is needed
for THIS product delta. Full public observer vtable/header consumers still need
integration recompilation; do not promise only four object rebuilds or old graph
reuse. Future preparation must inspect actual Native source/graph/provenance.

Fixed template third_party/jni_zero/jni_zero.gni SHA256
f76110787aca6cdf9d39c500cd37c6be3bd56feb95ae83aa8e07f95b54277beb
sets allow_private_called_by_natives=true. Full Proxy generation needs that
EXISTING production option for preexisting private callbacks. It was used for
the local generation, not added to GN or relaxed to admit the new public method.
20 generator Python file hashes match existing fixed-pin ledger. Exact generated
(I)V function was checked. This is actual JNI generation, not C++ compilation.

Required later integration: real JNI target, content Java + chrome_java/NullAway,
actual source/rule/toolchain-resolved objects for render_frame_host_impl.cc,
web_contents_impl.cc, media_web_contents_observer.cc and web_contents_observer_proxy.cc,
all header-dependent rebuilds, then APK. No object names are guessed here. Before
any host write/build, prepare a separate transaction against built Native evidence
and reported APK/provenance; current signed Native APK SHA is still unknown.

## Executed bounded checks

58-input Native/no-B selection and10 output hashes; repeated/drifted anchors
reject; unchanged CHECK/permission getter counts; current-contents enum-routing
Java fragment64 cases with doubles; fixed actual JNI generation/type check;
fresh fixed Chromium/Vanadium product composition. Complete Android Java types,
NullAway, native object/GN/link integration and new APK/device behavior remain
UNVERIFIED. No standalone model success is labelled Chromium compilation.
No saved-tree access/change/build/GN/Actions/B/clean/reset/sync/merge/Release/tag,
identity/signing/Secrets/runner change is performed. Product code and verification
only; future host apply/build preparation is explicitly separate.

Validation total:86 local tests PASS (6 new), actionlint/diff PASS. Native51
before-state matches the previous manifest; GetPendingZoomLevel and effective
fullscreen zoom observer bodies remain byte-identical. New nullable-proxy lookup
has4 actual-Java fragment cases (missing/destroyed/live/null contents), and the old assert-bearing
lookup body is unchanged. These are bounded tests, not complete Android/native
type checking or saved-host validation.

Additional composition cross-check:9 changed outputs equal the actual fresh
full pipeline outputs. WebContentsImpl.cc differs there because full branch
composition includes B; its Native/no-B before/after is independently checked
against selected baseline and both zoom method bodies are unchanged. No scratch
composition result is described as a successful host application or device test.
