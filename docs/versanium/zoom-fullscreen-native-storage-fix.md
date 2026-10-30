# Fullscreen zoom diagnostic storage correction

Base controller: `5f6f9aa18954ce077da44fedf1af20240168bb2b`.
This corrects a diagnostic compile defect, not fullscreen zoom behavior.
Source of Truth v1.25, the no-pending finding and unconfirmed device causality
remain. The full diagnostic APK build is still FAIL from the preceding attempt;
no new full build, link, APK or signing was performed in this correction task.

## Actual cause and complete scope

`Entry` owns `std::string key` and `std::string last`; their destructors make Entry
non-trivially destructible. Consequently `std::array<Entry,32>` is non-trivially
destructible too. It is not an intrinsic ban on std::array: an array of trivial
entries would not have the same lifetime requirement. The original static TLS
array violates Chromium's `-Wexit-time-destructors` policy, promoted by `-Werror`.

All six new native VSZoomLog helpers had the same declaration: browser
WebContentsImpl/RenderWidgetHostImpl, renderer FullscreenController/
WebFrameWidgetImpl/MediaCustomControlsFullscreenDetector/VideoPainter.
`SIMILAR_LIFETIME_RISKS_FOUND=6` means the known failure plus five identical
additional instances. The other new native static TLS values are unsigned and
uint64_t, both trivial. Streams, strings and frame-field temporaries elsewhere
are automatic objects. Java diagnostic weak-map state has JVM-managed lifetime
and is not this C++ destructor defect. No unrelated lifetime cleanup was done.

## Alternatives and selected ownership

| Alternative | Assessment |
|---|---|
| Trivial fixed character buffers / hashes | Would impose truncation or alter exact identity/payload equality; not appropriate for a representation-preserving correction. |
| TLS NoDestructor around the array / unowned heap pointer | Would retain string allocations after worker-thread exit. Rejected instead of merely silencing the warning. |
| Function-static NoDestructor holding ThreadLocalOwnedPointer | Selected. Existing Chromium convention, per-thread owned array, thread-exit deletion, bounded state and no exit-time static destructor. |

The fixed Chromium `base/threading/thread_local.h` explicitly provides
ThreadLocalOwnedPointer for non-trivial per-thread state; `Set(unique_ptr)` owns
the value and deletes it on thread exit/replacement. Its registry must outlive
threads. `base/message_loop/work_id_provider.cc` and
`base/i18n/number_formatting.cc` use the same NoDestructor/TLS-owner arrangement.
NoDestructor keeps the six small TLS registries for process lifetime; it does
not wrap or prevent deletion of the per-thread string arrays.

Each enabled helper allocates one owned array per live thread only when first
used. A thread's array is freed at exit; terminated threads do not accumulate
arrays. Registry initialization is C++ thread-safe function-static initialization;
array access is thread-local through the supported base facility. No shared
mutable Entry, custom lock, new process-global event ordering, JNI or observer
is introduced. Existing trivial TLS next/sequence values remain where they were.

The array still has32 entries; eviction, exact string equality,64-change cap,
limit marker, scopes, timestamps and sequence formatting are unchanged. No
event field or correlation representation changed. Gate OFF returns before
registry construction/allocation. No-pending, browser/renderer, geometry and
Java restore observations are unchanged; no product return/condition moved.

## Regression coverage

New `tests/test_native_storage.py`:3 tests, alongside the existing13 structural/
correlation tests,675 full-selector assertions and49 generated-Java assertions.

The gate compiles the actual six composed helper bodies with the pinned real
Clang and real `base/no_destructor.h`, using `-Wexit-time-destructors -Werror`.
An explicit pthread-backed TLS API/ownership double isolates that fixture from
the full base library. Assertions establish Entry/array non-trivial destruction,
wrapper trivial destruction, zero registry/allocation/logging when OFF, exact
dedup/cap behavior, independent per-thread sequences and cleanup of120 arrays
from20 joined workers. Six main-thread arrays remain bounded. Interleaved logs
are checked without inventing a global counter order.

Negative compiles reject the old TLS array, a non-trivial TLS string and a
non-trivial static vector. The test therefore checks the warning class, not
just one source spelling. A pinned before-helper fixture additionally proves
that undoing only the storage initialization restores the old evidence logic
byte-for-byte for all six copies.

The fixture cannot prove production base TLS implementation, all native APIs,
full linking or APK/device behavior. Real targeted translation-unit compilation
provides the separate integration check below; no warning suppression is used.

## Real Android Clang validation

Six exact production object recipes were obtained read-only with the saved
Ninja graph's `-t commands -s`. For each recipe, only the source input operand,
object output operand and depfile output operand were redirected to an external
evidence directory. The compiler, Android arm64 target, PGO/modules/plugins,
defines/includes and every warning/optimization/validation option were retained.
The actual headers and saved generated inputs were used. Exact original and
validation argv plus the three substituted indices are recorded externally.

Results, all RC0:

- media_custom_controls_fullscreen_detector.o (original failing TU)
- render_widget_host_impl.o
- web_contents_impl.o
- fullscreen_controller.o
- web_frame_widget_impl.o
- video_painter.o

`AFFECTED_NATIVE_COMPILE_RC=0`; the original exit-time destructor error is
resolved. There was no new compiler error. No full target, GN regeneration,
libchrome link, APK generation, signing, ADB or device operation was run.
Existing Error Prone/NullAway/compiler settings were not changed.

Other gates: PiP427/candidate6/active24, bundle5/native5/parse5/default-off,
Zoom481/41/18/67, render model67, pin model5 and protection-tool18 PASS.
The unchanged old67 product-decision model is run on a temporary copy with the
separately verified diagnostic blocks removed: that legacy fixture lacks base
diagnostic macros. The actual complete diagnostic selector is separately tested
by675 and the actual C++ compilation above. No protected fixture was edited.
Canonical Zoom24 blobs and working protected files are unchanged; retired34
remain absent. The ledger and all protected Zoom files remain untouched.

## Fresh tree and subsequent delta

The fresh source and fresh Controller remain at the previously applied5f6f9aa
diagnostic state. Candidate sources/objects were isolated externally; production
source and Ninja object outputs were not replaced. The previous failure evidence
and original APK/libchrome are preserved. No full stack reapplication or cleanup.

An exact six-source correction patch and before/after SHA256 manifest are prepared
for the next reviewed application to that existing tree, with forward-check PASS.
It changes only helper ownership and necessary includes. Controller patch/manifest
updates retain the same f7de before-input identities for new fresh constructions.
Existing 5f6f9aa trees require the narrow incremental correction, not a repeat of
the full eight-source overlay or patch.sh.

External compile/delta evidence:
`/home/takuma/versanium-fresh/phase1-36838/evidence/zoom-fullscreen-storage-fix-q8er4b33`.
The corrective commit is the commit containing this document; its exact SHA and
both normal-push results are recorded in the external final report to avoid a
self-referential commit identifier.

`ZOOM_FULLSCREEN_DIAGNOSTIC_BUILD=FAIL` (full build not resumed)

`MATCHED_DEVICE_EVIDENCE=NOT_YET_COLLECTED`

`ZOOM_FULLSCREEN_FIX_READY_FOR_IMPLEMENTATION=NO`

`NEXT=REVIEW_THEN_RESUME_NATIVE_INCLUSIVE_BUILD`
