# Spin-one Levelt and mixed first-panel report

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Status:
`CERTIFIED_SPIN_ONE_LEVELT_TAIL_AND_MIXED_FIRST_PANEL_PASS`.

## Regular Levelt frame

The large norm in the unfactored preflight came from the spin-one companion
entry proportional to \(\rho^{-2}\).  The exact state change

\[
\widehat Z=\operatorname{diag}(\rho,\rho^2)Z
\]

converts it to a regular-singular block.  For the selected spin-one column,
using \(\widehat X=\rho X\) and \(\widehat Y=\rho Y\) also makes

\[
\widehat D=D\operatorname{diag}(1,\rho^{-1}),\qquad
\widehat C=C\operatorname{diag}(1,\rho^{-1})
\]

regular.  The four-state base residue has characteristic polynomial

\[
\lambda(\lambda-1)(\lambda+4i\omega)^2
\]

and regular spin-one vector

\[
f_0=(0,0,1,-1)^T.
\]

The intrinsic tangent has zero residue, so the exponent is not moved.

## Compatible resonance

At order one, \(I-R_4\) has rank three.  Both base and tangent recurrence
right-hand sides lie in its range.  One free regular spin-two shear is fixed
to zero in each recurrence; the residual is exactly zero.  Therefore the
selected Levelt column has no forced logarithm in this normalization.

## Tail and first panel

On \(|\rho|\le1/2\), exact rectangular Cauchy evaluation gives

\[
M_B=\frac{16387}{768},\qquad
M_{\dot B}=
\frac{94804726516564748219}{987487424224985958}.
\]

The exact pivot estimate

\[
\|(nI-R_4)^{-1}\|_\infty\le\frac3n,\qquad n\ge2,
\]

is checked directly for \(2\le n\le12\) and by a Neumann bound thereafter.
The resulting order-five tail bounds at \(\rho_0=2^{-22}\) are below
\(2.736\times10^{-32}\) for the base and
\(6.867\times10^{-31}\) for the tangent.

Across the first panel of width \(2^{-30}\), the scaled coefficient norm is
below \(0.023473\); the order-12 operator tail is below
\(1.056\times10^{-31}\).  Direct regular-frame six-state transport and the
four-state dual-number transport have identical \(\omega\)-Taylor
coefficients and overlapping tail-enclosed transport and seed-output hulls.

## Boundary

This is a one-panel certificate.  Multipanel transport and the endpoint
normalizer shear \(K_H\) remain open.  Nothing here establishes \(T_+\), H4,
scattering, or bounded global transport.
