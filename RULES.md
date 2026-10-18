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