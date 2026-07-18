# BH-2A stage 4: the branches exchange flux through the horizon

## Verdict

`BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES`
(certificate `black_hole_programme/certificates/BH2A_CROSS_FLUX.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Fixture-level closure of the horizon flux matrix: m = 1, axial ℓ = 2,
ingoing-analytic modes, exact series arithmetic (order 16), frequencies
ω ∈ {3/5, 2/7} (verifier adds ω = 1/2 independently).

## Method

The composition route (`axial_flux_modes.py`): the ingoing Regge–Wheeler
mode from the certified master-equation series; the ingoing extra-branch
modes by forward recurrence of δRic[h] = ψ sourced by the certified
carrier solutions; conjugate partners as exact complex conjugates (all
pairings Hermitian); the certified Lee–Wald bilinear evaluated at two
interior radii, r-independent on shell.  **In-run validation: the
certified RW×RW null theorem — the control vanishes to < 10⁻¹² relative
at every fixture** (measured ~10⁻¹⁸–10⁻²³).

## Certified fixture facts

1. **Extra-branch horizon-flux norm nonzero, with sign.**
   F^r(extra, extra̅) is exactly imaginary with Im < 0, radius-stable to
   < 2% (values ≈ −330i·πα at ω = 3/5, ≈ −71.9i·πα at ω = 2/7):
   `i·F^r = +|v|·πα > 0 for α > 0` — the ingoing extra family is not
   null-degenerate at the horizon.  (The physical sign convention for α
   remains the theory-level choice recorded open since BH-0.)
2. **Nonzero Einstein × extra cross pairing** (≈ (−217+48i)πα and
   (−163+30i)πα): the branches genuinely exchange symplectic flux through
   the horizon.
3. Combined with the certified symplectically null RW block: **all
   horizon flux pairing in pure-Weyl gravity lives in the mixed and extra
   sectors** — Einstein waves alone are energetically inert, and whether
   pure-Weyl black holes radiate is decided by the extra branch's
   admission or exclusion.

## Development provenance

The mode constructions were debugged against two exact references: the
on-shell residual test (modes exact to ~10⁻²⁷) and the RW-null control
(which exposed a dropped e^{iωt} factor in an earlier flux evaluation —
all ∂_t terms had silently vanished).  Reduction traps (chart-singular
row choice; source-slot wiring) are documented in the pipeline module.

## What was NOT established

- exact symbolic ω-dependence of the flux blocks (fixture frequencies only);
- general ℓ, general m, the polar sector;
- the outer-boundary flux counterpart and falloff domains;
- the causal disposition of the extra branch (the remaining BH-2A item);
- any stability or ringdown statement.

## Receipts

```bash
python3 black_hole_programme/bh2a_cross_flux.py          # producer (~13 min, two frequencies)
python3 black_hole_programme/verify_bh2a_cross_flux.py   # verifier (~6 min, third frequency)
python3 -m pytest black_hole_programme/tests/ -q          # fast rail
```
