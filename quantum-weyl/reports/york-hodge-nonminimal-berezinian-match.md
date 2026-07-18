# York/Hodge and nonminimal Berezinian match

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This certificate continues the exact scalar FP reduction on the nonzero
spectrum of a compact four-dimensional Euclidean Einstein background.

For the York decomposition

\[
h_{\mu\nu}=h^{TT}_{\mu\nu}
 +2\nabla_{(\mu}v^T_{\nu)}
 +\left(\nabla_\mu\nabla_\nu-\frac14g_{\mu\nu}\nabla^2\right)\sigma
 +\frac14g_{\mu\nu}h,
\]

integration by parts and (R_{\mu\nu}=Rg_{\mu\nu}/4) give

\[
\lVert Lv^T\rVert^2
 =2\langle v^T,(\Delta_1^T-R/4)v^T\rangle,
\]

\[
\lVert S\sigma\rVert^2
 =\frac34\langle\sigma,
   \Delta_0(\Delta_0-R/3)\sigma\rangle.
\]

The implementation derives these coefficients in general dimension: the
vector shift is (R/d), while the traceless-scalar norm is
((d-1)\Delta_0(\Delta_0-R/(d-1))/d). Specializing to (d=4) forces the
(R/4), (3/4), and (R/3) coefficients; a (d=5) mutation is rejected.

Ignoring only operator-independent constants, the metric York Jacobian is

\[
J_h=
\left[
\det(\Delta_1^T-R/4)
\det(\Delta_0)
\det(\Delta_0-R/3)
\right]^{1/2}.
\]

The vector Hodge decompositions contribute

\[
J_\xi=\det(\Delta_0)^{-1/2},\qquad
J_{\bar\xi}=\det(\Delta_0)^{-1/2},\qquad
J_b=\det(\Delta_0)^{+1/2}.
\]

Therefore the unwanted scalar Laplacian cancels exactly:

\[
\frac12-\frac12-\frac12+\frac12=0.
\]

For every nonzero gauge-mode block, including the coupled scalar Diff/Weyl
block, the bosonic gauge-mode/multiplier matrix is

\[
\begin{pmatrix}0&M^T\\M&\alpha Y\end{pmatrix},
\]

whose determinant is (det(-M^TM)), independently of the gauge weight
(Y). Its Gaussian contributes (det M^{-1}), while the fermionic
antighost/ghost pair contributes (det M). Thus every such quartet has unit
nonzero-mode superdeterminant.

The surviving ghost factors are precisely

\[
\det(\Delta_1^T-R/4)^{1/2},\qquad
\det(\Delta_0-R/3)^{1/2},
\]

with ranks (3) and (1). At (R=12), their shifts are (-3) and
(-4), matching `ghost_depth_1` and `ghost_depth_0` in the standard
conformal-spin-two determinant.

## Claim boundary

The calculation is restricted to the common nonzero-mode domain. It does not
classify conformal-Killing or scalar zero modes, normalize the repository
physical TT Hessian, fix the algebraic auxiliary contour or phase, close the
complete multiplicity export, or compute a repository Slavnov breaking or QME
verdict. A mutation omitting the bosonic multiplier Hodge Jacobian leaves a
spurious `det(Delta_0)^(-1/2)` and is rejected.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.york_hodge_berezinian --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_york_hodge_berezinian
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_york_hodge_berezinian -v
```
