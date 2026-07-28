# EARS Specification: Crua

Crua (Spanish/Portuguese, fem. of *crudo/cru* — "raw") is a cross-language
CLI that checks whether code respects the raw hardware and runtime cost
model it executes on — cache-line layout, dispatch/type stability, thread
vs. event-loop concurrency models, and lock/STM contention — independent
of whether that code is logically correct or well-composed.

This document is self-contained. It assumes no prior conversation and no
familiarity with any other tool, though Section 1 notes where Crua
optionally consumes shape and effect-channel data already produced by a
composability checker called Vampiro, and where a coverage checker called
Livin can consume Crua's hotness data in return, if either is present.

## Normative status

This file is the normative product-requirements source. OpenSpec changes
define reviewed implementation slices and SHALL trace to, but cannot override,
the REQ IDs here. `openspec/project.md`, README files, and generated copies
under `docs/` are explanatory when they conflict with this file. A deliberate
requirements change therefore updates this file first and preserves existing
REQ IDs unless a requirement is explicitly retired.

---

## 0. Background & Motivation

Two functions can each pass every test and every composability check and
still be five times slower than necessary, because tests and type checkers
verify *what a value is*, not *where it lives* or *how the runtime
schedules it*. A thread-safe counter implemented as `long[] counters` with
one slot per thread is logically correct, passes every unit test, and is
five times slower under contention than the equivalent padded layout —
because adjacent slots share a cache line, and every core's write
invalidates every other core's cached copy of that line. The same shape of
problem recurs, differently, in every language: a Julia function that
looks numeric but returns `Union{Float64, Nothing}` from one branch forces
boxing and dynamic dispatch on every call; a Python loop over a numpy array
that could vectorize instead pays per-element interpreter overhead; a
Clojure `atom` updated from four threads at high frequency causes CAS-retry
storms that look like contention but are actually a data-layout problem
wearing a concurrency costume.

None of these are caught by a type checker (types matched), a linter (no
syntax rule was violated), a test suite (behavior was correct), or a
composability checker (the pieces fit together structurally and
compose in the right category). They require knowing, per language, which
structural shapes carry a disproportionate hardware or runtime cost, and
whether the code as written falls into one of them — and, where that
matters enough to act on, whether the claimed cost is real rather than
folklore, which requires actually measuring it in isolation rather than
asserting it from a rule.

Crua explicitly does not adjudicate correctness of concurrent
interleavings (races, lost updates, deadlock) — that is a job for a
model checker, not a cost-pattern linter. Crua also does not decide
*whether* two implementations are substitutable (that is Vampiro's
`optionality` axis) or whether a test suite reaches enough boundary values
(that is Livin's job) — Crua asks only whether a given, already-correct,
already-composed piece of code costs more than its own shape implies it
should.

---

## 1. Scope & Definitions

- **Cost pattern**: a named, structural antipattern associated with a
  disproportionate hardware or runtime cost relative to a straightforward
  fix of the same logical behavior.
- **Cost pattern kind**: a closed-but-extensible taxonomy tag on a cost
  pattern: `layout` (false sharing, missing padding/alignment,
  array-of-structs vs. struct-of-arrays mismatch), `dispatch` (type
  instability, boxed math, reflection-based interop, megamorphic call
  sites), `vectorization` (scalar loop over a structure with an available
  vectorized/bulk operation), `concurrency-model-mismatch` (code written
  as if a runtime provides parallelism it does not — e.g. CPU-bound work
  inside a GIL-bound thread, or vice versa), or `contention` (lock,
  atomic-CAS, or STM retry storms driven by write-frequency or layout, not
  by genuine logical contention).
- **Tier**: the evidentiary strength behind a finding. `0` (lexical —
  syntactic pattern match only), `1` (structural — cross-referenced
  against declared size/adjacency/type information), `2` (hotness-adjusted
  — Tier 1 combined with a static reachability estimate for how often the
  site executes), `3` (empirically verified — an isolated microbenchmark
  was generated and run, producing a measured ratio).
- **Cost catalogue**: a versioned, per-(cost pattern kind, language) table
  mapping a matcher to a severity floor and an explanation template,
  validated by conformance fixtures, the same mechanism used by Vampiro's
  idiom table and Livin's boundary catalogue.
- **Hotness class**: `reachable` (the site is statically reachable from a
  thread-spawn, parallel-loop, or otherwise repeated-invocation context
  with no upstream constraint ruling that out), `unreachable` (an upstream
  constraint establishes the site cannot execute at meaningful frequency —
  e.g. it runs once at process start), or `unknown` (cannot be determined
  from available shape/effect information). This mirrors Livin's
  reachability class, applied to execution frequency rather than value
  reachability.
- **Effect channel** (consumed, not computed, when Vampiro is installed):
  Vampiro's `plain`/`result`/`option`/`throws`/`async`/`stream`
  classification for a node. Crua uses this to determine a node's actual
  concurrency model — an `async` node in a single-threaded event-loop
  runtime (e.g. Python `asyncio`) cannot exhibit true cache-line
  contention between concurrent writers, regardless of how the code looks
  syntactically.
- **Confirmation status**: `unconfirmed` (Tier 0–2, no benchmark run),
  `confirmed` (Tier 3, measured ratio cleared the configured threshold with
  acceptable variance), `disconfirmed` (Tier 3, measured ratio did not
  clear the threshold — the pattern matched syntactically but did not cost
  what the catalogue predicted), or `inconclusive` (Tier 3 attempted, but
  variance across runs exceeded the acceptable bound).
- **Benchmark decision protocol**: unless project configuration overrides it,
  run the native benchmark tool for 5 warm-up rounds followed by 30 measured
  rounds for each variant in the same process and alternating order. The
  measured ratio is `median(as-found) / median(canonical-fixed)`, the
  confirmation threshold is `1.20`, and acceptable variance means each
  variant's measured-round coefficient of variation (sample standard
  deviation divided by mean) is at most `0.05`. The repro artifact records
  the effective values, tool/toolchain versions, OS, CPU model and logical
  core count. A ratio at least `1.20` with acceptable variance is `confirmed`;
  a lower ratio with acceptable variance is `disconfirmed`; excessive
  variance is `inconclusive`.
- **Severity**: the ordered levels `low < medium < high < critical`. Unless
  project configuration overrides it, gate mode uses threshold `high`.
- **Setup strategy**: the method used to construct inputs for a generated
  benchmark, in the precedence defined normatively by REQ-17: `verbatim`,
  then `harvested-fixture` (an existing repo-native constructor, property-test
  generator, test-file factory, or spec generator reused as-is), then
  `structural-synthesis` (a mechanically-generated instance built from an
  all-primitive type declaration), then `needs-agent-input` (no safe
  construction method found; a stub is emitted rather than a guessed value).
- **Repro artifact**: a generated, standalone benchmark file produced only
  under `crua verify`, containing an as-found variant and a canonical-fixed
  variant of the flagged site, run with the target language's native
  benchmarking tool (BenchmarkDotNet for C#, BenchmarkTools.jl for Julia,
  pyperf for Python, criterium for Clojure).
- **Shape source**: `vampiro` (shape/effect data consumed from an
  installed composability checker) or `standalone` (Crua's own reduced-
  precision extraction). Every finding records which source produced it.

---

## 2. Ubiquitous Requirements

- **REQ-1**: The tool shall obtain domain/codomain shape and effect-channel
  data for analyzed nodes, preferentially by consuming an installed
  composability checker's extracted data when available, and shall record
  shape source on every finding.
- **REQ-2**: The tool shall classify every candidate site into exactly one
  cost pattern kind from the closed-but-extensible taxonomy in Section 1,
  or `unclassified` if none applies.
- **REQ-3**: The tool shall maintain a versioned cost catalogue mapping
  each (cost pattern kind, language) pair to a matcher, a severity floor,
  and an explanation template, validated by conformance fixtures using the
  same mechanism as the family's other tools.
- **REQ-4**: Every finding shall carry a tier (0–3) and the evidence
  supporting that tier (query match, structural cross-reference, hotness
  class, or measured benchmark ratio).
- **REQ-5**: Every finding shall carry a rule ID, file and line, cost
  pattern kind, tier, hotness class, and shape source.
- **REQ-6**: The default `crua scan` command shall never generate or
  modify source or test files; it shall only report findings. Benchmark
  generation is a separate, explicitly opt-in mode (Section 5), consistent
  with the tool family's enforcement-not-generation default.

---

## 3. Event-Driven Requirements

- **REQ-7**: When a candidate site matches a Tier-0 lexical query, the
  tool shall attempt Tier-1 structural cross-reference (element size,
  adjacency, distinct-writer-context count, presence of padding/alignment
  annotation) before reporting a finding at or above the catalogue's
  severity floor.

  *Example*: `long[] counters = new long[threadCount]` written from
  distinct thread contexts with `Interlocked.Increment` raises a Tier-1
  `layout` finding once cross-referenced against `sizeof(long)` and thread
  count showing multiple counters share a 64-byte line.

- **REQ-8**: When a cost pattern kind is `dispatch` and the language
  exposes a static type-narrowing signal (an untyped/`Any`-typed field
  reachable from a hot path in Julia, a reflection warning in Clojure, a
  boxed generic in C#), the tool shall raise a Tier-1 finding citing the
  specific untyped or reflective path.

- **REQ-9**: When a site's hotness class is `reachable` and the cost
  pattern kind's severity floor is met, the tool shall escalate the
  finding's severity by one level relative to an otherwise-identical
  finding whose hotness class is `unreachable`.

- **REQ-10**: When effect-channel data (consumed from an installed
  composability checker, or derived standalone) indicates a node executes
  under a single-threaded concurrency model despite an `async` or
  thread-like syntactic appearance (e.g. Python `asyncio` coroutines), the
  tool shall suppress `layout` and `contention` findings for that node and
  evaluate only `dispatch` and `vectorization` findings.

- **REQ-11**: When `crua verify` is invoked against a Tier-1 or Tier-2
  finding, the tool shall attempt benchmark synthesis using the
  setup-strategy order in Section 5 and shall set confirmation status to
  `confirmed` only if the measured ratio between the as-found and
  canonical-fixed variants clears the configured threshold with
  acceptable variance across repeated rounds; otherwise it shall set
  `disconfirmed` or `inconclusive` as appropriate, never silently
  discarding the attempt.

---

## 4. State-Driven Requirements

- **REQ-12**: While gate mode is `gate`, the tool shall exit non-zero if
  any Tier-2-or-higher finding on a diff-touched node with hotness class
  `reachable` meets or exceeds the configured severity threshold.
- **REQ-13**: While gate mode is `guidance`, the tool shall report all
  findings without forcing a non-zero exit.
- **REQ-14**: While a candidate site's cost pattern kind cannot be
  classified into the taxonomy, the tool shall report it as
  `unclassified` explicitly, rather than silently excluding it.
- **REQ-15**: While `crua verify` is running and the required language
  toolchain (e.g. `dotnet`, `julia`, `pyperf`, `criterium`) is
  unavailable, the tool shall report `ToolchainUnavailable`, distinct from
  `disconfirmed`, and shall never treat unavailability as a pass.

---

## 5. Optional Feature Requirements

- **REQ-16**: Where no composability checker's shape/effect data is
  installed, the tool shall fall back to its own standalone extraction at
  reduced precision, recording `shape-source: standalone` on every
  finding produced in that run.
- **REQ-17**: Where `crua verify` is enabled, the tool shall select setup by
  this single precedence order: (1) use `verbatim` if it produces a compilable
  repro; otherwise (2) use `harvested-fixture` if a matching repo-native aid
  described by REQ-18 exists and produces a compilable repro; otherwise (3)
  use `structural-synthesis` if it produces a compilable repro; otherwise (4)
  use `needs-agent-input`. The tool shall stop at the first successful step.
- **REQ-18**: Where a repo-native construction aid is present (a
  property-test generator such as Hypothesis, `clojure.spec` generators,
  or a test-file factory function matching a `Create*`/`Build*`/`Make*`
  naming convention) for the flagged type, the tool shall try harvesting it
  after `verbatim` and before structural synthesis, exactly as ordered by
  REQ-17; an aid that does not produce a compilable repro shall not prevent
  fallback to structural synthesis.
- **REQ-19**: Where custom cost catalogue entries are supplied for
  project-specific types, the tool shall use them in place of, or in
  addition to, the built-in catalogue.
- **REQ-20**: Where diff-scoped mode is selected, the tool shall restrict
  scanning to nodes touched by the diff.
- **REQ-21**: Where output format `human`, `json`, or `sarif` is selected,
  the tool shall serialize identical underlying finding data in that
  format.

---

## 6. Unwanted Behavior Requirements

- **REQ-22**: If a cost catalogue entry has no defined matcher for the
  active language, the tool shall report `matcher:undefined` for that
  entry rather than silently treat it as absent.
- **REQ-23**: If benchmark synthesis lands on setup strategy
  `needs-agent-input`, the tool shall emit a stub repro file clearly
  marked as requiring agent completion, and shall not itself invent
  semantically arbitrary fixture values for non-primitive types.
- **REQ-24**: If a benchmark run's variance across repeated rounds
  exceeds the configured acceptable bound, the tool shall report
  confirmation status `inconclusive` rather than promote or silently
  discard the finding.
- **REQ-25**: If the same underlying cost pattern would be reported by
  both a full-repository scan and a diff-scoped scan, the tool shall
  deduplicate findings by a stable ID derived from rule, location, and
  shape hash.

---

## 7. Complex Requirements

- **REQ-26**: While shape source is `standalone`, when a finding's
  hotness class would otherwise be `reachable`, the tool shall instead
  report `unknown` unless standalone extraction can itself establish the
  upstream loop or thread-spawn context, since standalone mode's reduced
  precision cannot reliably confirm reachability on its own.
- **REQ-27**: When `crua verify` produces a `confirmed` Tier-3 finding for
  a node that also participates in an implementation cluster with a
  declared law suite (per a composability checker's optionality checks),
  the tool shall attach the measured performance divergence to the same
  finding as the law-suite result rather than reporting them separately.

---

## 8. Non-Functional Requirements

- **REQ-28**: A diff-scoped `crua scan` (Tiers 0–2 only) shall have a 95th
  percentile wall-clock duration below 9.0 seconds across 20 measured runs on
  the versioned `scan-moderate` fixture (100 diff-touched source files and 200
  candidate sites), after one unmeasured warm-up run, on the project's CI
  Linux runner with at least 4 logical CPUs, 8 GiB RAM, and SSD-backed storage.
  The verification report shall record the fixture hash, Crua build profile,
  OS, CPU model/core count, RAM, storage class, and all 20 durations. Runs in
  which another repository job shares the runner are invalid and shall be
  repeated.
- **REQ-29**: `crua verify` (Tier 3) is not subject to REQ-28's bound and
  shall be invoked as an explicit, separately-budgeted step, never run
  implicitly as part of `crua scan`.
- **REQ-30**: The cost catalogue and its conformance fixtures shall be
  versioned and reproducible byte-for-byte across repeated runs on
  unchanged input.

---

## 9. Traceability Notes

- Cost pattern classification and taxonomy → REQ-2, REQ-3, REQ-14.
- Tiering and hotness derivation → REQ-4, REQ-7, REQ-8, REQ-9, REQ-26.
- Concurrency-model awareness via consumed effect-channel data → REQ-1,
  REQ-10, REQ-16.
- Benchmark synthesis / `verify` mode → REQ-6, REQ-11, REQ-15, REQ-17,
  REQ-18, REQ-23, REQ-24, REQ-29.
- Reporting discipline (never silently omit, never silently generate) →
  REQ-5, REQ-6, REQ-14, REQ-15, REQ-22, REQ-24.
- Operational modes → REQ-12, REQ-13, REQ-19, REQ-20, REQ-21, REQ-28,
  REQ-30.
- Cross-tool combination with a composability checker → REQ-1, REQ-10,
  REQ-16, REQ-26, REQ-27.

---

## Appendix: Worked Examples

**Layout finding, Tier 1 → Tier 3 (C#)**
```csharp
long[] counters = new long[threadCount];
Parallel.For(0, threadCount, t => {
    for (int i = 0; i < iterations; i++)
        Interlocked.Increment(ref counters[t]);
});
```
Tier-0 query matches "atomic write into array element inside a parallel
context." Tier-1 cross-reference shows `sizeof(long) == 8` and
`threadCount` counters packed with no padding, so up to 8 counters share a
64-byte line — Tier-1 `layout` finding. Hotness class `reachable` (inside
`Parallel.For`) escalates severity per REQ-9. Under `crua verify`, setup
strategy `verbatim` lifts the declaration directly (REQ-17); BenchmarkDotNet
runs the as-found version against a `[StructLayout]`-padded variant,
measuring roughly a 5x ratio — confirmation status `confirmed`.

**Dispatch finding, standalone mode (Julia)**
```julia
global total = 0
function accumulate!(x)
    global total += x
    return total
end
```
`total` is a non-`const` global with no declared type, read and written
inside a function reachable from a hot loop. Without an installed
composability checker, standalone extraction (shape-source: standalone)
can see the untyped global but, per REQ-26, cannot itself confirm the
loop-hotness context with full precision — hotness class reported as
`unknown` rather than `reachable` unless the calling loop is also visible
in the scanned scope.

**Concurrency-model suppression (Python)**
```python
async def handle(counters, idx):
    counters[idx] += 1
```
Without effect-channel data, a Tier-0 query might flag this as a
false-sharing candidate (array indexed inside a concurrent-looking
context). Per REQ-10, if effect-channel data (consumed from an installed
composability checker or derived standalone) shows this runs under
Python's single-threaded `asyncio` event loop rather than true OS threads,
the `layout`/`contention` finding is suppressed entirely — no cache-line
contention is possible here regardless of syntactic appearance.

**Contention finding (Clojure)**
```clojure
(def counter (atom 0))
;; four threads, high frequency:
(dotimes [_ n] (future (swap! counter inc)))
```
High-frequency `swap!` from multiple threads on one `atom` is a
`contention` finding: CAS-retry storms driven by write frequency, not by
any logical necessity for shared mutable state. Tier-1 cross-reference
notes no sharding/striping of the counter. `crua verify` setup strategy
`structural-synthesis` builds a minimal repro (bare atom, N futures,
fixed iteration count) since the declaration is already self-contained;
criterium measures the as-found version against a striped/`java.util.
concurrent.atomic.LongAdder`-style variant.

**Harvested-fixture setup (C#, non-trivial type)**
```csharp
public class ShardedCounter {
    private readonly OrderContext _ctx;   // DI-injected, non-trivial ctor
    public long[] Shards;
}
```
`OrderContext` cannot be structurally synthesized (Level C). Rather than
invent a fake `OrderContext`, `crua verify` scans test files for a
`CreateOrderContext()`/`BuildOrderContext()` factory already used in the
suite (REQ-18) and reuses it verbatim in the generated repro. If no such
factory is found, setup strategy falls to `needs-agent-input`, and the
tool emits a stub repro file with a `// TODO: provide OrderContext
fixture` marker (REQ-23) rather than guessing.
