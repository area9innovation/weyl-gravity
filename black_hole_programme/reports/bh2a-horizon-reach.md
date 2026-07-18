# BH-2A stage 2: the extra branch reaches the horizon

## Verdict

`BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL`
(certificate `black_hole_programme/certificates/BH2A_HORIZON_REACH.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This answers, at the linear mode level on Schwarzschild, the central
question posed by the team brief: **the extra fourth-order Weyl branch
does reach the future horizon.**

## Exact results

Working in the ingoing Eddington–Finkelstein chart (v, r, x = cosθ) with
the certified extra-branch equation ½□ψ + C∘ψ = 0 on the axial ℓ=2
carrier (trace-free, divergence-free, ψ = δRic):

1. The divergence constraint solves for the third carrier component with
   a **polynomial** solution — the 1/(r−2m) singularity seen in the
   Schwarzschild chart is a pure chart artifact.
2. On Fourier modes e^{iωv}, r = 2m is a **regular singular point** of
   the first-order radial system (ρ²A → 0 componentwise).
3. The residue matrix has spectrum **{0, 0, −4imω, −2−4imω}**, the zero
   eigenvalue has geometric multiplicity 2, and the two kernel vectors
   span independent (P, Q) profiles: **at every frequency there is a
   two-parameter family of extra-branch solutions analytic at the future
   horizon** — ingoing-regular, no leading logarithm.
4. Benchmark: the Regge–Wheeler equation in the same chart has residue
   spectrum {0, −1−4imω} (scalar exponents {0, −4imω}) — the Einstein
   branch also has its ingoing-regular family.

## Consequence

Future-horizon regularity does **not** distinguish the extra branch from
the Einstein branch.  Any exclusion of the extra branch must come from
outer-boundary conditions, causal structure, or flux/sign data — never
from horizon regularity.  This sharpens the decision tree: the
brief's "does exclusion require future data?" question now lives entirely
at the outer boundary and in the flux matrix.

## What was NOT established

- the bilinear symplectic flux matrix and Lee–Wald signs (next chunk);
- outer-boundary domains and falloff classification;
- the causal disposition (initial-boundary formulation) of the extra
  branch;
- growth/stability data, general ℓ, polar sector, non-Einstein
  backgrounds, or any ringdown statement.

## Receipts

```bash
python3 black_hole_programme/bh2a_horizon_reach.py          # producer (~2 s)
python3 black_hole_programme/verify_bh2a_horizon_reach.py   # independent verifier (~3 s)
python3 -m pytest black_hole_programme/tests/ -q             # full suite
```

The verifier recomputes everything on the verifier-side
Schouten/Kulkarni–Nomizu pipeline.  Higher tiers not run: additive
certificate, no existing chain touched.
