# A/B common pipeline coverage — 2026-10-24 JST

Controller f4a2601 real-host read-only comparison matched actual applied evidence,
after-apk provenance and current inputs. Of40 installed source files,37 matched;
three did not. No apply/compile occurred. This is the user's host evidence, not
a new cloud host preflight. The prior selected-fixture PASS omitted real patch.sh
operations and must not be described as a host-complete source reproduction.

## Reproduction from fixed156 inputs

The actual Run9 order is selected Vanadium commits → patch.sh inherited edits,
F11 (line129 block), NTP156 else branch (line219), browser-context live check
(line248), MIXED profile changes (255–256) → zoom overlay → YouTube candidates →
Versanium resource branding → Test identity preparation. The last identity tool
validates but does not modify AndroidManifest.xml; branding does not edit these
three files. No new product patch was needed.

Missing operations were six single-line commands:

- Manifest: extractNativeLibs=false and application/pdf MIME.
- ChromeTabbedActivity:156 NTP override guard and two MIXED profile allowances.
- WebContentsImpl: HasLiveWebContentsForBrowserContext definition before ctor,
  matching its declaration and inherited teardown caller.

`selected_patch_pipeline.py` reads those exact commands from patch.sh rather
than inventing equivalent JSON/XML/C++ formatting. It requires six covered
operations; new selected-target operations stop for review. Historical pre152
NTP branch is explicitly excluded for fixed156. This is a selected-file coverage
check, not execution of the entire build or all possible shell constructs.

Corrected integration executes the common selected edits before F11; its
existing native zoom pass has already occurred. These edits target disjoint
anchors. A regression explicitly reverses only the scratch native overlay and
replays common→overlay in the actual order, proving identical final bytes.
All three final hashes also match the reported host values after F11/common
composition. No saved source is reordered or modified by this test.

| File | Reproduced installed/A SHA256 (equals reported host) |
|---|---|
| content/browser/web_contents/web_contents_impl.cc | ed5c624ed5786aa8eb579b721a32cac06c417b54428aa256f9e9b8abf020e44b |
| chrome/android/java/AndroidManifest.xml | 04f821ef52189aa3274ac117cbc73b90f288ab084bd23e3821196a901c258160 |
| chrome/android/java/src/org/chromium/chrome/browser/ChromeTabbedActivity.java | d21836bfcdf68768e7b0b962c71a5effd970d7af4d080aa423a477d3748b388e |

B WebContents hash is now
`0156c1d1dcbbc51097a84cad190c44b7ac007dd2d7b6bb5f977484181ba00bb2`.
It contains both the inherited live-context function and the zoom candidate.
All40 files stay in the regenerated installed/A/B manifest. The regenerated
`ab-zoom-selection.review.diff` is a review artifact with scratch paths, NOT a
saved-host apply command. No observed digest is added as an alternative or
inspection removed. Direct host bytes were not uploaded: cloud evidence is exact
generation with reported-SHA equality, while new host direct comparison remains
pending.

## Verification and boundaries

A/B generator uses corrected coverage tooling for ALL archived product
selections; product patches remain pinned. installed→A still changes only the
PiP controller Java, A→B only host_zoom_map_impl.cc and web_contents_impl.cc.
Regression removes each of the six commands individually and requires failure
to reproduce the full host triple; a new selected sed command also requires
coverage review. Pipeline-order/native overlay roundtrip PASS. Total local
migration/recovery/preparation tests51 PASS, selected A/B integrations PASS.
No real Chromium integration or device success is established by these checks.

The real host has established provenance equality and37 prior manifest matches;
the corrected triple is reproduced locally. Do not label the corrected40/40
host match verified until a fresh read-only comparison reports it. Retain old
evidence and use a new directory/filename. Require applied.json and
after-apk-provenance as before, then exact installed40/40; no allowlist/skip.
Existing apply helper conditions and original Run9 helper are unchanged. No
saved-tree apply/build, clean/reset/GN/sync/move, merge or Release occurred.
