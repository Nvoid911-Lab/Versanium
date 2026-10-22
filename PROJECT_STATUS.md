# Versanium Project Status

> Authoritative operational status for the Versanium project. Update this file whenever repository roles, active branches, build policy, current milestones, or blockers change.

Last reviewed: 2026-10-22 JST (IdeaPad recovery proposal; not yet device/build validated)

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
