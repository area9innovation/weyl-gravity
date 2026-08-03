# Reverse physics on Weyl gravity itself

**Certificate** `REVERSE_PHYSICS_WEYL_ACTION_V1`
**Proofs** `rocq/WeylActionClassification.v`, `rocq/WeylParityAndTopology.v` — zero axioms, 37/37 closed
**Gate** `rocq/run.sh` — `RESULT: 23 green (0 red)`, 21 fail-closed negative controls
**Second rail** tango `forge/examples/weyl_action_classification_gate.forge` — 37/37,
`verify -full`: `c==native`, ASan-clean on both backends
**Separation ledger** [`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md)

---

## The objection this answers

Every earlier certificate in this stream tested a carrier built to demonstrate
the method — a torus, a four-state Markov chain — or the Pais–Uhlenbeck toy. A
reviewer would say: *fine, but you have not done reverse physics on the theory
the repository is about.*

Correct. This one does.

## The law

```
S[g]  =  α ∫ √−g · C_abcd C^abcd
```

## The claim, and it is an equivalence

Modulo topological terms, `S` is the **unique** action satisfying

| tag | assumption |
|---|---|
| `RP-LOCAL` | the action is the integral of a local density |
| `RP-METRIC` | the metric is the only field |
| `RP-DIFF` | diffeomorphism invariance |
| `RP-WEYL` | local Weyl (conformal) invariance |
| `RP-DIM4` | spacetime is four-dimensional |

and every one of them is independent: drop it and a different action satisfies
the rest. The witnesses are exhibited, not asserted.

## 1. The computation, and it is small

Coordinates on the parity-even quadratic curvature sector:

```
X  =  a·Riem²  +  b·Ric²  +  c·R²          (a,b,c) ∈ ℚ³
```

The Gauss–Bonnet density is `E₄ = (1, −4, 1)`; the Weyl square in `D` dimensions
is `C²_D = (1, −4/(D−2), 2/((D−1)(D−2)))`, which at `D = 4` is `(1, −2, ⅓)`.
These two plus `R² = (0,0,1)` are a basis — rank 3, determinant nonzero, checked
on both rails.

Under `δg = 2σg` the Weyl square is invariant (`D = 4`), the Euler density is
topological, and

```
δ(√−g R²)  =  −12 √−g R □σ        so       δS  =  −12γ ∫ √−g σ □R
```

where `γ` is the `R²` coordinate in the basis `{C², E₄, R²}`. So **the entire
conformal anomaly of this sector is carried by one coordinate**, and Weyl
invariance is the single linear equation

```
a + b + 3c  =  0
```

Its solution space is two-dimensional — exactly `span{C², E₄}` — and modulo the
topological `E₄` that is one-dimensional. That is the theorem.

The whole thing is rational linear algebra in ℚ³. No floating point appears
anywhere, on either rail.

## 2. The assumption that turns out not to be one

"Four derivatives", or equivalently "quadratic in curvature", is normally listed
as a sixth input. **It is not an assumption.** A density `√−g X` with `X`
homogeneous of curvature-degree `k` has weight `D − 2k` under a *constant* Weyl
rescaling, so invariance forces `D = 2k`. At `D = 4` that is `k = 2` and nothing
else — and the same one-line computation excludes the cosmological term (`k=0`,
weight 4) and Einstein–Hilbert (`k=1`, weight 2).

So the standard motivation for conformal gravity uses one more physical input
than it needs. The derivative order is a *consequence* of `RP-WEYL` and
`RP-DIM4`.

The Forge rail checks the weight condition exhaustively over `D ∈ 2..12`,
`k ∈ 0..6`.

## 3. The independence witnesses

| drop | witness | what changes |
|---|---|---|
| `RP-WEYL` | `R²`, and with it every `(a,b,c)` | 1 parameter → 2 (3 before the quotient). This is quadratic gravity. |
| `RP-TOPO-INERT` | `E₄` | 1 → 2. The Euler density is Weyl invariant and is *not* a multiple of `C²`. |
| `RP-DIM4` | the weight `D − 4` | `√−g C²` is invariant **iff** `D = 4`. |
| `RP-PARITY` | `W₊²` | see §4 — the interesting one. |

Each is a theorem with a proof, and each has a fail-closed negative control in
the gate: a *false* claim that `R²` is invariant, that `E₄` is a multiple of
`C²`, that `C²` is topological, or that `W₊²` is parity-even, must all be
**rejected** by `coqc`. Without those, the witnesses would prove nothing.

## 4. Parity: independent on actions, redundant on field equations

This is the sharper half, and it is where the result stops being a restatement
of a textbook fact.

Adjoin the parity-odd Pontryagin density `P`. In four dimensions the Weyl tensor
splits into self-dual and anti-self-dual parts, and

```
C²  =  W₊² + W₋²          P  =  W₊² − W₋²
```

so **`[W₊²]` and `[W₋²]` — this programme's own two certified residual classes —
are exactly the parity eigenbasis of this sector.**

Both chiral halves are Weyl invariant. Neither is topological. The map
`(α,β) ↦ α W₊² + β W₋²` is injective, so this is a genuine **two-parameter
family of actions**. And yet:

```
α W₊² + β W₋²   has the same field equations as   ((α+β)/2) · C²
```

because the difference is `((α−β)/2)·P`, which is topological. So the
two-parameter family of actions has a **one-parameter family of field
equations**.

> **Parity invariance is independent as an assumption on the action and
> redundant as an assumption on the classical theory.** It may be deleted from
> the list without changing anything a classical observer could measure.

The fibre — the direction `RP-PARITY` was supposed to be constraining — is
exactly the Pontryagin direction, which is a gravitational **θ-angle**. That is
observable in principle, but only quantum-mechanically. So the assumption is
real; the level at which it becomes physical is one this programme's claim
boundary explicitly does not reach.

Stated in the repository's own terms: `RP-PARITY` is precisely the assumption
that ties `[W₊²]` and `[W₋²]` together, and classically it is free of charge.

## 5. A consistency check the formula was not fitted to

The `D`-dependent Weyl vector `C²_D = (1, −4/(D−2), 2/((D−1)(D−2)))` degenerates
to `E₄ = (1,−4,1)` **exactly at `D = 3`** — checked over `D ∈ 3..12`, true there
and false everywhere else. That is the coordinate shadow of the Weyl tensor
vanishing identically in three dimensions. Nothing in the setup was arranged to
produce it.

## 6. Two rails, two methods

| | method |
|---|---|
| **Rocq** | explicit change of basis + linear arithmetic over ℚ (`lra`) |
| **Forge** | Gaussian elimination over ℚ — `qm_rank`, `qm_det`, `qm_nullspace`, `qm_solve` |

Neither computes the other's answer. Re-running a producer is reproduction, not
verification; these are different algorithms reaching the same dimensions.

A note from building it: `lra` over `Q` does not reason through `Qdiv`, and
Coq's `exists!` carries **Leibniz** equality, which is the wrong equality on `Q`
— `1#2` and `2#4` are equal rationals and distinct terms. Both were caught by
the proof failing rather than by inspection, which is the argument for
mechanising this at all.

## 7. What this does **not** establish

- **The theorem's novelty.** That conformal gravity is the unique conformally
  invariant quadratic gravity in four dimensions is **classical and textbook**.
  What is new is the machine-checked zero-axiom derivation with the geometric
  inputs isolated, the independence witness per assumption, the derived
  derivative order, and the parity result.
- **The non-degeneracy input `G5`.** That some metric has `□R ≠ 0` is asserted,
  with a witness *named* (matter-dominated FRW, `a(t) = t^{2/3}`, `R = 4/3t²`)
  rather than formalised. What *is* proved is that the input is load-bearing:
  replace it by `False` and every action counts as invariant
  (`without_non_degeneracy_the_classification_is_vacuous`). The difference
  between a theorem and a tautology is visible in the development rather than
  argued in prose.
- **The conformal transformation laws or Gauss–Bonnet.** These are asserted
  classical differential geometry (`G1`–`G8` in the certificate), entered as
  coordinate vectors and weight formulas. A reader who rejects them rejects the
  result — they are listed precisely so that is possible.
- **The field equations.** That the variation of `∫√−g C²` is the Bach tensor is
  *not* derived here. Only the space of actions is classified; "same field
  equations" is *defined* as "differ by a topological term", which is
  `RP-TOPO-INERT`, not a computation.
- **Nonlocal, non-polynomial, or higher-degree actions, or matter couplings.**
- **That `RP-PARITY` is redundant quantum-mechanically.** It is not.
- **Anything about the BV–BFV complex, the residual cohomology, or the physical
  spectrum.** The `W±²` identity is between coordinate vectors, not a statement
  about the certified residual classes as cohomology. Per AGENTS.md those
  classes are centered deformation/vertex classes, not one-particle graviton
  states, and nothing here changes that. The two scoped Lorentzian no-go
  theorems are untouched.

## 8. The successor question

The weight argument says the conformally invariant curvature degree in `D`
dimensions is `k = D/2`. So:

- **odd `D` has no such sector at all** — a prediction, and a cheap one to state;
- **`D = 6` selects the cubic sector**, which has ten invariants before
  identities and a known three-dimensional conformal subspace plus the Euler
  density.

`WEYL_ACTION_SIX_DERIVATIVE_D6` would run the same exact linear algebra there
and test both whether the method scales and whether the parity result has an
analogue. That is the declared next gate.

## Verification

```bash
cd rocq && ./run.sh                                   # 23 green (0 red)
PYTHONPATH=. python3 -m reverse_physics.weyl_action_rocq --check

# upstream, in tango:
cd forge && FORGE_LIB=$PWD/lib forge -run \
    examples/weyl_action_classification_gate.forge    # exit 37
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_action_classification_gate.forge    # c==native, asan clean
```

## Tier receipt

- **Tier 0/1** — eighteen Rocq modules compile; gate 23 green / 0 red; `coqchk`
  axiom section `<none>`; 163/163 `Print Assumptions` closed; twenty-one
  fail-closed negative controls, four of them new for this result; sixteen
  provenance records hash-verified; 30-test Python suite green.
- **Upstream** — `weyl_action_classification_gate.forge` 37/37, `verify -full`
  `c==native`, ASan-clean on both backends.
- **Tier 2/3 — not run, and not required.** This adds two modules, a gate and a
  provenance record; it changes no shared operator, schema, or generated
  artifact that another certificate chain consumes, and touches nothing in the
  classical BV–BFV pipeline.
