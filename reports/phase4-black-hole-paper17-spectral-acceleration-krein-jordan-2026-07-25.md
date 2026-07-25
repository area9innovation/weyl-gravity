# Paper 17 spectral acceleration and Krein--Jordan geometry

## Result

Paper 17 now extends the critical-mass interpretation from spectral velocity
to spectral acceleration.  For an analytic massive Evans function with
simple zeros \(\omega_n(m)\), it defines

\[
\Theta_1=-\left.\partial_m\log a\right|_{m=0}\,d\omega,
\qquad
\Theta_2=-\left.\partial_m^2\log a\right|_{m=0}\,d\omega .
\]

Their local principal parts are

\[
\Theta_1=
\left[
\frac{\nu_n}{\omega-\omega_n}
+\operatorname{hol}
\right]d\omega,
\]

\[
\Theta_2=
\left[
\frac{\nu_n^2}{(\omega-\omega_n)^2}
+\frac{\xi_n}{\omega-\omega_n}
+\operatorname{hol}
\right]d\omega,
\]

where

\[
\nu_n=\omega_n'(0),
\qquad
\xi_n=\omega_n''(0).
\]

Evans renormalization changes these forms only by holomorphic one-forms.
Consequently their residues and closed-contour moments are intrinsic.  For
an analytic test function \(\varphi\),

\[
\frac1{2\pi i}\oint_\Gamma\varphi\Theta_1
=\sum_n\varphi(\omega_n)\nu_n,
\]

\[
\frac1{2\pi i}\oint_\Gamma\varphi\Theta_2
=\sum_n\left[
\varphi(\omega_n)\xi_n+\varphi'(\omega_n)\nu_n^2
\right].
\]

The acceleration has the unit-invariant Evans formula

\[
\xi_n=
-\frac{
a_{mm}+2\nu_na_{\omega m}+\nu_n^2a_{\omega\omega}
}{a_\omega}\bigg|_{(\omega_n,0)},
\]

and agrees with the augmented finite-part operator expression already
derived in the paper.

## Second critical jet

For

\[
J_2=\frac12\left.\partial_m^2R_m\right|_{m=0},
\]

the complete singular expansion at a simple QNM is

\[
J_2=
\frac{\nu_n^2P_n}{(\omega-\omega_n)^3}
+\frac{\nu_n\dot P_n+\frac12\xi_nP_n}
{(\omega-\omega_n)^2}
+\frac{\frac12\ddot P_n}{\omega-\omega_n}
+\operatorname{hol}.
\]

Thus the triple pole records squared spectral velocity, the double pole
combines acceleration with first projector motion, and the simple pole
records second projector motion.  If \(\nu_n=0\) but \(\xi_n\ne0\), the
first mass jet has no double pole while the second jet has a genuine double
pole.

The corresponding isolated local contour contribution is

\[
e^{i\omega_nt}
\left[
\frac12\ddot P_n
+it\,\nu_n\dot P_n
+\left(
\frac{it\,\xi_n}{2}-\frac{t^2\nu_n^2}{2}
\right)P_n
\right].
\]

For \(\omega_n=\omega_R+i\gamma\), \(\gamma>0\), the first-jet Jordan
envelope \(t e^{-\gamma t}\) is bounded, with maximum at
\(t=1/\gamma\) and value \(1/(e\gamma)\).  At the certified mode this is
approximately \(11.241M\) and \(4.135M\), respectively.  This is an
isolated-contour statement, not a theorem about the complete retarded
waveform or global stability.

## Canonical Krein--Jordan geometry

On a length-two root space with

\[
NV_0=0,\qquad NV_1=V_0,
\]

every nondegenerate Hermitian form satisfying \(N^\dagger G=GN\) has,
after an allowed root-chain shift and an overall rescaling, the unique
normal form

\[
G\sim
\begin{pmatrix}
0&1\\
1&0
\end{pmatrix}.
\]

The geometric and normalized generalized roots are null and pair
nontrivially.  No positive-definite form can make the nonzero nilpotent
self-adjoint.

The full graded second-order Laurent coefficient is the null rank-one map

\[
\mathbb R_{-2}
=\gamma_n V_0\otimes V_0^\flat,
\qquad
\mathbb R_{-2}^2=0.
\]

Its trace and determinant invariants vanish despite the operator being
nonzero.  This explains why the critical spectral determinant cannot detect
the enhanced nilpotent response.  The projected metric Green coefficient
remains only a rank-one operator; it is not asserted to be intrinsically
nilpotent after the grading is forgotten.

For separated branch signatures \(\sigma_0,\sigma_1\), a finite
nondegenerate first-order critical pairing exists precisely when
\(\sigma_1=-\sigma_0\).  Opposite signatures yield the hyperbolic limit,
whereas equal signatures leave only a rank-one limit after second-order
rescaling.  The finite-mass branch involution therefore has no bounded
positive nondegenerate critical limit.

## Independent verification

The exact verifier independently checks:

- the principal parts and residues of \(\Theta_1\) and \(\Theta_2\);
- the weighted second spectral-flow residue formula;
- the acceleration formula and its invariance under analytic Evans units;
- all three singular coefficients of \(J_2\);
- the isolated second-order contour polynomial;
- the maximum of \(t e^{-\gamma t}\);
- the matrix classification \(N^\dagger G=GN\) and the chain shift removing
  the lower-right Gram entry;
- square-zero null rank-one structure and determinant invisibility;
- opposite-sign and same-sign branch-form limits;
- the fail-closed claim boundary.

Nine new mutation tests reject sign, factor, chain-shift, metric-signature,
rank, and forbidden-promotion mutations.  The scoped suite passed 58 tests
in 48.880 seconds.  The full repository suite passed 149 tests in 1.21
seconds.

## Claim boundary

Established:

- exact first and second spectral-flow one-forms;
- exact weighted velocity and acceleration contour moments;
- exact unit-invariant Evans acceleration formula;
- exact second-jet Laurent coefficients and isolated-contour polynomial;
- exact bounded damped Jordan envelope;
- exact canonical Krein--Jordan classification on the critical root space;
- exact null rank-one nilpotency on the full graded extension space;
- exact opposite-sign confluence criterion;
- exact local obstruction to a positive self-adjoint nilpotent realization.

Not established:

- a validated numerical acceleration or multi-QNM acceleration contour;
- a numerical value for \(\xi_n\);
- a global retarded inverse-Laplace deformation;
- a complete waveform or stability theorem;
- a global physical or quantum positivity no-go;
- intrinsic nilpotency of the projected metric Green coefficient;
- all-multipole Bach nonsplitting.

CLOSE-OUT: DONE — Paper 17 now contains exact second-order spectral
kinematics and a unified local Krein--Jordan geometry, with all numerical,
causal, projected-nilpotency, and quantum promotions excluded.

EVIDENCE: `reports/PAPER17_SPECTRAL_ACCELERATION_KREIN_JORDAN_TIER_RECEIPT.json`
