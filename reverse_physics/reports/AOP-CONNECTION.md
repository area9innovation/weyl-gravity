# Two connections to the Assumptions of Physics programme

Where this stream's results bear on Carcassi and Aidala's reverse-physics
programme, and where conformal gravity bears on their open conjecture for
general relativity.

Written to be readable by them. Everything asserted about our side is
machine-checked with zero axioms; everything asserted about theirs is cited.

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

### 2.2 The proposed DOF count is not conformally invariant

The talk proposes counting degrees of freedom by a spatial volume. Under a
conformal rescaling `g → Ω²g`, the induced 3-metric goes `h → Ω²h`, so
`√h → Ω³√h` and

```
∫_U √h d³x  ⟼  ∫_U Ω³ √h d³x
```

**The count is not conformally invariant.**

For general relativity that is arguably harmless — GR has a preferred conformal
frame. But it is not harmless in general, and the theory where it bites is the
one this repository studies.

**Weyl (conformal) gravity** is invariant under exactly that rescaling. Its
action `∫√−g C_{abcd}C^{abcd}` is conformally invariant in four dimensions, so
`g` and `Ω²g` describe the *same* physical configuration. The proposed measure
assigns them **different degree-of-freedom counts**.

So conformal gravity is a clean carrier on which the proposal is ill-defined —
and not for exotic reasons. No Planck scale, no quantum gravity, no discreteness.
Just a classical field theory with a gauge symmetry the measure does not respect.

Their talk asks: *"Does lower bound on DOF count require an equally severe
revisitation of space-time?"* Conformal invariance is a concrete, non-Planckian
reason the answer may be yes — the difficulty appears already at the classical
level, in a theory that has been studied for fifty years.

**The constructive question**, which we have *not* answered: what is a
degree-of-freedom count in a theory with no preferred volume? Conformal gravity
forces it, and this repository has the certified conformal-weight bookkeeping —
a classical BV–BFV complex, certified residual cohomology, an explicit physical
spectrum — to attack it. That is an offer, not a result.

---

## 3. What is not claimed

- **No claim about GR.** Our carrier is `T⁴` with a flat structure and
  polynomial fields. Nothing here transfers to a dynamical spacetime.
- **No refutation of their classical theorem.** §1 concerns the interpretation of
  its factors; §2.1 concerns the *conjecture*, and is consistent with the theorem
  because `H¹` vanishes in the finite-dimensional case.
- **No reproduction of their derivation.** We test candidate assumptions on
  declared carriers; we do not reconstruct their argument, and have not checked
  it.
- **§2.2 is an observation, not a theorem.** The non-invariance is elementary.
  What would be a result — a conformally invariant replacement — is open.
- **The physics on our side is modest.** `symplectic/Hamiltonian ≅ H¹` is
  classical symplectic geometry. What is new is the assumption analysis and the
  mechanization, not the underlying mathematics.
- **No quantum, causal, or field-theoretic claim** beyond the declared carriers.

---

## 4. Reproducing our side

```bash
cd rocq && ./run.sh     # 14 green (0 red); coqchk axiom section <none>
```

Nine zero-axiom Rocq modules, nine fail-closed negative controls. The bridge
module is `rocq/ReversePhysicsAOPBridge.v`; the underlying results are in
`ReversePhysicsTorus*.v`. Certificates and their boundaries are in
`reverse_physics/certificates/`, and
[`OVERVIEW.md`](OVERVIEW.md) is the narrative account of the whole probe.

[rp]: https://arxiv.org/abs/2111.09107
[cmir]: https://arxiv.org/abs/2101.02107
[gr]: https://assumptionsofphysics.org/presentations/20241116-UMichRelativity.pdf
