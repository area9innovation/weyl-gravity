# Physics, geometry, mathematics — the separation ledger

Reverse physics asks which assumptions a law is *equivalent* to. That question
is only worth asking if you can say what counts as an assumption. This document
is the stream's answer, applied to Weyl gravity and then retrospectively to
everything else it has done.

The short version: **two categories are not enough.** Splitting a derivation
into "assumptions" and "the derivation" hides a third thing — the classical
results the derivation leans on, which are neither physical postulates nor
things the development proves. Naming that third category is what makes the
ledger checkable, and in this stream it changed the answer eight times.

---

## 1. Three categories

| | what it is | how it fails | who can attack it |
|---|---|---|---|
| **PHYSICS** | a claim about the world that could have been otherwise | an experiment | a physicist |
| **GEOMETRY** | a classical mathematical result imported, not re-derived | a textbook is wrong, or the import is misapplied | a mathematician, cheaply |
| **MATHEMATICS** | what this development actually proves | the proof assistant rejects it | nobody — `coqchk` already did |

The middle row is the one usually left implicit, and it is where most of the
real risk lives. In the Weyl-gravity result the *mathematics* is eight lines of
rational linear algebra that no reviewer will doubt; the *physics* is five
assumptions that are exactly what is under discussion; and everything in between
— Gauss–Bonnet, the conformal transformation laws, the chiral split — is
**imported**. A reader who wants to attack the result needs to know which of the
three they are attacking.

### 1.1 Three columns say what a theory *is*, not what it *does*

Comparing Weyl gravity to Einstein gravity needs two further axes, and they are
forced rather than chosen — see
[`OPENS-AND-CHALLENGES.md`](OPENS-AND-CHALLENGES.md).

A **direction**: OPENS, CHALLENGES, or SHARED. The third is the one people get
wrong, by charging Weyl gravity for a bill Einstein gravity also owes —
`RP-DIFF` is *shared*, so neither its cost nor its now-established witness
(§4.7) belongs to Weyl gravity alone.

A **level**: `L0` action, `L1` field equations, `L2` solution locus, `L3`
symplectic/dynamical, `L4` quantum. §3.2b below already shows the assumption
*count* changes between `L0` and `L1`. The comparison ledger shows something
stronger: the *truth value* changes too. `Ric(g) = Λg ⟹ B_mn(g) = 0` makes
"Einstein gravity is contained in Weyl gravity" true at `L2`, and
`REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED` makes it false at `L3`.
Both are established in this repository.

And it yields the organising claim that the three columns alone cannot state:
Einstein and Weyl sit over the *same base* and differ by *one swap* —
`RP-2ND-ORDER` for `RP-WEYL` — which is **forced**, because no four-dimensional
local metric action is both Weyl invariant and second order. So OPENS and
CHALLENGES are two halves of one trade, and the sharpest pair is a single
theorem read twice: `D − 2k = 0` both *derives* the derivative order (§4.3) and
*forces* the ghost (§7.5).

## 2. Five operational tests

These are what the stream actually uses, not a philosophy.

**T1 — the mechanisation test.** State the claim in a zero-axiom proof assistant
with all physical vocabulary removed. What survives as a *theorem* is
mathematics. What has to be *supplied as a hypothesis* is not. This is a
mechanical sorting procedure, and `Print Assumptions` reports the result.

**T2 — the counterfactual test.** Ask: what would have to be false for this to
fail? *An experiment* → physics. *A published theorem* → geometry.
*An arithmetic fact* → mathematics.

**T3 — the coordinate test.** A physical assumption must not depend on a
bookkeeping choice. If relabelling changes which assumption is being made, the
assumption is bookkeeping. This test killed one (§4.1).

**T4 — the witness test.** An assumption with no independence witness is doing
no work: it is either implied by the others or vacuous. Every assumption in a
finished reverse-physics ledger must come with a system satisfying all the
*others* in which the law fails.

**T5 — the level test.** An assumption can be independent at one level of
description and redundant at another. Naming the level is part of naming the
assumption. This is the whole content of §4.4.

Tests T1 and T4 are the ones the substrate mechanises. T2, T3 and T5 are
judgement, and the ledger records the judgement so it can be disputed.

---

## 3. The Weyl-gravity ledger

The law: `S[g] = α ∫ √−g · C_abcd C^abcd`.
Certificate `REVERSE_PHYSICS_WEYL_ACTION_V1`;
report [`weyl-action-reverse-physics.md`](weyl-action-reverse-physics.md).

### 3.1 PHYSICS — the assumptions under test

| tag | assumption | independence witness | verdict |
|---|---|---|---|
| `RP-LOCAL` | the action is `∫` of a local density | `k − j = D/2` has infinitely many solutions once inverse boxes are allowed | **independent** (§4.8) — locality is what makes the classification unique |
| `RP-METRIC` | the metric is the only field | `√−g φ⁴` — diff- and Weyl-invariant at derivative order **zero** | **independent** (§4.8) |
| `RP-DIFF` | diffeomorphism invariance | `√−g (g⁰⁰)²` — Weyl-invariant, not a scalar | **independent given `RP-METRIC`** (§4.7) |
| `RP-WEYL` | local Weyl invariance | `R²` — Weyl-variant, and outside `span{C², E₄}` | **independent; cuts 3 → 2** |
| `RP-DIM4` | `D = 4` | the weight `D − 4` | **independent; `√−g C²` invariant iff `D = 4`** |
| `RP-TOPO-INERT` | topological terms are physically inert | `E₄` — invariant, not a multiple of `C²` | **independent; cuts 2 → 1** |
| `RP-PARITY` | parity invariance | `W₊²` — invariant, not parity-even | **independent on actions, REDUNDANT on field equations** |

~~Two of these are honest about their status: `RP-LOCAL` and `RP-METRIC` bound
the coordinate space rather than being tested inside it.~~ **All seven now have
witnesses.** `RP-LOCAL`, `RP-METRIC` and `RP-DIFF` were *vacuous on the
carrier* — one phenomenon filed as two kinds of caveat — and all three have been
enlarged (§4.7, §4.8). Saying which is which is still the point of having a
column for it.

### 3.2 GEOMETRY — imported, isolated, never re-derived

| | statement | where it enters |
|---|---|---|
| `G1` | `E₄ = Riem² − 4Ric² + R²`; `C²_D = Riem² − (4/(D−2))Ric² + (2/((D−1)(D−2)))R²` | the coordinate vectors themselves |
| `G2` | `δR = −2σR − 2(D−1)□σ`, `δ√−g = Dσ√−g` | makes the `R²` component carry the whole anomaly |
| `G3` | `C^a_bcd` is Weyl invariant, so `√−g X` of curvature degree `k` has constant weight `D − 2k` | the dimension and derivative-order arguments |
| `G4` | `∫√−g E₄` is topological in `D = 4` | the topological quotient |
| `G5` | **non-degeneracy**: some metric has `□R ≠ 0` (matter-dominated FRW) | without it *every* action counts as invariant — **proved**, not asserted |
| `G6` | the parity-odd quadratic invariants are spanned by `P`; `P = C·C̃` in `D = 4` | the fourth coordinate |
| `G7` | `∫√−g P` is topological | the θ-angle direction |
| `G8` | `W±² = (C² ± P)/2` | the link to the certified residual classes |
| `N1` | Noether/diff: the metric variation of a local diff-invariant action is divergence-free | why `RP-DIVFREE` is not an assumption |
| `N2` | Noether/Weyl: the trace of the variation is a **nonzero** multiple of the anomaly. **Discharged** ([report](weyl-trace-law.md)) and sharper than stated: `g^mn E_mn = 2(a + b + 3c)□R` | the bridge between the two ledgers; the non-vanishing is proved load-bearing, and the multiple is `2` |
| `N3` | a topological term has identically vanishing variation | why `RP-TOPO-INERT` disappears on the field-equation side |

`G5` deserves its place in the list. It is the assumption that keeps the theorem
from being about nothing, and it is exactly the kind of thing that goes missing
when a ledger has only two columns. So it is not merely listed: the development
*proves* that removing it collapses the classification — with the input replaced
by `False`, every action comes out Weyl invariant. An imported result that
cannot be shown to be load-bearing does not belong in the middle column at all;
it belongs in a footnote, or nowhere.

### 3.2b The same law, the other vocabulary

A physicist writes the field equation, not the action, and the ledger changes:

| on the **action** | on the **field equations** |
|---|---|
| `RP-WEYL` | `RP-TRACELESS` — proved equivalent, both directions, via `N2` |
| `RP-TOPO-INERT` | *— nothing to assume —* |
| — | *`RP-DIVFREE` — free from `RP-DIFF` via `N1`* |

Two entries move, and both movements are findings.

`RP-TOPO-INERT` is an assumption **with an independence witness** on the action
side and **invisible** on the field-equation side: the variation of a
topological term vanishes identically, so the quotient has already been taken by
the time an equation exists. Divergence-freedom runs the other way — always
quoted as a property of the Bach tensor, it has no independence witness at all,
because it cannot be dropped while `RP-DIFF` is kept.

**So an assumption count is vocabulary-dependent.** Six on one side, five on the
other, for the same theory. A ledger that does not say which side it is counting
on is not saying anything. This is `T5` again, at a different level than §4.4.

### 3.3 MATHEMATICS — what is actually proved

Everything below is a theorem over ℚ in a zero-axiom development, and
independently a rank computation in exact rational Gaussian elimination:

- the parity-even sector is `ℚ³`, and `{C², E₄, R²}` is a basis (rank 3,
  `det ≠ 0`);
- Weyl invariance is the **single linear equation** `a + b + 3c = 0`;
- its solution space is **exactly** `span{C², E₄}` — both containments proved;
- modulo the topological subspace, the answer is **one-dimensional**;
- with parity adjoined: invariant subspace 3-dimensional, topological subspace
  2-dimensional, quotient `3 − 2 = 1`;
- `α W₊² + β W₋²` differs from `((α+β)/2)C²` by exactly `((α−β)/2)P`;
- tracelessness of the field equations is equivalent to Weyl invariance of the
  action, in both directions, and the two conditions pick out the same line;
- the constant-Weyl weight `D − 2k` vanishes iff `D = 2k`, so **odd dimensions
  admit no conformally invariant curvature action at any derivative order**, and
  each even dimension admits exactly one degree.

No floating point appears anywhere on either rail.

---

## 4. Eight times the separation changed the answer

This is the case for the method. Each row is a claim that looked like one
category and turned out to be another.

### 4.1 `inter_dof_closed` looked physical; it is bookkeeping

The torus reversal decomposed the law into three assumptions, of which only two
had a physical reading. The third looked like a defect until the split analysis
showed that for **every** pairing `P` of the coordinates, `intra_P ∧ inter_P` is
the same proposition — closedness — which mentions no split at all.

So the third assumption is the *remainder of a bookkeeping choice*, and the
first is not split-independent either: the same field is marginal for one
degree-of-freedom split and not for a rotated one, with both splits genuinely
symplectic. **Test T3.** Verdict: not physics.

This bears directly on Carcassi–Aidala's *infinitesimal reducibility*, which
presupposes a decomposition into independent degrees of freedom.

### 4.2 `RP-REVERSIBLE` looked independent; it is derived

It appeared under `consumed` in every certificate and `under_test` in none —
structurally, because on the Hamiltonian carriers every evolution is `exp(tA)`
and neither determinism nor reversibility can fail. Moving to a carrier where
they *can* fail gave

```
reversible  ⟺  deterministic ∧ conserves_information
```

**Test T4**, applied by building a carrier where the witness could exist.
Verdict: physics, but not an independent postulate.

### 4.3 "Four derivatives" looked like an assumption; it is a consequence

Standard motivations for conformal gravity list *quadratic in curvature* as an
input. It is not one. The constant-Weyl weight `D − 2k` forces `k = D/2`, so at
`D = 4` only `k = 2` survives — and the same one-line computation excludes the
cosmological term (`k = 0`) and Einstein–Hilbert (`k = 1`).

**Test T4.** Verdict: not an assumption at all. The standard motivation uses one
more physical input than it needs.

### 4.4 `RP-PARITY` is independent *and* redundant, depending on the level

The chiral family `α W₊² + β W₋²` is a genuine two-parameter family of
**actions** — the map is injective, and `W₊²` is provably not parity-even. But
it is a one-parameter family of **field equations**, because the difference is
`((α−β)/2)P` and `P` is topological.

**Test T5.** Verdict: independent on actions, redundant on the classical theory,
and physical again only in the quantum theory, where the coefficient of `P` is a
gravitational θ-angle. This programme's claim boundary does not reach that.

Stated in the repository's own terms: `RP-PARITY` is exactly the assumption that
ties `[W₊²]` and `[W₋²]` together — and classically it is free of charge.

### 4.5 A physics reading that was simply wrong

The coprime-hierarchy report claimed the obstruction is the channel through
which a ghost mode destabilises the healthy one. Audited exactly, it failed
twice: the coded free Hamiltonian is positive definite, and the obstruction
conserves `J = p·n̂₁ + q·n̂₂`, a positive charge that *bounds* both occupations
regardless of any ghost sign.

**Test T2.** The claim had no counterfactual — nothing was going to falsify it,
because it was an interpretation attached to a theorem rather than a claim in
its own right. It was retracted with proof:
[`coprime-charge-bound.md`](coprime-charge-bound.md).

That the ledger caught a claim *this stream published* is the strongest evidence
here that the discipline is load-bearing rather than decorative.

### 4.6 A physical quantity that provably cannot exist

*"How many degrees of freedom are in this region"* is not a well-posed question
in a conformally invariant theory. All three branches of the Carcassi–Aidala
trilemma close: the density branch by a parity obstruction in odd dimension, the
counting measure as uninformative, and the non-additive branch because on flat
space a dilation is conformal, so a unit ball and one of radius `10¹⁰⁰` tie —
additivity is never used.

What survives is a *relative* count, generated by a single scaling exponent, and
degree-of-freedom independence transposes to additivity of that exponent.

**Test T2** again, with the counterfactual supplied by the theory's own symmetry
group rather than by experiment.

---

### 4.7 An assumption believed untestable in principle, witnessed

`RP-DIFF` was recorded in §6 as having no independence witness *at all* — the
one entry where the ledger's own `T4` could not be applied, because
diffeomorphism invariance is what makes "the space of curvature scalars" the
right space to begin with.

That was true of the **carrier**, not the assumption, and §4.2 is the precedent:
`RP-REVERSIBLE` was unwitnessable on the Hamiltonian carriers for exactly the
same structural reason, and moving to a carrier where it *could* fail resolved
it immediately.

Enlarging to local metric densities at derivative order zero — dropping the
requirement that indices contract into scalars — the lowest weight-zero degree
`√−g h^ab h^cd` is **55-dimensional and entirely Weyl-invariant**, while its
diffeomorphism-invariant subspace is **exactly 0** (exact rank over ℚ, two
independent routines, with a control space whose known one-dimensional invariant
is found). Every element is a witness; `√−g (g⁰⁰)²` is the explicit one.

**Test T4**, applied by building a carrier where the witness could exist.
Verdict: independent — **given `RP-METRIC`**, since the Stückelberg escape is
blocked by the field content rather than refuted. The carrier is `EMPTY` rather
than `LIVE` for `RP-DIFF`; the witness stands, but the union with the curvature
scalars is the carrier to quote ([report](carrier-vacuity.md)).

And the consequence is the reason it matters. The witness has **zero**
derivatives, while §4.3's derived order says `k = D/2 = 2`. That derivation runs
through `G3`, the conformal weight of the *Weyl tensor* — already diff-covariant.
So **the derived derivative order requires `RP-DIFF`**: the stream's best result
was silently using the one assumption the ledger had marked as carrying no
weight. §4.3 still stands; what changes is that its input is now named.

[`diff-independence.md`](diff-independence.md)

### 4.8 And then the other two — the derived order needs all three

The vacuity audit ([report](carrier-vacuity.md)) found that `RP-DIFF` was not
alone: **`RP-LOCAL` and `RP-METRIC` are vacuous on the same carrier for the same
reason**, and §3.1's "assumed, not tested here" was recording that fact without
naming it. The same operation treats them
([report](carrier-enlargements.md)).

**`RP-METRIC`** — admit a compensator scalar. Weight bookkeeping gives
`k = 2D/(D−2)`, so `√−g φ⁴` is local, diffeomorphism-invariant, Weyl-invariant
and parity-even at **derivative order zero**. The exponent is not put in: it
falls out of two independent conditions and reproduces `φ⁶`, `φ⁴`, `φ³` in
`D = 3, 4, 6` — integer exactly when `(D−2) | 4`, which is the classical trio.

**`RP-LOCAL`** — admit inverse boxes. Invariance becomes `k − j = D/2`, with
**one** solution at `j = 0` and one per `j` otherwise. Locality is what makes
the classification *unique*, not merely finite.

**The joint statement is the finding.** §4.3's derived derivative order requires
**all three**, and each fails differently:

| drop | what becomes available |
|---|---|
| `RP-DIFF` | derivative order `0` — F3 forbids it only while `RP-DIFF` holds |
| `RP-METRIC` | derivative order `0` via `√−g φ^{2D/(D−2)}` |
| `RP-LOCAL` | every `k ≥ D/2`; uniqueness destroyed |

§4.3 said the standard motivation *"uses one more physical input than it needs"*.
That stands. What is now sayable is **which inputs it does need** — and all three
were untested until §4.7 and this.

It also fills in a row of the ghost table (§7.5) that read *"not analysed"*:
dropping `RP-DIFF` makes the pole-count argument **not run**. That is not the
same as removing the ghost, and is recorded at exactly the strength the
`RP-LOCAL` and `RP-METRIC` rows already carry.

---

## 5. The loop that closed

§4.6 found, without looking for it, that the parity balance excluded in odd
dimension **is** achievable in dimension four, at weights `(m,D) = (2,0)` —
exactly the weight of `C_abcd C^abcd`. At the time that was an observation:
conformal gravity is the even-dimensional case where a conformal density exists,
and a Cauchy surface is the odd case where it cannot.

§3 now closes that loop from the other side: the object whose existence the
counting argument predicted is not merely *a* conformal density in four
dimensions, it is — modulo topology — **the only one**.

Two independent lines of the stream, one about counting degrees of freedom and
one about classifying actions, meet on the same object. Neither was set up to
find the other.

---

## 6. Where the line is still blurred

Honest limits, because a separation ledger that claims to be clean is not one.

- **`RP-LOCAL` and `RP-METRIC` are not tested.** They bound the coordinate space
  rather than living inside it. To test them one would need a carrier containing
  nonlocal or multi-field actions, and this stream has not built one.
- ~~**`RP-DIFF` is invisible.** It is what makes "the space of curvature
  scalars" the right space at all, so it never appears as a row in a matrix.
  That is a real gap: an assumption doing structural work should still get a
  witness.~~
  **Closed** ([report](diff-independence.md), §4.7). The diagnosis was right and
  it was about the *carrier*, not the assumption — exactly as in §4.2. On the
  enlarged carrier of local metric densities at derivative order zero, the
  lowest weight-zero degree is 55-dimensional and its diff-invariant subspace is
  **exactly 0**, so every element is a witness; `√−g (g⁰⁰)²` is the explicit
  one. The conditional is real and is recorded: this is independence **given
  `RP-METRIC`**, because the Stückelberg escape is blocked by the field content
  rather than refuted.
- **The conformal results are for constant rescalings** where the weight
  argument is used. The full local group is used only through `G2`, and the
  no-go on conformal densities should strengthen under it — but that is not
  shown.
- **Geometry is imported wholesale.** `G1`–`G8` are standard, but they are the
  bulk of the intellectual content and none of them is machine-checked here.
  Deriving even `G1` from a formalised Riemann tensor would move a large block
  from the middle column to the right one.
  ~~**Half done**~~ **Now closed**
  ([discharge](weyl-geometry-discharge.md), [dual](weyl-dual-discharge.md),
  [trace law](weyl-trace-law.md)): `G1`, `G2`, `G3`, `G5` and `N1` are computed
  exactly against this repository's own curvature engine
  (`black_hole_programme/weyl_geometry.py`); `G6`'s computable clause and `G8`
  in **both signatures** are discharged against `local_bv/hodge.py`'s
  conventions; **`N2` is discharged** as a trace law; `G4`, `G7`, `N3` and
  `G6`'s spanning clause are **cited** to existing certificates, each carrying
  its source's own boundary. Every entry is now discharged or explicitly cited.
  Note what a discharge is: exact verification **at specific metrics**, stronger
  than an import and weaker than a theorem for all metrics.
  Two things turned out sharper than this document stated them. `G8` is **two**
  statements, not one — `W±² = (C² ± P)/2` is *Euclidean*, the Lorentzian form
  is `W±² = (C² ∓ iP)/2` with complex projectors, and the textbook form is
  checked **false** there. And `N2`'s "nonzero multiple of the anomaly" is
  `g^mn E_mn = 2(a + b + 3c)□R` — the multiple is `2`, and the anomaly
  *factorises* into the Weyl-invariance functional `a + b + 3c` times `□R`, so
  the kernel of the trace map is exactly `span{C², E₄}`. **`N2` and `G5` need
  the same witness**, which is a concrete reason the middle column has to stay
  visible.
- **The Bach tensor is never computed *by this stream*.** "Same field equations" is
  *defined* as "differ by a topological term". That is `RP-TOPO-INERT`, not a
  variational calculation. §3.2b classifies the *space* of field equations and
  proves the two vocabularies agree; naming the generator was done in prose, on
  the strength of Noether.
  **Corrected** ([report](weyl-geometry-discharge.md)): the repository has computed
  it all along — `black_hole_programme/weyl_geometry.py` carries an exact Bach
  tensor. Wiring the ledger to it discharges `N1` directly (`∇^a B_ab = 0`, the
  Noether/diff content, computed rather than imported) along with trace-freeness,
  conformal weight `−2`, and `B_ab = 0` on an Einstein metric — the last being why
  Schwarzschild solves Weyl gravity at all. ~~The **variational link itself**,
  `δ∫√−g C² = 4∫√−g B_mn δg^mn`, is still not re-derived here; it is checked
  elsewhere in this repository on the Nariai product family and is cited rather
  than repeated.~~
  **Now derived** ([report](weyl-trace-law.md)): the `C²` field-equation tensor
  is assembled from the quadratic pieces and compared against this repository's
  own independently computed Bach tensor, giving `E^(C²)_mn = 4 B_mn` exactly on
  every nonzero component, at a metric that is neither Einstein nor conformally
  flat. **The factor 4 is computed, not assumed**, and it agrees with the value
  cited to the Nariai product-family check
  (`d_quotient_classical/reports/nariai-action-derived-bach-endpoint.md`). So
  "same field equations" no longer rests on `RP-TOPO-INERT` as a *definition*:
  the field-equation side is now characterized by variation.
- **No reversal over a weakenable base.** Reverse mathematics compares against a
  base theory one can weaken. Every equivalence here is over a *declared
  carrier*. This is the stream's oldest open problem and it is not closed.
  **But it now has an operation and two worked instances**
  ([report](carrier-vacuity.md)). The correspondence is exact: *the carrier is
  the base, and an assumption vacuous on the carrier is an axiom the base
  already proves.* An assumption is `VACUOUS`, `LIVE` or `EMPTY` on a carrier;
  it can be witnessed iff it is not vacuous; and an assumption that is also a
  **construction constraint** of the carrier is vacuous, so the enlargement that
  makes it testable is the removal of that constraint. §4.2 and §4.7 are both
  instances. Auditing this ledger against it finds that **three** assumptions
  were vacuous on the carrier the classification used — `RP-LOCAL`, `RP-METRIC`
  and `RP-DIFF` — one phenomenon where §6 above recorded two kinds of caveat.
  **All three are now migrated** ([report](weakenable-base.md)), and the
  structure is a lattice: bases are subsets of the construction constraints,
  vacuity is **monotone** in it, and `(axioms) + (live assumptions)` is
  **constant**, so content is conserved and only its visibility moves. This
  stream therefore already sits at the weakest base it can state. **The problem
  is still not closed** — there is no proof system, no notion of what a base
  *proves* beyond identical satisfaction, and the weakest base is a description
  rather than a construction. It is no longer shapeless.
- **Nothing transfers between carriers.** The stochastic equivalence is four
  states and one step; the torus results are flat `T⁴` and polynomial fields.

---

## 7. How to attack this

The most efficient objections, in order of how much they would cost us:

1. **Reject `G5`.** ~~The witness metric is named, not formalised.~~
   **This attack is closed** ([report](weyl-geometry-discharge.md)). If `□R`
   vanished identically the classification would be vacuous — a theorem, not
   rhetoric (`without_non_degeneracy_the_classification_is_vacuous`). The witness
   is now **computed**: matter-dominated FRW gives `R = 4/(3t²)` — exactly the
   value that used to be asserted — and `□R = −8/(3t⁴) ≠ 0`, in this repository's
   own exact curvature engine. It is also shown to be a real CHOICE rather than a
   formality: Schwarzschild has `R ≡ 0`, so `□R ≡ 0`, and the vacuum solutions
   this repository mostly computes with **cannot** witness `G5`.
   The claim that "this development does not have a Riemann tensor" was true of
   this *stream* and false of the *repository* — the engine had a dozen consumers
   already. Searching the corpus before deriving would have found it.
2. **Deny `RP-TOPO-INERT`.** It is false quantum-mechanically, and the whole
   parity result is stated modulo it. Anyone working at the quantum level should
   reject §4.4's "redundant" and keep parity as a live assumption. We agree; the
   claim boundary says so.
3. **Attack the coordinate space.** If there are quadratic curvature scalars
   outside `span{Riem², Ric², R², P}` modulo total derivatives, the dimension
   count is wrong from the first line. There are not, but that is `G1`/`G6`,
   imported.
4. **Point out the theorem is textbook.** True, and stated in the certificate's
   `does_not_establish`. The claim is about the ledger, the witnesses, the
   derived derivative order and the parity result — not about the classification.
5. **Ask whether the ledger buys anything about gravity, or only about method.**
   That was the right question, and it has an answer:
   [`weyl-ghost-forced.md`](weyl-ghost-forced.md). The same equation `D − 2k = 0`
   that makes the derivative order derivable also pins the propagator's pole
   count at `D/2`, and two or more poles always include a negative residue — so
   **the uniqueness theorem and the ghost theorem are the same theorem**, and the
   ghost cannot be tuned away by picking a different conformal action. Dropping
   `RP-WEYL` or `RP-DIM4` provably does not help. That is a statement about the
   subject, not about the method, and the ledger is what surfaced it.
6. **Ask what any of this predicts.** The sharpest thing on offer is negative
   and cheap to check: the conformally invariant curvature degree in `D`
   dimensions is `k = D/2`, so **odd dimensions have no conformally invariant
   local curvature action at all**, at any derivative order, and each even
   dimension admits exactly one degree. Proved on both rails. `D = 6` selects
   the cubic sector, which is the declared next gate. Note this meets §4.6 from
   the other end: two different parity obstructions, on two different objects,
   with the same shape of conclusion, and four dimensions is where both are
   satisfied at once.

---

## 8. The one-line version

Reverse physics is only as good as its ledger, and a two-column ledger is not
one. Three columns — physics, imported geometry, proved mathematics — with a
mechanised test for the boundary between the second and third, and an
independence witness required for every entry in the first. Applied to Weyl
gravity it yields five assumptions instead of six, an equivalence rather than an
implication, one assumption that is independent and redundant at the same time
depending on what you are classifying — and the discovery that the *count itself*
depends on whether you write the theory as an action or as a field equation.

Applied to this stream's own earlier work, it retracted a published claim. And
applied to its own textbook result, it produced one that is not textbook: the
assumption set that makes the Weyl action unique is *incompatible* with
`RP-NO-GHOST`, which is a no-go in exactly the currency reverse physics deals
in.

Extended to a *comparison* between theories it needs two more axes — a direction
and a level ([`OPENS-AND-CHALLENGES.md`](OPENS-AND-CHALLENGES.md)) — and then
says something the three columns cannot: Einstein and Weyl differ by one forced
assumption swap, so what Weyl gravity opens and what it challenges are two sides
of a single trade rather than two lists.

---

## Verification

```bash
cd rocq && ./run.sh                                   # 24 green (0 red), 173/173 closed
PYTHONPATH=. python3 -m reverse_physics.weyl_action_rocq --check
PYTHONPATH=. python3 -m reverse_physics.weyl_vs_einstein_ledger --check   # 18 rows, 13/13 controls
PYTHONPATH=. python3 -m unittest discover -s reverse_physics/tests -t .

# the second rail, in tango:
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_action_classification_gate.forge    # 40/40, c==native, asan clean
```
