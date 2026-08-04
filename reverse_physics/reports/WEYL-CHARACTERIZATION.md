# What the Weyl action is equivalent to

The standing question of this stream, answered as it now stands.

> **Reverse physics** asks which minimal physical assumptions a law is
> *equivalent* to — not which assumptions imply it. The difference is that an
> equivalence requires every assumption to carry an **independence witness**: a
> system satisfying all the *others* in which the law fails.

This document is the consolidated answer for Weyl gravity. It states what is
established, what is imported, and what is open, and it points at the
certificate for each. Nothing here is new — it is the eight reports of this
ledger said once, in order.

**Verification.** All 14 exhaustive rails pass at this commit, the Rocq
gate is 28 green / 0 red, and the fast suite is 160 tests; see §8.

---

## 1. The law, and the answer

```text
S[g] = α ∫ √−g · C_abcd C^abcd
```

**Equivalent to** `RP-LOCAL ∧ RP-METRIC ∧ RP-DIFF ∧ RP-WEYL ∧ RP-DIM4`, modulo
topological terms — five assumptions, where the standard motivation for
conformal gravity uses six. The sixth, *"quadratic in curvature"*, is **derived**
rather than assumed.

Two things about that answer are worth more than the answer itself, because the
classification is textbook and they are not:

1. **Every assumption now has an independence witness.** This morning two of the
   seven rows read *"assumed, not tested here"* and one read *"no witness — the
   largest genuine hole"*. All three were the same phenomenon and all three are
   closed (§3).
2. **The derived derivative order is not free.** It requires three of the
   assumptions, each failing differently (§4). §4.3 of the separation ledger said
   the standard motivation *"uses one more physical input than it needs"*; what
   is now sayable is precisely **which inputs it does need**.

## 2. The four layers

| layer | what it is equivalent to | status |
|---|---|---|
| **The action** | five assumptions, modulo topological terms | **done**; every assumption witnessed |
| **The field equations** | `RP-WEYL ⟺ RP-TRACELESS` via the trace law; `RP-DIVFREE` free from `RP-DIFF` | **done, by variation** — `E^(C²) = 4B` computed, not cited |
| **The gauge structure** | `RP-DIFF` independent given `RP-METRIC` | **witnessed**; the anomaly question separately answered in the quantum chain |
| **The spectrum** | uniqueness theorem = ghost theorem, both from `D − 2k = 0` | **partial** — the ghost's *dynamical* consequence is open |

The assumption count is **vocabulary-dependent**: six written as an action, five
written as field equations, for the same theory. `RP-TOPO-INERT` is independent
on actions and invisible on field equations; `RP-DIVFREE` runs the other way. A
ledger that does not say which side it counts on is not saying anything.

## 3. The assumptions, and their witnesses

| tag | assumption | independence witness |
|---|---|---|
| `RP-LOCAL` | the action is `∫` of a local density | `k − j = D/2` has infinitely many solutions once inverse boxes are allowed — **locality is what makes the classification unique** |
| `RP-METRIC` | the metric is the only field | `√−g φ⁴` — diff- *and* Weyl-invariant at derivative order **zero** |
| `RP-DIFF` | diffeomorphism invariance | `√−g (g⁰⁰)²` — Weyl-invariant, not a scalar; the diff-invariant subspace of the lowest weight-zero degree is **exactly 0 of 55** |
| `RP-WEYL` | local Weyl invariance | `R²` — Weyl-variant, outside `span{C², E₄}` |
| `RP-DIM4` | `D = 4` | the weight `D − 4`; `√−g C²` is invariant iff `D = 4` |
| `RP-TOPO-INERT` | topological terms are inert | `E₄` — invariant, not a multiple of `C²` |
| `RP-PARITY` | parity invariance | `W₊²` — invariant, not parity-even |

The first three were the hard ones, and they were **one phenomenon**: each was
*vacuous on the carrier the classification used* — true of every element, hence
unwitnessable there for reasons having nothing to do with necessity. The cure in
each case was to remove the construction constraint that made it vacuous
([`carrier-vacuity.md`](carrier-vacuity.md),
[`diff-independence.md`](diff-independence.md),
[`carrier-enlargements.md`](carrier-enlargements.md)).

`RP-METRIC`'s witness exponent is the check worth quoting: `k = 2D/(D−2)` falls
out of two independent conditions and reproduces `φ⁶`, `φ⁴`, `φ³` in
`D = 3, 4, 6` — integer exactly when `(D−2) | 4`, the classical trio.

**Conditional, stated not hidden.** `RP-DIFF`'s independence is *given*
`RP-METRIC`: the Stückelberg escape is blocked by the field content rather than
refuted.

## 4. What the assumptions buy

**The derived derivative order requires three of them**, each failing
differently:

| drop | what becomes available |
|---|---|
| `RP-DIFF` | derivative order **0** — diff- and Weyl-invariance are never both satisfiable there, and without `RP-DIFF` only the second is required |
| `RP-METRIC` | derivative order **0** via `√−g φ^{2D/(D−2)}` |
| `RP-LOCAL` | every `k ≥ D/2`; uniqueness destroyed, not weakened |

**And the ghost is the same theorem as the uniqueness.** `D − 2k = 0` pins the
propagator's pole count at `D/2`, and for simple poles the residues alternate, so
two or more poles always include a negative one. The action is unique, therefore
**the ghost cannot be tuned away by choosing a better conformal action — there is
no other conformal action.** Dropping `RP-WEYL` keeps curvature degree 2;
`D = 6` is worse.

So the three assumptions that make the derivative order derivable are exactly
the three whose dropping could evade the ghost. For each, what is established is
that **the derivation fails** — not that the ghost is removed. A non-covariant,
nonlocal or multi-field theory is not thereby ghost-free.

## 5. The geometry column

*"The bulk of the intellectual content"*, and it was entirely imported. It is now
closed:

| | entry | status |
|---|---|---|
| `G1` `G2` `G3` `G5` `N1` | curvature identities, the non-degeneracy witness, `∇^a B_ab = 0` | **discharged** against this repository's own curvature engine |
| `G6` | `Riem·⋆Riem = C·⋆C` | **discharged** (computable clause); spanning clause cited |
| `G8` | `W±²` | **discharged, both signatures** |
| `N2` | the trace law | **discharged** |
| `G4` `G7` `N3` | topological | **cited**, each carrying its source's own boundary |

Two entries turned out sharper than the ledger stated them.

**`G8` is two statements, not one.** `W±² = (C² ± P)/2` is *Euclidean*; the
Lorentzian form is `W±² = (C² ∓ iP)/2` with complex projectors, and the textbook
form is **checked false** there.

**`N2` factorises.** `g^mn E_mn = 2(a + b + 3c)□R`, where `a + b + 3c = 0` is
exactly the classification's Weyl equation — so the kernel of the trace map is
`span{C², E₄}`, which *is* `RP-WEYL ⟺ RP-TRACELESS` with both directions.
**`N2` and `G5` need the same witness**, so a ledger that lost `G5` would
silently lose `N2`.

## 6. Against Einstein gravity

The two theories sit over the **same base** and differ by **one swap**, and the
swap is *forced*: no four-dimensional local metric action is both Weyl invariant
and second order.

```text
shared base   RP-LOCAL, RP-METRIC, RP-DIFF, RP-DIM4
Einstein      + RP-2ND-ORDER               →  a G_ab + b g_ab
Weyl          + RP-WEYL (+ RP-TOPO-INERT)  →  B_ab
```

**Both sides are now computed here**, at `D = 4` and curvature degree ≤ 2 for
the Einstein side ([`einstein-classification.md`](einstein-classification.md)) —
with no field-equation formula imported, the Lanczos tensor derived from the
forced head plus divergence-freedom and checked to vanish identically.

Because the swap is one trade, what Weyl gravity **opens** and what it
**challenges** are two halves of it, not two lists
([`OPENS-AND-CHALLENGES.md`](OPENS-AND-CHALLENGES.md)). The sharpest pair is a
single theorem read twice: the equation that lets you *derive* the derivative
order is the equation that *forces* the ghost.

And the comparison needs a **level**, because the same sentence flips:
*"Einstein gravity is contained in Weyl gravity"* is **true at the solution
level** (`Ric = Λg ⟹ B_mn = 0`) and **false at the symplectic level**
(`REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED`, Cauchy matrix ranks 0 and
2). Both halves are established in this repository. Einstein solutions sit inside
Weyl gravity as a **degenerate locus, not a subsystem**.

## 7. What is open

- **The ghost's dynamical consequence.** Whether it destabilises the physical
  sector is uncharacterized. `GHOST_MODEL_OBSTRUCTION` showed the coprime
  obstruction decides it in **neither** direction, and this stream has already
  retracted one reading of it with proof.
- **No Newtonian constant.** With no dimensionful constant in the action, the
  gravitational scale must be *generated*. Not established here.
- **A weakenable base.** Every equivalence is over a *declared carrier*, which is
  not the reverse-mathematics notion. The stream's oldest open problem — but it
  now has a stated operation and three worked instances
  ([`carrier-vacuity.md`](carrier-vacuity.md)).
- **Scope limits**, all stated in the certificates: the discharges are exact **at
  specific metrics**, not theorems for all metrics; the carrier work is at
  **derivative order zero** and the lowest weight-zero degree; the Einstein side
  is **degree ≤ 2 in `D = 4`**; `G4`/`G7` give only the **local** form of
  statements usually quoted globally; `N2` is **classical**, not the trace
  anomaly.

## 8. Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.<module> --check
```

for each of `weyl_action_rocq`, `weyl_ghost_forced`, `weyl_ghost_dipole`,
`weyl_geometry_discharge`, `weyl_dual_discharge`, `weyl_trace_law`,
`einstein_classification`, `diff_independence`, `carrier_vacuity`,
`carrier_enlargements`, `weyl_vs_einstein_ledger`, `lh_assembly`,
`ghost_model_obstruction_rocq`, `scattering_c_factorisation` —
**14 passed, 0 failed**, 289 s total. The sympy-backed rails need the mise
interpreter.

```bash
cd rocq && ./run.sh          # RESULT: 28 green (0 red); GATE: PASS
PYTHONPATH=. python3 -m unittest discover -s reverse_physics/tests -t .
                             # 160 tests OK
```

The Rocq gate carries fail-closed negative controls: false claims are submitted
to `coqc` and must be **rejected**. A gate that only ever accepts is not a gate.

The fast suite is the commit-loop rail; the expensive certificate rails are
deliberately kept out of it.

---

## The one-line version

The Weyl action is equivalent to five assumptions rather than implied by six;
every one of them now has an independence witness; the input that makes the
sixth derivable is three of the other five; and the assumption set that makes the
action unique is *incompatible* with `RP-NO-GHOST` — a no-go in exactly the
currency reverse physics deals in.
