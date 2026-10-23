# Versanium Decision Log

> Append-only record of material project decisions. Correct mistakes with a new decision entry; do not silently rewrite history except to fix formatting or factual transcription errors.

## 2026-10-19 — Establish durable cross-chat project control plane

**Decision:** Use GitHub, Notion, and ChatGPT Project Sources together rather than relying on chat-to-chat memory.

**Authority model:**

1. live GitHub state in Primary;
2. four authoritative GitHub documents;
3. ChatGPT Project Sources;
4. Notion planning/history;
5. Memory;
6. older individual chats/handoffs.

**Reason:** Separate ChatGPT conversations do not reliably carry the entire detailed state of every other conversation. Durable project sources reduce stale assumptions and make conflicts auditable.

**Operational consequence:** Any material state/policy change must update the appropriate GitHub control document. Notion and Project Sources are then refreshed as needed.

## 2026-10-18 — Correct repository roles

**Decision:** `Nvoid911-Lab/Versanium` is Primary / Source of Truth. `Nvoid911/Versanium` is Secondary / backup.

**Supersedes:** Earlier migration documentation that described `Nvoid911/Versanium` as Primary and the Lab repository as Secondary.

**Synchronization direction:** Primary → Secondary.

**Long-term intent:** After migration validation, the Personal Secondary repository may be archived.

**Reason:** The user explicitly corrected the earlier Primary/Secondary assumption and selected the Lab repository as the main authoritative repository.

## 2026-10-18 — CircleCI retired

**Decision:** CircleCI is no longer part of the intended Versanium CI/build architecture. GitHub Actions is the supported automated build path.

**Consequence:** Do not reintroduce CircleCI configuration without a new explicit decision.

## 2026-10-18 — Test-first release gating

**Decision:** Migration work must be validated through Test builds before production release. Production release is not implied by successful local tests or successful Test builds.

**Current gate:** `VERSANIUM_RELEASE_APPROVED` remains false until explicit user approval.

**Production repository:** Production stage/publish/attest is restricted to `Nvoid911-Lab/Versanium` under the current corrected repository-role model.

## 2026-10-18 — Preserve compatibility-sensitive inherited identity

**Decision:** Versanium is the user-facing project/product identity, but inherited package/application IDs, signing configuration, internal Titanium identifiers, upstream attribution, storage/resource identifiers, and other compatibility-sensitive values are not globally renamed.

**Reason:** Branding and technical identity are different layers. Broad replacement risks breaking updates, stored data, permissions, signing, extensions, build logic, or provenance.

**Consequence:** Identity changes require scoped migration design and validation.

## 2026-10-18 — Preserve feature histories separately until integration is intentional

**Decision:** DeX/mobile zoom, F11 toolbar/certificate work, Titanium version-update work, and YouTube PiP diagnostics may exist as separate branch histories. Branch presence does not mean automatic integration into stable/main.

**Specific note:** YouTube PiP diagnostic work remains experimental unless explicitly integrated after review.

## 2026-10-18 — Runner configuration evolved; current workflow wins

**Historical state:** Commit `a8098ae78f82b91b1a8dc48a54d4bcc514177207` implemented a fixed repository→runner mapping.

**Current reviewed Primary state:** Later migration commits changed the workflow to a constrained `runner_provider` choice (`blacksmith` or `sengi`) while keeping an allowlist of the two Versanium repositories and preventing arbitrary runner labels.

**Decision:** Treat the current Primary workflow as authoritative. Do not resurrect the older fixed repository→runner mapping solely because it appears in historical documentation or Memory.

## 2026-10-19 — Synchronization discrepancy discovered during control-plane setup

**Observation:** At the start of this documentation pass, Primary `migration/versanium` was at `7a3beb16851ce22989018ac609a7c98693231fc9`, while Secondary `migration/versanium` was still at older commit `a8098ae78f82b91b1a8dc48a54d4bcc514177207`. Primary and Secondary `main` also did not share the same tip.

**Decision:** Do not reinterpret this as a role reversal. Primary remains authoritative. Synchronize reviewed migration refs Primary → Secondary without force when ancestry permits. Main synchronization remains a separate consequential operation and is not performed merely as part of documentation setup.

## 2026-10-19 — Complete Primary → Secondary migration branch synchronization

**Decision:** Fast-forward Secondary `Nvoid911/Versanium` branch `migration/versanium` to the reviewed Primary documentation head.

**Previous Secondary head:** `a8098ae78f82b91b1a8dc48a54d4bcc514177207`

**Synchronized head:** `b40976ec3c209c805fba5326f2326e8324fc64d2`

**Transfer:** 15 commits, Primary → Secondary.

**Safety:** The Secondary head was verified as an ancestor of the Primary head before push. A normal fast-forward push was used; no force or force-with-lease operation was used.

**Verification:** After push, Primary and Secondary `migration/versanium` resolved to the same SHA, and the synchronized commit was independently retrievable from both repositories.

**Consequence:** The migration-branch discrepancy recorded earlier on 2026-10-19 is resolved. The two `main` branches remain outside this synchronization decision and must not be changed merely to make their tips match.

## Decision-entry template

For future material decisions append:

```text
## YYYY-MM-DD — Decision title

Decision:
Supersedes (if any):
Reason:
Consequences:
Verification / evidence:
```


## 2026-10-22 — Propose in-place recovery of IdeaPad Run #5

**Decision proposed for review:** Resume the preserved source/output in place via a dedicated opt-in mode in the existing manual workflow. Checkout the controller into a separate child directory and reject ordinary IdeaPad checkout when the old workspace exists. Do not move, clean, reset, sync, or reapply patches to the interrupted tree.

**Reason:** The initial IdeaPad job reached C++ compilation but was cancelled after approximately six hours. The user confirmed 14GB of output and Ninja/Siso state remain. Moving paths or repeating the original non-idempotent setup could discard useful work.

**Scope:** Primary-only arm64 Test recovery at original repository commit 6e7517e6de89e5a1230cebf906470795112466a3, unchanged GN arguments and default parallelism, 1200-minute recovery timeout, vmstat telemetry, temporary signing files, no production authorization. Mismatches fail closed without a full-build fallback.

**Validation/status:** Local checks only; review and real IdeaPad recovery remain pending. This does not declare a permanent persistent-workspace implementation or authorize dispatch. Old Run #5 reruns remain unsafe because workflow changes do not retroactively alter them.


## 2026-10-22 — Propose six local jobs for IdeaPad recovery

**Supersedes:** Retaining default recovery parallelism in the earlier Run #5 recovery decision.

**Reason:** User-supplied long-duration vmstat measurements show recurring memory pressure and swap traffic on the 12GB WSL instance. The default execution had twelve concurrent clang++ processes and very slow progress.

**Proposed change:** Use autoninja -j 6 for chrome_java and chrome_public_apk in recovery only. Scheduling is changed without changing GN inputs or cleaning incremental state. Six is an initial measured tuning candidate, not a promise of six-hour completion. Keep telemetry for comparison. Production remains blocked; Run 39624481319 is cancelled and a new Test dispatch requires user selection.

## 2026-10-23 — Propose 156 Test with explicit candidate and recovery separation

**Evidence:** Primary d64b78b and successful recovery Run39765620887 reuse the 155 tree from original source6e7517e. User confirmed F11 and persistent smartphone YouTube problems with working DeX. This was not a test of newly applied independent playback fixes. Official latest stable at work start is v156.0.8078.47.

**Review proposal:** Preserve upstream merge history/exact pins; adapt the zoom overlay's context to retain Chromium's newer CHECK. Add confirmed SAF backup/restore of absolute zoom values, retaining internal keys/migration marker and profile privacy. Add separately switchable, bounded YouTube-only PiP-attribute/background-visibility candidates and minimal non-content diagnostics. Keep these statuses distinct from build/device success.

**Build boundary:** Reject old resume mode on the new revision. Use an isolated fresh IdeaPad directory and explicit source/GN/toolchain provenance. Keep six local jobs as an initial conservative cap, with the 20-hour IdeaPad timeout and a required local host-capacity check. Do not clean/relabel/repatch the prior tree or dispatch a build. All production/main/tag gates remain unchanged.

**Remaining review blockers:** AndroidX package access and real preference UI/type validation, whole native/GN/renderer integration, inline PiP fullscreen limitations, native-vs-page pause diagnosis and actual Windows/WSL capacity. Notion/Project Sources need a verified refresh after reviewed integration, not before. A separate main documentation PR does not authorize code promotion or Release.
