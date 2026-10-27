# Versanium Project Status

> Current policy — 2026-10-28 JST: the former Versanium YouTube PiP,
> Diagnostics/unsafe diagnostics and Background candidates are **retired / superseded**.
> Their generators, runtime plumbing, dedicated apply controllers and tests are removed.
> Earlier candidate descriptions below and existing docs/versanium reports/manifests/logs
> are historical evidence, not current functionality or executable instructions.
> Zoom (phone/DeX, transfer, persistence, policy, backup), F11/display, branding,
> Chromium156 pins and non-PiP features remain unchanged. Saved generated source
> and existing APKs are untouched and still reflect their historical configuration.
> Future PiP work is limited to Brave #36838 (YouTube PiP lifecycle/dismiss),
> #33522 (background playback), #39765 (Chromium153+ screen-lock/onStop).
> No Brave code is ported here. Build/GN/Actions/APK/merge/release/tag/Production
> are prohibited in this cleanup phase; PR5 stays Draft/Open/unmerged, body unchanged.
> See [retirement plan and integrity ledger](docs/versanium/pip-candidate-retirement-2026-10-28/plan.md).
> Next: `READY_FOR_BRAVE_36838_33522_39765_READONLY_PORT_ANALYSIS`.


## 2026-10-27 JST — Saved integration review complete / Test Build NOT APPROVED

Current checkpoint supersedes pending saved integration/full-script/graph review
items in the historical entries below. Reviewed product commit:
`d1e3261690917bb29d75947c3e9d6bf89c44f728`, Primary branch
`next-test/156-zoom-transfer-pip`; branch/PR5 HEAD verified before docs edits,
PR5 Draft/Open/unmerged. Product code is unchanged by this checkpoint.

User-reported completed saved integration review: saved `out/Default` graph reuse
PASS; GN regeneration NOT REQUIRED based on graph/Siso evidence; `gn clean`
FORBIDDEN for the specified saved workspace; incremental recompilation REQUIRED.
Old saved patch.sh/generator must not be re-executed. Whole-script comparison is
reported resolved to only the reviewed shard2 one-line fix; historical distinct
script hashes remain preserved. Siso v1.6.3 / ProdCIPD=true and saved state reusable.
Deps/inputs audit:7+7 queries rc=0, source/header/Java visibility PASS,
protected state unchanged; content3 objects require rebuild, exclusive-access3
CURRENT. These are supplied host results, not a new local host audit/build.

Exact saved paths, Siso binary/state identity, evidence SHA256s, source/graph
identities and limits are recorded in the appended current checkpoint in
[stage reconciliation](docs/versanium/post-nullaway-stage-reconciliation.md#2026-10-27-jst--completed-saved-integration-review--current-state).
Prior95/99 repository test results remain historical; no new integration success
is inferred. Existing three untracked host files and all evidence are preserved.

### Test Build Gate

Test Build remains **NOT APPROVED**. Start only after explicit user approval in
a later step. Candidate then: current saved source + saved `out/Default`,
Siso/autoninja incremental `chrome_public_apk`; no reapply or GN regen/clean.
Refresh/present Context and check live host capacity/concurrency before execution.
Actions/APK/merge/release/tag/Production remain **NOT APPROVED**.
This work unit is documentation validation/commit/normal push only; no build/GN/
Actions/APK/source apply/merge/release performed. PR5 remains Draft/Open/unmerged;
its body retains historical entries and is not edited by this checkpoint.
Next gate: **WAITING_FOR_EXPLICIT_TEST_BUILD_APPROVAL**.


## 2026-10-27 JST — Shard2 patch.sh repository reconciliation

This latest entry supersedes the earlier stage-only note that shard2 was still
outside reviewed Git history. Preserve and publish the already-reviewed one-line
patch.sh context-menu fix; no rewrite or other patch behavior change. Fresh
fixed156/selected Vanadium source gives context-menu SHA256
`89380eab2e93a7c1f47782fa966f993642c2407a13b842518f7204e230e720c5`,
matching user-confirmed host post-fix. Target constant expression count0, exact
MOUSE/LONG_PRESS condition1, all surrounding file bytes unchanged.
Stage reconciliation b69195c remains ancestral; fresh TabImpl SHA remains
`de0b9b1bed2bd411c7ee4d0706ff2f943b082fdae3c76540bd70153095bb5831`.
Repository tests99 PASS (previous95 plus4 context-menu regressions), source/PiP
integration/model, actionlint/syntax/diff PASS; see
[shard2 review](docs/versanium/post-nullaway-shard2-reconciliation.md).
User reports shard2 exit0/no warnings/errors/constant diagnostic/OOM and later
chrome0–7/family/final-audit PASS. These host outcomes were NOT rerun/re-audited
here. Host patch.sh649b... and repository patch.sh4a922... are distinct whole-file
identities; host original bytes are unavailable, so remaining full-script diff
must be examined during saved integration review, not guessed or allowlisted.
Untracked stage helper/adapter/review files remain separate. Ready for the next
saved source/output/graph/tools/full-integration REVIEW, not Test Build approval.
No Actions, APK, real ErrorProne/NullAway, saved-tree apply, GN, sync/reset/clean,
merge, Release/tag or PR6 change. PR5 body cleanup remains a separate update target.

## 2026-10-27 JST — Post-NullAway repository reconciliation

Latest scoped repository change: remove the dead private TabImpl stage parameter
and four literal hook arguments in the current generator. Fresh fixed156 + selected
Vanadium reproduction equals user-confirmed post-fix TabImpl SHA256
`de0b9b1bed2bd411c7ee4d0706ff2f943b082fdae3c76540bd70153095bb5831`.
Direct hooks3 + environment1, old declaration/arguments0, no-arg declaration1,
mobile/null1. Native/JNI, passive diagnostic gates, zoom/F11/identity/signing unchanged.
User reports saved-host stage fix applied and PASS; corrected shard5, shard6/7
and family-audit evidence locations are recorded in
[reconciliation review](docs/versanium/post-nullaway-stage-reconciliation.md).
Host evidence bytes are not available here; do not turn this report into an
independent full-family audit, C++/APK build or device success claim.

Local repository validation: selected source reproduction, diagnostic/decision
Java doubles, DOM/native scope models, and repository tests; exact results in review.
Historical preparation positive fixture is now explicitly pinned to7b60873;
its original strict gate still rejects changed generator bytes. No old helper,
manifest, provenance, saved source/output or processor setting was changed.
Existing uncommitted shard2 patch.sh fix and host-only preparation work remain
outside this stage-only commit. Fresh full-build readiness is NOT approved:
review those pending changes and saved-output/full integration provenance first.
No Actions/APK/real-host analysis/GN/dependency sync/merge/release/tag here.

## Historical 2026-10-26 JST — Uncommitted chrome shard5 dead-label correction

User reports content0/1 and chrome0–4 PASS; chrome5 fails only on unused
TabImpl stage parameter; chrome6/7 unexecuted. Current generator removes the
unused parameter and four literal arguments, retaining hook positions/count,
mobile,null and passive diagnostic/native scopes. Current source tests now
assert all four hooks and reject callback revival. Selected fixed156/Vanadium
source generation PASS; passive Java doubles9, decision/dismiss doubles15 and
candidate DOM model37 PASS. These are NOT real Chromium NullAway/ErrorProne.
Host validation output is unavailable in this cloud; shard5 rerun NOT PERFORMED.
Existing uncommitted patch.sh shard2 fix and historical helpers/manifests retained.
No commit/push/PR update, GN, dependency sync, APK/Actions or shard6+ execution.


Latest collection9db02a6 stopped BEFORE CIPD/jars: small()1MiB cap rejected normal
inventory-bearing applied.json (sucsAo evidence). No new provenance finding.
Replacement complete collector is documented in cipd-collector-large-record-review.md:
separate bounded256MiB receipt reader with MemAvailable-based budget/schema/hash
validation; package limits retained. Five local fixture regressions PASS.
Old evidence/collector and applying controller7b60873 unchanged; no host retry run.

Latest host report (2026-10-26 JST): content candidate10 apply/verify PASS under
controller7b60873; TQNw0X/applied.json is the baseline, Default graph/output unchanged.
No verification output/GN/compile yet. User reports C226.6GiB vs WSL815GiB,
RAM available11GiB/swap32GiB; physical backing-volume capacity, not virtual free,
governs approval. Three actual processor jar SHA256 now recorded in
nullaway-cipd-host-followup.md; they identify observed bytes, not CIPD-instance proof.
Package-local metadata absence is inconclusive: gclient may manage at .gclient
root with central .cipd/pkgs metadata. Saved actual tool revision/layout remains
to be confirmed by one bounded read-only batch. Keep original applying controller
for --verify; docs-only compatibility proof does not rewrite old controller fields.

Latest host result (user-reported TQNw0X/read-only.json, controller7b60873):
READ_ONLY_COMPLETE; no product GN regeneration indicated by real graph+depfile;
saved ErrorProne=false, separate analysis records0, NullAway NOT_PROVEN.
No host source apply/GN/compile. Earlier discovery failures below are historical.
Isolated NullAway output plan prepared in docs/versanium/nullaway-isolated-output-plan.md.
Only future verification args: ErrorProne=true, static_analysis="on", warnings-as-errors=true;
Default args/output/old helper gate unchanged. Candidate source-only apply/verify
must precede candidate analysis; no Native-only analysis may validate new code.
Real source/graph/processor/shard coverage + synchronous successful execution
required before separate review of the gate; no NullAway PASS yet.

Latest product candidate: content ingress + cleanup persistent-false diagnostics
via WebContentsObserver/Android proxy/JNI, no content→chrome/TLS dependency.
Fixed renderer API/security/navigation/renderer-gone branches and generic wrapper/
dispatch brackets; generic arrival alone is not root attribution. False unchanged/
no-player/send begin/returned separate, none claims renderer completion.
New58 selection retains Native/no-B baseline; old helpers/manifests untouched.
See content-fullscreen-diagnostic-review.md and content-diagnostic-host-preparation.md.
Independent Native58/10-file host preparation now available; no host execution.
Native signed host APK hash user-confirmed: fba3cbd639abdb0c00d9e7c1d4621e61580efde1fb9126ce8545437261923bc7.
Signature record has no graph link: derive through actual source/provenance records; never rewrite it.
Saved NullAway graph/flag must be checked; ordinary Java is not NullAway proof.

Latest Native device trial: Galaxy S23, diagnosis/background/PiP ON, restart
confirmed, brief PiP/audio stop/no crash. Full72-stage log saved. Actual EAM
d1/controller d2 selects tab-caused exit; two d3/d4 guard returns are nested
loss/Base call-outs, not independent external counts. media_stopped44.083 is
before onStop stop_not_playing44.331; NO stop_suspend_called this trial.
Do not carry over Forward's SYSTEM-suspend attribution. Initial upstream exit
and earliest pause caller remain unknown; signed Native APK SHA256 now user-confirmed above.
See native-diagnostic-device-review-2026-10-25.md. No product/host changes or B.

Latest host report: source-only apply/verify PASS, GN gen exit0, toolchain
android_clang_arm64, no compile at native-diagnostic-evidence-NQzDtk. Audit failed
because partition(':') split escaped $:. Bytes lexer now decodes literal paths,
includes implicit outputs in duplicate checks, rejects unsupported variables.
Old source-record controller is preserved; audit-only descendant proof required.
See native-graph-escape-reaudit.md. No source/GN reapply or host operations here.

Latest native preparation: standalone prepare_native_diagnostic.py and new
post-GN audit_native_graph.py, no historical helper imports/changes. Baseline
built Forward lnxJen applied/after-apk/current provenance + distribution APK
0264aec7… exact hash.50 before/header absent→51 source-only after; other43/B,
tools/args/signing source/output preserved. Source apply and manual GN generation
are separate gates. GN required for modified BUILD.gn; objects resolved from
actual loaded bytes graph + GN source/rule/toolchain, no guessed target names.
See native-diagnostic-build-preparation.md. No real-host apply/GN/compile.

Latest candidate (2026-10-25 JST): EAM JNI entry/controller selected-branch/
context-output native diagnostics and synchronous nesting depth implemented.
Normal non-shutdown profile, HTTPS exact YouTube, diagnosis ON and live actual
WebContents/current-tab gates; no eligibility repeats or exit/stop behavior change.
50→51 selection retains Forward43/B exclusion. Content renderer/browser/security
initial ingress remains deferred/unmeasured; not a PiP fix. See
config-a-origin-forward-native-review.md. Old helpers unchanged, no host apply/build.

Latest Forward② evidence (2026-10-25 JST): restart confirmed; PiP briefly
visible/audio stopped/no crash. Wrapper→ExclusiveAccess forwarding precedes
accepted exit; normal Activity branch absent, downstream FullscreenManager not
excluded. Fixed156 EAM JNI→FullscreenController→context→Java Base path and
recursive WebContents exit chain verified in source. First native requester
remains unknown. See config-a-origin-forward2-review.md and complete device log.
Native diagnostic scope/lifetime/JNI/target design documented; no product fix,
saved-host changes or build. Existing67 tests/source audits remain bounded checks.

Latest preparation: prepare_config_a_origin_forward.py adds independent
read-only/explicit3-file apply/precompile verify against completed AOrigin
LfbK0s evidence (not A/installed). Pinned43 manifest, fixed-source reconstruction,
other40/B exclusion, external backup/intent/provenance/full output checks;
partial failure stops without rollback. See config-a-origin-forward-apply.md.
Java転送経路の確認用。native要求元は未確定。No saved-host apply/compile.

Latest candidate: AOriginForward adds wrapper-entry and existing Activity
delegate-branch fixed labels, plus a scoped current-tab controller bridge.
Baseline is built/signed AOrigin evidence config-a-origin-evidence-LfbK0s,
NOT A or installed60b.43-input selection changes3 Java files, retains other40
and excludes B. New diagnostic does not establish the initial native caller;
scoped native follow-up is considered but deferred pending bridge/lifetime review.
See docs/versanium/config-a-origin-forward-review.md. No saved-host apply/build.

Latest AOrigin② device evidence (2026-10-24 JST): restart directly confirmed;
no visible PiP, audio stopped, no crash. Framework entry precedes accepted exit
104ms, successful move-to-back108ms, SYSTEM suspend205ms; STOPPED/tab hidden
are subsequent. First requester remains unknown. Fixed156 external native→Java
wrapper→Activity delegate→FullscreenManager path bypasses local origin labels.
See [AOrigin② review](docs/versanium/config-a-origin2-review.md). B and all
saved-host operations/builds remain deferred; old helper/manifest gates unchanged.

Latest AOrigin preparation: new config-a-origin manifest adds original Base to A40 (41 total), preserves other39 and defines only two Java changes. New independent prepare_config_a_origin.py uses completed A applied.updated_provenance + A after-apk, never installed60b; reconstructs fixed-source before/after, defaults read-only, explicit two-file transaction with full external backups/intent/output state and precompile recheck. No B selection. See docs/versanium/config-a-origin-apply.md; real host41 preflight and new integration/device are pending. Previous A real compile/sign/log evidence remains confirmed. No saved-host apply/build/Actions authorized here.

Latest ConfigA evidence: user reports A signed APK4cae4391…c18317, same certificate and actual Java/APK compile/install success. New A OFF log identifies video permission denial after active fullscreen passes, no entry; ON confirms reason6 moveTaskToBack(true) returned true, reason7 then inactive, SYSTEM suspend returned, media_stopped and framework exit. First fullscreen-exit requester is still unproven. Supplied A posts do not directly reconfirm all instructed conditions/restart/crash outcomes; do not inherit older APK outcomes as new evidence. Two-Java-file origin diagnostic candidate records existing Base handler request branches only, with current normal YouTube tab gates, no extra permission/eligibility queries or exit-policy changes. B remains unapplied; existing zoom work is preserved. See docs/versanium/config-a-pip-origin-review.md. No new build/apply authorized here.

Latest config-A gate: user confirms b341 host applied/after-apk/current provenance equality and installed40/40 match. A apply/compile remains unperformed. New prepare_config_a.py is independent, A-only, default read-only, explicit one-controller-Java apply and precompile verify; fixed-source recipe and all40 before/after hashes are checked, full generated-output state and external backup/intent are retained. B remains deferred until A device logs. See docs/versanium/config-a-apply.md. No saved-host mutation/build/Actions authorized here.

Latest A/B coverage correction: f4a2601 real-host provenance/current inputs matched but installed manifest was37/40. Six inherited patch.sh operations affecting WebContentsImpl/Manifest/ChromeTabbedActivity were omitted from selected fixtures. Fixed156 reproduction now equals all three reported real hashes, inherited by installed/A/B; B WebContents hash is0156c1d1…00bb2. No skip/alternative-hash acceptance. Local51 checks and selected integrations PASS; corrected real-host40/40 remains pending. See docs/versanium/ab-pipeline-coverage-review.md. No saved-tree apply/build/Actions/merge/Release.

Latest preparation: stage A selects installed60b zoom plus257b PiP branch diagnostics; stage B adds3452 video zoom only after A device logs. No branch rollback. Temporary selected-source assembly asserts exact one-file A and two-file B deltas and records hashes in docs/versanium/ab-selection-manifest.json. Real saved-tree comparison must start from actual diagnostic applied.json + after-apk-provenance.json; no real-host gate/application is claimed. See docs/versanium/ab-test-preparation.md. Prior restart is directly user-reported; future restart remains instruction until reported. No apply/build/Actions/GN/sync/merge/release.

Latest PiP comparison (2026-10-24 JST): installed Diagnostic APK, smartphone YouTube100%, diagnosis/background ON, restart after changes user-reported. PiP candidate OFF: audio continues/home but no PiP, attempt blocked/no entry in supplied log; tab playback/manual stop work. PiP candidate ON: framework entry confirmed, dismiss6 +88ms, dismiss7 +181ms, stop_suspend +328ms (pre-call only), framework exit +374ms; tab and inline-home playback continue, manual stop/crash safety retained in reports. Candidate effect is conditional and must not be called globally ineffective. Narrow branch-only instrumentation is added; dismissal/stop policy remains unchanged pending first-cause evidence. Video zoom candidate at3452edd is retained and still unbuilt; these earlier APK logs do not validate it. See [comparison](docs/versanium/pip-device-comparison-2026-10-24.md). No build or saved-tree apply is authorized.

Current 2026-10-24 JST follow-up: user checkpoint confirms Diagnostic APK d01c7633… built/signed/installed with the same certificate; diagnosis-only smartphone/DeX playback and restart show no crash in reported conditions. Video fullscreen size tracks page zoom with diagnosis ON/OFF and also in old Titanium F11 Test (corrected comparison). New zoom correction defers to temporary zoom, avoids saving temporary setter changes, and applies a rendering-only100% override for DOM fullscreen plus effective video, restoring current environment zoom on exit. It is NOT compiled/device-tested. See [video zoom review](docs/versanium/video-fullscreen-zoom-review.md). Prior unbuilt-diagnostics status below is historical. Neither saved Run9 nor the four-file diagnostic recovery helper is modified/reused. PiP remains unresolved; no build/Actions/merge/Release authorized by this update.

> Authoritative operational status for the Versanium project. Update this file whenever repository roles, active branches, build policy, current milestones, or blockers change.

Last reviewed: 2026-10-24 JST (manual156 APK/device evidence; diagnostic CHECK hazard corrected, new APK unbuilt)

## Project

Versanium is an unofficial Android browser derived from Titanium Browser for Android. It targets normal smartphone use, large-screen Android use, Samsung DeX, and keyboard/mouse workflows.

User-facing product name and distributed APK branding are Versanium. Upstream attribution and inherited technical identity are preserved where changing them would break compatibility, provenance, signing, or migration behavior.

## Repository roles

| Role | Repository | Status |
|---|---|---|
| Primary / Source of Truth | `Nvoid911-Lab/Versanium` | Active |
| Secondary / backup | `Nvoid911/Versanium` | Active during migration; intended for archive after migration validation |
| Upstream reference | `jqssun/android-titanium-browser` | External upstream |

The Primary repository is authoritative. Normal synchronization direction is **Primary → Secondary**. Never infer repository roles from older migration reports or old chat history.

## Historical Git state at the 2026-10-19 review

Primary `Nvoid911-Lab/Versanium`:

- default branch: `main`
- `main`: `4ca486ba88313aa95bbccf67812435c13edb3bc7`
- reviewed `migration/versanium` synchronization point before this status refresh: `1fe02df8dd2a7dd7d31582229e2a3b47ef4989be`
- relevant preserved branches include `feature/dex-mobile-zoom`, `feature/f11-toolbar`, `feature/youtube-pip`, and `update/titanium-155.0.8059.79`

Secondary `Nvoid911/Versanium` at review:

- default branch: `main`
- `main`: `6755ccfd5d5c8a5e8fa3620be6da9ccd4a399aa7`
- reviewed `migration/versanium` synchronization point: `1fe02df8dd2a7dd7d31582229e2a3b47ef4989be`

On 2026-10-19, Secondary `migration/versanium` was first fast-forwarded from `a8098ae78f82b91b1a8dc48a54d4bcc514177207` to `b40976ec3c209c805fba5326f2326e8324fc64d2` in a 15-commit non-force synchronization. Two documentation commits were then fast-forwarded to `d2ef18cef2f7fa82c131c6f2716e1d34c23fd66a`. After the Project Sources refresh policy was formalized in `RULES.md`, one additional documentation commit was fast-forwarded to `1fe02df8dd2a7dd7d31582229e2a3b47ef4989be`. Each synchronization used the normal Primary → Secondary direction with no force push and was followed by SHA equality verification.

This `PROJECT_STATUS.md` refresh itself creates a newer Primary commit after the reviewed synchronization point above; synchronize that resulting reviewed Primary ref to Secondary before treating the control plane as fully synchronized again.

The `main` branches remain separate and are not implicitly synchronized by migration-branch operations. Any `main` change remains a separate consequential operation requiring review and approval.

## Build and release policy

Current `migration/versanium` workflow facts on Primary:

- workflow: `Versanium Build`
- trigger: manual `workflow_dispatch` only
- allowed repositories: the two Versanium repositories only
- runner provider is manually selected from reviewed choices: `blacksmith`, `sengi`, or `ideapad`
- runner labels are constrained to `blacksmith-8vcpu-ubuntu-2404`, `sengi-standard-8-ubuntu-2404`, and `versanium-ideapad`
- default build is Test
- Test artifact: `Versanium-Test`
- artifact retention: 7 days
- production approval flag: `VERSANIUM_RELEASE_APPROVED: 'false'`
- production stage/publish/attest is restricted to `Nvoid911-Lab/Versanium`
- no production release is authorized until explicit user approval after testing

Older documentation that maps a fixed runner to each repository is historical. The current Primary workflow allows selection between the three reviewed providers while still rejecting arbitrary runner labels.

## Identity and compatibility policy

Do not perform broad Titanium→Versanium replacement. Preserve inherited identifiers where required for compatibility and provenance.

Current project intent:

- user-facing branding: Versanium
- upstream attribution: retained
- signing configuration: retained unless explicitly approved
- internal Titanium identifiers and compatibility-sensitive storage/resource identifiers: retained unless a specific migration is designed and validated
- Test builds must remain isolated from the normal installed app identity

## Current development status

Completed or established:

- repositories renamed to Versanium
- Primary/Secondary roles corrected: Lab is Primary; Personal is Secondary
- migration branch contains branding/migration work and test/release guards
- Primary/Secondary `migration/versanium` reviewed history synchronized by non-force fast-forward through `1fe02df8dd2a7dd7d31582229e2a3b47ef4989be` on 2026-10-19
- Project Sources refresh triggers, ordering, notification, and freshness verification are formalized in `RULES.md` and mirrored in the Notion Project Hub
- Titanium 155.0.8059.79 update work is preserved
- DeX/mobile zoom work is preserved
- F11 toolbar/certificate diagnostic work is preserved
- YouTube PiP investigation remains a separate experimental history
- CircleCI is retired from the intended project workflow; GitHub Actions is the supported CI/build path

Still requiring validation before production release:

- synchronize this status-refresh commit Primary → Secondary before considering the documentation control plane fully synchronized
- regenerate and replace `Versanium_Project_Context.md` after that synchronization
- review the latest Titanium/upstream delta before the next Test build
- review build optimizations before the next Test build
- retain awareness of the Titanium/Chromium YouTube PiP issue during browser validation
- run a manual GitHub Actions Test build only when the user explicitly chooses to do so
- validate APK on Galaxy S23 / Android 16 / One UI 8.5, including smartphone and Samsung DeX behavior
- production Release remains blocked until explicit approval

## Working responsibility split

- **ChatGPT:** project coordinator; requirements, research, architecture, documentation, GitHub inspection/edits when available, Codex instructions, build-error analysis, and final decisions with the user.
- **Codex:** repository implementation, editing, tests, commits, synchronization, and PR work when Codex is available and selected for the task.
- **GitHub Actions:** automated build/test/release execution only under the checked-in workflow and approval gates.
- **User:** approves consequential transitions, manually validates device behavior, and authorizes Test/Release execution where required.

## Start-of-chat rule

Any ChatGPT conversation working on Versanium should first resolve current project state in this order:

1. live GitHub state in Primary;
2. these four authoritative project documents;
3. current ChatGPT Project Sources;
4. Notion planning/history pages;
5. Memory;
6. older individual chat content.

If sources conflict, higher-ranked evidence wins and the conflict must be recorded in `DECISIONS.md` or this status file as appropriate.
## 2026-10-22 — IdeaPad Run #5 recovery proposal

Live Primary integration HEAD checked before this change: `6e7517e6de89e5a1230cebf906470795112466a3` (PR #2 merged). Secondary synchronization after the October 19 snapshot has not been reverified; do not infer equality.

Run #5 (`39567794721`, job `119114201472`) is completed/cancelled. Build step ran from 2026-10-21 17:15:05 to 23:15:29 JST with no explicit timeout override in the original workflow, consistent with the default 360-minute timeout. Full log retrieval failed, so exact last target and build-time OOM absence remain unverified.

User-provided local evidence: Chromium 53GB, `out/Default` 14GB, retained Ninja/Siso state, patched Chromium HEAD prefix `8b1224debc`, arm64 Versanium Test package, no remaining compiler processes, and Windows C: free 323088138240 bytes. Current idle swap usage and empty current dmesg search do not prove build-time memory behavior.

This proposed change adds `resume_ideapad` (default false) to the existing manual workflow. Recovery is restricted to Primary + IdeaPad + Test, retains the original source/output paths, checks the pinned Run #5 inputs, and uses a child controller checkout so checkout cleanup does not touch the preserved tree. It bypasses build.sh setup/hooks/patching/sudo and resumes chrome_java then chrome_public_apk. Recovery alone has a 1200-minute job timeout and resource telemetry. Normal IdeaPad builds refuse an existing workspace before checkout. Old workflow reruns do NOT gain this protection.

Validation: 20 local migration/recovery unit checks and shell syntax checks pass. No Actions build, on-device validation, merge, production release, or Secondary synchronization was performed for this proposal. General persistent-workspace provisioning and automatic source-update handling remain future work; this is narrowly scoped recovery, not a general cache implementation.

Next: review/merge the recovery PR into migration/versanium; verify upstream/PiP awareness required by RULES before authorizing a new manual Test run. Dispatch the new branch revision with runner_provider=ideapad, f11_test_build=true, resume_ideapad=true. Never rerun Run #5. Review telemetry and validate the APK on Galaxy S23 and DeX. Refresh Notion/Project Sources after authoritative integration and reviewed synchronization settle; the October 19 Context is stale regarding IdeaPad and build state.


## 2026-10-22 — Limit IdeaPad recovery to six jobs (proposal)

PR #3 was merged into migration/versanium at 630c950c8e6cc940a85c9a5cf4aad5a7c0473c61. The resulting Run 39624481319 was explicitly cancelled by the user; GitHub confirms completed/cancelled. It must not be treated as a successful Test build.

At about 10h53m, the user reported 1951/37342 tasks. A naive task-count extrapolation is not a reliable completion forecast. Longer vmstat samples showed repeated swap-in/out, swap-out peaks around 27MB/s, free memory dipping to about 80MB, and kernel CPU up to 52%. Twelve clang++ processes were present. This supports reducing concurrency to relieve memory pressure; it does not exclude sleep, power or thermal limits.

Proposed change: pass -j 6 to both recovery autoninja targets. Preserve source paths, GN args, existing outputs, signing isolation, guards and the 20-hour timeout. There is no clean/reset or new build dispatch. Actual improvement must be measured after review/merge and explicit Test execution. Validation: 21 migration/recovery unit checks, inline shell syntax, bash -n and git diff --check. General persistent provisioning and Secondary/Notion/Project Sources refresh remain pending; do not interpret earlier proposal snapshots as current build success.

## 2026-10-23 — Successful 155 recovery and next-Test review

This section supersedes the *current-state* wording of the October 22 proposal snapshots above; their historical evidence remains intact. Live Primary integration before this work was `d64b78be40b15dee889c24c67ba689777e090ca7`.

Run [39765620887](https://github.com/Nvoid911-Lab/Versanium/actions/runs/39765620887) is **success**, using the saved original 155 source through the IdeaPad recovery route. It did not reapply a new PiP fix. The user confirmed F11, smartphone YouTube PiP/tab-background failures and working DeX playback/PiP. Mobile/DeX zoom is in use; backup/restore is now required. APK binary inclusion has not been independently inspected.

A review branch `next-test/156-zoom-transfer-pip` proposes the official stable Titanium 156.0.8078.47 input, native patch adaptation, SAF zoom backup/restore, opt-in YouTube-only candidates/diagnostics and an isolated fresh IdeaPad tree with provenance. These are **implemented review candidates with limited local checks, not built or device-verified**. See [next-Test review](docs/versanium/next-test-156-review.md) for exact revisions, test scopes and the device matrix.

The 156 revision rejects old resume mode. It preserves the old successful tree/output and uses a new run-ID directory for a fresh build. Do not reinterpret old state as a new source version. No Test Build is authorized in this work unit: review comes first and the user controls later manual execution.

Outstanding before calling it build-ready: pinned AndroidX package access (network proxy HTTP403), actual SAF preference screen/type/lifecycle verification, complete JNI/native/GN integration checks where feasible, local Windows/WSL/account/capacity evidence, and review of the limited inline-PiP candidate. Main still has old Titanium-facing presentation; a separate documentation-only main PR is proposed without promoting code or releasing an APK.

Notion/Project Sources were unavailable to this workspace and have not been marked updated. At least the October 19 context described above is historical. After reviewed integration and Primary→Secondary synchronization settle, verify/refresh the canonical context following RULES; do not label this unmerged proposal a settled release.


### PR5 follow-up review (unmerged)

The review branch now preserves legacy finite zoom values in backups, explicitly rejects numerically unsafe SAF restores without changing current data, and restores only owned PiP attributes across same-document display moves. The frame-wide native CHECK exception has been replaced by a dedicated fixed-payload JNI route; generic JavaScript APIs retain pinned upstream restrictions. Migration/root branch state remains unchanged pending PR5 review. Exact AndroidX snapshots, cloud403 classification, unverified SAF/native/device conditions and read-only build-host/ref/input steps are in the review report. PR6 remains a separate unmerged main presentation change. No Actions/build/Release/tag/main merge was performed.


## Run9 — actual156 build failure and limited recovery preparation

Run39951209951 / #9 used7d9102f4f0e35dec9f69425de44cd889836a88ac and failed. API confirms Build failure/provenance upload; the user's log reports GN generation and chrome_java success, then native failure because the fixed GURL API has host(), not host_piece(). The old model's invented API and our incomplete real-header review did not detect it. The Run9 task counts are not an ETA/reuse guarantee.

This branch corrects exactly three calls, preserves every scope restriction and adds pinned-header comparison. A NEW156 manual preflight/apply/verify helper validates the original artifact digest and provenance, existing source/output paths, GN arguments/toolchain/state, then can change only that native scope's accessors. It never compiles or cleans/syncs/repatches/moves the tree. Old155 recovery and the Workflow remain untouched. See [Run9 recovery](docs/versanium/run9-incremental-recovery.md) for the actual-object-first future command, evidence links and STOP conditions.

The cloud could not download the original artifact/log payload; actual host provenance/state/object target verification and object compilation have NOT occurred here. The helper's temporary-fixture tests are not a host recovery. This information-source update precedes any future resumption. No Actions/build/main merge/Release/tag has been executed as part of this correction. The former 'unbuilt156' text above is historical; Run9 attempted156, with no successful APK established. PR6 remains separate.

### Run9 preflight parser follow-up

The user ran read-only preflight with controller093f787 and encountered UnicodeDecodeError at byte1319 in the unrelated android_clang_arm rust/lazy_static lib.ninja. The parser also incorrectly treated same-basename objects in other toolchains as ambiguous. The original Run9 log confirms the failed target is obj/content/browser/browser/render_frame_host_impl.o. The user confirms no saved source/output change or compilation occurred before this stop.

The helper now reads build definitions as bytes without lossy decoding, requires exactly one definition of that exact logged target, and checks cxx plus the exact explicit source. Duplicate definitions reject even when identical; other toolchains are distinct. Regression tests cover those cases and byte preservation. All prior provenance/original SHA/GN/toolchain/limited-diff/output guards remain intact. Next step is a new read-only preflight using the updated separate controller and a fresh evidence filename, not apply/build. Updated host preflight and native compilation remain unverified; see the Run9 report. No Actions/build/main merge/Release/tag was performed.

## 2026-10-24 — Manual156 success and diagnostic crash blocker

User Context v1.9 sections17–18 report real object/APK incremental success, existing-key signing and S23 installation. Signed APK SHA256:87c5b11aea148856f13cc7aab46a5ac1d2b4a0590ae068c19a2e7a52fa5837cf. Run9 remains failure; no new Actions artifact. F11/zoom/backup/restart basics work. Diagnostics alone crashes mobile and DeX; background-only improves tab playback but PiP flashes/closes; PiP-only does not improve defaults. Earlier unbuilt/host-unverified statements above are historical. Data-clearing recovery prevents claiming untouched155 data migration success.

Static investigation found an unconditional diagnostic native permission getter whose observer CHECKs require a fullscreen player. This hazard is removed, but no crash stack confirms the user's root cause. Diagnosis now only logs existing controller stages; it cannot authorize candidate JNI/JS or result callbacks. Background candidate code remains unchanged. No speculative PiP exit/suspension fix is included. See [device review](docs/versanium/156-device-diagnostics-review.md) for evidence, tests and safe next comparison. New code is NOT built/device-tested. The old three-token Run9 recovery controller must not be used for this correction. No Actions, saved-tree apply, merge, Release or tag. External Notion/Project Sources updates are not claimed.

### Next Test incremental preparation (target60b0037)

A separate read-only-first helper and [reviewable preparation](docs/versanium/next-test-diagnostic-build-preparation.md) now define how to compare the APK-completed saved Run9 tree with the diagnostic correction. Exact selected-source comparison identifies four changed applied files: PiP controller Java, TabImpl Java, RFH C++, and about_flags C++. The fixed payload header, WebContents JNI/API/implementation, BUILD.gn and flag metadata are unchanged and pinned by hash. Old `prepare_run9.py` remains unchanged and strict.

Real-host preflight has NOT run. It requires the original ZIP, prior ebfc applied evidence and an actual saved post-correction provenance JSON; it recomputes source/GN/toolchain provenance and derives the RFH/about_flags objects plus chrome_java from the saved graph. Future apply is explicit and separately authorized; future narrow gates are chrome_java then both actual C++ objects, with provenance before any separately approved APK continuation. PiP remains unresolved. No saved-tree mutation, build, Actions, merge, Release or tag occurred in this preparation.

The first real-host read-only attempt at controller b401856 stopped safely before mutation/compilation on flag-metadata hash drift. Investigation proved the old expected293f hash was from a selected-source fixture that skipped patch.sh's 11 expiry overrides and added only the three Versanium flags. Fixed HEADc155 → ordered expiry-only47f → exact candidate insertion now reproduces dc5, equal to the user-reported saved hash. The helper now derives and directly compares this pipeline; it does not allowlist the observed hash alone. Actual host bytes were not uploaded, so cloud evidence is exact generation plus SHA equality; the corrected host preflight remains pending.

Content-origin preflight630a64b stopped at JNI discovery in host evidence oj2Q3e;
no apply/GN/compile. Fixed156 jni_zero template confirms missing jni_headers path.
New graph audit checks full gen/jni_headers/.../WebContentsObserverProxy_jni.h,
exact action/default arm64 identity, direct Java input and native/Java dependency
closure. Java/NullAway remains NOT REACHED on host. Use new evidence/controller;
see content-diagnostic-host-preparation.md JNI correction section.

Host b85fc37 JNI discovery PASSED, Java discovery stopped (NDSMal); no apply/GN/
compile. Java family now derived from exact fixed156 rule/default toolchain,
source/outputs/recipe and dependencies, never Ninja filename. Separate ErrorProne
and shard actions scanned independently; compiler flag absence is not analysis
absence. Actual host Java/NullAway inspection remains incomplete and unexecuted.

2026-10-26 latest CIPD collection v2-5N3hJj user report: depot4be4e4628e093c4ad50210db5dcfa05a88280bda matches expected, tracked clean; central root chromium and3 exact package/subdir/instances found. Manifest sizes/hash correspond to reported actual jars. Primary LUCI iid/caspb/manifest sources confirm rawURLBase64(digest+tag02)=SHA256. New external receipt and isolated-output→GN-only steps in cipd-content-receipt-and-gn-preparation.md. Local consistency is not independent authenticity; actual receipt not run. Candidate58/Default/controller7b preserved; no output/GN/analysis.
