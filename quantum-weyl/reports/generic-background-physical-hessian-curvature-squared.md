# Generic-background physical Hessian at curvature order two

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The projected monic algebraic curvature-squared block of the traceless
physical Hessian is now imported from Appendix A of Ohta--Percacci,
arXiv:1506.05526.  The pure-Weyl specialization is made directly as

\[
 (\alpha,\beta,\gamma)=\left(\frac16,-1,\frac12\right),
 \qquad
 \alpha R^2+\beta R_{\mu\nu}^2+\gamma R_{\mu\nu\rho\sigma}^2
 =\frac12 C^2.
\]

After the traceless projection, the leading tensor is \(K=1/4\), so the
source block is multiplied by four to obtain the monic \(U_{(2)}\).  The
certificate retains all eighteen printed rows, including six rows killed by
the traceless projector and the exact cancellation
\((\beta/2+\gamma)R_{\mu\alpha}R_{\nu\beta}=0\).  Nine nonzero rows survive on
the scalar-flat domain.

## Gauge-ordering crosswalk

The source fixes \(c-d=-1/3\) and chooses \((d,c)=(1,2/3)\).  The repository
operator corresponds to \((d,c)=(0,-1/3)\).  With
\(\chi_\mu=\nabla^\nu h_{\mu\nu}\),

\[
 Y_d-Y_0=d[\nabla_\mu,\nabla_\nu],
 \qquad
 S_{\rm gf}(0)-S_{\rm gf}(1)
 =\frac12\int\chi_\mu R^{\mu\nu}\chi_\nu .
\]

In the source monic-Hessian normalization this is

\[
 H_{1,\rm repo}-H_{1,\rm source}=2G_{\rm Ric},
 \qquad
 G_{\rm Ric}(L,H)=(\nabla\!\cdot L)_\mu
 R^{\mu\nu}(\nabla\!\cdot H)_\nu .
\]

The difference is curvature-linear and contains derivatives on both
fluctuations.  It therefore changes \(H_1\), not the algebraic
curvature-squared \(H_2\).  Five exact component fixtures regress the ratio
two.

## Round check and claim boundary

On a round four-sphere the algebraic block is \(+24K^2\) on TT tensors.  It
must not be identified with the full order-\(K^2\) remainder.  Contracted
derivative indices in \(H_1\) contribute \(-16K^2\), leaving

\[
 24K^2-16K^2=8K^2,
\]

which is the constant term in the monic factorization
\((A+2K)(A+4K)\).  The repository functional Hessian is half of this.

This closes the missing algebraic \(H_2\) input only.  Polarization into two
labelled curvatures, the mixed \(H_1H_2\) trace, its projection against the
certified `M14` corner class, and the complete physical third-curvature
functions remain open.

## Verification receipt

Observed on 2026-07-19:

- Tier 1 generator: `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_curvature_squared` — PASS, 0.23 s.
- Tier 1 freshness check: the same command with `--check` — PASS, 0.20 s.
- Tier 1 independent replay: `PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_curvature_squared` — PASS, 0.19 s.
- Tier 1 scoped unit suite: `PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_curvature_squared` — PASS, 0.34 s (8 tests; unittest body 0.166 s).
- Tier 2 active-frontier and residual-atlas chain: the module checks and scoped suites recorded by those generated artifacts — PASS, 9.6 s.
- Tier 2 Paper 12 claim-map emit/check/independent replay — PASS, 0.6 s.
- Tier 3 full repository suite was not run: this import closes one coefficient input but does not freeze a theorem or promote a lifecycle state.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_curvature_squared --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_curvature_squared
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_curvature_squared
```
