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
