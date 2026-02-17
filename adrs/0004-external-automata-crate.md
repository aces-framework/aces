# ADR-0004: External Automata Crate for Verification

## Status

Accepted

## Context

ACES's Tier 2 (semantic) verification requires automata theory operations:
labeled transition system construction, NFA/DFA closure operations, and
language inclusion checking (antichain algorithm). These are needed to
implement GTDL-style formal proofs that detection rules cover specified
attack paths.

The Rust ecosystem lacks a general-purpose automata theory library comparable
to Java's dk.brics.automaton or Python's automata-lib. Existing Rust crates
cover only FSM patterns or regex-specific automata, not the formal methods
operations ACES needs.

## Decision

Build an independent automata theory crate (working name TBD), published on
crates.io with no ACES dependency. The crate provides:

- Labeled Transition System (LTS) construction
- NFA/DFA with full closure operations (union, intersection, complement,
  product)
- Language inclusion checking (antichain algorithm)
- Bisimulation / simulation relation checking
- Synchronous/asynchronous product composition

The dependency chain:

```text
automata crate (independent, crates.io)
    ^
aces-sdl (Tier 2 verification)
    ^
aces-runtime
```

## Consequences

- Fills a genuine gap in the Rust ecosystem. The formal methods community
  currently has these tools only in C++ (QuAK, Limi, SPOT), Java
  (dk.brics.automaton), and Python (automata-lib).
- ACES does not depend on a single-project library — the crate is useful
  to any Rust project doing model checking, protocol verification, or
  formal analysis.
- The crate must be built and maintained. This is a strategic investment,
  not incidental work.
- Property-based testing (proptest) is essential for verifying algebraic
  properties of automata operations (e.g., L(complement(A)) =
  complement(L(A))).
