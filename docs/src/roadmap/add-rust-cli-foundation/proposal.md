> **Status:** Active OpenSpec proposal; not implemented or deployed. The source under `openspec/changes/` is authoritative.

# Change: Add Rust CLI foundation

## Why
Crua needs one executable contract that later analysis changes can extend without redefining command, configuration, finding, or exit semantics.

## What Changes
- Create a stable-toolchain Cargo workspace exposing a thin `crua` binary.
- Reserve `scan` and `verify` without claiming analysis or benchmark execution.
- Establish deterministic configuration precedence, shared finding types, and numeric exit categories.

## Impact
- Affected capability: `cli-foundation`
- Future code: Cargo workspace, CLI/configuration boundary, shared domain types
- Source requirements: REQ-4, REQ-5, REQ-6; contract references: REQ-11–REQ-15, REQ-21, REQ-29

## Approval
Implementation SHALL NOT begin until a human approves this proposal and the normative EARS source.
