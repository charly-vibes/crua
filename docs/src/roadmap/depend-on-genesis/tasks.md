> **Status:** Active OpenSpec proposal; not implemented or deployed. The source under `openspec/changes/` is authoritative.

## 1. Dependency
- [ ] 1.1 Add `genesis = { git = "https://github.com/charly-vibes/genesis", tag = "v0.1.0" }` to `Cargo.toml` (once `add-rust-cli-foundation` lands the skeleton).
- [ ] 1.2 Verify build with envelope/suggestions/managed_block modules stable.

## 2. Source envelope
- [ ] 2.1 Route `--json` (findings) through `genesis::envelope`, findings under `data`.
- [ ] 2.2 Conformance: top-level keys match the shared shape.

## 3. Source suggestions
- [ ] 3.1 Register crua's command list with `genesis::suggestions::SuggestionEngine`.
- [ ] 3.2 Wire the error sink to emit `genesis::suggestions` fix-footers.

## 4. Source managed_block
- [ ] 4.1 Source injector mechanics from `genesis::managed_block`.
- [ ] 4.2 Carry WAI/OPENSPEC/DONT blocks so `wai status` detects crua (wai-bdqw.9).

## 5. AIX artifacts
- [ ] 5.1 Ship `llms.txt`/`llm.txt` via `genesis::aix` (hand-write minimally until stable).
