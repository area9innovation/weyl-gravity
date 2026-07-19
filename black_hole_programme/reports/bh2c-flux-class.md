# BH-2C stage 3: finite-flux boundary class — Einstein selected at infinity

## Verdict

`BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY`
(certificate `black_hole_programme/certificates/BH2C_FLUX_CLASS.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

The last station of the planning directive's asymptotic gate, decided at
the fixture level (axial ℓ = 2, ω = 3/5).

## Exact results

1. **Composed metric log tails.** Solving δRic[h] = ψ at r → ∞ per
   carrier formal solution: the pure-power ansatz is inconsistent and
   the single-log ansatz e^{iμr}Σ(aₙ + bₙ ln r)r^{s−n} is consistent
   with nonzero log part — in both characteristic sectors. The
   homogeneous formal systems are log-free (stage 1), so the logs are
   injected by the source resonance: the inhomogeneous realization of
   the repeated characteristic root.
2. **Flux power table** (leading (r-power, log-power) of the EF slice
   density F^v on conjugate pair classes):
   E×E: (−2, 0) both sectors — slice norm **finite**;
   E×X: (0, 0) and (1, 0) — divergent;
   X×X: (0, 1) and (2, 0) — divergent.
3. **Invariance.** The divergent classes cannot be cancelled by
   Einstein-shifts of the composed representatives (class leading powers
   cannot cancel across rows).

## Consequence

At the fixture mode level, the finite-slice-norm asymptotic phase space
at infinity contains **exactly the Einstein sector**. The extra branch —
causally unavoidable at the horizon by the certified dispositions — is
excluded at infinity by symplectic-norm finiteness: a phase-space
normalization, not a local boundary condition. Together the two ends
give the full picture of pure-Weyl branch selection at ℓ = 2.

## What was NOT established

- symbolic-frequency and polar tables; summability of the log series;
- an asymptotically flat phase-space/charge-algebra construction;
- general ℓ; stability vocabulary stays locked.

## Receipts

```bash
python3 black_hole_programme/bh2c_flux_class.py            # producer (~3 min)
python3 black_hole_programme/verify_bh2c_flux_class.py     # independent verifier (~3 min)
python3 -m pytest black_hole_programme/tests/test_bh2c_flux_class.py -q  # fast rail
```
