# The reversal: the law is equivalent to three independent assumptions

**Certificate** `REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1`
**Proof** `rocq/ReversePhysicsTorusReversal.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 8 green (0 red)` — `GATE: PASS`
**Closes** `REVERSE_PHYSICS_REVERSAL` — the standing gap since the first turn

## What was missing

Every theorem in this stream ran one way: assumptions ⟹ law, or one level of the
chain ⟹ the next. That is the forward half of reverse physics. Reverse
mathematics needs the other half — `T ⟺ A` over a base, plus **independence**,
which is what pins `A` as the *content* of `T` rather than merely sufficient for
it, and what stops the axiom set from being padded.

## The theorem

```
hamiltonian k a b  ⟺  A1 ∧ A2 ∧ A3
```

at every mode, where

| | assumption | vocabulary |
|---|---|---|
| **A1** | `marginal` — each DOF independently conserves its own phase-space area | **physical** |
| **A2** | `inter_dof_closed` — the four cross-DOF closedness equations | **geometric** |
| **A3** | `no_uniform_drift` — at the zero mode the field vanishes | **topological** |

The forward direction is the reversal proper: from the law alone, each assumption
is derived.

`marginal_iff_intra_dof_closed` is what licenses calling A1 physical — the
marginal condition and the intra-DOF closedness equations are proved to be the
*same statement*, not one merely implying the other.

## Independence

Each assumption has an explicit witness satisfying the other two and failing the
law:

| drop | witness | reading |
|---|---|---|
| A1 | `X = cos(2πq₁)∂_{q₁}` at mode `e_{q₁}` | one DOF drives itself |
| A2 | `X = cos(2πq₂)∂_{q₁}` at mode `e_{q₂}` | pure inter-DOF shear |
| A3 | `X = ∂_{q₁}` at the zero mode | uniform translation |

None is redundant. The gate enforces this: one negative control is a false proof
that A1 alone suffices, which would contradict A2/A3 independence, and it is
rejected.

## The degree-of-freedom split is now a theorem, not an assumption

> **Corrected by `REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1`.** The theorem below is
> true, but this billing was too generous: `{(q₁,q₂),(p₁,p₂)}` is **isotropic**
> — ω vanishes on both blocks — so it is not a degree-of-freedom split, and what
> was shown is dependence on an arbitrary *coordinate pairing*. The honest and
> strictly stronger replacement is `marginal_not_invariant_under_admissible_splits`,
> which witnesses the dependence between two genuinely symplectic splits. See
> [that report](torus-split-rocq.md).

The whole stream — since the G0 certificate — has carried "the DOF split is an
input, not derived" as a *declared assumption*. `marginal_depends_on_the_dof_split`
proves it: the **same field** is marginal for the pairing `{(q₁,p₁), (q₂,p₂)}` and
not marginal for `{(q₁,q₂), (p₁,p₂)}`.

So A1 is not a property of the dynamics alone. It is a property of the dynamics
*together with a choice of what counts as a degree of freedom*.

## The uncomfortable finding

The law decomposes into three independent pieces, and **only two of them can be
stated in physical vocabulary**. A1 is a physical postulate; A3 is a clean
topological one, removing exactly the `b₁(T⁴)` obstruction. A2 is neither — a
geometric consistency condition between degrees of freedom, and no physical
reading of it is offered here.

A reverse-physics programme wants the law equivalent to a set of *physical*
assumptions. Here a third of the decomposition resists that reading. Whether A2
has an honest physical formulation is open; if it does not, this is a bound on
how much of Hamiltonian structure is physically axiomatizable at all.

**Resolved by `REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1`:** A2 is the *remainder* of a
bookkeeping choice. A1's split-dependence cancels against it exactly — for every
pairing, `intra_P ∧ inter_P` is the same proposition — so the physical/geometric
division is not canonical. See [that report](torus-split-rocq.md).

## How far this is, and is not, reverse mathematics

This is the first result in the stream at `EQUIVALENCE_CERTIFIED`, and the
promotion is **scoped**.

The base theory — what `RCA₀` plays in reverse mathematics — is the carrier
declaration: `T⁴` with fixed coordinates, fixed `ω`, fixed DOF split,
trigonometric-polynomial fields, rational coefficients. That is **definitional
context, not an axiom schema**. A genuine reverse-mathematics base is a system
one can *weaken and compare against*; this is a declaration one either adopts or
does not.

So: an equivalence over a declared carrier, with independence — real, and the
half that was missing. Not yet a reversal over a weakenable base.

## Ledger

```
Print Assumptions    28/28 across three modules, closed under the global context
coqchk axioms        <none>
negative controls    3, all rejected
gate                 8 green (0 red)
```

## What this does not establish

- **An equivalence over a weakenable axiomatic base** — see above.
- That these three assumptions are the *only* such decomposition; minimality
  among alternative decompositions is not addressed.
- A physical reading of A2.
- Anything about general symplectic manifolds, non-polynomial fields, or
  dimensions above four.
- The per-mode dimension counts, which remain the Forge gate's computation.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_PARAMETERISED_BASE` — quantify over DOF splits and symplectic
forms so the base becomes something that can be *weakened*. That is what would
turn this scoped equivalence into a reverse-mathematics reversal proper, and
`marginal_depends_on_the_dof_split` is the first step toward it.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.torus_reversal_rocq --check
```

## Tier receipt

- **Tier 0/1** — three modules compile; gate 8 green / 0 red from a clean tree;
  `coqchk` empty axiom section; all provenance records hash-verified and
  byte-deterministic; 30-test Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
