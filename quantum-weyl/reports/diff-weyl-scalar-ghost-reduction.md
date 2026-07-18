# Diff x Weyl scalar ghost reduction

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

On a four-dimensional Euclidean Einstein background, use

\[
  R_{\mu\nu}=\frac R4 g_{\mu\nu},\qquad
  \Delta_0=-\nabla^2,
\]

and the conformally invariant vector gauge together with trace gauge

\[
  F_\mu=\nabla^\nu h_{\mu\nu}-\frac14\nabla_\mu h,
  \qquad F_W=h.
\]

For

\[
  Qh_{\mu\nu}=\nabla_\mu\xi_\nu+\nabla_\nu\xi_\mu
  +2\omega g_{\mu\nu},
  \qquad \xi_\mu=\xi^T_\mu+\nabla_\mu c,
\]

the scalar Faddeev--Popov block from `(c, omega)` to the longitudinal part of
`F_mu` and `F_W` is

\[
  M_{\rm scalar}=
  \begin{pmatrix}
  -\frac32(\Delta_0-R/3)&0\\
  -2\Delta_0&8
  \end{pmatrix}.
\]

The zero in the upper-right entry is derived: the Weyl variation cancels
between the divergence and trace subtraction in `F_mu`. The longitudinal
curvature shift follows from

\[
  \nabla^2\nabla_\mu c
  =\nabla_\mu\nabla^2c+R_{\mu\nu}\nabla^\nu c.
\]

Consequently,

\[
  \det M_{\rm scalar}=-12\,\det(\Delta_0-R/3).
\]

Thus the rank-two longitudinal-Diff/Weyl ghost input produces exactly one
background-dependent differential scalar determinant. At the standard unit
curvature normalization `R=12`, this is `Delta_0-4`, matching the certified
`ghost_depth_0` factor with `M_squared=-4`. The remaining factor `-12` is
operator independent. Its regulated infinite-dimensional normalization is
part of the still-open measure ledger, so no background-independence claim is
inferred for that normalization.

The calculation also keeps a general vector-gauge trace coefficient `beta`.
Although only `beta=1/4` makes the block triangular, its determinant is
independent of `beta`. A negative control drops one of the two Einstein Ricci
contributions; the resulting `R/4` row fails the target identity.

## Remaining analytic gap

This closes the scalar operator and rank mismatch, not the complete
multiplicity theorem. The following still have to be matched in one
gauge-fixed functional integral:

- the York/Hodge functional-measure Jacobian;
- antighost, multiplier, and general nonminimal Berezinian factors;
- the complete repository physical Hessian and auxiliary normalization;
- zero modes, contour, phase, and determinant measure;
- total integration-row and factor coverage through
  `REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER`.

No repository anomaly coefficient, regulated Slavnov breaking, QME verdict,
quantum (D)-Cartan class, residual transfer, or Lorentzian quantum theory is
claimed.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.scalar_ghost_reduction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_scalar_ghost_reduction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_scalar_ghost_reduction -v
```
