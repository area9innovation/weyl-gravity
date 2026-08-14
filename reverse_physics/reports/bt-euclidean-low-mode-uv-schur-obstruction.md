# BT lowest-mode/ultraviolet Schur-complement obstruction

**Date:** 2026-08-14

**Certificate:** REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1

**Dependency:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

**Lifecycle:** OBSTRUCTION_PROVED

## Result

The failure of global bilaplacian strong convexity cannot be avoided merely by
asking for curvature in one lowest Fourier mode. The previously found
degenerating direction contains a fixed nonzero lowest-mode component mixed
with the highest alternating mode. Exact elimination of that ultraviolet
direction makes the effective lowest-mode Hessian tend to zero.

This blocks a field-independent, pointwise Schur-complement or anisotropic
Brascamp--Lieb proof of the interacting covariance estimate. It does not
disprove the covariance estimate itself. This family alone leaves an
action-weighted or annealed estimate open. The exact successor
REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1 shows that
its quarter-power scaling is not the global threshold: every exponent below
one half is obstructed by a second family.

## Exact mode decomposition

Work in the spatially constant sector of the \(6^4\) lattice and set
\(x=2^a\), with center

\[
 k(a)=(-a,0,0,-a,a,a).
\]

Choose the lowest and highest time-circle modes

\[
 h=(2,1,-1,-2,-1,1),\qquad
 g=(1,-1,1,-1,1,-1).
\]

They are orthogonal and obey

\[
 (-\Delta_6)h=h,\qquad (-\Delta_6)g=4g,\qquad
 \|h\|^2=12,\quad\|g\|^2=6.
\]

The degenerating direction from the global-convexity obstruction is exactly

\[
 v=(-1,-1,1,1,1,-1)=-\frac23h+\frac13g.
\]

In particular, \(v\cdot h=-8\) and \(\|P_hv\|^2=16/3\). Its action Hessian is

\[
 D_v^2A=\frac{8(x+1)}{x^2}
\]

per spatial site. Therefore

\[
 \frac{D_v^2A}{\|P_hv\|^2}
 =\frac32\frac{x+1}{x^2}\longrightarrow0.
\]

No positive field-independent Hessian lower bound can control even the
projection onto this single lowest mode.

## Exact two-mode Schur complement

Let \(H_{hh},H_{hg},H_{gg}\) denote the mixed action Hessians in the basis
\((h,g)\). Direct differentiation gives the Laurent polynomials

\[
\begin{aligned}
H_{hh}={}&4x^4+8x^3-4x-2x^{-1}+2x^{-2}+4x^{-4},\\
H_{hg}={}&8x^4+16x^3-8x-16x^{-1}-8x^{-2}+8x^{-4},\\
H_{gg}={}&16x^4+32x^3-16x+16x^{-1}+32x^{-2}+16x^{-4}.
\end{aligned}
\]

The effective lowest-mode curvature after optimizing the alternating
coordinate is

\[
 \kappa(x)=H_{hh}-\frac{H_{hg}^2}{H_{gg}}
          =\frac{\det H}{H_{gg}}.
\]

The determinant is

\[
 \det H=288\left(
 x^3+3x^2+2x-1-x^{-1}-x^{-2}-x^{-3}
 +x^{-5}+x^{-6}\right).
\]

For \(x\geq2\), every denominator is positive and elementary grouping gives

\[
 0<\kappa(x)\leq\frac{72}{x},\qquad
 \lim_{x\to\infty}x\kappa(x)=18.
\]

All entries and \(\kappa\) acquire the common spatial factor \(216\) on the
full lattice, so the curvature ratios are unchanged.

## The action cost of the bad curvature

At the same center, the action per spatial site is

\[
 A(x)=x^4+2x^3-3x^2-4x+6
      -2x^{-1}-x^{-2}+x^{-4}.
\]

Thus

\[
 \frac{A(x)}{x^4}\longrightarrow1,\qquad
 \kappa(x)A(x)^{1/4}\longrightarrow18.
\]

The inverse effective curvature grows only like the fourth root of the action
along this exact family. Since the Gibbs density contains \(e^{-A}\), this
family does not obstruct an averaged inverse-curvature estimate. The exponent
is family-specific, however. The successor period-three family has
\(\kappa\sim36/x\) and \(A\sim4x^2\), so
\(\kappa A^{1/4}\to0\) and the first exponent it does not obstruct is one
half.

## Meaning for the continuum gate

Three pointwise routes are now closed:

1. global bilaplacian strong convexity;
2. a nonnegative pointwise Schwinger--Dyson mode remainder;
3. field-independent curvature after projecting to, and Schur-complementing
   around, a lowest mode.

The next falsifiable target is the volume-normalized half-action-density lower
bound identified by the successor certificate, followed by an annealed Gibbs
estimate of that weight. A weaker positive radial virial constant or a direct
normalized marginal estimate remains the alternative.

This result does not establish or refute the actual interacting \(H^{-1}\)
bound, tightness, a continuum measure, a Born rule, Krein reconstruction, or
anything LORENTZIAN-CAUSAL.

## Verification

Run sequentially:

    python3 reverse_physics/bt_euclidean_low_mode_uv_schur_obstruction.py --check
    python3 reverse_physics/verify_bt_euclidean_low_mode_uv_schur_obstruction.py
    python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_low_mode_uv_schur_obstruction
