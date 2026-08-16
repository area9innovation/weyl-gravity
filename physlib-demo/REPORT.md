# Lean/Physlib bridge report

The pilot succeeds as a deliberately narrow two-rail certificate.  The Forge
artifact `STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1` remains authoritative
for the typed BV operations, Green data, support conditions, and nonlinear
source identities.  Lean 4.32 with a content-pinned Physlib dependency checks
the final universal algebraic implication: the stated reduction and
arity-three identities force the second source to be `q1`-closed.

The formal file contains two theorems.  The first proves the exact rational
coefficient cancellation.  The second proves closure in an arbitrary rational
module from two explicit hypotheses.  Physlib's informal-result metadata links
the mathematical theorem to its physical reading without pretending that the
reading itself has been formalized.

Lean reports the Mathlib axiom footprint `propext`, `Classical.choice`, and
`Quot.sound` for both theorems.  There are no `sorry`, `admit`, or locally
declared `axiom` tokens in the source.  The independent checker pins the Lean,
Mathlib, and Physlib revisions, verifies both source hashes, enforces the
`LOCAL-ALGEBRAIC` boundary, rejects promoted causal claims, and can replay Lean.

This result does **not** formalize the source `q2/q3` identities, the Green
homotopies, causal support, Hadamard conditions, positivity, or a Lorentzian
quantum theory.  Those are the natural successive formalization targets; the
demo establishes the interface and assurance split needed to approach them.
