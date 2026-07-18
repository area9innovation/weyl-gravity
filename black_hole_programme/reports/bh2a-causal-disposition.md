# BH-2A stage 5: the extra branch is causally unavoidable

## Verdict

`BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE`
(certificate `black_hole_programme/certificates/BH2A_CAUSAL_DISPOSITION.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

## Exact results (Schwarzschild m = 1, axial ℓ = 2, symbolic real ω)

- **Dispersion** of the extra-branch carrier at r → ∞:
  (λ² − ω²)² — the extra branch propagates on exactly the Einstein
  characteristics (massless/luminal), with two-dimensional amplitude
  spaces per direction.
- **Growth exponents**: σ ∈ {±2imω, ±2imω − 1} — pure Coulomb log-phases
  (r^{2iω}·e^{iωr} = e^{iωr*}) with amplitudes r⁰ and r⁻¹: **no growing
  asymptotic solutions at real frequencies**.
- **RW control**: the Einstein master equation shows the same
  characteristics and log-phases (simple roots) — the branches are
  asymptotically indistinguishable by falloff.

## The disposition

Combining the certified facts — the extra branch (i) reaches the future
horizon with a two-parameter ingoing-regular family, (ii) carries nonzero
horizon flux, and (iii) is bounded oscillatory radiation on the Einstein
characteristics at infinity — **no causal decay or regularity
prescription at either boundary excludes the extra branch** at the axial
ℓ = 2 linear mode level.  Exclusion could only be imposed as a branch
projection on scattering data, tying both temporal ends: not a causal
initial-boundary condition.  This realizes the decision-tree alternative
"removing the extra branch requires a future boundary condition":
pure-Weyl black-hole exteriors cannot be causally truncated to the
Einstein sector, and their radiation lives in the mixed/extra sectors.

With this, all BH-2A axial ℓ = 2 items are certified: operator and branch
split, horizon reach, flux matrix (null RW block, nonzero cross and extra
blocks), and the causal disposition.

## What was NOT established

- complex-frequency (quasinormal/instability) structure;
- general ℓ, general m, the polar sector;
- a full initial-boundary well-posedness theorem for the fourth-order
  exterior problem;
- nonlinear/all-orders statements, stability, ringdown (BH-3 vocabulary
  stays locked pending the polar sector and the coordinator's review).

## Receipts

```bash
python3 black_hole_programme/bh2a_causal_disposition.py          # producer (~2 s)
python3 black_hole_programme/verify_bh2a_causal_disposition.py   # independent verifier (~2 s)
python3 -m pytest black_hole_programme/tests/ -q                  # full suite
```
