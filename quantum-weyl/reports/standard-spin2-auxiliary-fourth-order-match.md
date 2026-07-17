# Standard spin-two auxiliary/fourth-order match

Dependency tags: `EUCLIDEAN-SPECTRAL`, `LOCAL-ALGEBRAIC`.

The standard conformal-spin-two determinant contains the physical transverse
traceless pair

\[
A=\Delta_2^\perp(2),\qquad A+2=\Delta_2^\perp(4).
\]

Because the factors differ by the scalar endomorphism (2I), they commute.
Introduce an algebraic transverse-traceless auxiliary field (f) with

\[
S_{\rm aux}
=\frac12\langle h,2Ah\rangle+\langle h,Af\rangle
-\frac12\langle f,f\rangle.
\]

The exact auxiliary equation is (f=Ah). Substitution gives

\[
S_{\rm aux}\big|_{f=Ah}
=\frac12\langle h,A(A+2)h\rangle.
\]

At an eigenvalue (lambda), the block Hessian and its determinant are

\[
K(\lambda)=
\begin{pmatrix}2\lambda&\lambda\\ \lambda&-1\end{pmatrix},
\qquad
\det K=-\lambda(\lambda+2).
\]

The machine verifies both this determinant identity and the Schur complement
over exact rational polynomials. Replacing the upper-left block (2A) by
(3A) leaves residuals (-\lambda) and (+\lambda), so the test detects an
incorrect auxiliary normalization.

For a translation-invariant normalized algebraic-(f) measure,

\[
\det K=\det(-I_f)\det[A(A+2)],
\]

and the first factor has no background-dependent logarithmic coefficient.
This does not fix its contour phase or finite normalization.

## Claim boundary

This closes only the local Gaussian identity for the two standard physical
TT factors. The repository physical Hessian has not been identified with
(A(A+2)); the full ghost and nonminimal operator rows, action normalization,
auxiliary contour, finite phase, zero modes, determinant measure, and
regulated Slavnov functional are not matched. It is not a repository
ellipticity, coefficient, QME, Cartan, residual-transfer, or Lorentzian
certificate.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.auxiliary_fourth_order_match --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_auxiliary_fourth_order_match
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_auxiliary_fourth_order_match -v
```
