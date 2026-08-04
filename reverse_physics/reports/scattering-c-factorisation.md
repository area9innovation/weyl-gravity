# Does the scattering `C` factorise? — an independent reproduction, and two corrections

> **Read this first.** An earlier version of this report presented its contents
> as a *reduction of an open question*, with explicit `T₊` as the missing input.
> Both claims were wrong, and the corrections are the useful part.
>
> **(i) The reduction already existed.**
> `black_hole_programme/phase4/channel_factorized_c_pullback_test_v1`
> (lifecycle `CLASSIFIED`) states the criterion in a sharper normalisation, with
> necessity, sufficiency, a determinant audit and **four** exact fixtures. What
> was derived here is the same criterion in a `T₋`-congruent presentation — a
> cross-check, not a discovery.
>
> **(ii) The missing input is `T₋`, not `T₊`.** That contradicts nothing but my
> own step 2: once `K₊ = G − K_H`, the outgoing connection *drops out*. Their
> `minimal_missing_object` is *"a certified full 3×3 `T₋` enclosure on the
> cell"*, and they record **rejecting** an imported `T₋` point matrix for having
> no interval enclosure and a nonzero Stokes residual.
>
> **(iii) A failure mode was missed** — spectrum inside the interval with the
> operator **not diagonalizable**. Their `jordan_inside_interval` fixture. It is
> proved below.

> **Follow-up, and it settles the prior question.**
> [`c-factorisation-not-determined.md`](c-factorisation-not-determined.md) runs
> the criterion against the **actual** `G` and `H_H` and shows both outcomes are
> reachable inside the admissible set — a YES witness (`K_H = G/2`, spectrum
> `{½,½,½}`) and 528 NO witnesses. So the certified data does not determine the
> answer: **an explicit `T₋` is logically unavoidable.**

## Their criterion, which is the answer

```
K_H = A†H_H A,   K₊ = R†G₊R = G − K_H,   L_H = G⁻¹K_H

a channel-factorized positive fundamental symmetry exists
   ⟺  L_H is diagonalizable over ℂ  and  spec(L_H) ⊂ (0,1)
```

with `A = T₋⁻¹`, `R = T₊T₋⁻¹`. Their four fixtures cover every mode: `positive`,
`negative_eigenvalue`, `nonreal_pair`, and `jordan_inside_interval`.

## That this report's derivation is the same statement

The triple `(H_out, M, N)` below is `T₋†(K_H, K₊, G)T₋`, so
`spec(N⁻¹H_out) = spec(L_H)`, and the condition `spec(H_out⁻¹N) ⊂ (1,∞)` is
theirs inverted. Two derivations from scratch reaching the same criterion is
worth recording; it is not a new result.

---

## The original framing follows, corrected

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

### 2. The input is missing — and it is `T₋`

| | status |
|---|---|
| `G₋`, `G₊`, `H_H` | **explicit**, exactly, as functions of `ω` (`axial_null_flux_gram`) |
| `T₋` | **THE BLOCKER.** Proved to exist and be invertible with exact determinant `−(2ω−i)(4ω−i)²A_in₂²A_in₁/(4(ω−i))` — but `A_in_s` are Jost amplitudes with **no closed form** for Regge–Wheeler. Their `minimal_missing_object`: *"a certified full 3×3 Tminus enclosure on the cell"*. An imported point matrix was **rejected** — no interval enclosure, nonzero Stokes residual. |
| `T₊` | separately uncertified — ~30 packages mention it, every explicitness flag `false`, transport at `r = 487/16` heading for `r = 4` — **but it is not what blocks this test.** It drops out via `K₊ = G − K_H`. |

So the missing input is the **incoming connection**. The earlier version of this
report named `T₊`, contradicting its own step 2.

They also have a partial result I did not: `0 < det(L_H) < 0.9786…` on the cell,
from `det(L_H) = 1/(|A_in₂|⁴|A_in₁|²)` and the Wronskian `|A_in_s|² = 1+|A_out_s|²`.
Positive and below one — consistent with `spec ⊂ (0,1)` but, as they note, *"neither
this product nor the endpoint inertias determines the three generalized eigenvalues
or diagonalizability."*

### 3. Nothing weaker will do

Everything the programme certifies about these three forms is their **inertia**:
`(1,2,0)` for each. Two witnesses, `H = diag(1,−1,−1)` throughout:

| | `M` | minors of `M` | minors of `M+H` | pencil |
|---|---|---|---|---|
| **YES** | `diag(2,−3,−5)` | `2, −6, 30` | `3, −12, 72` | `(x−2)(x−3)(x−5)` — three **positive** roots |
| **NO** | `[[1,2,0],[2,1,0],[0,0,−1]]` | `1, −3, 3` | `2, −4, 8` | block `[[1,2],[−2,−1]]`: trace 0, det 3 → `x²+3`, **non-real** |

**And the mode I missed.** With `G = [[0,1],[1,0]]` and `L = [[½,1],[0,½]]`,
`K_H = GL = [[0,½],[½,1]]`: `L` is `G`-self-adjoint, its spectrum is the double
root `½ ∈ (0,1)` — *inside the interval* — and `L − ½I` is nonzero with square
zero. A genuine Jordan block, and obstructed. **A spectrum condition alone is not
sufficient**, which is precisely what their `jordan_inside_interval` fixture
records and what the earlier version of this report got wrong by omission.

`H` itself has minors `1, −1, 1`. **All five matrices have sign pattern
`(+,−,+)`** — inertia `(1,2,0)` by Jacobi's rule. The witnesses match *every*
structural fact the programme certifies, and they answer oppositely.

> **A certified `T₋` enclosure is not a convenience. It is logically required.**

The witnesses are real symmetric — a special case of Hermitian — which is enough:
realising both outcomes *inside* the certified inertia class shows the class does
not decide.

## What this report is actually worth

Not the reduction — that was already `CLASSIFIED`. What survives:

- **an independent derivation of the same criterion**, from the Stokes identity,
  without having read theirs. Two routes to one criterion is a real cross-check;
- **the `T₋`-congruent presentation** `N = M + H_out`, which is a slightly
  different way to see why `T₊` drops out;
- **exact machine checks** of the intertwining relation *and its necessity*;
- **a correction**, recorded rather than edited away.

The lesson is the ordinary one: I should have searched the corpus for prior work
on the question before deriving it. The certificate's `--check` fails closed on
drift in the black-hole certificates, which is the mechanism that would have
surfaced this had I wired it first.

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
