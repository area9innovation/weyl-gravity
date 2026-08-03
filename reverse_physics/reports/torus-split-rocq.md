# Why the third assumption isn't physical — and a correction

**Certificate** `REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1`
**Proof** `rocq/ReversePhysicsTorusSplit.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 9 green (0 red)`
**Corrects** `marginal_depends_on_the_dof_split` in the reversal certificate

## The correction first

The reversal certificate proved `marginal_depends_on_the_dof_split` by comparing
the standard pairing `{(q₁,p₁),(q₂,p₂)}` against `{(q₁,q₂),(p₁,p₂)}` and billed
it as *"the degree-of-freedom split is an input"*.

That second pairing is **isotropic** — ω vanishes on both of its blocks
(`alt_pairing_is_isotropic`). It is not a decomposition into degrees of freedom
at all; it pairs directions that are not conjugate. The theorem is true, but what
it showed was dependence on an arbitrary *coordinate pairing*.

Worse for the original billing: of the three ways to pair four coordinates,
**exactly one is symplectic**. The other two are both isotropic
(`third_pairing_is_isotropic`).

The honest version needs a genuinely admissible alternative. Take

```
V₁′ = span(∂q₁+∂q₂, ∂p₁+∂p₂)      V₂′ = span(∂q₁−∂q₂, ∂p₁−∂p₂)
```

`rotated_split_is_admissible` proves each block is symplectic (`ω = 2` on each)
and the two are ω-orthogonal. Then:

**`marginal_not_invariant_under_admissible_splits`** — the field
`X = cos(2πq₁)∂_{q₂}` (one degree of freedom driving the other's coordinate) is
marginal for the standard split and **not** marginal for the rotated one. Both
splits are real degree-of-freedom decompositions.

So the downstream claim survives and is strictly stronger than before.

## The explanation

A1 depends on the split. The law does not. So the dependence must cancel
somewhere — and `split_dependence_cancels` shows exactly where:

> For **every** pairing `P` of the four coordinates, `intra_P ∧ inter_P` is the
> same proposition: closedness. And closedness mentions no split at all.

`law_decomposes_three_ways` makes the consequence explicit: the law admits three
different `A1 ∧ A2 ∧ A3` decompositions, differing only in how the labour is
divided between the "physical" conjunct and the "geometric" one.

**So A2 is not a mysterious extra postulate. It is the remainder of a bookkeeping
choice.** Having elected to call two of the six closedness equations "each degree
of freedom conserves its own information", A2 is whatever is left over. Choose a
different split and the same content divides differently.

## What this costs the programme

This is the part worth sitting with.

A reverse-physics assumption ought not to depend on a coordinate choice. **A1
does.** So "each degree of freedom independently conserves information" cannot
stand as a fundamental assumption on its own. Only its conjunction with the
remainder is split-independent — and that conjunction is just *"preserves ω"*,
which is the law's own geometric content, not a physical postulate.

The decomposition into a physical part and a geometric part is therefore **not
canonical**. That is a real limitation on reverse-physics-style axiomatizations
of this law, not a defect of the formalisation. It also bears directly on
Carcassi–Aidala's infinitesimal reducibility, which presupposes a decomposition
into independent degrees of freedom: here that decomposition is provably a
choice, and the assumption built on it inherits the arbitrariness.

## Ledger

```
Print Assumptions    8/8 this module; 36/36 across four modules
coqchk axioms        <none>
negative controls    4, all rejected — including a false claim that
                     marginal is split-invariant
```

## What this does not establish

- **Full `Sp(4)` invariance.** The cancellation is proved for the three
  *coordinate* pairings, and split-dependence is witnessed between *two*
  admissible splits. The continuum `Sp(4)/(Sp(2)×Sp(2))` is not quantified over.
- **A physical reading of A2.** This explains why A2 resists one; it does not
  supply one.
- That no *other* decomposition into physical assumptions exists — only that the
  intra/inter one is not canonical.
- Anything about general symplectic manifolds, non-polynomial fields, or
  dimensions above four.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_SP4_ORBIT` — quantify over the full continuum of symplectic
splits rather than three pairings and two samples, upgrading "not canonical" to a
statement about the whole orbit.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.torus_split_rocq --check
```

## Tier receipt

- **Tier 0/1** — four modules compile; gate 9 green / 0 red from a clean tree;
  `coqchk` empty axiom section; five provenance records hash-verified; 30-test
  Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
