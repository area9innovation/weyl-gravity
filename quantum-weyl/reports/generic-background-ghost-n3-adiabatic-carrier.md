# Generic ghost three-insertion adiabatic carrier

Dependency tag: `EUCLIDEAN-SPECTRAL`.

## Exact result

The cubic-curvature, three-Ricci-insertion row uses only the flat Endo inverse

\[
G_0(p)=\frac1{p^2}\left(I-\frac13nn^T\right),
\qquad n=\frac p{|p|}.
\]

For a symmetric Ricci endomorphism (R), exact isotropic averaging in four
dimensions gives

\[
\left\langle\operatorname{tr}(PRPRPR)\right\rangle_{S^3}
=\frac{503}{648}\operatorname{tr}R^3
+\frac{11}{864}(\operatorname{tr}R)(\operatorname{tr}R^2)
-\frac1{5184}(\operatorname{tr}R)^3,
\]

where (P=I-\frac13nn^T). Including (W=-2R) and the (1/3) coefficient of
the cubic term in (\operatorname{Tr}\log(H_0+W)) gives

\[
J_3\left[
-\frac{503}{243}\operatorname{tr}R^3
-\frac{11}{324}(\operatorname{tr}R)(\operatorname{tr}R^2)
+\frac1{1944}(\operatorname{tr}R)^3
\right],
\qquad
J_3=\int\frac{d^4p}{(2\pi)^4}\frac1{(p^2)^3}.
\]

On the scalar-flat carrier, only the first term remains.

Polarization gives the full zero-momentum `S3` carrier on three symmetric
endomorphisms. In the basis

\[
\frac12\bigl[\operatorname{tr}(R_1R_2R_3)
+\operatorname{tr}(R_1R_3R_2)\bigr],\qquad
\frac13\sum_{\rm cyc}\operatorname{tr}(R_1)\operatorname{tr}(R_2R_3),
\qquad
\prod_i\operatorname{tr}(R_i),
\]

the angular coefficients remain `(503/648, 11/864, -1/5184)` and the
Tr-log coefficients remain `(-503/243, -11/324, 1/1944)`. The verifier checks
the full `S3` stabilizer on noncommuting symmetric matrices and recovers the
diagonal cubic polynomial.

## Why this is not yet the triangle form factor

At zero external momentum, (J_3) is scaleless and infrared singular in four
dimensions. The rational tensor numerator is exact, but it does not determine
the nonzero-momentum three-point kernel or an IR prescription. The repository
normalization map from this Ricci carrier to the source (I10) carrier is also
not frozen. No local counterterm, complete ghost determinant, repository form
factor, (\Gamma_1), or (Q_1) is inferred.

## Independent replay

The verifier does not reuse the closed invariant formulas. It enumerates all
pairings in the second, fourth, and sixth isotropic sphere moments for a
symbolic diagonal symmetric endomorphism, reconstructs the invariant
polynomial, and checks the stored rational coefficients.

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_adiabatic_carrier --emit
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_adiabatic_carrier
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_adiabatic_carrier
```
