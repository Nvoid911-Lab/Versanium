# Versanium Project Rules

> Stable operating rules for Versanium. `PROJECT_STATUS.md` records changing state; this file records the rules that govern how state may change.

Last reviewed: 2026-10-19 JST

## 1. Source-of-truth hierarchy

When information conflicts, use this order:

1. actual current GitHub state in `Nvoid911-Lab/Versanium`;
2. `PROJECT_STATUS.md`, `RULES.md`, `ARCHITECTURE.md`, `DECISIONS.md` on the active reviewed Primary branch;
3. ChatGPT Project Sources;
4. Notion project planning/history;
5. ChatGPT Memory;
6. older chat messages, handoff notes, or historical reports.

Historical documents remain useful as provenance but must not override a newer authoritative decision.

## 2. Repository roles

- Primary / Source of Truth: `Nvoid911-Lab/Versanium`.
- Secondary / backup: `Nvoid911/Versanium`.
- Normal synchronization direction: Primary → Secondary.
- Secondary must not become the source of new authoritative changes while it is designated backup.
- After migration is validated, Secondary may be archived as previously decided.
- Never force-push merely to make the repositories look synchronized. Stop and investigate divergence first.

## 3. Branch and change policy

- Development/migration work stays off `main` until reviewed and approved.
- `migration/versanium` is the current integration branch for the Versanium migration.
- Feature/diagnostic histories may remain on dedicated branches until intentionally integrated.
- Do not merge to `main`, create a release, create a production tag, or change release approval merely because local checks pass.
- Consequential identity, signing, release, or repository-role changes require explicit user approval.

## 4. Build policy

- GitHub Actions is the supported automated build path.
- CircleCI is retired and must not be reintroduced without a new explicit decision.
- Do not trigger Actions merely to inspect configuration or because documentation changed.
- Before the next Test build, review:
  - current Titanium/upstream version and relevant differences;
  - build optimization opportunities and risks;
  - known Titanium/Chromium YouTube PiP behavior and any relevant fixes/regressions.
- Test-first policy remains in force.
- Production Release remains blocked while `VERSANIUM_RELEASE_APPROVED` is false.
- A production release requires explicit user approval and must execute only from the Primary repository under the checked-in release guards.

## 5. Product identity and upstream policy

- User-facing name: Versanium.
- Versanium remains an unofficial derivative of Titanium Browser for Android.
- Preserve upstream attribution and license information.
- Do not globally replace `Titanium`/`titanium` strings.
- Package/application IDs, signing identity, internal compatibility identifiers, storage keys, authorities, resource identifiers, and inherited upstream identifiers must not be changed casually.
- Any identity migration requires a scoped plan, compatibility analysis, tests, and explicit approval.
- Test builds must use an isolated test identity when the current implementation provides one.

## 6. Roles: ChatGPT / Codex / GitHub Actions / User

### ChatGPT

Acts as project coordinator and decision-support layer:

- clarify requirements and constraints;
- inspect current GitHub state before relying on remembered state;
- research upstream/current issues;
- design implementation and migration plans;
- maintain authoritative project documentation when changes are made through ChatGPT;
- prepare precise Codex instructions when Codex is used;
- analyze build/test failures;
- identify conflicts between sources instead of silently choosing stale information.

### Codex

When available and intentionally used:

- edit repository files;
- run local/repository tests;
- commit/push reviewed implementation;
- synchronize approved refs;
- prepare PRs;
- report exact changed files, tests, and commit SHAs back to ChatGPT/user.

### GitHub Actions

- execute checked-in automated build/test/release workflows;
- never substitute for user approval gates;
- production release behavior must remain fail-closed.

### User

- approves consequential transitions;
- decides when to spend build capacity/run manual workflows;
- validates APK behavior on real hardware;
- explicitly authorizes production release.

## 7. Documentation update rule

A decision is not considered fully synchronized across chats until the durable sources are updated.

When a change affects project state:

1. implement/verify the change in Primary where applicable;
2. update `PROJECT_STATUS.md` in the same work unit;
3. update `ARCHITECTURE.md` if structure or technical boundaries changed;
4. append the decision and rationale to `DECISIONS.md` if it changes policy, roles, architecture, or an earlier decision;
5. update `RULES.md` only when a stable operating rule changes;
6. synchronize the reviewed Primary ref to Secondary;
7. update the Notion project hub/history when the change matters for planning or human-readable history;
8. refresh ChatGPT Project Sources when their snapshot/reference is stale.

Do not duplicate every transient detail in every system. GitHub carries technical truth; Notion carries planning/history; Project Sources provide the shared ChatGPT entry point.

## 8. ChatGPT Project Sources rule

Project Sources should contain or point to a compact Versanium project index that states:

- Primary and Secondary repository roles;
- source-of-truth hierarchy;
- the four authoritative GitHub documents;
- Notion's role;
- instruction to verify live GitHub state before answering state-sensitive questions.

Project Sources are a shared context layer, not a replacement for live GitHub verification.

### 8.1 Canonical Project Sources file

- The canonical shared-context filename is `Versanium_Project_Context.md`.
- Keep the filename stable when refreshing it so multiple dated or differently named snapshots do not coexist and create ambiguity.
- The file is an index/snapshot, not technical Source of Truth. Live Primary GitHub and the four authoritative GitHub documents remain higher priority.
- A stale Project Sources snapshot must never override newer live Primary state.

### 8.2 Refresh triggers

ChatGPT must evaluate Project Sources freshness during Versanium work. Refresh is required when a confirmed change makes the current context materially stale, including changes to:

- Primary/Secondary repository roles or synchronization state;
- active integration branch or an important recorded branch HEAD/reference;
- `PROJECT_STATUS.md`, `RULES.md`, `ARCHITECTURE.md`, or `DECISIONS.md` when the changed content is represented or summarized in Project Sources;
- build/CI architecture, runner policy, Test/Release gating, or release policy;
- product architecture, major feature status, compatibility/identity policy, or upstream relationship;
- stable project roles, operating rules, or material decisions;
- major completed/current/next-work state used for cross-chat handoff;
- Notion planning/history when the Project Sources snapshot explicitly mirrors that information;
- any conflict where Project Sources no longer matches live Primary GitHub.

A refresh is normally not required for transient investigation notes, speculative ideas, failed temporary experiments, or minor commits that do not change the shared project snapshot.

### 8.3 Refresh decision and notification

- ChatGPT is responsible for detecting when a refresh trigger has occurred during work it can observe.
- When a refresh is required, ChatGPT must explicitly tell the user that `Versanium_Project_Context.md` is stale and identify the material reason.
- Do not silently continue treating a known-stale snapshot as current.
- If the user must manually replace the Project Sources attachment, ChatGPT must generate the replacement file and clearly request replacement of the old canonical file with the new one.

### 8.4 Refresh order

Unless a recovery situation requires otherwise, refresh in this order:

1. verify live Primary GitHub state;
2. implement and verify the technical/state change;
3. update the four authoritative GitHub documents as applicable;
4. synchronize the reviewed Primary ref to Secondary without force and verify the result;
5. update Notion when planning/history changed materially;
6. regenerate `Versanium_Project_Context.md` from the resulting authoritative state;
7. notify the user that Project Sources replacement is required;
8. user replaces the old canonical Project Sources file with the regenerated file;
9. subsequent chats use the refreshed context, while still verifying live GitHub for state-sensitive work.

Do not regenerate the canonical context before the authoritative GitHub state for that work unit is settled. This avoids immediately creating another stale snapshot.

### 8.5 Freshness verification

After a Project Sources refresh:

- verify that repository roles and the source hierarchy are still correct;
- verify that any recorded important branch/ref state matches the intended post-change state;
- verify that summaries of the four authoritative documents do not contradict those documents;
- verify that completed/current/next-work sections reflect the settled work unit;
- remove superseded current-state claims rather than preserving them as if still active;
- preserve historical facts only when they remain useful and are clearly labeled as history.

If Project Sources and live GitHub disagree at any later time, live Primary GitHub wins and this refresh procedure must be invoked again when the difference is material.

## 9. Notion rule

Notion is for:

- roadmap and planning;
- discussion summaries;
- decision context that is useful to humans;
- backlog and unresolved questions;
- links back to authoritative GitHub documents.

Notion must not silently override live code, branch state, CI configuration, or the four authoritative GitHub documents.

## 10. Conflict handling

When two sources disagree:

- do not merge the claims into an invented compromise;
- verify live GitHub state;
- identify which source is stale;
- correct the durable documentation;
- record a material policy correction in `DECISIONS.md`;
- only then continue implementation based on the corrected state.

## 11. Script/instruction presentation preference

When giving the user Termux or similar shell-script replacements, prefer a complete copy-paste version suitable for deleting the existing file contents in `nano` and replacing them in one operation, rather than fragmentary patches.

## 12. User-specified information-source checkpoint (2026-10-24)

Before every Test/normal/rebuild/resume, create or refresh and present the current information-source file. Also create a real downloadable file when asked to make/update an information-source or handoff file, including unmerged/in-progress state clearly labeled as such. Refresh material build/PR/device outcomes before the next decision. Do not require a merge or interrupt an authorized operation solely to call a snapshot settled.

Record JST date, purpose/delta, repository roles, branch/SHA/PR, upstream pins, exact build path/inputs/Test identity, prior outputs, verified/unverified results, known risks and device criteria. Check current runner/WSL/memory/disk/concurrency before execution; never reuse old readings as current. After execution record actual run/attempt/head/time/runner and outcome/artifact; never invent future runs. File creation is not authorization to start a build. Preserve the user's latest execution prohibition.

Use Versanium_Project_Context.md with version/history inside. Present a download link; Project Sources replacement by the user, GitHub documents and Notion synchronization are separate operations. State any unavailable/unsynchronized layer. Include references and approval scope without Secrets/keys/authentication data. This supplements section8's settled-state ordering for explicitly requested pre-build/in-progress snapshots.
