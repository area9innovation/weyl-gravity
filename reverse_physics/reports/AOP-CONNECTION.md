# Two connections to the Assumptions of Physics programme

Where this stream's results bear on Carcassi and Aidala's reverse-physics
programme, and where conformal gravity bears on their open conjecture for
general relativity.

Written to be readable by them. Everything asserted about our side is
machine-checked with zero axioms; everything asserted about theirs is cited.

**Sources for their side** are the published papers and the 2024 Summer School
lecture slides, read directly. We have **not** read the book
(*Assumptions of Physics*, Michigan Publishing, v2 2023), so where a slide is
terse we say which of two readings we are responding to rather than assert one.
§2.1b–2.1d were written against the slides' own labelled characterizations, and
quote them.

---

## 0. What we are responding to

Their established classical result ([Found. Phys. **52**, 40 (2022)][rp];
[*Classical mechanics and infinitesimal reducibility*, 2021][cmir]) is

> Hamiltonian mechanics ⟺ determinism/reversibility + independence of the
> degrees of freedom (+ kinematic equivalence).

The structure carrying it, as presented in [*Reverse Physics for GR*][gr]
(Michigan, 16 Nov 2024, slide 2), is the symplectic form written as a tensor
product

```
ω_ab = [[0, 1], [−1, 0]] ⊗ I_n
```

with the two factors given **distinct physical readings**:

| factor | reading on the slide |
|---|---|
| `J` | *"Area within each DOF"* — `Areas = #confDOF` |
| `⊗ I_n` | *"Scalar product across DOFs"* — `#states = ∏ #confDOF` |

And their open conjecture, from the same talk:

> **GR ⟺ det/rev + DOF independence for infinitely many (dense) DOFs**

with `#DOFs` proposed as a spatial volume, `∫_U √−g d³x` — *"#DOFs are the
points on the Cauchy surface, #conf are the possible field values at each
point"*. The talk closes on open questions, not results.

Two connections follow. The first is a comment on the established theorem's
*interpretation*. The second is about the conjecture, and it is the one where
conformal gravity has something specific to say.

---

## 1. The tensor factorisation is bookkeeping, not physics

**Our carrier.** Trigonometric-polynomial vector fields on `T⁴` with
`ω = dq₁∧dp₁ + dq₂∧dp₂`. Everything block-diagonalises over Fourier modes, so
each mode is an exact rational problem. This is a *field theory*, which is why
it can speak to the conjecture and not only the theorem.

**The bridge is proved, not assumed.** `omega_is_J_tensor_I` checks entrywise
that the `ω` this development has used throughout is exactly their `J ⊗ I₂`,
once the interleaved ordering `(q₁,p₁,q₂,p₂)` is matched to the block ordering
`(q₁,q₂,p₁,p₂)`. `alpha_of_is_contraction_with_omega` pins down that our
`ι_X ω` is contraction with that form and nothing else.

**The finding.** Their two factors are given distinct physical readings. But the
division of the closedness conditions into *within-DOF* and *across-DOF* depends
on which Lagrangian decomposition is called "the degrees of freedom", and

> for **every** such decomposition, the conjunction is the same proposition.

`split_dependence_cancels`: for each of the three pairings `P` of the four
coordinates, `intra_P ∧ inter_P ⟺ closed`, and `closed` mentions no
decomposition at all. The split is visible in each factor and invisible in the
product.

**And the `J` factor alone is frame-dependent.**
`marginal_not_invariant_under_admissible_splits`: the field
`X = cos(2πq₁) ∂_{q₂}` preserves the area within each degree of freedom for the
standard decomposition and **fails to** for the rotated one

```
V₁′ = span(∂q₁+∂q₂, ∂p₁+∂p₂)     V₂′ = span(∂q₁−∂q₂, ∂p₁−∂p₂)
```

and `rotated_split_is_admissible` proves both are genuine symplectic
decompositions — each block symplectic, the blocks ω-orthogonal.

**So:** *"each degree of freedom independently conserves its information"* is not
a statement about the dynamics alone. It is a statement about the dynamics
**together with a choice of what counts as a degree of freedom**, and the law is
invariant under changing that choice while the assumption is not.

**This does not refute the theorem.** The conjunction is invariant, which is why
the theorem holds. It is a claim about the decomposition used to give it physical
meaning — and it bears on *infinitesimal reducibility*, which presupposes a
decomposition into independent degrees of freedom. Here that decomposition is
provably a choice, and an assumption built on it inherits the arbitrariness.

*(An earlier version of our own theorem compared against the pairing
`{(q₁,q₂),(p₁,p₂)}`, which is **isotropic** — ω vanishes on both blocks — so it
is not a degree-of-freedom decomposition at all. We corrected that and record it
here because the same trap is easy to fall into: of the three ways to pair four
coordinates, exactly one is symplectic.)*

---

## 2. The GR conjecture needs a term the classical theorem does not have

This is the substantive one.

### 2.1 On a field theory with topology, preserving ω is not enough

On `T⁴`, the chain has **four** levels, not three:

```
Hamiltonian ⊆ symplectic ⊆ marginal ⊆ volume-preserving
```

The finite-dimensional case has only three, because `H¹(ℝ^{2n}) = 0` collapses
*preserves ω* and *is Hamiltonian* into one condition. A field theory need not.

Computed in Forge with exact rational rank, then proved in Rocq for **all**
Fourier modes:

| N | vol | marg | symp | ham | **symp−ham** | marg−symp | vol−marg |
|---|---|---|---|---|---|---|---|
| 0 | 4 | 4 | 4 | 0 | **4** | 0 | 0 |
| 1 | 244 | 180 | 84 | 80 | **4** | 96 | 64 |
| 2 | 1876 | 1300 | 628 | 624 | **4** | 672 | 576 |
| 3 | 7204 | 4900 | 2404 | 2400 | **4** | 2496 | 2304 |

The two local gaps **grow** with resolution. The symplectic→Hamiltonian gap is
**4 at every truncation**, and every nonzero mode contributes exactly zero to it.
The whole obstruction sits in the zero mode and equals `b₁(T⁴)`. Nothing in the
computation mentions cohomology; the Betti number is reproduced, not assumed.

The witness is physically plain: **uniform translation** `X = ∂_{q₁}`. It is
deterministic, reversible, preserves the area within each degree of freedom,
preserves the total phase-space volume, preserves ω — and admits **no global
Hamiltonian**.

`aop_conjecture_needs_a_topological_term` and
`aop_missing_term_is_exactly_the_first_cohomology` state this in their
vocabulary. The gate carries a negative control asserting that preserving ω
suffices; it is rejected.

**Consequence for the conjecture.** *GR ⟺ det/rev + DOF independence for dense
DOFs* cannot hold as stated on a state space with `b₁ ≠ 0`, because the
right-hand side is satisfied by fields the left-hand side excludes. The
conjecture needs a third ingredient — a cohomological condition — with no
counterpart in the finite-dimensional theorem. Their slide asks
`δ∫L dⁿs = ???`; whatever the answer, it must carry such a term.

### 2.1b Where this sits in the twelve-fold diagram

§2.1 was written against the GR conjecture. The 2024 Summer School lecture
([*Classical Mechanics*][ss2024], slides 15–41) gives a sharper target: twelve
labelled characterizations, stated as equivalent **for a single degree of
freedom**, and a two-block diagram for multiple degrees of freedom.

```text
HM-G   ⟺  DI-CURL           DR-JAC  ⟺  DR-DIV
  ⇕          ⇕        ⟹        ⇕          ⇕
DI-POI ⟺  DI-SYMP           DR-DEN  ⟺  DR-VOL
```

*"For multiple DOFs, statements about areas are stronger than statements about
volumes."* The strictness is witnessed on slide 40 by linear drag on one degree
of freedom and linear acceleration on the other: `∂_a S^a = −b + b = 0`, so
`DR-DIV` and `DR-VOL` hold, while the curl is `−b ≠ 0`, so `DI-CURL` and
`DI-SYMP` fail. No Hamiltonian.

Our chain refines that picture in two places.

**A level between the blocks.** Our four-level chain is

```text
Hamiltonian ⊆ symplectic ⊆ marginal ⊆ volume-preserving
```

The left block is `symplectic`; the right block is `volume-preserving`. **Our
`marginal` — each degree of freedom conserves its own information — lies
strictly between them and has no label in the diagram.** It is not a
reformulation of either side: on the linear carrier the separation threshold is
exactly `n = 2` and the gap grows as `2n(n−1)`
(`REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_GENERAL_N_V1`), and on `T⁴` both local
gaps `symp−marg` and `marg−vol` grow with resolution (table in §2.1). So the
one-way arrow between the blocks factors through a third condition, and the
factorisation is quantitative.

**The left block itself is carrier-dependent.** `HM-G` and `DI-SYMP` sit in the
same block, identified. That identification is correct on `ℝ^{2n}` and **false
on a state space with `b₁ ≠ 0`**: preserving `ω` is closedness, having a
Hamiltonian is exactness, and the two differ by `H¹`. On `T⁴` the gap is exactly
`b₁(T⁴) = 4` at every Fourier truncation, with every nonzero mode contributing
zero — proved in Rocq for all modes, with uniform translation `X = ∂_{q₁}` as
the explicit witness.

So the twelve-fold equivalence carries an **unstated hypothesis on the state
space**, not merely the stated one on the number of degrees of freedom. Adding
`H¹ = 0` to the single-DOF qualifier would make it exact.

### 2.1c The same point in our own vacuity vocabulary

This is worth stating in the language of
[`carrier-vacuity.md`](carrier-vacuity.md), because it is the first time we have
turned that instrument on someone else's assumption set rather than our own.

An assumption is `VACUOUS` on a carrier when it holds on every element, and it
**cannot be witnessed there** — "no witness found" and "no witness can exist
here" are different findings. The reverse-mathematics reading is that the
carrier is the base, and a vacuous assumption is an axiom the base already
proves.

`ℝ^{2n}` has `H¹ = 0`. On it, *closed* and *exact* coincide, so the distinction
between `DI-SYMP` and `HM-G` is not merely hard to see — **it is not expressible
there at all**. The carrier has the identification built in, exactly as our
curvature-scalar carrier had diffeomorphism invariance built in until we enlarged
it. Our `T⁴` carrier is the enlargement, and the gap it exposes is `b₁ = 4`.

We found three such assumptions in our own ledger by this route, and the same
audit run against the twelve-fold list flags one identification rather than an
assumption. That is a weaker finding than ours were, and it is worth being clear
that it is a **scope correction, not a refutation**: every one of the twelve
characterizations is correct where it is stated.

### 2.1d The `IND-*` characterizations are stated per degree of freedom

Slide 41 gives four physical characterizations of degree-of-freedom
independence:

```text
IND-DOF    the system is decomposable into independent DOFs
IND-STAT   statistically independent distributions over each DOF
IND-INFO   informationally independent distributions over each DOF
IND-UNC    peaked distributions whose uncertainty is the product over each DOF
```

All four are stated **over each DOF**, which is the shape our split analysis
bears on directly.

Slide 37 supplies the natural defence: `ω` itself picks out what a degree of
freedom is — `ω(dξ, dζ) ≠ 0` iff `{ξ, ζ} = {q^i, p_i}` for some `i`, so
*"orthogonality represents independence"*. That fixes what counts as a
**conjugate pair**. It does not fix **which set of conjugate pairs**, because a
symplectic transformation mixing degrees of freedom produces another set that
`ω` certifies equally.

And that is exactly where our result bites
(`REVERSE_PHYSICS_TORUS_SPLIT_ROCQ_V1`): **the same field is marginal for one
degree-of-freedom split and not for a rotated one, with both splits genuinely
symplectic.** A per-DOF property is therefore not an invariant of the system
unless something beyond `ω` fixes the decomposition.

Two readings, and we do not claim to know which is theirs:

- If `IND-*` is meant as *"there exists a decomposition such that…"*, it is
  well posed and our result is only a warning that the decomposition is part of
  the claim and should be quantified over explicitly.
- If it is meant as *"for the decomposition"*, it inherits the ambiguity, and
  the question *what fixes the split?* is load-bearing rather than
  presentational.

The stream's own version of this finding is that `inter_dof_closed` looked
physical and turned out to be the remainder of a bookkeeping choice — for
**every** pairing `P`, `intra_P ∧ inter_P` is the same proposition, closedness,
which mentions no split at all (§4.1 of the separation ledger). We were the ones
who had to retract a reading there, which is why we raise it as a question
rather than an objection.

[ss2024]: https://assumptionsofphysics.org/presentations/2024SummerSchool/1-ClassicalMechanics.pdf

### 2.2 The fourth desideratum: a parity obstruction

The talk proposes counting degrees of freedom by a spatial volume. Under a
conformal rescaling `g → Ω²g` the induced 3-metric goes `h → Ω²h`, so
`√h → Ω³√h` and the count is not invariant. That much is elementary. The
question is whether *any* repair exists — and the answer is sharper than the
observation.

**Conformal invariance is not a fourth item in your trilemma.** It is a *filter
on which resolutions are admissible*: if `g` and `Ω²g` are the same physical
configuration, they must receive the same count. Applying the filter to the
three branches of

> 1. every point is a single DOF · 2. finite volume carries finitely many ·
> 3. the count is additive — **"Pick two!"**

gives:

| branch | conformally invariant? | informative? |
|---|---|---|
| drop 1 → a density measure `∫_U ρ dvol` | **no** — theorem below | yes |
| drop 2 → the counting measure | yes (it never sees the metric) | **no** — every infinite region gets the same value |
| drop 3 → a non-additive count | not excluded | not excluded |

**The theorem.** Under `g → Ω²g` with constant `Ω`, a local scalar built
polynomially from the metric, its inverse, the Riemann tensor and covariant
derivatives is fixed — *for weight purposes* — by `m` curvature factors and `D`
derivative indices. Every index is contracted in a pair, so `D` is even, and

```
weight = 2m − 2·(4m+D)/2 = −(2m + D)     — always even
```

The volume element on a `d`-manifold has weight `+d`. A density is conformally
invariant exactly when the weights cancel, `2m + D = d`. **For odd `d` there is
no solution.**

A Cauchy surface is three-dimensional. Three is odd.

`no_conformal_dof_density_on_a_cauchy_surface` — machine-checked, zero axioms.
The gate carries a control asserting such a density exists; it is rejected.

So the failure of `∫√h d³x` is not a bad choice of density. **No choice works.**

**And the last branch falls too.** We first concluded that an informative
conformally invariant count must be *non-additive*. It cannot be that either.

On flat space a dilation `φ_λ(x) = λx` pulls the flat metric back to a
**constant** rescaling, `φ_λ*δ = λ²δ`. So for any count natural under
diffeomorphisms and invariant under constant Weyl rescaling,
`μ(φ_λ U) = μ_{λ²δ}(U) = μ(U)` — and **every ball has the count of the unit
ball, whatever its radius**. A ball of radius 1 and a ball of radius 10¹⁰⁰ tie.

**Additivity is never used** in that argument — it is a group action on regions,
not a decomposition of them — which is exactly why dropping additivity buys
nothing.

| branch | status under conformal invariance |
|---|---|
| drop 1 → density | excluded by parity in odd dimension |
| drop 2 → counting measure | invariant but uninformative |
| drop 3 → non-additive | excluded, and equally uninformative |

`no_informative_conformal_count` — machine-checked, zero axioms, with a control
asserting the count grows with radius, rejected.

**So the reading is not that the count is hard to construct.** In a conformally
invariant theory, *"how many degrees of freedom are in this region"* is not a
well-posed question. Your conjecture is stated in terms of such a count, so it
cannot be transported to conformal gravity as written — not because the count is
unknown, but because it cannot exist.

Your talk asks: *"Does lower bound on DOF count require an equally severe
revisitation of space-time?"* On this evidence the revisitation is not optional,
and one of the reasons forcing it is entirely classical.

**The even-dimensional counterpart.** In dimension four the balance *is*
achievable: `2m + D = 4` admits `(m, D) = (2, 0)` — a quadratic curvature
invariant. That is exactly the weight carried by `C_{abcd}C^{abcd}`, the
conformally invariant action of Weyl gravity. So conformal gravity is the
even-dimensional case where a conformal density exists, and a Cauchy surface is
the odd-dimensional case where it cannot.

### 2.3 What replaces the count

The refutation is not the end of the story, and the positive answer is sharp.

Replace the absolute count by a **relative** one, `ν(U,V)` = degrees of freedom
in `U` relative to `V`. Dilation invariance now acts on both arguments, so
`ν(B_r, B_s)` depends only on the **ratio** `r/s` — not degenerate at all, and
exactly what conformal invariance always says: there is no length, only ratios
of lengths.

Add the chain rule `ν(U,W) = ν(U,V)ν(V,W)` and write `f(t) = ν(B_t, B_1)`.
Chaining through `B_b` and dilating by `b`:

```
f(ab) = f(a)·f(b)        hence      f(2ⁿ) = f(2)ⁿ
```

**The whole family is generated by one number.** What survives of "how many
degrees of freedom" is not a function on regions — it is a **single scaling
exponent**.

And the two results are one phenomenon: if a region could serve as an absolute
reference, `f(2) = 1` and the exponent collapses. **The exponent is nonzero
precisely because there is no conformally invariant reference.**

**And your assumption transposes rather than dies.** `#states = ∏ #confDOF` is a
product of counts, and counts do not exist here. But with composite regions as
products, the composite dilation acting diagonally, and the relative count
factorising across independent subsystems — the direct translation of your
assumption — the generating numbers multiply:

```
f_AB(t) = f_A(t)·f_B(t)      hence     g_AB = g_A·g_B      i.e.    d_AB = d_A + d_B
```

**Additivity of the exponent**, proved, and with no logarithm anywhere:
`2^{d_A+d_B} = 2^{d_A}·2^{d_B}` means the multiplicative statement *is* the
additive one. A control asserting the composite keeps only one subsystem's
exponent is rejected, so independence genuinely adds.

The factorisation itself is a hypothesis — it is what is being transposed, not
what is being proved.

**Three honest limits.** There *are* conformal invariants on a 3-manifold — the
gravitational Chern–Simons invariant is one (Chern–Simons, *Ann. Math.* 1974),
and you will think of it immediately. It is not reached by any of the above: it
is **global rather than a local density**, so parity does not apply; and it is
real-valued modulo a framing ambiguity, neither monotone nor region-additive, so
it is not a *count*. It bounds what we claim rather than contradicting it.

The obstruction is for densities built from the **metric alone**. Introducing a compensator or dilaton of nonzero weight evades it — but
only by choosing a scale, which is what conformal invariance forbids. That fork
is real physics, not a loophole. And *realisability* is not addressed: the
arithmetic says which weights are available, not which `(m, D)` are actually
realised by some invariant. The negative result needs only the necessary
condition, so it is unaffected.

---

## 3. What is not claimed

- **No claim about GR.** Our carrier is `T⁴` with a flat structure and
  polynomial fields. Nothing here transfers to a dynamical spacetime. §2.2 is
  about conformal weights, which are kinematic, and says nothing about dynamics.
- **No refutation of their classical theorem.** §1 concerns the interpretation of
  its factors; §2.1 concerns the *conjecture*, and is consistent with the theorem
  because `H¹` vanishes in the finite-dimensional case.
- **No reproduction of their derivation.** We test candidate assumptions on
  declared carriers; we do not reconstruct their argument, and have not checked
  it.
- **§2.2 closes all three branches, but under stated hypotheses.** The parity
  theorem needs densities built from the metric alone; the dilation argument
  needs naturality, monotonicity and flat space, all explicit. Counts using
  extra structure — a compensator or dilaton — are untouched, and evade by
  choosing a scale. What replaces a count is not proposed.
- **The physics on our side is modest.** `symplectic/Hamiltonian ≅ H¹` is
  classical symplectic geometry. What is new is the assumption analysis and the
  mechanization, not the underlying mathematics.
- **No quantum, causal, or field-theoretic claim** beyond the declared carriers.

---

## 4. Reproducing our side

```bash
cd rocq && ./run.sh     # 18 green (0 red); coqchk axiom section <none>
```

Thirteen zero-axiom Rocq modules, thirteen fail-closed negative controls. The bridge
is `rocq/ReversePhysicsAOPBridge.v`, the parity obstruction
`rocq/ReversePhysicsConformalCount.v`, the refutation
`rocq/ReversePhysicsNoConformalCount.v`, the positive answer
`rocq/ReversePhysicsRelationalCount.v`, the transposed assumption
`rocq/ReversePhysicsExponentAdditivity.v`, and the underlying results are in
`ReversePhysicsTorus*.v`. Certificates and their boundaries are in
`reverse_physics/certificates/`, and
[`OVERVIEW.md`](OVERVIEW.md) is the narrative account of the whole probe.

[rp]: https://arxiv.org/abs/2111.09107
[cmir]: https://arxiv.org/abs/2101.02107
[gr]: https://assumptionsofphysics.org/presentations/20241116-UMichRelativity.pdf
