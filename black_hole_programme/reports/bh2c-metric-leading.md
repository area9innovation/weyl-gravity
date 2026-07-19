# BH-2C stage 2: leading-order metric reconstruction and flux symbol

## Verdict

`BH2C_METRIC_RECONSTRUCTION_LEADING_ORDER_CLASSIFIED`
(certificate `black_hole_programme/certificates/BH2C_METRIC_LEADING.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Decides the metric-reconstruction station of the planning directive's
asymptotic gate at leading order.

## Exact results (Schwarzschild m = 1, ℓ = 2, symbolic ω)

1. **Metric enhancement bound.** The leading constant matrices of both
   sourced composition h-systems (axial and polar) are resonant in both
   characteristic sectors with kernel dimension exactly one: a carrier
   source ~ e^{iμr}r^σ can enhance the composed metric by **at most one
   power of r** (rank-1 Fredholm alternative); off the resonant
   direction the metric inherits the carrier falloff.
2. **Flux density symbol.** Substituting monomial radiative profiles
   into the certified axial Lee–Wald F^t:
   F^t ~ (96/5)πiα(λ−ω)²(λ+2ω)·r^{p₁+p₂} + subleading — the density
   **vanishes on-characteristic** (double zero at λ = ω): radiative
   pairs have subleading symplectic density; the finite-slice-norm
   question is decided at subleading order (recorded open).
3. Homogeneous sector eigenstructures of both leading matrices recorded.

## What was NOT established

- all-orders metric reconstruction (resonant-direction enhanced series);
- the finite-flux boundary class (subleading on-characteristic powers);
- the polar flux density symbol; summability; general ℓ.

## Receipts

```bash
python3 black_hole_programme/bh2c_metric_leading.py            # producer (~30 s)
python3 black_hole_programme/verify_bh2c_metric_leading.py     # independent verifier (~30 s)
python3 -m pytest black_hole_programme/tests/test_bh2c_metric_leading.py -q  # fast rail
```
