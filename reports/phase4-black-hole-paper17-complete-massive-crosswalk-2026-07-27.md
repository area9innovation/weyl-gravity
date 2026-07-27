# Paper 17 complete massive axial first-jet crosswalk

Date: 2026-07-27

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete coupled Schwarzschild axial massive-spin-two equations were
transformed at \(m=\mu^2=0\) into the massless tensor/vector
Regge--Wheeler basis.  The state transformation has determinant
\(\omega^{-4}\), and its first-order intertwining identity is exact.

The reverse tensor-to-vector mass tangent is rationally removable.  The
remaining tensor tangent has projective density

\[
\mathcal I_{\rm phys}
=
\frac{(r-2)(3r^4\omega^2-20r+30)}
{3r^5\omega^2}
=
\mathcal K_{U_2}\!\left(\frac{r}{6\omega^2}\right)+\frac13f.
\]

Consequently,

\[
[\mathcal I_{\rm phys}]=\frac13[f],
\qquad
[\mathcal I_{\rm Bach}]
=\frac{3i\omega}{2}[\mathcal I_{\rm phys}].
\]

The stronger equality \([\mathcal I_{\rm phys}]=[f]\) fails generically:
the exhaustive rational gauge system has coefficient rank \(3\), augmented
rank \(4\), and obstruction
\[
\frac{80(\omega^2-3)}{3\omega^2}.
\]

The complete-system normalization therefore corrects the earlier scalar
graded factor.  At fixed nonzero frequency the tangent relation is
\[
m=\frac{3i\omega}{2}\tau,
\]
which is not a global reparameterization because it depends on the spectral
variable.

## Endpoint audit

The raw massive phase derivative contributes
\(-\sigma i r/(2\omega)\).  The exact complete-system projective gauge adds
\(\sigma i r/(3\omega)\), leaving
\(-\sigma i r/(6\omega)\).  Multiplication by \(3i\omega/2\) gives the Bach
coefficient \(\sigma r/4\).  The Coulomb-power derivative vanishes.

This proves agreement of the leading differentiated endpoint class.  It
does not prove all-orders analytic dependence of the matrix Jost bases or
exclude an opposite-Jost admixture.

## Claim boundary

Established:

- exact complete coupled massive axial first-jet factorization;
- exact removal of the reverse tensor-to-vector tangent;
- exact factor \(1/3\) in the physical tensor projective class;
- exact factor-three Bach crosswalk;
- leading differentiated endpoint-phase agreement.

Not established:

- an all-orders matrix-Volterra differentiated-Jost theorem;
- equality of the intrinsic selector with a physical massive-QNM velocity;
- a global causal exterior resolvent or retarded contour deformation.

## Verification

```text
python3 black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/produce.py
python3 black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/verify.py
python3 -m unittest -v black_hole_programme.phase4.axial_complete_massive_jet_crosswalk_v1.test_crosswalk
python3 paper/generate_17_pure_weyl_extension_claim_map.py
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m unittest -v paper.test_17_pure_weyl_extension_claim_map
```

All commands passed.  The mutation tests reject a changed imported flow
coefficient, the false unit normalization, and promotion to a physical
massive-QNM slope.

Primary literature used to identify the complete massive axial equations:
Brito--Cardoso--Pani, Phys. Rev. D 88, 023514 (2013), and
Antoniou--Gualtieri--Pani, Phys. Rev. D 111, 064059 (2025).
