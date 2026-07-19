# BH-2C stage 1: asymptotic formal structure — no Jordan logarithms

## Verdict

`BH2C_ASYMPTOTIC_FORMAL_SYSTEM_LOG_FREE_BOTH_PARITIES`
(certificate `black_hole_programme/certificates/BH2C_ASYMPTOTIC_JORDAN.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This decides the first station of the planning directive's asymptotic
gate (Paper 14's "first-order matrix and Jordan form"): the
integer-spaced exponents at infinity do **not** force logarithms.

## Exact results (Schwarzschild m = 1, ℓ = 2, EF chart)

1. **Axial carrier (symbolic real ω)**: the sectors μ ∈ {0, −2ω}
   (t-chart λ = ±ω) have σ-roots {0, −1} and {−4iω, −4iω−1} — gap-1
   integer resonances. The formal series from the top σ of each sector
   pass the resonance consistently: a **log-free four-dimensional formal
   fundamental system** e^{iμr}r^σ × (series in 1/r).
2. **Polar carrier, μ = 0 sector (symbolic real ω)**: jet-window count:
   nullity 6 = 3 tail (leading-matrix kernel) + **3 genuine log-free
   solutions** (exponents −1, −2, −3) — the full sector dimension.
3. **Polar μ = −2ω sector (fixtures ω = 3/5, 2/7)**: same count, again
   **3 genuine log-free solutions** (exponents −4iω−{1,2,3}).

The formal fundamental systems at infinity are log-free in both parity
sectors — no Jordan blocks at the formal level.

## What was NOT established

- symbolic-frequency polar μ = −2ω count (fixture-level only);
- Borel/analytic summability of the formal series;
- metric reconstruction at infinity (composition asymptotics) and the
  finite-flux boundary class — the remaining BH-2C stations;
- general ℓ; stability vocabulary stays locked.

## Receipts

```bash
python3 black_hole_programme/bh2c_asymptotic_jordan.py            # producer (~8 min)
python3 black_hole_programme/verify_bh2c_asymptotic_jordan.py     # independent verifier (~8 min)
python3 -m pytest black_hole_programme/tests/test_bh2c_asymptotic_jordan.py -q  # fast rail (<1 s)
```
