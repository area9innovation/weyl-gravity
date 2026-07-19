# BH-2 ω = 0: static-sector classification

## Verdict

`BH2_OMEGA_ZERO_STATIC_SECTOR_CLASSIFIED`
(certificate `black_hole_programme/certificates/BH2_OMEGA_ZERO.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Closes the ω = 0 caveat carried by every reach certificate: the static
sectors of both carrier systems are finite, log-classified, and nonempty.

## Exact results (Schwarzschild m = 1, ℓ = 2, EF chart)

1. **Axial carrier at ω = 0**: residue spectrum {0 (alg 3, geo 2), −2}.
   The zero eigenvalue acquires a Jordan block — one leading logarithmic
   static solution. Both kernel directions extend log-free: a
   **two-parameter log-free static family**, matching the ω ≠ 0 reach
   dimension. Horizon regularity does not exclude static axial carrier
   deformations either.
2. **Polar carrier (traceless slice) at ω = 0**: residue spectrum
   {0 (alg 3, geo 3), +1, −1, −3} — all integers. The +1 resonance
   obstructs two of the three exponent-0 directions (genuine
   logarithms); one exponent-0 and the exponent-1 direction survive:
   a **two-parameter log-free static family**.
3. **Controls**: the axial RW system classifies cleanly; the certified
   polar Einstein (K, H₁) system carries explicit 1/ω coefficients and
   **degenerates at ω = 0** — the static polar Einstein sector needs its
   own reduction (recorded as a missing object, fail-closed).

## What was NOT established

- static metric composition (δRic[h] = ψ at ω = 0) and static
  flux/charge assignments for the log-free families;
- matching to the BH-1 ℓ = 0 parameter modes;
- a static-adapted polar Einstein reduction;
- general ℓ; any stability interpretation of the logarithmic solutions.

## Receipts

```bash
python3 black_hole_programme/bh2_omega_zero.py            # producer (~10 s)
python3 black_hole_programme/verify_bh2_omega_zero.py     # independent verifier (~10 s)
python3 -m pytest black_hole_programme/tests/test_bh2_omega_zero.py -q  # fast rail (<1 s)
```
