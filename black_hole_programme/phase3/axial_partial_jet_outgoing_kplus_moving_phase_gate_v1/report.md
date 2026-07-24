# Outgoing analytic K-plus gate

## Exact endpoint diagnosis

The joint outgoing reduced frame has rank three, but its endpoint
\(\tau\)-dependence is not captured by a static rephasing.

For the spin-two pencil \(A_{\rm RW}+\tau E_{\rm RW}\), subtract the fixed
outgoing logarithmic phase derivative

\[
-2i\omega-\frac{4i\omega}{r}.
\]

The exact asymptotic entries include

\[
(E_{\rm RW})_{12}=\frac34r+O(1),\qquad
(E_{\rm RW})_{22}=-\frac34+O(r^{-1}).
\]

Differentiating the characteristic polynomial of the reduced branch gives

\[
\dot q_+=-\frac34,\qquad \dot p_+=0.
\]

The irregular coefficient is removed by the canonical polynomial
eigenvector gauge

\[
B=\operatorname{diag}\left(\frac34,0\right),
\qquad E_{-1}+[A_0,B]=0.
\]

Thus the complete first-order moving factor contains both the scalar phase

\[
\exp\!\left[\left(-2i\omega-\frac34\tau\right)r\right]
r^{-4i\omega}+O(\tau^2).
\]

and \(I+\tau rB\). Their combined logarithmic generator is

\[
\dot q_+I+B
=\operatorname{diag}\left(0,-\frac34\right).
\]

The spin-one block and its phase are \(\tau\)-independent. At \(r=31\), the
relative common-gauge normalizer consequently has

\[
\partial_\tau\log h=\frac{93}{4}.
\]

This is a nonzero exact obstruction to the requested \(\tau\)-independent
rephasing.

## What remains valid

The canonical endpoint recurrence still has zero forced logarithms for
XI2/XI3, unit leading factor amplitudes, and zero free EI2 constants.
Therefore the formal canonical \(K_+=0\) calculation remains intact.
However, the fixed-phase R/S checkpoints must first be reissued as

\[
\dot R_{\rm mov}
=\dot R_{\rm fixed}
+\operatorname{diag}\left(0,\frac{93}{4}\right)R,
\]

\[
S_{\rm common}=h_0S,\qquad
\dot S_{\rm common}
=h_0\left[
\dot S_{\rm fixed}
+\operatorname{diag}\left(0,\frac{93}{4}\right)S_Y
\right],
\]

where

\[
h_0=\frac{32}{31}e^{i\omega(64+4\log32)}.
\]

Until that correlated moving-phase checkpoint is independently certified,
analytic \(K_+=0\) is withheld. No \(T_+\), Stokes, scattering, or flux
assembly is attempted.

CLOSE-OUT: SHORTFALL — exact nonstatic outgoing phase derivative identified; analytic K_plus requires a reissued moving-phase correlated checkpoint.

EVIDENCE: `black_hole_programme/phase3/axial_partial_jet_outgoing_kplus_moving_phase_gate_v1/certificate.json`

MISSING-DEP: outgoing moving-phase correlated checkpoint at r=31 with the exact componentwise diag(0,93/4) tangent corrections
