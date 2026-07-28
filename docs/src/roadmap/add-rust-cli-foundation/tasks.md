> **Status:** Active OpenSpec proposal; not implemented or deployed. The source under `openspec/changes/` is authoritative.

> Implementation is blocked until human approval of the normative EARS source and this proposal.

## 1. CLI Tracer
- [ ] 1.1 RED: add failing help/version snapshots that require `scan`, `verify`, and configuration options without claiming either operation ran.
- [ ] 1.2 GREEN: create the minimal stable-toolchain Cargo workspace and thin `crua` binary that satisfy the snapshots.
- [ ] 1.3 REFACTOR: separate parsing from command transport without adding analysis, then run focused tests, workspace tests, rustfmt, and Clippy with warnings denied.

## 2. Configuration and Exit Tracer
- [ ] 2.1 RED: add failing tests for `CLI > CRUA_* > crua.toml > EARS defaults`, nearest-file discovery, invalid-value failure, and exact exit codes 0/2.
- [ ] 2.2 GREEN: implement only configuration loading and typed exit categories; reserve policy exit 1 without implementing gate behavior.
- [ ] 2.3 REFACTOR: remove parsing duplication, snapshot the configuration/exit contract, and rerun workspace quality gates.

## 3. Finding Contract Tracer
- [ ] 3.1 RED: add compile-fail/construction tests requiring every REQ-5 field and closed enums for cost pattern kind, tier, hotness class, and shape source.
- [ ] 3.2 GREEN: implement the minimal shared finding types without scanners, output serialization, or policy behavior.
- [ ] 3.3 REFACTOR: centralize validation invariants and run focused plus workspace quality gates.

## 4. Acceptance
- [ ] 4.1 Run all unit, integration, documentation, and snapshot tests plus `cargo fmt --check` and Clippy with warnings denied.
- [ ] 4.2 Trace tests to REQ-4/REQ-5/REQ-6 and confirm no analysis, reporting, gating, benchmark, or toolchain behavior is claimed.
- [ ] 4.3 Run `openspec validate add-rust-cli-foundation --strict` and record approval and verification evidence before implementation completion.
