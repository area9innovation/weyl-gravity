# Does the scattering `C` factorise? — the question, reduced

**Certificate** `REVERSE_PHYSICS_SCATTERING_C_FACTORISATION_V1`
**Proof** `rocq/WeylScatteringCFactorisation.v` — zero axioms, 14/14 closed
**Gate** `rocq/run.sh` — `RESULT: 27 green (0 red)`, 27 fail-closed negative controls
**Second rail** tango `forge/examples/weyl_scattering_c_factorisation_gate.forge` — 28/28, `verify -full` clean
**Answers** the open condition in
`black_hole_programme/phase4/axial_local_commutant_spectral_c_v1`

---

## The question

`axial_local_commutant_spectral_c_v1` certifies that a compatible fundamental
symmetry `C_out` exists on the combined future space, and flags as **open**
whether it factorises

```
C_out  =  C_+  ⊕  C_H
```

over null infinity and the horizon. Its claim flag
`endpoint_block_diagonal_scattering_c_established` is `false`, and its stated
physical test is *"explicit `T_+`"*.

[`ghost-and-the-black-hole.md`](ghost-and-the-black-hole.md) argued this is now
**the** question about the ghost: a `C` that factorises is a positivity statement
one could plausibly call physical; one that does not is a formal device.
Everything else about the ghost is settled.

## The answer, in three parts

### 1. The question is finite

With `S = (R, A)ᵀ`, `R = T₊T₋⁻¹`, `A = T₋⁻¹`, and the oriented Stokes identity
`G₋ = R†G₊R + A†H_out A`:

**(a) The two boundary symmetries are not independently choosable.**
`C₊ ⊕ C_H` preserves `ran(S)` with a *common* `C₋` exactly when

```
C₊  =  T₊ C_H T₊⁻¹
```

The horizon symmetry determines the null-infinity one. This is the structural
reason the question is nontrivial — and the Forge rail checks both that the
conjugate intertwines *and that a perturbation of it does not*, so the relation
is necessary, not merely sufficient.

**(b) Pull the Stokes identity back by `T₋`.** With no new input:

```
T₋†G₋T₋  =  T₊†G₊T₊  +  H_out          i.e.   N = M + H_out
```

**(c) The whole question becomes a pencil.** Requiring `C₊` and `C_H` to be
fundamental symmetries of their own boundary forms, and congruing by `T₊`:

> Do `H_out` and `M := T₊†G₊T₊` carry a **common fundamental decomposition**?

which holds exactly when `det(M − λH_out)` has all roots real and positive with
`H_out⁻¹M` diagonalisable. By (b), equivalently: **the spectrum of `H_out⁻¹N`
lies in `(1, ∞)`.**

*Why that criterion is right.* If a common decomposition exists, both forms are
block-diagonal for it, so `H⁻¹M` is too, and on each block `M = λH` with both
definite of the same sign — hence `λ > 0`. Conversely, if `H⁻¹M` is
diagonalisable with positive spectrum, its eigenspaces are `H`-orthogonal,
`M = λH` on each, exactly one eigenspace carries the single positive
`H`-direction, and taking `L₊` inside it with `L₋` its `H`-complement gives a
decomposition simultaneously fundamental for both.

**An open scattering condition is a 3×3 generalised eigenvalue problem.**

### 2. The input is missing — and precisely which one

| | status |
|---|---|
| `G₋`, `G₊`, `H_out` | **explicit**, exactly, as functions of `ω` (`axial_null_flux_gram`) |
| `T₊` | **not certified explicit.** `axial_explicit_tplus_band_v1`: `explicit_Tplus_certified = false`, `does_not_establish` "the outgoing trace map T_plus", lifecycle `NUMERIC-ENCLOSURE`, radial transport at `r = 487/16` heading for `r = 4` |
| `T₋` | proved invertible with exact determinant `−(2ω−i)(4ω−i)²A_in₂²A_in₁/(4(ω−i))` — but `A_in_s` are Jost amplitudes with **no closed form** for Regge–Wheeler |

So the missing input is the **connection**, not the forms. And it is already the
declared objective of another package.

### 3. Nothing weaker will do

Everything the programme certifies about these three forms is their **inertia**:
`(1,2,0)` for each. Two witnesses, `H = diag(1,−1,−1)` throughout:

| | `M` | minors of `M` | minors of `M+H` | pencil |
|---|---|---|---|---|
| **YES** | `diag(2,−3,−5)` | `2, −6, 30` | `3, −12, 72` | `(x−2)(x−3)(x−5)` — three **positive** roots |
| **NO** | `[[1,2,0],[2,1,0],[0,0,−1]]` | `1, −3, 3` | `2, −4, 8` | block `[[1,2],[−2,−1]]`: trace 0, det 3 → `x²+3`, **non-real** |

`H` itself has minors `1, −1, 1`. **All five matrices have sign pattern
`(+,−,+)`** — inertia `(1,2,0)` by Jacobi's rule. The witnesses match *every*
structural fact the programme certifies, and they answer oppositely.

> **Explicit `T₊` is not a convenience. It is logically required.**

The witnesses are real symmetric — a special case of Hermitian — which is enough:
realising both outcomes *inside* the certified inertia class shows the class does
not decide.

## What changed

Before: *"whether `C_out` factorises is a separate scattering condition"* — an
open statement with no stated test.

After: a named 3×3 generalised eigenvalue problem, with its algebra verified
exactly, its one missing input identified by name, and a proof that no cheaper
route exists. The certificate's `--check` **fails closed on drift in
`axial_explicit_tplus_band_v1`** — so the moment `T₊` lands, this record breaks
and says the test can be run.

## Two rails

| | method |
|---|---|
| **Forge** | exact rational matrices: the pullback identity on two independent instances, the intertwining relation *and its necessity*, Jacobi inertia by leading minors, the pencil cubic by exact Lagrange interpolation with its discriminant |
| **Rocq** | the witnesses over ℚ: sign patterns, root locations, `x²+3 ≥ 3`, and the two lemmas showing a common decomposition forces positive eigenvalues |

## A note on the hygiene rail

The first draft of the Rocq module was **rejected** — because its *prose*
contained the bare a-d-m-i-t verb, which the source-hygiene regex cannot
distinguish from a tactic. The second draft was rejected too: the note explaining
the first rejection used the word again.

The bluntness is deliberate, and the right response was to reword rather than
relax the check. Worth recording, because a gate that only ever passes is not a
gate.

## What this does **not** establish

- **The answer.** `T₊` is unavailable; the test cannot be run.
- **The general pencil equivalence as a Rocq theorem.** It is argued in the
  module header and its consequences computed exactly on the Forge rail; Rocq
  proves the *witnesses*, which is what the no-shortcut conclusion rests on.
- **That a factorising `C` would be "physical".** That is the assumption
  lattice's reading, not a theorem.
- **Any `LORENTZIAN-CAUSAL` statement.** The black-hole certificates read here
  carry `REDUCED-MODE` and none is promoted.
- **Anything about the BV–BFV complex, the residual classes, the physical
  spectrum, or the quantum theory.** The two scoped Lorentzian no-go theorems are
  neither used nor affected.

## Verification

```bash
cd rocq && ./run.sh                                   # 27 green (0 red), 212/212 closed
PYTHONPATH=. python3 -m reverse_physics.scattering_c_factorisation --check

cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_scattering_c_factorisation_gate.forge
```
