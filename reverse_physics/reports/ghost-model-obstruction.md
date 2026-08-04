# The obstruction was never what bounded it

**Certificate** `REVERSE_PHYSICS_GHOST_MODEL_OBSTRUCTION_ROCQ_V1`
**Proof** `rocq/GhostModelObstruction.v` — zero axioms, 17/17 closed
**Gate** `rocq/run.sh` — `RESULT: 28 green (0 red)`, `coqchk` axiom section `<none>`
**Answers** `GHOST_MODEL_OBSTRUCTION`, declared by
[`coprime-charge-bound.md`](coprime-charge-bound.md)

---

## The question this answers

The predecessor refuted a physics gloss this stream had published, and then
recorded the limit of its own replacement: **the model it argued in has no
ghost.** Its free Hamiltonian is `w₁n̂₁ + w₂n̂₂` with both frequencies positive,
so the charge `J = p·n̂₁ + q·n̂₂` that bounds the occupations is available for a
reason that has nothing to do with the obstruction. It declared the successor:

> `GHOST_MODEL_OBSTRUCTION` — redo the deformation with a genuinely indefinite
> `h₀ = w₁n̂₁ − w₂n̂₂`. Under `a₂ ↔ a₂b` the conversion kernel becomes pair
> creation, so the two models plausibly see **mirror-image obstruction loci**. If
> that is right, the coprime hierarchy is a statement about *which channel is
> resonant* — not about stability at all, in either model.

The conclusion is **confirmed**. The phrasing was **not quite right**, and the
correction is the interesting part.

## The loci do not mirror — they coincide

`conj2`, the relabelling `a₂ ↔ a₂b` that turns a positive-frequency mode into a
ghost, is an involution preserving total degree, nonnegativity and diagonality,
and it carries the ghost-resonant sector **bijectively** onto the healthy one:

```
ghost_resonant p q m   ⟺   resonant p q (conj2 m)
```

It acts on **monomials, not on `(p,q)`**. So the set of ratios admitting an
obstruction is *literally the same* in both models, and the whole coprime
hierarchy — the order law, the critical degree `p+q`, the classification, the
even-`p` kernel-parity clause — transports unchanged.

What mirrors is the **channel**:

| | healthy `h₀ = p·n̂₁ + q·n̂₂` | ghost `h₀ = p·n̂₁ − q·n̂₂` |
|---|---|---|
| obstructing monomial | conversion `a₁^q a₂b^p` | pair creation `a₁^q a₂^p` |
| its conjugate | `a₁b^q a₂^p` | pair annihilation `a₁b^q a₂b^p` |
| surviving charge | `p·n̂₁ + q·n̂₂` | `p·n̂₁ − q·n̂₂` |
| bounds occupations? | **yes** | **no** |

The classification theorem in the ghost model has *identical hypotheses* to the
healthy one — same positivity, same coprimality, same critical degree. Only the
two named monomials differ, and they are the images of the healthy ones under
`conj2`.

## Where the models part

A diagonal quadratic charge `α·n̂₁ + β·n̂₂` acts on a monomial with eigenvalue
`α(n₁−m₁) + β(n₂−m₂)`. Conserving it on the ghost model's critical sector
requires conserving it on pair creation, which forces

```
q·α + p·β = 0
```

and for `p, q > 0` that forces `α` and `β` to have **strictly opposite signs**
unless the charge is trivial. The only surviving charge is proportional to
`p·n̂₁ − q·n̂₂`, whose level set through the origin is an unbounded ray of
physical states. The healthy model's same-shaped argument yields `(p, q)` — both
positive — which bounds.

**Same `p`, same `q`, same nonnegativity. Only the sign of `h₀` differs.**

## What this actually says

**The bound proved in the predecessor is a consequence of the definiteness of the
free Hamiltonian, not of the obstruction.**

That is the reverse-physics content, and it is a separation rather than a fact
about a toy. The obstruction is identical across the two models — same ratios,
same degree, same classification, exchanged by a relabelling — and it bounds in
one and not the other. So:

- the **obstruction** is `MATHEMATICS`: a statement about a critical degree and a
  coprimality condition;
- the **boundedness** is `PHYSICS`: a statement about a positive-definite `h₀`.

Conflating them is exactly what produced the original wrong gloss. The
predecessor showed the obstruction does not *destabilise*; this shows the thing
that *bounds* is not the obstruction either. Both readings attributed to the
obstruction a stability role it never had, in opposite directions.

## What this does not establish

- **That the ghost model is unstable.** Only that the charge argument bounding
  the healthy model has no counterpart. An unbounded level set *permits* growth;
  it does not produce it.
- **That the ghost model's cubic vertex actually contains the pair-creation
  monomial** with nonzero coefficient. That is a computation in the deformation,
  not a statement about the resonant sector.
- **That no higher-degree conserved quantity bounds it.** Only diagonal quadratic
  charges `α·n̂₁ + β·n̂₂` are considered. Ruling out the rest is what a genuine
  instability claim would need.
- **The bracket action on monomials**, which is the definition `ghost_freq` here
  as it was in the predecessor — certified in Forge as a polynomial identity,
  not derived from the implementation inside Rocq.
- **Anything about Weyl gravity**, the BV–BFV complex, or the residual classes.
  The Weyl ghost *is* a genuinely indefinite system, which is why this question
  was worth asking, but this is a two-mode toy and the gap is not bridged here.

## Negative controls

Both are new, and both are load-bearing:

- a **false** claim that the conversion kernel is resonant in the ghost model is
  rejected — without it the two models would obstruct through the same channel
  and the separation would be vacuous;
- a **false** claim that the surviving ghost charge can be positive is rejected —
  without it the sign of `h₀` would be doing no work, which is the entire content
  of the module.

## Verification

```bash
cd rocq && ./run.sh                     # RESULT: 28 green (0 red)
PYTHONPATH=. python3 -m reverse_physics.ghost_model_obstruction_rocq --check
```

## Tier receipt

- **Tier 0/1** — twenty-three Rocq modules compile; gate 28 green / 0 red;
  `coqchk` axiom section `<none>`; **234/234** `Print Assumptions` closed;
  twenty-nine fail-closed negative controls, two of them new for this result;
  the pinned sources are hash-verified and drift is checked to fail closed.
- **Tier 2/3 — not run, and not required.** This adds a module, two controls and
  a certificate. It changes no shared operator, schema or generated artifact that
  another certificate chain consumes; the predecessor's certificate is unmodified
  and re-derived by hash above.
