> **Source:** Generated from `openspec/project.md` during the documentation build.

# Project Context

## Purpose
Crua is a cross-language static-analysis CLI that checks whether code respects
the raw hardware and runtime cost model it executes on — cache-line layout,
dispatch/type stability, thread vs. event-loop concurrency models, and
lock/STM contention — independent of whether that code is logically correct
or well-composed.

The authoritative product requirements are in `crua-ears-spec.md`. Preserve
its requirement IDs (`REQ-*`) in proposals, tests, findings, and traceability
notes.

## Tech Stack
- Implementation language: Rust, organized as a Cargo workspace and exposed
  as the `crua` CLI binary.
- Rust baseline: stable toolchain, rustfmt formatting, Clippy linting, and
  Cargo-native unit, integration, and documentation tests.
- Language analysis: tree-sitter or a language-native parser behind
  front-end plugins.
- Core model: a language-agnostic representation of nodes, cost patterns,
  hotness classes, and shape sources.
- CLI output: human-readable, JSON, and SARIF.
- Benchmark generation: per-language native benchmarking toolchains
  (BenchmarkDotNet for C#, BenchmarkTools.jl for Julia, pyperf for Python,
  criterium for Clojure).

## Project Conventions

### Code Style
- Format with rustfmt and keep Clippy clean.
- Use domain terms from the EARS specification consistently: cost pattern,
  cost pattern kind, tier, hotness class, confirmation status, setup strategy,
  shape source, effect channel.
- Keep built-in vocabularies closed and project extensions explicitly
  declared and validated. Unknown cost patterns remain `unclassified`;
  never silently coerce them to a successful/default case.
- Use stable requirement and rule IDs. A finding always has a rule ID, file,
  line, cost pattern kind, tier, hotness class, and shape source.

### Architecture Patterns
- Keep language-specific pattern recognition in versioned, conformance-tested
  front-end plugins.
- Maintain a versioned cost catalogue mapping each (cost pattern kind, language)
  pair to a matcher, severity floor, and explanation template.
- Prefer consuming shape/effect data from an installed composability checker
  (Vampiro) when available; fall back to standalone extraction at reduced
  precision otherwise.
- Support diff-scoped analysis as the interactive/agent default and full
  repository analysis as an incremental mode.
- Never generate or modify source or test files by default; benchmark
  generation is an explicitly opt-in mode (`crua verify`).

### Testing Strategy
- Develop every behavior from an OpenSpec scenario traceable to one or more
  EARS requirement IDs.
- Maintain a shared, versioned conformance-fixture suite for every front-end
  plugin and cost catalogue entry.
- Test all supported output formats against the same underlying finding data.
- Include negative fixtures for unclassified patterns, unavailable toolchains,
  inconclusive benchmarks, and suppressed concurrency-model findings.
- Benchmark diff-scoped scans with moderate cost-pattern count; the target is
  single-digit seconds.

### Git Workflow
- Use OpenSpec changes for new capabilities, architecture changes, breaking
  behavior, and performance work. Do not implement a proposal before approval.
- Keep commits focused and preserve requirement IDs in change artifacts and
  test names where practical.
- Pull-request CI should run diff-scoped `scan` in `gate` mode at the
  configured severity threshold.

## Domain Context
Crua checks whether code costs more than its shape implies. Its core
taxonomy of cost pattern kinds:

- `layout` — false sharing, missing padding/alignment, AoS vs. SoA mismatch
- `dispatch` — type instability, boxed math, reflection-based interop,
  megamorphic call sites
- `vectorization` — scalar loop where a vectorized/bulk operation exists
- `concurrency-model-mismatch` — code written as if a runtime provides
  parallelism it does not (e.g. CPU-bound work inside a GIL-bound thread)
- `contention` — lock, atomic-CAS, or STM retry storms driven by
  write-frequency or layout

Findings are tiered (0–3) by evidentiary strength: lexical match, structural
cross-reference, hotness-adjusted, or empirically verified via generated
benchmark.

## Important Constraints
- Static analysis must never execute analyzed source code.
- Unknown or unsupported cost patterns must be visible in output, never
  silently omitted or treated as absent.
- Benchmark generation (`crua verify`) must never run as part of `crua scan`;
  it is an explicitly separate, separately-budgeted step.
- `guidance` mode never fails solely because of findings; `gate` mode fails
  only when findings on diff-touched nodes meet the configured threshold.
- Toolchain unavailability is `ToolchainUnavailable`, not `disconfirmed` or
  success.
- The repository is greenfield. `openspec/specs/` describes built truth, so do
  not copy aspirational EARS requirements there before implementation; add
  them through reviewed changes and archive them as capabilities ship.

## External Dependencies
- Git diff/repository metadata for diff-scoped analysis and hotness
  reachability estimation.
- Per-language tree-sitter grammars or native parser APIs.
- Per-language benchmarking toolchains for `crua verify` mode.
- Optionally: installed Vampiro composability checker for shape/effect data.
- CI platforms capable of consuming generated pipeline configuration and SARIF.