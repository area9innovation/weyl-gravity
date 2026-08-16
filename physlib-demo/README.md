# Physlib bridge demo

This isolated Lake package demonstrates how a Forge certificate can become a
kernel-checked Lean theorem without conflating the two assurance layers.

The source certificate is
`STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1`.  Lean proves only its final
universal algebraic implication: the receiver's reduction of the second
source together with the diagonal arity-three identity forces exact closure
because `1/2 - 3/6 = 0`.  The Forge certificate continues to own the geometry,
typed Green homotopies, causal support and finite-tree theorem.

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
lake build
lake env lean WeylPhyslibBridge/StrictWeylSecondSource.lean
python3 check_bridge.py --run-lean
```

The final two commands in the Lean source print the theorem axiom footprint.
The external verifier additionally checks the exact Physlib revision and the
SHA-256 of the Forge source certificate; a theorem string alone is not treated
as provenance.

## Boundary

The demo does not formalize the full BV complex, the `q₂/q₃` identities, the
Green homotopies, support-indexed function spaces, Hadamard wavefront sets, or
physical positivity.  It establishes a small but real two-rail result:

- Forge verifies the scientific premises and their scope;
- Lean's kernel verifies the final implication from those premises.
