# The last branch falls: no conformally invariant DOF count exists

**Certificate** `REVERSE_PHYSICS_NO_CONFORMAL_COUNT_ROCQ_V1`
**Proof** `rocq/ReversePhysicsNoConformalCount.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 16 green (0 red)`
**Closes** `REVERSE_PHYSICS_NONADDITIVE_CONFORMAL_COUNT` — **by refutation**

## The gate asked to construct or refute. The answer is refute.

The parity theorem closed the density branch and left the non-additive branch —
the one their quantum-measure resolution points at — as the only place an answer
could live. It doesn't survive either.

## The argument

Work on **flat space**. A Minkowski slice is certainly a physical configuration,
so any proposed count must behave sensibly there.

A dilation `φ_λ(x) = λx` pulls the flat metric back to a **constant** rescaling
of itself, `φ_λ*δ = λ²δ`. So for any count natural under diffeomorphisms and
invariant under constant Weyl rescaling:

```
μ(φ_λ U) = μ_{φ_λ*δ}(U) = μ_{λ²δ}(U) = μ(U)
```

Taking `U` to be the unit ball: **every ball has the count of the unit ball,
whatever its radius.**

With monotonicity and `μ({x}) = 1`, every nonempty bounded region is squeezed
between `1` and that one constant — the count is bounded by a universal number
that does not depend on the region at all.

`a_unit_ball_and_a_cosmological_ball_count_the_same` puts it concretely: a ball
of radius 1 and a ball of radius 10¹⁰⁰ receive the same count.

## Why the non-additive branch does not escape

**Additivity is never used.** The argument is a group action on regions, not a
decomposition of them. That is precisely why dropping additivity — their
resolution for quantum mechanics — buys nothing here.

## All three branches are now closed

| branch | status under conformal invariance |
|---|---|
| drop 1 → density measure | excluded by **parity** in odd dimension |
| drop 2 → counting measure | invariant but **uninformative** — every infinite region alike |
| drop 3 → non-additive count | excluded **here**, and equally uninformative — every ball ties |

## What this actually says

The honest reading is **not** that the count is hard to construct.

> In a conformally invariant theory, *"how many degrees of freedom are in this
> region"* is not a well-posed question.

A quantity assigning the same value to a unit ball and a ball the size of the
observable universe is not counting anything.

**Consequence for their conjecture.** *GR ⟺ det/rev + DOF independence for
infinitely many dense DOFs* is stated in terms of a DOF count. In a conformally
invariant setting no such count exists — so the conjecture cannot be transported
to conformal gravity as written. Not because the count is unknown, but because
it cannot exist.

## What this does not establish

- **The geometric inputs are hypotheses, not derived.** That a dilation pulls the
  flat metric back to a constant multiple, that balls are dilations of the unit
  ball, that a bounded region contains a point and sits in a ball — all are
  explicit hypotheses of the theorem statements. The differential geometry is
  asserted; the group-action consequence is proved.
- **Flat space only.** Which suffices, because flat space is a configuration any
  count must handle — but nothing is claimed about curved or
  non-conformally-flat cases.
- **Constant conformal factors only.**
- **Conformal invariants on 3-manifolds do exist** — the gravitational
  Chern–Simons invariant, for one. It is global rather than local, real-valued
  modulo framing, and neither monotone nor region-additive, so it is not a
  count and is not reached by this argument.
- **Extra structure is untouched.** A compensator or dilaton breaks
  naturality-plus-Weyl-invariance by choosing a scale — which is what conformal
  invariance forbids. That fork is stated, not resolved.
- **No claim about GR or its dynamics.** This engages one conjecture from one
  talk.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's own
  derivation.

## Next gate

`REVERSE_PHYSICS_WHAT_REPLACES_A_COUNT` — if a region-count cannot exist in a
conformally invariant theory, what does the DOF-independence assumption become?
A relational or ratio-valued notion is the obvious candidate. Not explored here.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.no_conformal_count_rocq --check
```

## Tier receipt

- **Tier 0/1** — eleven modules compile; gate 16 green / 0 red from a clean tree;
  `coqchk` empty axiom section; eleven provenance records hash-verified; 30-test
  Python suite green.
- **Tier 2/3 — not run, and not required.** Nothing outside `reverse_physics/`
  and `rocq/` imports or is imported by this work; no freeze, tag or promotion.
