> **Status:** Active OpenSpec proposal; not implemented or deployed. The source under `openspec/changes/` is authoritative.

# Change: Depend on genesis

## Why

crua is spec-stage with no `src/` yet — the right time to build on `genesis`
from day one rather than reimplement CLI/AIX/self-healing infra and port
later. crua's `add-rust-cli-foundation` change establishes the CLI skeleton;
this change composes with it by sourcing the cross-cutting pieces from
genesis (the shared crate the tool-craft playbook §8 and Appendix A.4
describe).

## What Changes

- Add `genesis` git dependency (pinned by tag `v0.1.0`) to `Cargo.toml`.
- Source the JSON envelope from `genesis::envelope` (crua's `cli-foundation`
  "Shared finding contract" maps findings under `data`).
- Source self-healing errors from `genesis::suggestions` (crua's
  `cli-foundation` "Stable exit categories" gains the `Suggestion` footer).
- Source the managed-block injector from `genesis::managed_block` so crua
  carries WAI/OPENSPEC/DONT blocks and participates in `wai status` detection
  (the `wai-bdqw.9` signal).
- Ship `llms.txt`/`llm.txt` via `genesis::aix` once stable.
- Keep all crua domain logic (cost-pattern catalogue, hotness classes,
  tree-sitter front ends, benchmark generation). The genesis boundary rule
  protects this.

## Impact

- Affected specs: `cli-foundation` (MODIFIED — envelope, suggestions, managed
  block sourced from genesis). Composes with, does not replace,
  `add-rust-cli-foundation`.
- Blocked by: genesis tagging `v0.1.0`.
- Coordinates with crua's EARS spec (crua-ears-spec.md) — no REQ changes
  there; this is CLI infrastructure, not domain behavior.
