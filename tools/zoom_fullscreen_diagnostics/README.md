# Matched fullscreen zoom diagnostics

Implementation checkpoint on controller `f7de4458deb0f96417830f75e399da2cfc0e56d9`.
Source of Truth v1.25 remains unchanged. This package adds observations, not a
fullscreen fix. Chromium reviewed base remains
`1d17a2e2ee147bb7d6ae2ab6abdb3a2510c17775`.

`OBSERVED_DEVICE_BEHAVIOR`: user reports normal at 100%, shrink/margins below
100%, enlargement/clipping above 100%; severity increases with distance from
100%. `CAUSAL_ROOT_CAUSE=UNCONFIRMED`. No matched device evidence was collected
by this implementation. No 300→200 change is included.

## Installation and activation boundary

The canonical 24 protected Zoom files and their ledger are untouched. An
independent eight-file generated-source overlay runs **after** the existing
Zoom, Phase 1 and Versanium transforms in `patch.sh`. It refuses missing,
drifted or partially installed inputs, checks the entire patch before writing,
verifies exact output SHA256, and is idempotent on its complete output.
Fixtures contain the full eight actual f7de-composed fresh-tree source inputs,
compressed without timestamps, with before/after SHA256 in the manifest.

`apply.py --root PATH` is read-only by default. `--apply` is a source mutation
for a separately reviewed future installation. **Neither was used to mutate
the fresh tree in this task.** Do not rerun the whole Phase 1 patch on that
already patched tree. A future incremental preparation must also install the
new passive Java fullscreen callback from this controller, with separate input
and output verification; the eight-file native/EnvironmentZoom overlay alone
does not replace that controller file. No source-list registration was added.

Logging is OFF unless the browser process has the dedicated existing-command-
line switch `--versanium-zoom-fullscreen-diagnostics`. The same switch is
forwarded to child processes. Nothing enables it automatically. Future build
review must establish its activation on the actual test APK. Native logs use
Chromium `LOG(INFO)`; Java uses `Log.i("VersaniumZoomFS", ...)`. Both contain
`VSZOOMFS event=...`; existing `VSPIP` text and gates retain their meanings.

When OFF, no diagnostic sample/cache is initialized, no extra diagnostic
getter runs, and no diagnostic log is emitted. Native observations are all
Android-gated. No new JNI, source registration, media/visibility/permission
decision, persisted setter, resume or fullscreen correction is introduced.
The passive Chrome callback checks CommandLine before referencing EnvironmentZoom;
the gate-off fixture fails if that class is initialized by this callback.

## Evidence points

| Event | Actual source point / meaning |
|---|---|
| ZOOM_STATE | Existing EnvironmentZoom calculation, reusing its raw resolved user exponent and font-adjusted result once. This is a calculation snapshot, not an observed UI click or persistence write. |
| FULLSCREEN_REQUEST | Existing browser and renderer request points, with frame identity. |
| FULLSCREEN_ENTER / EXIT | Existing renderer transitions and passive Java Tab observer. Java observer is limited by the existing live YouTube watch diagnostic scope and Phase 1 gate. Native measurements are not host-hardcoded. |
| FULLSCREEN_CORRECTION_REQUEST | Entry to the existing effective-video-fullscreen callback; existing UpdateZoom remains where it was. |
| FULLSCREEN_CORRECTION_SKIP | Actual no-pending branch before its unchanged return; also unknown RFH, independent child, temporary zoom and later nonqualifying paths. No return-expression getter is rerun to fabricate a value. |
| FULLSCREEN_CORRECTION_SELECTED | Inside the existing fullscreen-video branch before its unchanged `return 0.0`; selection only. |
| ZOOM_WIDGET_FRAME | Existing widget→actual RFH mapping before independent-ancestor normalization, main RFH ID and frame token. |
| VISUAL_PROPERTIES_COMPUTED | Actual browser exponent just calculated; not a send. Geometry fields are explicitly marked not-yet-populated at this source point. |
| VISUAL_PROPERTIES_DEFERRED | Existing pending-ACK early return; absence of SEND must not imply transport. Other existing send guards remain unchanged. |
| VISUAL_PROPERTIES_SEND | After the existing actual UpdateVisualProperties Mojo invocation, with actual sent exponent, grant, CSS zoom, device scale, display and viewport device-pixel size. Not a receiver ACK. |
| VISUAL_PROPERTIES_RECEIVED | Immediately before existing SetZoomInternal; incoming grant is distinguished from the previously stored grant, which updates later. |
| RENDERER_ZOOM_ADOPTED | After the actual SetLayoutZoomFactor invocation, including adopted exponent and actual layout factor. Existing clamp/test/plugin paths remain. Not proof of raster output. |
| FULLSCREEN_LAYOUT source=intersection | Existing IO callback snapshot, guarded nonempty entries; geometry-valid flag and root/target/intersection CSS-pixel boxes. Target is the element box, not necessarily the painted movie. |
| FULLSCREEN_LAYOUT source=paint | Existing foreground nonposter, nonprivate video-paint path after original cached-drawing/empty bounds guards. Actual replaced-content bounds and content box; transformed unclipped root-paint box and geometric clip in the same root-paint space. Not a screenshot, decoded frame capture, occlusion test or pixel-readback. |
| ZOOM_RESTORE | Next existing EnvironmentZoom calculation after passive Java fullscreen exit. `restore_action=none`; compare raw exponent bits only for the same internal environment/host slot. Missing before sample/changed slot => unknown. No restoration write. |

No-pending can return nonzero page zoom without reaching SELECTED. Join its
widget/frame to the following COMPUTED/SEND and ZOOM_STATE to see the actual
value. At 100%, a zero by itself proves neither correction selection nor
propagation. An absent send/adoption/paint/restore sample is incomplete evidence.
Java's enter value is explicitly the last calculation, not a new unsafe query.

## Correlation and coordinate contract

Capture all processes with logcat timestamps and PID/TID; native `tick_us` uses
monotonic TimeTicks, `seq` is **module/thread scoped**, Java `seq_wc` is scoped
to its diagnostic sample. Never sort separate module counters as one global
sequence. No tab pointer, URL, host/query, title, DOM or account data is logged.
The environment/host slot is retained internally only for equality, never output.

Java maps tab/WC identity to **main RFH child/route IDs** using existing Java
APIs. Browser maps those IDs to frame tokens and widget process/route IDs.
Renderer supplies the same local frame token plus its current document token.
Browser grant_count scopes each widget fullscreen session. In renderer RECEIVE,
use the **received** grant, not the stored previous grant; local adoption follows
that received update synchronously. Some independent zoom ancestor cases differ
from the actual widget frame: keep that distinction; do not merge frames.

`correlation.py` accepts **explicitly normalized records**, not raw log lines.
It deliberately does not guess joins by nearest timestamp, invent a document
identity on browser events, or borrow PiP generation. A reviewer must establish
the unambiguous frame/document/widget/grant interval from the raw timeline and
known trial boundaries. Navigation, competing updates, unknown IDs, missing
links or eviction/limit markers make the chain incomplete. Do not fill unknown
identities with the current tab. Normalized trial/WC/frame/document/widget/grant
must match; missing or mismatched identities fail closed. SELECTED, actual SEND,
RECEIVED, ADOPTED and valid subsequent geometry are separate stages.
`correction_applied` in the helper means this staged chain was observed; it is
**not** proof that zoom caused the device symptom.

IO boxes are CSS px in the IO root/target coordinate contract (the existing
observer converts to CSS pixels). Paint-local bounds already include paint
offset; root-paint bounds use the existing paint property transform and geometric
clip. **Root-paint px are not declared device px.** Failed projection or infinite
clip is explicit. Android window fields are decor View dimensions, not guaranteed
WindowMetrics bounds; display dimensions are read-only Display.getRealSize
results. Renderer visible viewport fields are explicitly device px; renderer
fullscreen viewport is labeled Blink viewport units. No CSS/DIP/device/root-
paint cross-space ratio is permitted without separately proven conversion.
Intersection element bounds alone must not substitute for actual content bounds.

Logging deduplicates identical native event/scope payloads, uses 32 thread-local
entries per module, caps changed samples at 64 per key, and emits a limit marker.
Java uses weak WC keys, no retained WC in sample values, deduplication and a
128-sample cap with marker. No frame/timeupdate log is added. Paint observations
can be absent when existing cached-drawing guards return; that is not evidence
of absent video. Restart between matched trials if limits were reached.

## Review and validation limits

Native diagnostic blocks remove to restore **all seven C++ files byte for byte**;
Java inverse restores the original calculation and generated class byte for
byte. Existing VSPIP blocks compare byte for byte. The complete actual
GetPendingZoomLevel method is run before/after with doubles, including the
previously uncovered no-pending branch. No conditional/return relocation is used.

Tests: Python overlay/correlation13, full-selector675 assertions, actual generated
Java49 assertions; existing PiP JVM427 (candidate6 / active24), bundle5,
native5, default-off and Java parse5; existing Zoom policy481, bridge41,
persistence18, real Android JSON backup67, rendering model67, pin model5,
canonical overlay/changed-anchor and settings resource checks; protection tool18.
Runtime/fixture checks are explicitly **not** Chromium/Android/NullAway/native
integration compilation or device validation. Extra source API inspection does
not replace that future build gate. No GN/build/APK/signing/ADB/Run9 operation.

Matched trials remain planned: 50/100/200%, three repeats each, same video,
orientation/display/device and test artifact; phone and DeX are separate trial
families. Compare shrink/normal/overflow with transmitted/adopted scale and actual
content/clip geometry; preserve original user zoom after exit. v1.25 reproduction
facts and the no-pending bypass hypothesis are retained, not upgraded to proof.

`MATCHED_DEVICE_EVIDENCE=NOT_YET_COLLECTED`

`ZOOM_FULLSCREEN_FIX_READY_FOR_IMPLEMENTATION=NO`
