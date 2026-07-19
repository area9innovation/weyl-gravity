# BH-2B stage 5: polar cross-block and extra-block horizon flux

## Verdict

`BH2B_POLAR_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES`
(certificate `black_hole_programme/certificates/BH2B_POLAR_CROSS_FLUX.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

With the certified null polar Einstein block (stage 4), this establishes
at the fixture level that **all polar symplectic horizon flux lives in
blocks involving the extra branch and the pairing is nondegenerate** —
pure-Weyl black-hole radiation is carried by the extra sector in *both*
parity sectors of ℓ = 2.

## The composition (realized Ricci image)

δRic[h] = ψ is solved in the EF polar RW-like 4-function class by a
sourced Frobenius recurrence plus homogeneous corrections fixed by the
three unused δRic rows. Key structural facts, all verified exactly:

- the sourced relations carry a ρ⁻¹ slot (the algebraic solves divide by
  coefficients ~ B); the recurrence starts at order 0 with the s₋₁
  source coefficient;
- individual carrier modes need Einstein-family homogeneous corrections;
  the joint realized-image conditions close on the **full 3-dim analytic
  carrier space** — every ingoing-regular polar carrier mode lifts to a
  metric perturbation, with **all seven δRic rows verified on every
  composed mode** to series depth;
- the independent Einstein control mode (t-chart certified system lifted
  to EF with exact phase transform) satisfies all seven rows;
- the conformal-gauge carrier direction lifts as h = Φg exactly.

## Fixture flux matrix (ω = 3/5, m = 1, radii ρ = 1/4 and 1/2)

The 5×5 matrix i·F^r/(πα) between conjugate mode pairs
(Einstein, gauge lift, three composed carrier modes):

- **Controls**: Einstein×Einstein ~ 6e-8, gauge×anything ~ 1e-11,
  gauge×gauge ~ 1e-28 — at least nine orders below physical values
  (these are the certified null theorem and conformal degeneracy acting
  as in-run truncation gauges);
- **the matrix is Hermitian with real diagonals to series truncation**
  (deviations bounded by the null-control scale ~1e-11);
- **Einstein×extra cross-flux nonzero**, e.g. i·F^r[E, X0]/(πα) ≈
  40.6 − 6.85i — and this is **representative-independent** (invariant
  under Einstein-shifts of the composition since the Einstein block is
  null);
- **extra-block diagonal Hermitian norms positive at the canonical
  representatives**: ≈ +80.8, +52.8, +61.8;
- r-independence across the two radii to 4–5 significant digits
  (truncation-limited), as required for a conserved flux.

## Invariance boundary (fail-closed)

The extra×extra values shift under the Einstein ambiguity of the
composition (the cross block is nonzero, so the flux form does not
descend to the extra quotient). Positivity is certified **at the
canonical representative only** (recurrence free parameters zeroed —
deterministic and documented). The invariant sign question needs the
null-quotient pairing theory and is recorded as a missing object;
`invariant_extra_sign_certified` stays false.

## What was NOT established

- invariant extra-block signs; symbolic-frequency block values;
- outer-boundary domains; causal disposition of the polar extra branch;
- general ℓ; ω = 0; growth/stability; ringdown vocabulary stays locked.

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_cross_flux.py            # producer (~30 min)
python3 black_hole_programme/verify_bh2b_polar_cross_flux.py     # independent verifier (~30 min)
python3 -m pytest black_hole_programme/tests/test_bh2b_polar_cross_flux.py -q  # fast rail (~2 s)
```

The verifier re-runs the whole pipeline on the VbGeo
Schouten/Kulkarni–Nomizu engine and cross-checks the stored ρ = 1/4 flux
matrix entry-by-entry. Heavy rails are split from the per-commit fast
rail per the test-tier policy; inputs pinned by hash.
