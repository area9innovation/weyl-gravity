# BH-2A stage 3: the flux matrix and the symplectically null Einstein branch

## Verdict

`BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL`
(certificate `black_hole_programme/certificates/BH2A_FLUX_MATRIX.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

## Exact results (Schwarzschild, axial ℓ=2)

1. **The general bilinear.**  The sphere-integrated Lee–Wald symplectic
   density F^t and radial flux F^r between two arbitrary axial
   perturbations, stored exactly (built with the fast action-derived
   machinery of `linearized_theta.py`, revalidated in-producer against
   both certified BH-1B values).
2. **The off-shell 4α identity.**
   `∂_tF^t + ∂_rF^r = 4α∮√g[h_B·δB(h_A) − h_A·δB(h_B)]` holds exactly
   off shell — proving on-shell conservation and pinning the bilinear as
   the action-derived Lee–Wald current of S = α∫C² (not a
   scale-ambiguous Wronskian).
3. **The RW block and the null theorem.**  On-shell Regge–Wheeler pairs
   give exactly

   ```text
   F^r = −192πα(ω₁² − ω₂²) ψ₁ψ₂ / (5 ω₁ω₂ r),
   ```

   which **vanishes identically for conjugate pairs ω₂ = ±ω₁**: the
   Einstein/Regge–Wheeler branch is **symplectically null** in pure Weyl
   gravity — Einstein gravitational waves carry zero Lee–Wald flux at
   linear order in this theory.  Validated independently by exact
   rational point evaluation (generic data, two radii, ODE-supplied
   derivatives) against the unreduced bilinear.

## Interpretation

Together with the certified facts that H ≡ 0 on the static Schwarzschild
ensemble and that the extra branch reaches the horizon, this completes a
consistent picture: in pure Weyl gravity the Einstein sector alone is
energetically inert, and **all symplectic pairing must live in the
Einstein × extra cross-block** — the critical-gravity structure.  Whether
pure-Weyl black-hole radiation carries flux is therefore decided entirely
by the causal/boundary disposition of the extra branch.

## What was NOT established

- the RW × extra cross-block and extra × extra block values;
- horizon and outer-boundary flux signs on the ingoing-regular extra
  family;
- operator domains and the causal disposition of the extra branch;
- general ℓ, polar sector, non-Einstein backgrounds, any
  stability/ringdown statement.

## Receipts

```bash
python3 black_hole_programme/bh2a_flux_matrix.py           # producer (~2 min, stage timings in certificate)
python3 black_hole_programme/verify_bh2a_flux_matrix.py    # independent verifier (~95 s)
python3 -m pytest black_hole_programme/tests/ -q            # fast rail
```

The verifier rebuilds the bilinear and the off-shell identity on the
verifier-side Schouten/Kulkarni–Nomizu pipeline and re-runs the point
validation against the stored forms.  Higher tiers not run: additive
certificate, no existing chain touched.
