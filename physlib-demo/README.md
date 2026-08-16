# Physlib bridge demo

This isolated Lake package contains two demonstrations of how Forge
certificates can become kernel-checked Lean theorems without conflating the
two assurance layers.

The conclusion-only bridge starts from
`STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1`. Lean proves its final
universal algebraic implication: the receiver's reduction of the second
source together with the diagonal arity-three identity forces exact closure
because `1/2 - 3/6 = 0`.

The finite-receiver bridge starts from
`STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1`. Its first layer replays the
serialized certificate. Its semantic layer imports five unary, twenty-two
ordered binary, and one ternary operation signatures. Lean then constructs all
212 typed composites, derives their suspended Koszul multipliers, matches all
72 source channels, and recomputes every zero defect by aggregating unweighted
raw path values. The pre-summed defects and signed path inventory are no longer
premises. Forge continues to own the natural differential formulas, their raw
fixture evaluation, the arbitrary-input identity, geometry, Green homotopies,
and causal support.

## Installation

Install `elan`, the Lean toolchain manager, once:

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | \
  sh -s -- -y --default-toolchain none --no-modify-path
source "$HOME/.elan/env"
```

The package pins Lean `v4.32.0` and Physlib commit
`ba2a946586c7de1ff394607afd1dd7fe8539a364`.  There is no global Physlib
installation: Lake checks out the dependency inside `.lake/packages`.

```bash
cd physlib-demo
lake update
lake exe cache get
lake build
```

The first cache download is large.  Later builds reuse it.  The existing
Pais--Uhlenbeck project in `lean/` is also tested on Lean/Mathlib `v4.32.0`,
but remains a separate Lake package so that adding Physlib here cannot
silently change its dependency graph.

## Reproduction

```bash
cd physlib-demo
python3 generate_minimal_arity_three.py --check
python3 generate_finite_graded_evaluator.py --check
lake build
lake env lean WeylPhyslibBridge/StrictWeylSecondSource.lean
lake env lean WeylPhyslibBridge/MinimalArityThree.lean
lake env lean WeylPhyslibBridge/FiniteGradedEvaluator.lean
python3 check_bridge.py --run-lean
```

The final two commands in the Lean source print the theorem axiom footprint.
The external verifier additionally checks the exact Physlib revision and the
SHA-256 of the Forge source certificate; a theorem string alone is not treated
as provenance.

## Boundary

The demo does not formalize the full BV complex, natural `q₁/q₂/q₃`
operator evaluation, the arbitrary-input arity-three theorem, Green
homotopies, support-indexed function spaces, Hadamard wavefront sets, or
physical positivity. It establishes a small but real two-rail result:

- Forge verifies the scientific premises and their scope;
- Lean's kernel verifies a final implication, a finite serialization, and the
  graded finite evaluator that derives and aggregates its `q₁/q₂/q₃` paths.

The generated proof passports shown by the Reverse Physics Atlas report this
scope, the imported premises, and the current axiom footprint. They are an
assurance axis; they do not change evidence grades or completion gates.
