# BT center-hypersurface Gaussian envelope

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_CENTER_HYPERSURFACE_GAUSSIAN_ENVELOPE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle:
`EXACT_CENTER_REDUCTION_AND_POINTWISE_GAUSSIAN_ENVELOPE_PROVED_NORMALIZED_ENTROPY_OPEN`

## Result

The lowest-mode center change of variables has no hidden field-dependent
Jacobian. Combining that exact fact with the two preceding BT theorems gives
a pointwise estimate on the fully integrated weight of every lowest-mode
fiber.

Let

\[
 h_x=\cos(2\pi x_\mu/L+\alpha),\qquad
 E=h^\perp,\qquad
 V_\eta(t)=S_\lambda(\eta+t h).
\]

The all-background curvature certificate proves

\[
 V_\eta''(t)\geq \kappa_L,
 \qquad \kappa_L={2\over9}N\omega_L^2.
\]

Thus every fiber has one center (m(\eta)), defined by
(V_\eta'(m)=0). If

\[
 Z_\eta=\int_{\mathbb R}e^{-V_\eta(t)}\,dt,
\]

then the new bound is

\[
 \boxed{
 Z_\eta\leq
 3\sqrt{\pi\over N\omega_L^2}\,
 \exp\left[-{N\omega_L^2\over12}m(\eta)^2\right].}
\]

This is an actual BT estimate, uniform in the orthogonal background, lattice
volume, nonzero coupling, axis, and real phase. It is stronger than a
pointwise action bound because the selected one-dimensional fiber has already
been integrated exactly up to the certified Gaussian upper bound.

It is not yet a normalized Gibbs-moment theorem. The remaining issue is the
weighted number of orthogonal backgrounds having a given center. An exact
positive Gaussian-tube family below shows that this transverse entropy can
cancel a Gaussian center cost even when all the general properties currently
available for BT are retained. The next proof must therefore use more of the
specific BT cross-section geometry.

## Exact center chart and Jacobian

Define the center hypersurface

\[
 \Sigma=\{\phi:D_hS_\lambda(\phi)=0\},\qquad
 \chi(\eta)=\eta+m(\eta)h.
\]

Strict fiber curvature makes (m(\eta)) unique. Analyticity and the implicit
function theorem give

\[
 Dm(\eta)[k]=-
 {\operatorname{Hess}S_\lambda(\chi)[h,k]
  \over
  \operatorname{Hess}S_\lambda(\chi)[h,h]}.
\]

Every line parallel to (h) therefore meets (Sigma) exactly once, so
projection from (Sigma) to (E) is an analytic bijection. In orthogonal
coordinates, the global map

\[
 F(\eta,s)=\eta+(m(\eta)+s)h
\]

has derivative matrix

\[
 \begin{pmatrix}I&0\\ Dm&1\end{pmatrix}.
\]

Its determinant is exactly one. The ambient measure is simply

\[
 d\phi=\lVert h\rVert\,d\eta\,ds,
\]

where the factor (lVert h\rVert) is constant, not a function of the field.

The same cancellation can be written intrinsically on (Sigma). If
(H=\operatorname{Hess}S_\lambda(\chi)), the graph-area and projection
formulas give

\[
 d\eta={H[h,h]\over\lVert h\rVert\lVert Hh\rVert}
          \,d\mathcal H_\Sigma,
 \qquad
 d\phi={H[h,h]\over\lVert Hh\rVert}
          \,d\mathcal H_\Sigma\,ds.
\]

Thus a large tilt of the center graph cannot by itself create extra ambient
volume: graph area and projection angle cancel exactly.

## Derivation of the Gaussian envelope

Recenter the fiber:

\[
 Z_\eta=e^{-S_\lambda(\chi)}I(\chi),\qquad
 I(\chi)=\int_{\mathbb R}
 e^{-[S_\lambda(\chi+s h)-S_\lambda(\chi)]}\,ds.
\]

The curvature theorem gives

\[
 I(\chi)\leq\sqrt{2\pi\over\kappa_L}
 =3\sqrt{\pi\over N\omega_L^2}.
\]

Because (eta\perp h), the real phase component of the lowest Fourier
coefficient of (chi=\eta+m h) is (m/2). The axial-slice coercivity theorem
therefore gives

\[
 S_\lambda(\chi)
 \geq {N\omega_L^2\over3}|\widehat\chi(e_\mu)|^2
 \geq {N\omega_L^2\over12}m^2.
\]

Multiplying these two inequalities proves the boxed estimate.

## Why pointwise decay is not normalization

The normalized center law is proportional to (Z_\eta d\eta). A Gaussian
upper bound on each value of (Z_\eta) says nothing by itself about how much
(eta)-volume maps to a given value of (m).

At regular values, the missing pushforward can be displayed by the coarea
density

\[
 g_L(u)=\int_{m^{-1}(u)}
 {I(\chi)e^{-S_\lambda(\chi)}\over|\nabla_E m|}
 \,d\mathcal H.
\]

At singular values the same object must be understood as the pushforward
measure rather than through this density formula. The target is a uniform
bound on its normalized second moment, or an actual BT sequence on which that
moment diverges.

## Exact positive Gaussian-tube countermodel

For an integer (R>1), put (d=R^2) and consider

\[
 V_R(t,s,z,w)=
 (t-s)^2+t^2
 +{1\over2}e^{-(1-R^{-2})s^2}z^2
 +{1\over2}\sum_{j=1}^{d}w_j^2.
\]

This is a positive, even potential with a unique critical point and zero at
the origin. It has the global pointwise cost (V_R\geq t^2). Completing the
square gives

\[
 (t-s)^2+t^2=2(t-s/2)^2+s^2/2.
\]

Every (t)-fiber therefore has curvature four, center (m=s/2), constant
Gaussian width (sqrt{\pi/2}), and center cost at least (2m^2). Its center
change of variables is the same kind of unit-determinant shear.

Nevertheless, integrating (z) contributes

\[
 \sqrt{2\pi}\,e^{(1-R^{-2})s^2/2},
\]

which cancels all but (e^{-s^2/(2R^2)}) of the center decay. Hence

\[
 \operatorname{Var}(m)={R^2\over4},
 \qquad
 \operatorname{Var}(t)={R^2+1\over4}.
\]

Both diverge as (R\) grows. With the (R^2) spectator variables,

\[
 \mathbb E[V_R]=R^2+1
\]

in ambient dimension (R^2+3), so even extensive mean action does not fix
the logical gap.

The exact (R=5) fixture has (25) spectators, narrowing exponent (24/25),
center variance (25/4), total (t)-variance (13/2), mean action (26),
and ambient dimension (28). On the center graph (t=s/2), the graph-area
factor squared is (5/4). The Hessian sends the (t)-direction to
((4,-2,0,\ldots)), so its intrinsic projection factor squared is (4/5).
Their product is exactly one, independently verifying the Jacobian
cancellation in this nontrivial tilted example.

This family is deliberately not called a BT counterexample. It is not the BT
action, not a local lattice model, and not evidence that the actual BT moment
diverges. It proves only that no theorem using the listed general ingredients
alone can close the normalized moment.

## Meaning for the programme

One proposed barrier has been removed: the center hypersurface itself does
not carry a dangerous coordinate Jacobian. The finite-volume BT measure now
has a clean pointwise Gaussian envelope after the selected mode is integrated.

The surviving barrier is sharper than before. We need a BT-specific bound on
the normalized cross-section entropy, preferably in the exact
residual-spectrahedral coordinates already certified. A successful next
checkpoint is

\[
 N\omega_L^2\,\mathbb E[m^2]\leq C
\]

uniformly in (L), or an actual BT diverging-volume sequence. Only after the
one-mode gate closes should the argument be extended over dyadic Fourier
shells to decide the interacting (H^{-1}) moment.

## Boundary

This certificate does not establish a normalized BT center or lowest-mode
moment, divergence of an actual BT moment, an interacting (H^{-1}) theorem,
tightness, continuum identification, a Born rule, Krein reconstruction, or
anything `LORENTZIAN-CAUSAL`. No literature-priority claim is made.

## Verification

Run sequentially under the 500 MB cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_center_hypersurface_gaussian_envelope.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_center_hypersurface_gaussian_envelope.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_center_hypersurface_gaussian_envelope

## Verification receipt

The final producer byte check passed in 0.04 seconds with peak RSS 20468 KiB.
The independent verifier passed all 15 checks in 0.10 seconds with peak RSS
30368 KiB. All 10 focused tests passed in 0.13 seconds with peak RSS 30436
KiB, including six adversarial certificate mutations. Python compilation
passed in 0.04 seconds with peak RSS 15760 KiB. Every Python command ran under
the 500 MB virtual-memory cap.

The Science Forge planning import passed with 1667 nodes, zero invalid items,
and zero malformed events in 7.37 seconds with peak RSS 201208 KiB under
`GOMEMLIMIT=300MiB` and `GOGC=50`. Tier 2 uses unchanged, content-addressed
predecessor certificates. Tier 3 was not run because the normalized moment
and continuum lifecycle states remain open. The Science Forge shadow rail was
skipped because no registered shadow input changed; that skip is not recorded
as a pass.
