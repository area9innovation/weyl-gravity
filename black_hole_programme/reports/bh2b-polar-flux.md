# BH-2B stage 4: the polar Einstein branch is symplectically null

## Verdict

`BH2B_POLAR_FLUX_STAGE1_EINSTEIN_BRANCH_SYMPLECTICALLY_NULL`
(certificate `black_hole_programme/certificates/BH2B_POLAR_FLUX.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

With the axial RW-null theorem (BH-2A stage 3), this closes the
Einstein-block flux question in **both parity sectors of ℓ = 2**:
Einstein gravitational waves carry zero Lee–Wald flux in pure Weyl
gravity. All symplectic pairing lives in blocks involving the extra
branch — the critical-gravity structure is now certified even-parity too.

## Exact results

Schwarzschild (symbolic m), t-chart RW polar gauge, rational chart
x = cosθ, action-derived Lee–Wald machinery (`linearized_theta.py`):

1. **Machinery controls**: conformal × parameter degeneracy and the
   static pair current 48α/(19r²) reproduce the certified BH-1B values.
2. **General polar bilinear**: sphere-integrated F^t and F^r between two
   arbitrary RW-gauge polar perturbations (H0, H1, H2, K)_{a,b}(t,r),
   stored exactly in the certificate.
3. **Off-shell 4α identity**:
   ∂_t F^t + ∂_r F^r = 4α ∮√g [h_B·δB(h_A) − h_A·δB(h_B)] — verified
   exactly; pins the action normalization and proves on-shell
   conservation.
4. **Einstein-block null theorem**: substituting two on-shell polar
   Einstein modes (K_i, H1_i)e^{iω_i t} (H2 = H0, algebraic H0, reduction
   modulo the certified 2-dim system of stage 3), the radial flux is an
   exact bilinear whose four coefficients ALL carry (ω₁+ω₂); the
   diagonal (K,K) and (H1,H1) coefficients carry (ω₁²−ω₂²); the cross
   coefficients obey exact swap antisymmetry. **For conjugate pairs
   ω₂ = −ω₁ the flux vanishes identically.** Closed forms (example):
   C_KK = 16παmr(ω₁−ω₂)(ω₁+ω₂)/(5(r−2m)).
5. **Conformal-gauge degeneracy**: the pairing of the linearized
   conformal direction h = Φg (Φ = φ(t,r)P₂, arbitrary φ) with an
   *arbitrary* (off-shell) RW-gauge polar perturbation vanishes exactly:
   F^t = F^r = 0. The conformal direction certified as the polar carrier
   gauge in stage 2 is an exact degeneracy of the sphere-integrated
   presymplectic form — polar flux statements need no conformal quotient
   at the bilinear level.

## Consequence

The decisive physical objects in the polar sector are now, exactly as in
the axial sector, the Einstein × extra and extra × extra flux blocks.
Combined with the certified polar horizon reach (stage 2), pure-Weyl
polar radiation lives entirely in the extra/mixed sectors.

## What was NOT established

- polar extra × extra and Einstein × extra block values and signs
  (requires the polar δRic[h] = ψ composition — next chunk);
- horizon flux signs on the polar extra family;
- outer-boundary domains, causal disposition, general ℓ, ω = 0,
  growth/stability, or any ringdown statement (vocabulary locked).

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_flux.py            # producer (~20 min)
python3 black_hole_programme/verify_bh2b_polar_flux.py     # independent verifier (~20 min)
python3 -m pytest black_hole_programme/tests/test_bh2b_polar_flux.py -q   # fast rail (~2 s)
```

The verifier re-runs everything on the VbGeo Schouten/Kulkarni–Nomizu
pipeline and cross-checks the stored bilinear and block coefficients.
The heavy rails are intentionally split from the per-commit fast rail
(Tier 1) per the test-tier policy; unchanged inputs are pinned by hash.
