# The parity-odd candidates were not scalars

**Certificate** `REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1`
**Rails** Forge — `curvature_coord_scalar_control_gate` 19/19 (ASan-clean),
`curvature_invariants_parity_gate` 22/22 (rebuilt), `curvature_invariants_d6_gate` 27/27,
`curvature_invariants_deriv_gate` 40/40
**Dependency tag** `LOCAL-ALGEBRAIC`

> **This retracts [`REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1`](parity-field-equations.md)
> outright and corrects two counts in `REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1`.**
> Both are recorded below with the exact numbers that replace them.

---

## 1. What went wrong

A contraction is covariant only when each repeated index appears once **up** and once
**down**. Eight of the parity-odd candidates did not satisfy that. The published
`D = 6` count of 2 came entirely from two of them.

The defect lives in how a candidate is specified. Each operand is a *slot spec* — which
slots feed the `ε`, which take a contracted index — and the **variance is implicit in
which pre-raised array you hand it**. `cu012` is `C^{abc}{}_d`; `cu01` is `C^{ab}{}_{cd}`.
Pass the wrong one, or transpose two free slots, and the spec still type-checks, still
runs, still returns a number.

## 2. Why every existing check passed it

Three separate guards should have caught this. None could.

**The conformal test is vacuous on Weyl-built candidates.** It compares `g` with
`e^{2σ}g` where `σ` vanishes at the base point. But `C^a{}_{bcd}` is conformally
invariant with **no derivative-of-`σ` terms at all** — so *any* product of Weyl tensors,
contracted in *any* index pattern, passes automatically. The gate's own comment called
these candidates "conformally invariant by construction". That was true, and it was
exactly why the test could say nothing.

**The weight count cancels.** The two mismatched pairs were one down-down and one up-up,
contributing `−2` and `+2`. Total weight `−6`, precisely correct.

**Nothing ever asked whether a candidate was a tensor.** That is the real gap: the
apparatus tested conformal behaviour and never tested covariance.

## 3. The falsifier

Change chart by `x = A y` with `A ∈ SL(n, ℤ)`:

```
g'_ab(y) = A^k_a A^l_b g_kl(A y)
```

A genuine scalar takes the same value at the base point in both charts. `det A = 1`
keeps the arithmetic exact and preserves `|det g| = 1` there — which is what keeps the
Levi-Civita **symbol** equal to the **tensor** and the whole sector rational.

```
D = 6
  R                      896                896                INVARIANT
  C_abcd C^abcd          508481/10          508481/10          INVARIANT
  sum R_ab R_ab  (bad)   3277979/4          22671990           CHART-DEPENDENT
  sw0 as written         6566972251/160     -200078513393/160  CHART-DEPENDENT
  sw1 as written         1641849747/64      -7821381917/64     CHART-DEPENDENT
  sw0 repaired           0                  0                  INVARIANT
  sw1 repaired           0                  0                  INVARIANT
```

`6566972251/160` is, exactly, the number the retracted certificate published as `L(g)`
in its conformal-invariance control.

Three charts — unit lower-triangular, unit upper-triangular, and their **non-triangular
product** — over two metrics. The rig is calibrated in both directions: `R`, `C²` and the
**Pontryagin density** transport correctly and Pontryagin is nonzero, while a
deliberately malformed `Σ_ab R_ab R_ab` moves on every run. Without that negative half,
"everything passed" would mean the test was blind.

## 4. The corrected counts

| | published | **corrected** |
|---|---|---|
| `D = 4`, weight 4 (Pontryagin) | 1 | **1** — unchanged |
| `D = 4`, weight 6 | 2 | **1** |
| `D = 6`, weight 6 | 2 | **0** |
| odd `D`, weight 6 | none | **none** — unchanged, an index-parity argument |

In `D = 6`, `rankV = 0`: after repair **every** candidate — algebraic and derivative,
Weyl-built and Riemann-built — is identically zero. The sector is empty.

**Riemann is not traceless**, so the covariant repairs vanishing for Riemann *as well as*
Weyl means the index pattern itself is empty. No choice of curvature tensor rescues it.

### That zero is now a count, and it has a mechanism

**Rail** `curvature_parity_enumeration_gate` — 12/12, 26m11s.

The zero above was established over a **hand-built candidate list**, which is the very
weakness that admitted the eight defects. It is now enumerated mechanically.

One `ε` (6 lower indices) against three curvature tensors (12 slots): six slots feed the
`ε`, six pair off — `C(12,6) × 15 = 13,860`. The **first Bianchi identity**, verified in
the gate as an exact componentwise identity rather than sampled, forces the `ε` split to be
exactly `(2,2,2)`: `ε` antisymmetrises everything it touches and `C^{[abc]d} = 0` kills any
tensor handing it three or more slots. That leaves `6³ × 15 = 3,240`, swept whole over two
fixtures. All 15 matchings run, not just the 8 without self-pairs, so tracelessness is
*exercised* rather than assumed.

**Variance is derived, not chosen.** Sixteen variance variants are precomputed by bitmask,
and each pattern selects operands by raising exactly the slots it needs — the `ε` slots and
one end of each contracted pair. Nothing is hand-written. That is the discipline whose
absence caused this whole correction.

| sweep | nonzero of 3240 |
|---|---|
| generic, no symmetry | **3240** |
| antisymmetric within pairs only | **2208** |
| + pair-exchange symmetry | **0** |
| Weyl | **0** |
| Riemann | **0** |

> **The pair-exchange symmetry `C_{abcd} = C_{cdab}` is what empties the sector.**

Not Bianchi and not tracelessness — the pair-symmetric control violates Bianchi (verified)
and is not traceless, and still vanishes everywhere. And antisymmetry within each pair is
**not sufficient on its own**: 2208 patterns survive it. One identity does all the work.

**Bianchi was asserted as the mechanism twice** — once in designing the control, once after
the first run. Both wrong. Neither reached a certificate because the control was built so
that it *could* refute them, which is the entire argument for a control that can fail.

**Three attempts at that control, and the first two proved nothing.** Riemann was the
obvious choice and is useless: a self-pair gives either zero or a Ricci-type object,
symmetric in the two indices that feed the `ε`, so Riemann vanishes too. The second was a
"generic" tensor that **wasn't generic** — `param(seed,a,b,c,d,a+b)` reduces to
`seed·31 + 6a + 5d (mod 7)`, independent of `b` and `c`, so it factorises and the
antisymmetrisation annihilates it. That control returned zero for a reason unrelated to what
it tested, and cost two twenty-minute runs. Packing indices injectively
(`a + 6b + 36c + 216d`) with a multiplier coprime to the modulus fixes it, and the generic
sweep now fires on **all 3240** — which is what makes the zeros mean anything.

## 5. What replaces the retracted result

The retracted certificate concluded that parity is **load-bearing** on the `D = 6` field
equations. The evidence now points the opposite way: with no parity-odd invariant to
adjoin, `RP-PARITY` is **vacuous** in `D = 6` — there is nothing there to be independent
about.

That is still a statement that the `D = 4` situation does not travel, and it is still the
second such finding after uniqueness. But it is the **opposite direction**, and it is
**not** established here — it follows only if the candidate family is complete, which §7
says it is not. It is recorded as the reading the evidence favours, not as a result.

## 6. The eight defects

| dimension | candidate | defect |
|---|---|---|
| `D = 4` | 2 | middle operand `u012` put `b3` up; `rup` had it up too |
| `D = 4` | 4 | `d1_012` put `b1` up; `d1up` had it up too |
| `D = 4` | 5 | `u01` put `b1` up; `d2up` had it up too |
| `D = 4` | 7 | the Weyl copy of candidate 2 |
| `D = 6` | 2 | middle operand's two free slots transposed |
| `D = 6` | 7 | middle `rup` put `b3` up; third `rup` had it up too |
| `D = 6` | 8 | `ralt2` raised slot 2 twice; the raise belonged on slot 1 |
| `D = 6` | 9 | an `ε` index on a **down** slot, *and* `b1` up on both operands |
| `D = 6` | 10, 11 | the transposition and the double raise, Weyl-built — **the published count** |

**Candidate 9 is the one worth naming.** It was **zero as written**, so no wrong number
ever pointed at it. It could only be found by asking whether the contraction was
well-formed. Repairing it can turn a zero into a nonzero, so it had to be fixed *before*
"`D = 6` is empty" meant anything.

## 7. What this does **not** establish

- **Not that no parity-odd conformal invariant exists in `D = 6`.** The enumeration is
  exhaustive over one `ε` and three **undifferentiated** curvature tensors. The
  **derivative** patterns — `ε ∇R ∇R` and `ε R ∇∇R` — are a different space and are **not
  swept**. The parity gate finds its own derivative candidates zero, but that is a
  hand-built list again, and hand-built lists are exactly what failed here.
- **The control sweeps are not as exhaustive as the curvature ones.** The `(2,2,2)`
  restriction is justified *by* the first Bianchi identity, so it is sound for Weyl and
  Riemann, which satisfy it, and **not** for the Bianchi-violating controls — for those,
  patterns handing three or more slots to the `ε` are not swept. The control statements are
  about that subspace and are weaker than the curvature result.
- **The `D = 4` weight-4 Pontryagin row is untouched** — still 1, still nonzero, still
  conformally invariant, still chart-invariant. That is the row the ledger's `RP-PARITY`
  rests on, so `REVERSE_PHYSICS_WEYL_ACTION_V1` and the gravitational theta-angle are
  **unaffected**.
- **The parity-even counts are unaffected.** Both parity-even gates now carry the same
  chart rail and pass it in `D = 4, 5, 6` — `curvature_invariants_d6_gate` 27/27 and
  `curvature_invariants_deriv_gate` 40/40 — so `REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1`
  and `REVERSE_PHYSICS_DERIVATIVE_CONFORMAL_COUNT_V1` both stand. The defect was specific
  to the parity gate's slot-spec mechanism; the parity-even candidates are written with
  their up/down pairings explicit.
- **One thing is observed and not explained.** In `D = 4` the malformed `sw1` was
  chart-**invariant** across all six comparisons despite not being covariantly formed —
  presumably a four-dimensional identity. It is repaired regardless. Recorded as an
  observation.
- Nothing global, nothing about dynamics, the ghost, or anything quantum.

## 8. The rail this leaves behind

The chart control is now **inside the gates that make the claims**, not in a one-off
script: `curvature_invariants_parity_gate` audits every candidate per-dimension and names
any that moves, and both parity-even gates — `curvature_invariants_d6_gate` and
`curvature_invariants_deriv_gate` — do the same for their own candidate sets.

One nuance that cost a false alarm and is worth keeping: the parity-even gate's
componentwise diagnostics (`ci_comp_sq` — squared components, used deliberately because a
contracted norm can vanish on a nonzero tensor under an indefinite metric) are **not
scalars by design**, and only their *vanishing* is ever read. The rail compares candidates
by **value** and those diagnostics by **vanishing**.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify examples/curvature_coord_scalar_control_gate.forge   # 19/19, ASan-clean
forge -run examples/curvature_invariants_parity_gate.forge
forge -run examples/curvature_invariants_d6_gate.forge            # 27/27
forge -run examples/curvature_invariants_deriv_gate.forge         # 40/40, 11m12s
```

Exact rational arithmetic throughout. No floating point, no tolerance.
