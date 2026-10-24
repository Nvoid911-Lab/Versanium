# EAM native diagnostic implementation — 2026-10-25 JST

Purpose: identify the first **observed EAM entry**, actual FullscreenController
branches, and synchronous reentry. This is diagnosis, not a PiP fix. Initial
renderer/browser/security requester before the EAM boundary remains unmeasured.
Forward② full log and reported brief-PiP/audio-stop/no-crash/restart remain in
config-a-origin-forward2-review.md and its complete log, without reinterpretation.
`persistent_video_returned` is not renderer completion. Zoom/B remains separate.

## Adopted product changes

`apply_fullscreen_native_origin.py` validates fixed156 anchors before writing a
fresh selected tree. It is NOT an apply controller for saved Run9. Added after
Forward in the fresh patch pipeline. Existing recovery/preparation helpers and
their manifests are unchanged and cannot apply this candidate.

Seven existing files change and one header is added:

- generic ExclusiveAccessContext interface: default no-op diagnostic hook;
- Android context header/implementation: override forwards actual request
  WebContents, fixed stage int and bounded nesting int synchronously to Java;
- ExclusiveAccessManagerAndroid: label at actual exit JNI ingress, AFTER the
  existing FromJavaWebContents and non-null DCHECK, before real controller call;
- FullscreenController: actual entry and already selected branch labels, loss
  notification and context-output call labels; no permission getter repeats;
- Java ExclusiveAccessContext: generated-JNI reporter and a label in its existing
  non-null active-tab branch before FullscreenManager forwarding;
- common exclusive_access BUILD.gn: lists new header;
- new header: trivial inline thread_local integer + noncopyable RAII scope.

Manifest `config-a-origin-forward-native-manifest.json`: Forward43 retained,
seven fixed inputs added (50 before), eight outputs changed/added (51 after).
The scope header must be absent before. All existing43 including native page/
video zoom stay byte-identical; B is excluded in this selection. Full fresh
pipeline composition also contains unbuilt B on this branch; scratch pipeline
PASS does not authorize selecting that pipeline on the host.

## What fixed stages mean

All native labels start `origin6_native_`, followed by fixed stage and `_dN`.
Depth0..64 is accepted; other stages/depths are dropped. Not a tab/player/profile
identifier or a count of independent requests. No arbitrary stack/text/URL logs.

|Stage|Meaning|Limit|
|---|---|---|
|eam_jni_entry|Actual native EAM exit JNI member entered past original non-null DCHECK|Does not identify renderer/browser caller before wrapper|
|controller_entry|Actual FullscreenController::ExitFullscreenModeForTab entered|Can also be called without this JNI entry|
|within_tab_return|Existing within-tab helper returned true|Helper can have side effects; not a permission failure|
|window_or_tab_return|Existing composite window/pending OR exclusive-tab mismatch guard returned|Cannot distinguish operands without changing evaluation; deliberately aggregate|
|context_not_fullscreen_return|Existing context IsFullscreen call returned false|No extra IsFullscreen call is made|
|tab_caused_exit|Existing tab-caused branch selected before ExitFullscreenModeInternal|Not proof internal cleanup completed; internal early returns remain|
|browser_state_loss|Other existing path reached NotifyTabExclusiveAccessLost|Not proof a user deliberately requested browser exit|
|notify_access_lost|Existing non-null exclusive-tab loss branch before clearing state and calling out|May be initiated by other callers; can be depth0|
|context_exit_call|Original request contents still live before context()->ExitFullscreen|Context/Java may later suppress/no-op; not completion|
|native_context_to_base (no depth suffix)|Actual Java context non-null-active-tab branch before onExitFullscreen|Downstream scoped bridge can suppress event; not original native source|

The manager scope increments depth across the real call; controller adds another
scope. A usual Java→native root has JNI d1/controller d2. A synchronous recursive
JNI call inside it has d3/controller d4. A later non-nested call returns to d1;
an autonomous loss notification can have d0. This measures the instrumented
synchronous scopes only, not full stack depth, operation identity or async
parentage. Missing outer labels can result from filtering, destroyed objects or
uninstrumented paths. Repeated labels are not independent root counts. Existing
logger duplicate suppression can omit repeated identical stage strings.

## Scope, JNI, threads and lifetime

Native Report override drops off-UI-thread/no-contents/no-Java-context events.
It also gates diagnostic switch, normal non-shutdown BrowserContext and HTTPS
exact youtube.com/www.youtube.com/m.youtube.com before crossing JNI. These are
privacy/scope checks, not re-execution of PiP eligibility or fullscreen permission.
Java receives the actual native WebContents Java reference (not an inferred
active tab). It requires live context native pointer, live non-null contents,
live normal mActiveTab and identical tab.getWebContents; then the unchanged
Forward bridge requires current controller tab and unchanged scoped logger
requires diagnosis ON, native library ready, live Activity/WebContents, normal
profile and HTTPS exact allowed YouTube. No new eligibility/permission getter,
CHECK exception, profile persistence or page execution is introduced.

JNI is an additional @CalledByNative instance method on existing Java context,
package-private because the fixed generator rejects private callbacks. Generated
signature is `(Lorg/chromium/content_public/browser/WebContents;II)V` returning
void, receiving JavaRef<jobject> obj/contents and JniIntWrapper stage/depth.
Native uses actual GetJavaWebContents() plus integer stages. Fixed public header
declares WebContents::GetWeakPtr() and Android GetJavaWebContents(); controller
header declares its WeakPtr factory. New hook uses existing content public
forward declaration; no content→chrome dependency is added.

Fixed native GetJavaWebContents reaches WebContentsAndroid::GetJavaObject,
whose Java WebContentsImpl.getJavaObject retrieves the existing wrapper from
sWebContentsMap. The diagnostic does not construct a substitute wrapper; null
mapping is rejected by the Java reporter. This supports actual reference-identity
matching to tab.getWebContents rather than a guessed URL or profile match.

Branch callback captures only controller/WebContents WeakPtrs. If a helper
synchronously destroys either, later diagnosis is suppressed. Internal exit
captures original contents WeakPtr before exclusive tab is cleared, checks it
only after the original controller WeakPtr guard, then reports before original
context call. There is no post-call dereference added. Loss notification reports
before original state-clear/call-out. Reporter does only scoped checks/logging,
no nested message loop, activity mutation, playback or asynchronous task.

RAII destructor touches only thread-local counter, even if owner is destroyed;
no raw this/contents/context is retained by it. No return callback is scheduled.
Existing native context destroy zeros Java native pointer and destroys its tab
observer; subsequent Java reporting returns early. UI-only logging means no
cross-thread Java calls; TLS depth is never an asynchronous propagation token.
Actual behavior/lifetime integration still requires real build/device checks.

## Deferred entrances and safe alternative

RendererFrameHost API, generic WebContents exit, security-drop and renderer-gone
entrances are NOT implemented here. Nor are other EAM JNI methods (tab deactivate/
detach/close/ExitExclusiveAccess), escape paths or every internal early return.
Controller entry/loss without EAM JNI can narrow these but cannot attribute them.
It is not safe to infer current Java tab from an arbitrary native frame or to
include chrome JNI headers in content. A complete next design needs a reviewed
generic WebContentsDelegate/observer diagnostic hook, implemented at Android
embedder delegate and routed by actual tab to this scoped reporter, with fixed
enums and destruction-safe local references. Browser/security branches would
emit only inside their actual chosen branches; renderer scope would require a
live current primary frame. Do not add global last-caller state or weaken CHECKs.
This wider public-interface/GN/JNI/lifetime change is deferred rather than
claiming the current candidate identifies every initial request.

Current candidate is sufficient to test EAM JNI entry, guard branch and nesting
hypotheses; **not sufficient alone to prove the original content-side cause**.
No blanket fullscreen/onStop suppression, feature OFF or grace change is made.

## Build graph and real compilation still required

Fixed chrome_java_sources.gni lists Java context; chrome_java consumes that list.
Existing //chrome/android:chrome_jni_headers generates its header, included by
Android context; //chrome/android:jni_headers aggregates it. Android native
source_set //chrome/browser/ui/android/exclusive_access:exclusive_access already
depends on that JNI group, content/public/browser and common exclusive_access.
Common //chrome/browser/ui/exclusive_access:exclusive_access lists new header;
desktop implementations use default no-op hook and acquire no JNI dependency.
The Android target's existing common-target public deps expose //url; explicit
gurl.h include uses fixed GURL::host(), not the nonexistent host_piece().
No source-list additions/new Java class/resource/identity changes or dependency
cycle. TLS ODR isolation was tested in two standalone translation units; actual
component/toolchain integration is not established (reviewed args specify
is_component_build=false; future host args must still be checked).

Future real checks: generated JNI target + chrome_java/NullAway; actual saved
graph's exclusive_access_context_android.o, exclusive_access_manager_android.o
and fullscreen_controller.o with exact source/rule/toolchain; then full APK
integration. Object names here identify sources, not guessed executable Ninja
targets. New header/GN changes may need GN regeneration: STOP under current
no-GN policy, never silently regenerate or pretend old graph covers new inputs.
No old3-token/A/AOrigin/Forward helper authorizes this selection. Before future
apply/build prepare a new transaction against real built Forward evidence,
new input/output provenance and explicit graph-update review. No build now.

## Executed verification versus unverified

- Fixed-source selection and seven transformed files retain every original line
  in order, existing permission/branch getter counts unchanged; drift/repeat reject.
- 50→51 scratch manifest reproduction retains all43 Forward inputs and no B.
- Actual generated Java reporter fragment:110 stage/depth/null/dead/private/
  wrong-contents cases with doubles PASS. Downstream logger gates are unchanged;
  this is not compilation of complete Android classes or NullAway.
- Actual new scope header compiled standalone across2 C++ translation units;
  nesting/reset and deletion of an unrelated owner do not affect counter teardown.
  This does NOT compile FullscreenController or any Chromium API.
- JNI generated with20 Python generator files byte-matched to fixed Chromium
  pin; actual generated function/signature checked. Initial private visibility
  rejection was corrected, no generator flag relaxed.
- Fresh fixed Chromium/selected Vanadium product composition PASS in scratch;
  this includes branch B only in scratch, not in the native selection or host.

Real Chromium native object/Java/NullAway/GN integration and new APK/device result
remain UNVERIFIED. No saved Run9 access/change, build/Actions, B application,
clean/reset/sync/GN regeneration, merge, Release/tag, key/Secrets/runner change.

Validation total:72 local tests PASS (5 new native selection/lifetime-scope/
Java/JNI tests), actionlint and diff checks PASS. Transaction/host evidence is
not available in this cloud; no real-host match is asserted. New JNI generation
is reproducible via check_native_origin_jni.py with pinned generator tree,
selected source tree and a NEW separate output directory.
