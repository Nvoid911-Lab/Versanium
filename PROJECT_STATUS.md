# Versanium Project Status

> Authoritative operational status for the Versanium project. Update this file whenever repository roles, active branches, build policy, current milestones, or blockers change.

Last reviewed: 2026-10-19 JST

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

## Current Git state at review

Primary `Nvoid911-Lab/Versanium`:

- default branch: `main`
- `main`: `4ca486ba88313aa95bbccf67812435c13edb3bc7`
- reviewed `migration/versanium` synchronization point: `b40976ec3c209c805fba5326f2326e8324fc64d2`
- relevant preserved branches include `feature/dex-mobile-zoom`, `feature/f11-toolbar`, `feature/youtube-pip`, and `update/titanium-155.0.8059.79`

Secondary `Nvoid911/Versanium` at review:

- default branch: `main`
- `main`: `6755ccfd5d5c8a5e8fa3620be6da9ccd4a399aa7`
- reviewed `migration/versanium` synchronization point: `b40976ec3c209c805fba5326f2326e8324fc64d2`

On 2026-10-19, Secondary `migration/versanium` was fast-forwarded from `a8098ae78f82b91b1a8dc48a54d4bcc514177207` to the reviewed Primary documentation head `b40976ec3c209c805fba5326f2326e8324fc64d2`. The transfer contained 15 commits, used no force push, and the two migration refs were verified at the same SHA after synchronization.

The `main` branches remain separate and are not implicitly synchronized by the migration-branch operation. Any `main` change remains a separate consequential operation requiring review and approval.

## Build and release policy

Current `migration/versanium` workflow facts on Primary:

- workflow: `Versanium Build`
- trigger: manual `workflow_dispatch` only
- allowed repositories: the two Versanium repositories only
- runner provider is manually selected from reviewed choices: `blacksmith` or `sengi`
- runner labels are constrained to `blacksmith-8vcpu-ubuntu-2404` and `sengi-standard-8-ubuntu-2404`
- default build is Test
- Test artifact: `Versanium-Test`
- artifact retention: 7 days
- production approval flag: `VERSANIUM_RELEASE_APPROVED: 'false'`
- production stage/publish/attest is restricted to `Nvoid911-Lab/Versanium`
- no production release is authorized until explicit user approval after testing

Older documentation that maps a fixed runner to each repository is historical. The current Primary workflow allows selection between the two reviewed providers while still rejecting arbitrary runner labels.

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
- Primary/Secondary `migration/versanium` reviewed history synchronized by non-force fast-forward on 2026-10-19
- Titanium 155.0.8059.79 update work is preserved
- DeX/mobile zoom work is preserved
- F11 toolbar/certificate diagnostic work is preserved
- YouTube PiP investigation remains a separate experimental history
- CircleCI is retired from the intended project workflow; GitHub Actions is the supported CI/build path

Still requiring validation before production release:

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