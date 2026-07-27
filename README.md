# Crua

Crua is a planned cross-language Rust CLI for checking whether code respects
the raw hardware and runtime cost model it executes on — cache-line layout,
dispatch/type stability, thread vs. event-loop concurrency models, and
lock/STM contention — independent of whether that code is logically correct
or well-composed.

The project is currently in specification and proposal review. No application
implementation has started. The authoritative requirements are in
[`crua-ears-spec.md`](crua-ears-spec.md).

## Documentation

The documentation site publishes the authoritative EARS specification and all
active OpenSpec proposals, designs, tasks, and capability deltas:

<https://charly-vibes.github.io/crua/>

GitHub Pages is deployed from an Actions artifact. The repository does not use
or require a `gh-pages` branch.

## Local documentation build

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_docs.py
mkdocs build --strict
```

## Planning validation

```bash
openspec validate --all --strict --no-interactive
python scripts/check_planning.py
```

Implementation remains blocked until the human approval gate recorded in
`.beads/issues.jsonl` approves all OpenSpec proposals.