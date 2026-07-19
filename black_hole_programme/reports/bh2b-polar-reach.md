# BH-2B stage 2: the polar extra branch reaches the horizon

## Verdict

`BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL`
(certificate `black_hole_programme/certificates/BH2B_POLAR_REACH.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Together with the axial reach theorem (BH-2A stage 2) this closes the
horizon-reach question for **both parity sectors of ℓ = 2**: no
future-horizon regularity condition can truncate a pure-Weyl exterior to
its Einstein sector.

## Exact results

Working in the ingoing Eddington–Finkelstein chart (v, r, x = cosθ) on
Schwarzschild (symbolic m), with the certified polar extra-branch operator
(BH-2B stage 1) E[ψ,S] = ½□ψ + C∘ψ − ⅙∇∇S − (1/12)g□S and the
linearized-Bianchi constraint ∇ᵃψ_ab = ½∇_b S on the polar ℓ=2
trace-coupled carrier (harmonics P₂, ∂ₓP₂ and the traceless tensor
harmonic W = (3/2, −3(1−x²)²/2)):

1. **Bianchi cascade.** The three constraint rows solve *algebraically*
   for the (vx), (rx) and W-sector components, with x-independent
   solutions — the polar analogue of the axial polynomial constraint.
   Four free radial functions remain: (a, bc, cc, f).
2. **The system is 3 equations in 4 functions.** The constrained operator
   satisfies two exact tensor identities, identically in the free
   functions: g^{ab}E_ab = 0 (the operator is traceless — the coefficients
   ½ − ⅙ − 4/12 = 0 conspire exactly) and ∇ᵃE_ab = 0. Combined with the
   algebraic-solvability pattern of the harmonic ansatz, the four rows
   (vx), (rx), angular-P₂, angular-W are consequences of (vv), (vr), (rr).
3. **The underdeterminacy is conformal gauge.** For arbitrary φ(r), the
   carrier ψ_conf = −∇∇Φ − ½g□Φ (= δRic[Φg], Φ = φ e^{iωv}P₂) satisfies
   the Bianchi constraint and annihilates all seven operator rows —
   linearized conformal covariance of the Bach tensor around a Bach-flat
   background, verified exactly. This gauge direction is *absent in the
   axial sector* (Φg has no odd-parity part), which is why the axial
   carrier system was square.
4. **Traceless slice.** S = (2bc + B₀cc + 2f)P₂e^{iωv}, so S = 0 is the
   algebraic slice f = −bc − B₀cc/2. On it the principal part
   diagonalizes to the scalar wave operator ((r−2m)/2r on each diagonal).
5. **Regular singular point and spectrum.** The 6-dim Fourier first-order
   system has a regular singular point at r = 2m with residue spectrum
   **{0 (×3), 1−4imω, −1−4imω, −3−4imω}**, zero eigenvalue of geometric
   multiplicity 3, and independent (a, bc, cc) kernel data. Polynomial
   Frobenius fixtures at ω = 3/5, 2/7 (m = 1) confirm the analytic family
   is exactly 3-dimensional — no log obstruction.
6. **Gauge quotient.** Residual gauge in the slice is □Φ = 0, with
   horizon exponents {0, −4imω}. The regular gauge mode is a nonzero
   all-regular carrier direction (one of the three analytic directions);
   the singular gauge mode has component exponents
   (−4imω, −4imω−1, −4imω−2), i.e. leading state behavior −3−4imω.
   Quotienting leaves a **two-parameter physical ingoing-regular polar
   extra-branch family at every real ω ≠ 0** — the exact polar twin of
   the axial two-parameter reach theorem.

## Consequence

Future-horizon regularity cannot exclude the polar extra branch either.
Exclusion — if it exists at all — must come from outer-boundary
conditions, causal structure, or flux/sign data, in both parity sectors.
The polar sector adds one genuinely new structural fact: the conformal
gauge mode lives entirely in the polar sector, and any polar flux or
observable must be checked for conformal-gauge invariance before use.

## What was NOT established

- polar bilinear symplectic flux matrix and Lee–Wald signs (next chunk);
- the Zerilli/Einstein-branch polar benchmark (must be derived by
  ansatz fitting against the certified rows, not imported from memory);
- outer-boundary domains and falloff classification (polar);
- causal disposition of the polar extra branch;
- ω = 0 static sector, general ℓ, growth/stability data, non-Einstein
  backgrounds, or any ringdown statement (BH-3 vocabulary stays locked).

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_reach.py            # producer (~3 min, symbolic m)
python3 black_hole_programme/verify_bh2b_polar_reach.py     # independent verifier (~3.5 min)
python3 -m pytest black_hole_programme/tests/test_bh2b_polar_reach.py -q   # fast rail (<1 s)
python3 black_hole_programme/atlas/generate_atlas_fragment.py              # atlas row
python3 residual_atlas/validate_fragment.py black_hole_programme/atlas/black-hole-atlas-fragment.json
```

The verifier re-runs the entire fail-closed analysis on the verifier-side
Schouten/Kulkarni–Nomizu curvature pipeline (`VbGeo`). Higher tiers not
run: no shared-core algebra changed; the axial certificate chain is
untouched (checked by content hash in the atlas evidence pins).
