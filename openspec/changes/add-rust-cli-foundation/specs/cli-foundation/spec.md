## ADDED Requirements

### Requirement: Stable command and configuration foundation
The system SHALL expose a `crua` binary with discoverable `scan` and `verify` command families. It SHALL discover at most one `crua.toml` from the working directory through the repository root and apply configuration precedence `CLI argument > CRUA_* environment variable > crua.toml > normative EARS default`; an invalid higher-precedence value SHALL produce a configuration failure rather than fall through. This capability SHALL NOT claim source analysis or benchmark execution. Source references: REQ-6, REQ-11, REQ-29.

#### Scenario: Commands are discoverable before analysis exists
- **WHEN** a user requests top-level help
- **THEN** `scan`, `verify`, and configuration options are shown without reporting findings or running a benchmark

#### Scenario: Configuration sources conflict
- **WHEN** a setting has different valid values in a CLI argument, `CRUA_*` environment variable, and discovered `crua.toml`
- **THEN** the CLI value is selected

#### Scenario: Higher-precedence configuration is invalid
- **WHEN** an invalid environment value overrides a valid file value and no CLI value is supplied
- **THEN** command handling fails with exit code 2 and does not use the file value

### Requirement: Stable exit categories
The system SHALL reserve numeric exit code `0` for successful command handling, `1` for policy/gate failure, and `2` for configuration or operational failure. The foundation SHALL NOT produce policy failures because gate evaluation is outside this capability. Contract references: REQ-12, REQ-13, REQ-15.

#### Scenario: Help succeeds
- **WHEN** the user requests valid help or version information
- **THEN** the process exits with code 0

### Requirement: Shared finding contract
The system SHALL define a finding type requiring rule ID, file path and line, cost pattern kind, tier, hotness class, shape source, and tier evidence. Cost pattern kind, tier, hotness class, and shape source SHALL use the closed values defined by the normative EARS source. The foundation SHALL NOT create or serialize findings. Source references: REQ-2, REQ-4, REQ-5.

#### Scenario: A successor constructs a finding
- **WHEN** a later capability constructs a finding through the shared type
- **THEN** every REQ-5 field and tier evidence are required and unknown closed-vocabulary values cannot be represented
