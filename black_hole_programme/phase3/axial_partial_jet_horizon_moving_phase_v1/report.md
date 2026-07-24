# Moving-phase horizon partial-jet report

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Status:
`CERTIFIED_MOVING_PHASE_TAIL_AND_FIRST_PANEL_PARTIAL_JET_PASS`.

## Exact result

The imported spin-two factor has already removed the selected ingoing phase:
the projective-cocycle certificate records
\(\psi=e^{i\omega r_*}P\), and the regular \(P\)-germ is the zero-eigenvalue
line of

\[
R_H=\begin{pmatrix}0&0\\3/2&-1-4i\omega\end{pmatrix}.
\]

The intrinsic tangent matrix \(E\) has no residue:

\[
E_{-1}=\lim_{\rho\to0}\rho E=0.
\]

With

\[
r_H=\binom{1}{3/[2(1+4i\omega)]},\qquad
\ell_H^T=(1,0),
\]

the exponent perturbation is exactly

\[
\dot\lambda_H=
\frac{\ell_H^TE_{-1}r_H}{\ell_H^Tr_H}=0.
\]

The \(\tau\)-jet therefore introduces no new horizon logarithm.

## Correct reduced rail

Instead of exponentiating the singular two-mode coefficient, the package
constructs the selected Frobenius coefficients

\[
(nI-R_H)f_n=\sum_{k<n}A_kf_{n-1-k},
\]

\[
(nI-R_H)g_n=
\sum_{k<n}(A_kg_{n-1-k}+E_kf_{n-1-k}),
\]

with \(f_0=r_H\) and \(g_0=0\).  The exact pivot is

\[
\det(nI-R_H)=n(n+1+4i\omega).
\]

Five orders were derived exactly.  Their all-order tail is bounded using

\[
\|(nI-R_H)^{-1}\|_\infty\le \frac{5}{4n},
\]

and exact Cauchy row bounds on \(|\rho|\le1/2\):

\[
M_A=\frac{26755}{3072},\qquad
M_E=\frac{33017860638199260970}{493743712112492979}.
\]

Writing \(x=\rho_0/(1/2)=2^{-21}\),
\(p=(5/4)M_A/2\), and \(q=(5/4)M_E/2\), the scalar majorants are

\[
F(x)=(1-x)^{-p},\qquad
G(x)=q[-\log(1-x)](1-x)^{-p}.
\]

The resulting tails after order five are less than
\(3.5490\times10^{-36}\) and \(1.1768\times10^{-34}\), respectively.

The tail-enclosed finite value at
\(\rho_0=2^{-22}\) was evaluated on the first frequency child using
`IvTaylor4_omega tensor dual_tau`; compilation and execution passed.

## First-panel result

Across the panel of width \(2^{-30}\), the phase-reduced pure-spin-two
coefficient has scaled norm below \(0.017581\).  An order-12 Peano--Baker
majorant gives operator tail below \(2.464\times10^{-33}\).  The direct real
repeated block

\[
\begin{pmatrix}A&E\\0&A\end{pmatrix}
\]

and the \(A+\varepsilon E\) dual-number transport have equal
\(\omega\)-Taylor coefficients and overlapping tail-enclosed transport and
seed-output hulls.

## Honest remaining shortfall

This is only the selected pure-spin-two first panel.  The spin-one companion
still needs its own Levelt/phase initializer, after which the mixed
spin-one-to-spin-two column and further panels must be propagated.

The prior `ANALYTIC_TAIL_NONCONTRACTIVE` refusal is therefore classified as
an endpoint-representation failure: it applied a matrix exponential to the
singular all-mode coefficient.  In particular, the imported spin-one
companion block has

\[
\lim_{\rho\to0}\rho^2A_x
=\begin{pmatrix}0&0\\-i(4\omega-i)&0\end{pmatrix},
\]

so its unfactored companion representation alone makes the naive coefficient
norm diverge.  A complete three-channel endpoint initializer must separately
apply the spin-one Levelt/phase reduction.  The refusal is not evidence
against the exact bulk partial jet, \(T_+\), or H4.
