> **Status:** Active OpenSpec proposal; not implemented or deployed. The source under `openspec/changes/` is authoritative.

# cli-foundation spec delta: depend on genesis

## MODIFIED Requirements

### Requirement: Shared finding contract

crua's JSON finding output SHALL wrap its findings in `genesis::envelope::Envelope`, nesting the finding list under `data`, so crua's `--json` shape matches the rest of the suite.

#### Scenario: scan emits shared envelope

- **WHEN** `crua scan --json` is run
- **THEN** the emitted JSON SHALL have top-level keys `ok`, `envelope_version`, `cli_version`, `envelope_kind`, `data`, `warnings`, `hints`, `meta`
- **AND** the cost-pattern findings SHALL be nested under `data`.

### Requirement: Stable exit categories

crua SHALL source its self-healing error footers from `genesis::suggestions` (the `Suggestion` enum: `DidYouMean`/`WrongOrder`/`ContextHint`/`Fix`), rather than implementing a local copy.

#### Scenario: typo suggestion from genesis

- **WHEN** an unknown crua subcommand is run
- **THEN** crua SHALL emit a "Did you mean …?" footer via `genesis::suggestions`
- **AND** SHALL NOT define a local `Suggestion` enum.
