# Weyl-graviton `Box R` coefficient and scheme conversion

## Result

The matched conformal-transverse zeta/proper-time calculation gives the raw
strict-Weyl trace-anomaly coordinate

\[
b_{\Box}^{\rm raw}
=\frac72\log\frac32-\frac{159}{80}.
\]

The result is reconstructed exactly from the published heat-kernel rows

\[
2\,\mathrm{tr}\,a_2^H-\mathrm{tr}\,a_2^Y-2\,\mathrm{tr}\,a_2^M.
\]

The repository has independently certified

\[
s\!\int R^2=-12\int\omega\Box R\pmod {d_h}.
\]

Consequently the finite strict-metric counterterm carrying the raw scheme to
the repository `BoxR=0` scheme is

\[
z_R^{\rm raw\to0}
=\frac1{12}b_{\Box}^{\rm raw}
=\frac7{24}\log\frac32-\frac{53}{320}.
\]

This is a relative normalization between two declared schemes. It is not an
observational choice of the remaining finite coupling, nor an all-loop
equivalence of strict theories: adding `R(g)^2` changes the scalar dynamics
beyond this one-loop conversion.

The source quotes `199/15` in its (C^2) row. In repository conventions this
is (eta_2=2c), whereas the certified anomaly coordinate is
(c=199/30). The source (C^2) number is therefore retained only as a
convention guard, not imported over the repository coordinate. Its
(-87/20) Euler row and the local `R^2` variation convention agree directly.

## Independent cross-check

Before the scheme change, the anomaly-induced local term has coefficient

\[
z_{R,\mathrm{ind}}^{\rm raw}
=\frac{391}{960}-\frac7{24}\log\frac32.
\]

Adding the exact scheme conversion cancels the logarithms and gives

\[
z_{R,\mathrm{ind}}^{\rm raw}+z_R^{\rm raw\to0}
=\frac{29}{120},
\]

which is precisely the coefficient in the existing repository
Paneitz/Riegert certificate.

The nonzero sign is also exact: the four-term alternating-series bounds

\[
\frac{77}{192}<\log\frac32<\frac{391}{960}
\]

prove (b_{\Box}^{\rm raw}<0) without floating-point arithmetic.

## Three different `R^2` questions

They must not be conflated:

1. `R(g)^2` is a conformally noninvariant strict-metric counterterm. It moves
   the exact `omega BoxR` coordinate.
2. `R(g_hat)^2` is a BRST-invariant (H^{0,4}) class of the tau-adic
   compensator theory. Its finite coefficient changes (Q_1) but does not
   undo the scheme calculation above.
3. The finite momentum-dependent nonlocal `R^2` form factor requires a
   covariant nonlocal expansion of the complete fourth-order tensor and
   nonminimal vector determinants. Neither a local (a_2) coefficient nor
   the anomaly equation determines it.

The third calculation remains open. The primary analytic source explicitly
identifies it as a separate future calculation:
[Barvinsky et al., arXiv:2308.05251](https://arxiv.org/abs/2308.05251).

## Claim boundary

This is `LOCAL-ALGEBRAIC` plus `EUCLIDEAN-SPECTRAL`. The source universal
functional traces are imported, not rederived. Their exact final-row
arithmetic, the repository BRST primitive, the scheme conversion and the
`29/120` cross-check are independently replayed. The certificate does not fix
the dressed `R(g_hat)^2` normalization, compute the nonlocal `R^2` form factor
or cubic `C^2` completion, supply complete `Gamma1` or `Q1`, authorize
residual transfer, or make a Lorentzian claim.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.box_r_scheme_conversion --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_box_r_scheme_conversion
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_box_r_scheme_conversion
```
