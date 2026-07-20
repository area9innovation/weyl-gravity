# Background-specific five-form-factor spectral shortfall

Date: 2026-07-20

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Selected datum

The first background-specific retry selects the compact Euclidean Berger
product

\[
M=S^1\times SU(2),\qquad
g=d\theta^2+\sigma_1^2+\sigma_2^2+4\sigma_3^2,
\]

with the circle length \(2\pi\), no boundary and the product orientation.
In the declared orthonormal frame its exact curvature data are

\[
\operatorname{Ric}=\operatorname{diag}(0,-1,-1,2),\qquad
R=0,\qquad |\operatorname{Ric}|^2=6,\qquad |C|^2=12.
\]

It is therefore compact, scalar-flat, non-Einstein and
non-conformally-flat. Unlike flat \(T^4\), it has nonzero
Schur-sensitive curvature. Unlike round \(S^4\) and
\(S^2(1)\times S^2(2)\), it meets the scalar-flat geometric gate and is not
used as a special-background interpolation fixture.

The local rows specialize exactly to

\[
\operatorname{Wres}(K):\frac83,\qquad
\operatorname{Wres}(K^2):\frac49,\qquad
\partial_{\log\mu}\log\det_3 S_L:\frac{22}{9},
\]

as densities with the common \((4\pi)^{-2}\) factor omitted.

## First missing analytic object

No repository artifact supplies

```text
SCALAR_FLAT_BERGER_S1_S3_PRIMED_SCHUR_RESOLVENT
```

for

\[
S_L=I+\frac13\Delta_0^{-1}\delta Wd.
\]

The required payload must give the Fourier-\(n\)/\(SU(2)\)
representation-block resolvent, normalized primed scalar/vector
projectors, all zero and matched zero-pole factors, insertion
eigenprojectors through third metric variation, uniform high-mode estimates,
and exact or interval-certified finite `det3` and weighted-trace rows. The
reference scale and Agmon-ray phase policy are declared; the spectral payload
must certify primed invertibility and any crossings.

This is the first failure because the independently frozen ambiguity matrix
has rank ten. Its transpose kernel is zero, so complete symbol, residue and
local scale data cannot determine even one nonzero finite Schur-sensitive
combination.

A typed external-analysis request is filed at
`planning/forge-requests/scalar-flat-berger-spectral-measure.json`.

## Claim boundary

This is an exact shortfall theorem and candidate selection, not an evaluation
of the five finite functions. It does not provide a universal table,
\(\Gamma_1\), \(Q_1\), a QME disposition, or any Lorentzian, Hadamard, state,
particle, scattering or unitarity result.

## Evidence

- `quantum-weyl/spectral/euclidean/certificates/BACKGROUND_SPECIFIC_FIVE_FORM_FACTOR_SPECTRAL_REALIZATION_SHORTFALL.json`
- `quantum-weyl/spectral/euclidean/background_specific_five_form_factor_spectral_shortfall.py`
- `quantum-weyl/spectral/euclidean/verify_background_specific_five_form_factor_spectral_shortfall.py`
- `quantum-weyl/spectral/euclidean/tests/test_background_specific_five_form_factor_spectral_shortfall.py`
- `quantum-weyl/spectral/euclidean/schema/background-specific-five-form-factor-spectral-realization-shortfall-v1.schema.json`
