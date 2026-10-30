# AOriginForward diagnostic candidate — 2026-10-24 JST

Baseline is the **already built and signed AOrigin**, evidence
`/home/takuma/versanium/config-a-origin-evidence-LfbK0s`.
Preserve its applied.json.updated_provenance and after-apk-provenance.json.
Neither A nor installed60b is the before state. Cloud does not have this host
evidence; equality is user-host verification still required before any future apply.

## Product selection

`apply_fullscreen_delegate_origin.py` transforms three Java files:

- TabWebContentsDelegateAndroidImpl: fixed label
  `origin6_webcontents_delegate_forward` immediately before the existing delegate call.
- ActivityTabWebContentsDelegateAndroid: fixed labels
  `origin6_activity_delegate_exclusive_forward` and
  `origin6_activity_delegate_fullscreen_forward`, inside the existing non-null
  manager branches immediately before their existing calls.
- FullscreenVideoPictureInPictureController: tab-only reporting bridge. It checks
  non-null/live/non-private tab, finds existing controllers whose current tab is
  identical, and calls the existing scoped diagnostic logger. No Activity is
  inferred from a nullable window or Context; no new native pointer/Tab is retained.
  sControllers is the existing UI-thread registry populated at creation and removed
  at controller destroy. No registration or asynchronous callback is added.
  The existing logger still gates diagnostic flag/library/activity teardown/live
  WebContents/normal profile/HTTPS exact YouTube. It logs no page-derived string.

No getter/eligibility re-evaluation, no fullscreen/stop/playback behavior change,
no new JNI, resources, C++ or GN target. All three classes are existing
chrome_java sources; real chrome_java/NullAway integration remains required.
The full fresh-source patch pipeline invokes the new transform after AOrigin.
It still contains the separately reviewed B candidate in the branch: **do not
use that full pipeline to update the saved AOrigin tree**.

The selection manifest holds43 files: original AOrigin41 plus the two pristine
forwarding classes. Only the controller and two forwarding classes change;
other40 inputs (including Base and original native zoom) remain byte-identical.
Before controller hash ad3efea4…; after86911a7b…. Other exact hashes are in
`config-a-origin-forward-manifest.json`. Fixed forwarding source hashes are
verified by check_external_fullscreen_trace.py. Scratch selection/regression
tests reproduce new bytes from those inputs. This is **not a host apply helper**.
All old helpers/manifests remain unchanged; none authorizes these extra files.

## What the next diagnostic could distinguish

|Observation|What it identifies|What it cannot establish|
|---|---|---|
|wrapper_forward before accepted exit|External Java WebContents delegate boundary reached for current scoped tab|Who called native exit; a direct Java caller is not excluded|
|activity_delegate_fullscreen_forward|Existing normal feature branch and non-null manager selected|Renderer API vs browser/security request|
|activity_delegate_exclusive_forward|Existing ExclusiveAccess branch and non-null manager selected|Subsequent ExclusiveAccess processing/native origin|
|wrapper only|Wrapper reached, later marker absent or suppressed|Null manager/changed tab/teardown vs other loss; absence is not proof|
|Existing Base local request label then accepted exit|That scoped local request occurred before acceptance|Unique causal attribution if reentrancy/other requests intervene|
|accepted exit without new forwarding labels|Accepted Base exit with no observed forwarding boundary|Direct caller vs filtered events; cannot assert native path absent|

Labels are sequential observations, not correlation IDs. Existing privacy/tab
scope can suppress a callback, and state can change between adjacent labels.
Multiple observer labels may be a single observer loop, not separate requests.
Keep AOrigin② visible result and restart confirmation separately from future
results. Compare known OFF/ON settings after restarting each trial, and capture
from before framework entry through exit/media-stop without URL/title logs.

## Minimal native follow-up considered, not adopted

The Java labels can narrow the forwarding route, but are **not sufficient to
identify its initial native caller**. Fixed-source evidence supports these next
boundaries, requiring a separately reviewed scoped bridge:

|Native site|Potential fixed label|Scope/lifetime and required target|
|---|---|---|
|RenderFrameHostImpl::ExitFullscreen before actual delegate call|renderer_api_exit|Actual originating frame must be live, current primary main frame, normal context, HTTPS exact YouTube and diagnostic enabled. No permission getter/CHECK changes. Compile saved graph's render_frame_host_impl.o in //content/browser:browser first.|
|WebContentsImpl::ExitFullscreen and ExitFullscreenMode|browser_entry / exit_dispatch|A browser entry marker alone does not mean user intent; generic dispatch also receives renderer exits. Use actual live WebContents and scope checks; do not store pointers or access this after delegate call, which can destroy it. Compile actual saved web_contents_impl.o in //content/browser:browser.|
|ForSecurityDropFullscreen selected branch; renderer-gone fullscreen cleanup branch|security_drop / renderer_gone|Label actual selected branch only. Re-checking fullscreen for diagnosis is forbidden. Renderer-gone may have no live current frame: suppression must remain inconclusive. Same WebContents target.|

A safe bridge would carry only a fixed enum to a current UI-thread Java
WebContents→Tab/controller mapping, with shutdown/destroy/private/current-tab/
YouTube/flag gates. Avoid global mutable origin state across nested delegate
calls, raw pointer retention, arbitrary stack or URL logging. Existing Java
reporter is Tab-based and is not presently a native API; there is no reviewed
cross-boundary mapping/lifetime implementation here. Adding this requires JNI
generation/type review, Java/NullAway integration, affected native objects and
APK integration. Exact Ninja object/rule/source/toolchain must be resolved from
the preserved graph, not guessed from the GN name. Native logging is therefore
deferred rather than bypassing scope or inventing a safe mapping.

## Validation and remaining gates

Actual transformed Java forwarding methods with doubles exercise32 feature/
manager/live/private combinations plus null/mismatched-tab bridge cases; the
feature getter executes exactly once and manager calls retain original counts.
Removing diagnostic calls/bridge restores exact original bytes. Repeated and
missing anchors reject. Manifest tests enforce AOrigin baseline and no B selection.
These tests do not compile the complete classes, validate all Android imports,
or prove NullAway/thread/lifetime behavior on device.

Executed:62 preparation/migration unit tests PASS (including3 new tests);
32 real-method Java-double cases plus null/mismatch PASS; fresh selective fixed
Chromium/Vanadium source pipeline PASS; actionlint and diff checks PASS.
The full selective pipeline exercises the branch's B composition in temporary
scratch only, while the43-input manifest test explicitly retains AOrigin native
hashes and selects no B. Neither test reads or modifies the real saved host.
Existing AOrigin/Run9/diagnostic/A apply helpers and B product patch are unchanged.

Before separately authorized future Test: read-only compare AOrigin applied
updated_provenance == after-apk provenance == current input; AOrigin43 hashes;
GN/toolchain/output evidence; reproduce selected3 file bytes; review a new
transaction controller with backups/provenance/output preservation. Existing
AOrigin helper still expects its original two-file A→AOrigin transaction and
must not be relaxed. Then real chrome_java/NullAway, incremental APK and same-key
signing under a distinct ConfigAOriginForward filename, retaining all prior APKs.
No such apply/controller/build operation is executed or authorized by this report.
