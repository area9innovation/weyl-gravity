# Generic ghost `n=3` pole-three integrated functions

## Result

The ten generic nonexceptional pole-three rows in the third-curvature ghost
triangle are now integrated exactly. Every row has the form

\[
 A_J(x)J(x_1,x_2,x_3)
 +A_{21}(x)\log\frac{x_2}{x_1}
 +A_{31}(x)\log\frac{x_3}{x_1}
 +R_{\rm corner}(x),
\]

with all four coefficients stored as exact rational functions. This is
`EUCLIDEAN-SPECTRAL`. The pole-four `I29_123` row remains open, so this is ten
of eleven generic ghost `n=3` functions and not a complete ghost determinant.

## Scalar-triangle differential system

Writing

\[
 \lambda=x_1^2+x_2^2+x_3^2
 -2x_1x_2-2x_1x_3-2x_2x_3,
\]

the first derivative is

\[
 \lambda\,\partial_{x_1}J
 =(x_2+x_3-x_1)J
 -\frac{x_1+x_2-x_3}{x_1}\log\frac{x_2}{x_1}
 -\frac{x_1+x_3-x_2}{x_1}\log\frac{x_3}{x_1},
\]

with the other two rows obtained cyclically. The machine verifies all six
`S3` relabellings, Euler homogeneity

\[
 x_1\partial_{x_1}J+x_2\partial_{x_2}J+x_3\partial_{x_3}J=-J,
\]

and all three mixed-derivative integrability identities. In the two-log
basis the derivative masters are

\[
 M_{x_1}=-\partial_{x_1}J
 =\frac{x_1-x_2-x_3}{\lambda}J
 +\frac{x_1+x_2-x_3}{x_1\lambda}\log\frac{x_2}{x_1}
 +\frac{x_1+x_3-x_2}{x_1\lambda}\log\frac{x_3}{x_1},
\]

\[
 M_{x_2}=-\partial_{x_2}J
 =\frac{-x_1+x_2-x_3}{\lambda}J
 -\frac{2}{\lambda}\log\frac{x_2}{x_1}
 +\frac{-x_1+x_2+x_3}{x_2\lambda}\log\frac{x_3}{x_1}.
\]

The architecture and bubble descendants agree with Kol and Mazumdar,
[arXiv:1909.04055](https://arxiv.org/abs/1909.04055); the stored identities
are independently replayed in repository conventions.

## Punctured-corner flux

The previous relative-IBP certificate correctly proved that a primitive with
zero punctured-corner flux does not exist in the declared degree-four ansatz.
It described the remaining angular carrier too broadly as a corner-log
system. The explicit canonical primitives simplify more strongly.

For every representative, the two coordinate vertices have zero leading
pair, while the `alpha0` vertex satisfies

\[
 U_C=V_C.
\]

The oriented angular flux is therefore reduced by

\[
 \int_0^{\pi/2}
 \frac{\cos^2\theta+\sin^2\theta}
 {(a\cos\theta+b\sin\theta)^2}\,d\theta
 =\frac1{ab}.
\]

The individual cosine and sine moments contain logarithms and `pi`, but these
cancel in the equal-weight sum. Thus the punctured corner contributes the
exact rational term

\[
 R_{\rm corner}=-\frac{U_C}{x_1x_3}
\]

for a representative, transported by the certified simplex permutation for
the other orientations. The two logarithms in the final functions arise
from the scalar-triangle derivative system, not from an additional corner
master.

## Exact regressions

At `x1=x2=x3=1`, the logarithms vanish and
`partial_xi J=-J/3`. For all ten channels:

- the computed `J` coefficient equals the stored Clausen-master coefficient;
- the oriented corner flux equals the stored rational term;
- the sum reproduces the earlier exact symmetric-point integral.

The integrated identity

\[
 I28_{123}+I28_{132}+I28_{231}=0
\]

holds separately in all four basis coordinates.

## Artifacts

- `spectral/euclidean/generic_scalar_triangle_differential_system.py`
- `spectral/euclidean/certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json`
- `spectral/euclidean/verify_generic_scalar_triangle_differential_system.py`
- `spectral/euclidean/generic_background_ghost_n3_pole3_integrated_functions.py`
- `spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json`
- `spectral/euclidean/verify_generic_background_ghost_n3_pole3_integrated_functions.py`

Both certificates use strict Draft 2020-12 schemas. Independent verifiers
reconstruct the differential rows, rational partial-fraction angular moments,
corner fluxes, ten channel reductions, symmetric-point regressions, dependency
hashes, and fail-closed lifecycle flags.

## Remaining gate

The next coefficient-bearing task is the pole-four `I29_123` reduction. Even
after it is closed, the same-gauge generic physical fourth-order Hessian is a
separate required input before the complete repository third-curvature
functions or complete `Gamma1/Q1` can be claimed.
