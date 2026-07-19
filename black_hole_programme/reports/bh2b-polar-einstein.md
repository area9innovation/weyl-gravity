# BH-2B stage 3: the polar Einstein branch is exactly two-dimensional

## Verdict

`BH2B_POLAR_EINSTEIN_BRANCH_REDUCED_TWO_DIMENSIONAL`
(certificate `black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This is the polar Einstein-branch benchmark: the analogue of the axial
Regge–Wheeler anchor, derived entirely from the repository's own
linearized machinery, and the solution basis the polar flux matrix will
be built on.

## Exact results

t-chart RW polar gauge on Schwarzschild (symbolic m), ℓ=2 Fourier modes:
h = (B·H0, H1, H2/B, K) × P₂ e^{iωt}, δRic[h] = 0:

1. The traceless angular (W-sector) row is exactly (H0 − H2)/2 — the
   Einstein branch forces **H2 = H0**.
2. The (tr), (tx), (rx) rows solve uniquely for K′, H1′, H0′; the (tt)
   row becomes an algebraic constraint solving H0 in terms of (K, H1);
   the derivative of the algebraic H0 agrees exactly with the first-order
   H0′ relation; the remaining rows vanish identically. **The polar
   Einstein branch is exactly the 2-dim system dY/dr = M(r)Y,
   Y = (K, H1)** (M recorded in the certificate; the (3m+2r) structure
   emerges from the derivation).
3. Raw (K, H1) has a double pole at the horizon (t-chart artifact); in
   the adapted variables (K, B·H1) the system is regular singular with
   t-chart residue spectrum **{+2imω, −2imω}** (the e^{±iωr*} pair) and
   ingoing-convention spectrum **{0, −4imω}** — *identical to the
   certified axial RW benchmark*: a one-parameter ingoing-regular polar
   Einstein family.
4. δRic = 0 ⟹ δB = 0 exactly by the certified general split identity
   (BH-2B stage 1): the branch injects into the Bach kernel.

## What was NOT established (fail-closed)

- **Schrödinger-form master scalar (Zerilli anchor): OPEN.** Bounded
  rational ansatz classes for ψ = aK + bH1 with ω-independent potential
  (numerators to degree 5 with and without ω² terms over r(3m+2r) and
  r(3m+2r)²; the inverse metric-reconstruction ansatz with poles at
  r = 2m) contain no solution; structured Moncrief-shaped candidates
  built from the derived reduction also fail. The obstruction is that
  the true combination carries ω-dependence in denominators (visible in
  the algebraic H0's ω³ terms), outside all searched classes. Nothing
  in this certificate depends on the master scalar; the 2-dim system
  itself is the complete branch description.
- polar flux matrix and Lee–Wald signs; outer-boundary domains; causal
  disposition; general ℓ; ω = 0; growth/stability; ringdown vocabulary
  remains locked.

## Consequence for the programme

The polar flux matrix (next chunk) can now be computed directly modulo
the first-order system — the Einstein-branch solutions are (K, H1) pairs
of the recorded M — mirroring how the axial flux stage used RW master
solutions. The conformal-gauge direction certified in BH-2B stage 2 is
NOT in this branch (δRic[Φg] ≠ 0), so the Einstein-branch flux block
needs no conformal quotient; the extra and cross blocks do.

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_einstein.py            # producer (~30 s)
python3 black_hole_programme/verify_bh2b_polar_einstein.py     # independent verifier (~30 s)
python3 -m pytest black_hole_programme/tests/test_bh2b_polar_einstein.py -q   # fast rail (<1 s)
```

The verifier re-runs everything on the VbGeo Schouten/Kulkarni–Nomizu
pipeline and cross-checks the recorded M and algebraic H0. Higher tiers
not run: no shared algebra changed; unchanged certificates are pinned by
hash.
