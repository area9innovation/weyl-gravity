# Local Einstein-sector Cauchy truncation — Schwarzschild exterior

## Verdict

`BH_LOCAL_CAUCHY_TRUNCATION_SELECTS_EINSTEIN_MODULO_CONFORMAL_GAUGE`
(certificate
`black_hole_programme/certificates/BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json`,
tag `LOCAL-ALGEBRAIC`, lifecycle `CLASSIFIED`).

Coordinator bypass work item
`black-hole-local-einstein-cauchy-truncation`, CLOSE-OUT: **DONE** — the
stop condition's branch (A) holds in the axial sector unconditionally and
in the polar sector modulo the conformal-gauge orbit, with the polar
obstruction certified exactly as branch (B) and the smallest repairing
hypothesis identified (conformal gauge-fixing / traceless slice).

## Setting

Schwarzschild exterior r > 2m (symbolic m), static chart, Cauchy surface
Σ = {t = const}; carrier operator
L ψ = ½□ψ + C∘ψ − (1/6)∇∇S − (1/12)g□S with S = tr ψ; Cauchy data
ψ|_Σ = 0, ∇_nψ|_Σ = 0; smooth ℓ = 2 harmonic classes, both parities. No
horizon or timelike boundary condition is used or hidden.

## Exact identities (all zero-remainder, symbolic m)

- **Axial**: S ≡ 0 on the class, so L = ½□ + C∘; L is supported on the
  three axial rows; the Bianchi vector has only the φ component; and
  ∇ᵃ(Lψ)_aφ = ½□B_φ exactly.
- **Polar**: g^{ab}(Lψ)_ab ≡ 0 (PDE-level tracelessness — the conformal
  direction is not controlled by the equation), and
  ∇ᵃ(Lψ)_ab = ½□B_b exactly in all four components, with
  B_b = ∇ᵃψ_ab − ½∇_bS.
- **Conformal trace relation**: S(ψ_conf(Φ)) = −3□Φ (verified on the
  witness; matches BH2B_POLAR_REACH).

## Conclusions

1. **Axial (A)**: L is normally hyperbolic componentwise; by the standard
   energy estimate for tensor wave systems on globally hyperbolic domains
   (cited, not re-proved), zero Cauchy data propagates ψ = 0, and the
   constraint propagates by scalar wave uniqueness. Local Cauchy data
   selects and preserves the linear Einstein image.
2. **Polar (B → A modulo gauge)**: the exact witness
   ψ_conf(Φ = t⁴χ(r)P₂) has zero Cauchy data, is nonzero, and satisfies
   Lψ = 0 — naive uniqueness fails. The smallest additional hypothesis is
   conformal gauge-fixing: solving −3□Φ₀ = S(ψ) with zero Cauchy data and
   subtracting ψ_conf(Φ₀) leaves a tracefree solution of the normally
   hyperbolic system ½□ + C∘, which vanishes; hence every zero-data
   solution lies on the conformal-gauge orbit, and on the traceless slice
   uniqueness is exact.
3. **Exact sequence** (no direct sum, no surjectivity):
   0 → ker(δRic) → ker(δBach) → ker(L) ∩ im(δRic); with zero Cauchy data
   the right-hand object is {0} axially and the conformal orbit polarly.
4. **Endpoint comparison**: this local initial-data truncation is
   logically independent of the certified endpoint diagnostics (horizon
   analyticity, falloff), which do *not* select the Einstein branch. The
   referee's distinction is resolved: ψ|_Σ = 0, ∇_nψ|_Σ = 0 is a
   constraint-compatible, well-posed invariant-subspace condition on the
   declared exterior domain.

## Mutation

Dropping the ∇_nψ datum admits the exact time-odd witness
u = (ψ(t) − ψ(−t))/2 built from a certified ingoing axial mode: u|_Σ = 0
but ∂_tu|_Σ ≠ 0 and u ≠ 0 (the inline Frobenius mode's imaginary part is
verified nonzero). The weakened hypothesis is rejected.

## What was NOT established

- general ℓ, m; a canonical Einstein-plus-extra splitting; surjectivity
  of δRic onto ker(L) (metric-lift questions are separate and under
  repair on a different work item);
- nonlinear closure, stability vocabulary, scattering;
- a re-derivation of the standard normally-hyperbolic uniqueness theorem
  (cited fail-closed as textbook input).

## Receipts

```bash
python3 black_hole_programme/bh_cauchy_truncation.py           # producer (~2 min)
python3 black_hole_programme/verify_bh_cauchy_truncation.py    # independent verifier (~2 min)
python3 -m pytest black_hole_programme/tests/test_bh_cauchy_truncation.py -q
```
