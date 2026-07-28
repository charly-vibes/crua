## Context
This greenfield tracer establishes only contracts needed by later capabilities.

## Goals / Non-Goals
- Goals: discoverable command families, deterministic configuration, domain-safe finding fields, and stable exit categories.
- Non-goals: parsing source, producing findings, serializing output, applying gate policy, generating benchmarks, or invoking toolchains.

## Decisions
- Use a Cargo workspace with a thin `crua` binary and library-owned CLI/configuration/domain contracts.
- Discover at most one `crua.toml` by walking from the working directory to the repository root; apply precedence `CLI > CRUA_* environment > crua.toml > EARS defaults`. Invalid values fail rather than falling through.
- Reserve exits `0` for successful command handling, `1` for a future policy/gate failure, and `2` for configuration or operational failure. This change can exercise only `0` and `2`.
- Model closed vocabularies as Rust enums and require the REQ-5 finding fields at construction; do not add output-format serialization yet.

## Risks / Trade-offs
- Reserved contracts constrain successors; snapshots make intentional breaking changes visible.
- Combining configuration and operational failures at exit `2` limits shell-level diagnosis; structured diagnostics can distinguish them later.
