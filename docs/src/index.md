> *"We went all the way down south*
> *We were frothing at the mouth*
> *Coming down to Derby town*
> *We'd beaten everyone around, singing"*
> — Sumo

# Crua

Crua is a planned cross-language Rust CLI that checks whether the pieces of a
codebase cost more than their shape implies — cache-line layout, dispatch/type
stability, thread vs. event-loop concurrency models, and lock/STM contention —
independent of whether that code is logically correct or well-composed.

> **Draft and unimplemented**
>
> EARS 1.0.0 and any OpenSpec changes are active proposals awaiting human
> approval. This site documents intended behavior; it does not claim that
> the CLI has been implemented.

## Start here

- Read the [authoritative EARS specification](specification/ears.md).
- Review the [implementation roadmap](roadmap/index.md).
- See the [project context](project-context.md) for architecture and testing
  constraints.
- Read [contributing](contributing.md) before changing requirements or starting
  implementation.

## Documentation provenance

The Pages site is assembled directly from `crua-ears-spec.md` and
`openspec/changes/` during CI. The rendered copies are generated artifacts;
the repository source files remain authoritative.