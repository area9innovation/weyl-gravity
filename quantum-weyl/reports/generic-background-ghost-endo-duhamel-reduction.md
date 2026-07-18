# Generic-background ghost Endo–Duhamel reduction

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

The generic Diff×Weyl ghost obstruction does not force a completely new heat
kernel calculus. With the positive Euclidean convention
\(H=-M_{\mathrm{eff}}\), the operator splits exactly as

\[
H=H_0+W,
\qquad
H_0=F-\frac12\nabla\nabla\!\cdot,
\qquad
F=-\Box\mathbf1+\operatorname{Ric},
\qquad
W=-2\operatorname{Ric}.
\]

The base \(H_0\) is the nondegenerate Endo vector operator with
\(\alpha=-1/2\). Its transverse and longitudinal principal eigenvalues are
\(1\) and \(3/2\), and its heat kernel is exactly

\[
K_{H_0}(t)=K_F(t)-\nabla\nabla'\int_t^{3t/2}ds\,K_{\Delta_0}(s).
\]

The finite proper-time interval is important: no artificial infinite-range
IR integral is introduced. On nonzero modes,

\[
\det{}'H_0
=\det{}'F\,
\frac{\det{}'((3/2)\Delta_0)}{\det{}'\Delta_0},
\]

so the difference between the Endo base and the minimal vector determinant is
the local zeta-scaling term
\(\zeta_{\Delta_0}(0)\log(3/2)\). Generic nonlocal ghost corrections are
therefore localized to insertions of the endomorphism
\(W=-2\operatorname{Ric}\).

## Cubic-curvature work table

Because \(W=O(\mathcal R)\), the determinant through
\(O(\mathcal R^3)\) contains only:

| Ricci insertions | maximum remaining Endo-kernel order |
|---:|---:|
| 0 | 3 |
| 1 | 2 |
| 2 | 1 |
| 3 | 0 |

Thus the generic ghost calculation is a finite set of one-, two- and
three-insertion traces, not an uncontrolled expansion of the original
nonminimal operator.

## Claim boundary

This is an exact determinant reduction, not the evaluated determinant. The
Ricci-insertion traces, their third-curvature carrier coordinates, and the
generic physical fourth-order Hessian kernel remain open. No repository
form-factor coefficient, complete `Gamma1/Q1`, residual transfer, Lorentzian
QME, Hadamard, particle, positivity or unitarity theorem follows.

The formula is specialized from the version-pinned primary source
Barvinsky–Kalugin–Wachowski, arXiv:2508.06439v2; the source archive and TeX
hashes are stored in the certificate.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_endo_duhamel_reduction --emit
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_endo_duhamel_reduction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_endo_duhamel_reduction
```
