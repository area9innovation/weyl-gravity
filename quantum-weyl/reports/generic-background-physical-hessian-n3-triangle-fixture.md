# Exact physical-Hessian three-linear triangle fixture

## Result

The same-gauge physical Hessian imported through first curvature order is now
an operational momentum-space kernel.  On the scalar-flat restriction the
source `V/N/U` rows define a rank-nine traceless-metric vertex, and its formal
adjoint completion is

\[
A(k,q)=\frac12\left[S(k,q)+S(-k,q+k)^T\right].
\]

The exact identity

\[
A(k,q)=A(-k,q+k)^T
\]

has zero component defects.  Omitting the completion produces 62 defects on
the stored rational fixture, so the check is sensitive to the seam that would
otherwise invalidate cyclic trace manipulations.

The external scalar-flat Ricci carriers are transverse and traceless.  Their
linearized Riemann tensors are reconstructed from

\[
h_{\mu\nu}=\frac{2R_{\mu\nu}}{k^2},
\]

and independently satisfy both pair antisymmetries, pair exchange, the first
algebraic Bianchi identity, and contraction back to the input Ricci tensor.

## Exact interior fixture

The nonexceptional Euclidean momenta are

\[
k_1=(1,-1,-2,-2),\quad
k_2=(-2,1,0,2),\quad
k_3=(1,0,2,0),
\]

with \((k_1^2,k_2^2,k_3^2)=(10,9,5)\).  At

\[
(\alpha_0,\alpha_1,\alpha_2)
=\left(\frac7{15},\frac15,\frac13\right),
\qquad
\Delta=\frac{104}{45},
\]

the exact rank-nine loop trace has maximum loop degree six and 210 canonical
monomials.  Feynman parametrization of

\[
\frac1{D_0^2D_1^2D_2^2}
\]

and the bosonic \(\tfrac12\operatorname{Tr}\log\) coefficient give the four
integrated Wick weights

\[
1,\qquad \frac16,\qquad \frac1{24},\qquad \frac1{48}.
\]

Their common \(\Delta^{-4}\) numerator is

\[
-\frac{3532544138843839}{11210083593750},
\]

and hence the physical kernel at this interior point, before the universal
\((4\pi)^{-2}\) factor, is

\[
\boxed{-\frac{3532544138843839}{319810083840000}}.
\]

The nonzero value is an operational coefficient-bearing fixture.  It proves
that the imported covariant Hessian rows, their Fourier signs, the traceless
metric representation, the loop routing, Feynman shift and Wick reduction
compose consistently on one generic point.

## Claim boundary

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This result does not yet provide the full alpha polynomial, its projection to
the five third-curvature carriers, simplex integration of the physical tensor
triangle, the curvature-squared `H2` layer, mixed `H1/H2` traces, complete
repository form factors, `Gamma1`, `Q1`, residual transfer, a Lorentzian QME,
a Hadamard state, or a particle theorem.

The next coefficient-bearing gate is:

```text
INTERPOLATE_PHYSICAL_N3_COMMON_NUMERATOR_PROJECT_TO_FIVE_CARRIERS_AND_IMPORT_CURVATURE_SQUARED_H2
```

## Artifacts

- generator: `quantum-weyl/spectral/euclidean/generic_background_physical_hessian_n3_triangle_fixture.py`
- certificate: `quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json`
- independent verifier: `quantum-weyl/spectral/euclidean/verify_generic_background_physical_hessian_n3_triangle_fixture.py`
- strict schema: `quantum-weyl/spectral/euclidean/schema/generic-background-physical-hessian-n3-triangle-fixture-v1.schema.json`
- scoped tests: `quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_hessian_n3_triangle_fixture.py`

## Reproduction and test tier

Run:

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_n3_triangle_fixture --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_n3_triangle_fixture
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_n3_triangle_fixture
```

Tier 0 covers Python compilation, JSON parsing and strict Draft 2020-12 schema
validation, Markdown inspection, and `git diff --check`.  Tier 1 covers the
three commands above. On the recorded workstation they passed in `15.71 s`,
`16.58 s`, and `17.38 s`, respectively; the scoped test contains eight cases.
The affected Paper 12 and active-frontier claim chains are Tier 2 because this
fixture updates their coefficient-bearing open edge. Frontier regeneration,
check, independent verification and eight scoped tests passed; the measured
check, verifier and test times were `0.17 s`, `0.27 s`, and `0.51 s`. The main
Paper 12 PDF settled in two clean passes in `1.18 s`, and the supplement in
three clean passes in `1.83 s`; neither final log contained errors, warnings,
undefined references, underfull boxes, or overfull boxes. The regenerated
Paper 12 claim map check and its independent verifier passed in `0.06 s` and
`0.05 s`. The generated atlas check, independent verifier and seven scoped
tests passed in `0.61 s`, `0.74 s`, and `1.54 s`; the common fragment
validator also passed.

Three fail-closed integration checks initially rejected stale receiving
assumptions: the frontier test still named the predecessor gate (`0.48 s`),
the Paper 12 verifier still expected 46 rather than 47 inputs (`0.04 s`), and
the atlas still enforced 21 entries/11 guards before the new non-particle row.
Each receiver was updated to the new exact dependency, then its complete
scoped chain was rerun as recorded above. These failures were not counted as
passes and promoted no claim.
Tier 3 is not required: this is neither a freeze, lifecycle promotion, shared
core-algebra change, nor release.
