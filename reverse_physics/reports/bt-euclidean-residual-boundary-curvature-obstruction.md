# BT residual-boundary curvature obstruction

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

Lifecycle: METHOD_OBSTRUCTION_PROVED

## Result

The residual spectrahedral boundary is pointwise strictly convex, but it does
not have the global positive curvature bounds needed by a standard boundary
spectral-gap route. This is already exact on the four-cycle. At the physical
coupling \(\lambda=0.4\), the Gaussian weighted mean curvature also becomes
strictly negative.

This closes one proposed proof method. It does **not** prove that the actual
normalized BT low-mode moment diverges, and it does not obstruct every
Poincare, transport, or intrinsic boundary inequality.

## Boundary geometry

Let

\[
 K(r)=-\Delta+\operatorname{diag}(r),\qquad K(r)\Omega=0,\qquad
 \Omega_x>0,
\]

on the principal smooth boundary of the convex spectrahedron
\(\mathcal C_G=\{r:K(r)\succeq0\}\). Normalize
\(u=\Omega/\|\Omega\|_2\). The lowest eigenvalue
\(F(r)=\lambda_{\min}(K(r))\) is simple on this stratum, and

\[
 \nabla F=u^2.
\]

The spectrahedron lies on the \(F\geq0\) side, so its outward unit normal is

\[
                 n_{\rm out}=-\frac{\Omega^2}{\|\Omega^2\|_2}.
\]

Consequently

\[
 T_r\partial\mathcal C_G
 =\left\{h:\sum_x\Omega_x^2h_x=0\right\}.
\]

For a tangent direction \(h\), simple-eigenvalue perturbation gives

\[
 D^2F(r)[h,h]
 =-2\left\langle \operatorname{diag}(h)u,
 K(r)^+\operatorname{diag}(h)u\right\rangle.
\]

The sign from the outward normal therefore yields

\[
 \boxed{
 \mathrm{II}_r(h,h)=\frac{2}{\|\Omega^2\|_2}
 \left\langle\operatorname{diag}(h)\Omega,
 K(r)^+\operatorname{diag}(h)\Omega\right\rangle.}
\]

For nonzero tangent \(h\), the vector
\(\operatorname{diag}(h)\Omega\) is nonzero and orthogonal to \(\Omega\).
The pseudoinverse \(K^+\) is positive definite on that orthogonal complement.
Thus the principal boundary is strictly convex at each finite point.

If \(P_T\) denotes the Euclidean projector onto the tangent space, its mean
curvature is

\[
 H(r)=\frac{2}{\|\Omega^2\|_2}\operatorname{tr}\!\left[
 P_T\operatorname{diag}(\Omega)K(r)^+\operatorname{diag}(\Omega)P_T
 \right].
\]

For the Gaussian surface reference density
\(\exp[-\|r\|_2^2/(2\lambda^2)]\), the weighted mean curvature in the same
orientation is

\[
 H_\lambda=H-\frac{\langle r,n_{\rm out}\rangle}{\lambda^2},\qquad
 \langle r,n_{\rm out}\rangle
 =\frac{\Omega^T(-\Delta)\Omega}{\|\Omega^2\|_2}.
\]

These formulas concern the Gaussian surface reference measure. The actual BT
pushforward has the additional reciprocal tree Jacobian described by the
predecessor certificate.

## Exact four-cycle family

On \(C_4\), take the geometric-mean-one family

\[
                     \Omega(q)=(q,1,1,q^{-1}),\qquad q>0.
\]

Its exact residual is

\[
 r(q)=\left(-\frac{(q-1)(2q+1)}{q^2},\ q-1,
            -\frac{q-1}{q},\ (q-1)(q+2)\right).
\]

Choose

\[
                         h(q)=(0,0,1,-q^2).
\]

Since \(\langle\Omega(q)^2,h(q)\rangle=0\), this is tangent. Exact solution
of the bordered linear system for \(K(q)^+\) gives

\[
 \left\langle\operatorname{diag}(h)\Omega,
 K(q)^+\operatorname{diag}(h)\Omega\right\rangle
 =\frac{q(2q+1)}{(q+1)^2}.
\]

Also

\[
 \|\Omega(q)^2\|_2=\frac{q^4+1}{q^2},\qquad
 \|h(q)\|_2^2=q^4+1.
\]

The normal curvature in this trial direction is therefore

\[
 \kappa_{\rm trial}(q)
 =\frac{\mathrm{II}(h,h)}{\|h\|_2^2}
 =\frac{2q^3(2q+1)}{(q+1)^2(q^4+1)^2}.
\]

It obeys

\[
 \lim_{q\to\infty}\kappa_{\rm trial}(q)=0,\qquad
 \lim_{q\to\infty}q^6\kappa_{\rm trial}(q)=4.
\]

The smallest principal curvature is no greater than this trial value. Hence
there is no positive field-uniform lower bound on the second fundamental form,
even for the fixed graph \(C_4\). Pointwise strict convexity and uniform
strict convexity are genuinely different statements here.

## Weighted mean-curvature sign at lambda 0.4

The same bordered inverse gives

\[
 H(q)=\frac{2q^2P_{10}(q)}{(q+1)^2(q^4+1)^3},
\]

where

\[
 P_{10}(q)=q^{10}+3q^9+3q^8+2q^6+2q^5+2q^4+3q^2+3q+1.
\]

The normal Gaussian-drift term is

\[
 \langle r,n_{\rm out}\rangle
 =\frac{2(q-1)^2(q^2+q+1)}{q^4+1}.
\]

At \(\lambda=2/5\), evaluation at the rational point \(q=2\) gives

\[
 H=\frac{28568}{44217},\qquad
 \langle r,n_{\rm out}\rangle=\frac{14}{17},\qquad
 H_{2/5}=-\frac{398039}{88434}<0.
\]

The corresponding exact trial curvature is

\[
                        \kappa_{\rm trial}(2)=\frac{80}{2601}.
\]

In fact,

\[
                         \lim_{q\to\infty}H_{2/5}(q)=-\frac{25}{2}.
\]

These rational identities are not inferred from a numerical fit. After
clearing their displayed nonzero denominators, the relevant numerator degree
is at most fourteen. The independent verifier reconstructs the bordered
inverse at the fifteen exact rational points \(q=1,\ldots,15\); agreement
there certifies the cleared polynomial identity. The limits then follow from
the leading degrees and coefficients.

Thus global positivity of the Gaussian weighted mean curvature also fails.

## Literature disposition

Kolesnikov and Milman's
[Gaussian boundary theorem](https://arxiv.org/abs/1601.02925) is a
curvature-weighted Poincare-type inequality, not an unrestricted
dimension-free variance bound for arbitrary boundary observables. Their
[weighted-boundary spectral-gap results](https://arxiv.org/abs/1711.08825)
include a theorem assuming both
\(\mathrm{II}\geq\sigma g\) and positive weighted mean curvature
\(H_\mu\geq\xi\).

The exact \(C_4\) family violates both global hypotheses relevant to that
route. Therefore those results cannot simply be inserted after the residual
pushforward to obtain the missing BT low-mode estimate. Moreover, the actual
BT surface law includes the inverse spanning-tree Jacobian, so it is not the
bare Gaussian boundary measure in the first place.

This is a method-specific obstruction. It leaves open inequalities using
variable curvature, intrinsic Bakry--Emery structure, transport, localization,
or a direct treatment of the exact normalized one-mode marginal.

## Foundations consequence

The dependency cut is now sharper:

1. The rational \(C_4\) matrices, bordered inverse, tangent witness, and
   negative weighted mean curvature are finite exact algebra.
2. Simple-eigenvalue perturbation and the second fundamental form are
   finite-dimensional analysis.
3. The desired all-volume marginal estimate remains a separate analytic
   theorem.

This is classified only as USED_BY_DISPLAYED_PROOF. No weakest-base or
reverse-mathematical equivalence has been established.

## Next gate and boundaries

Do not continue searching for a global positive-curvature spectral-gap
constant. The live route is again the exact normalized one-mode marginal:
vary the positive ground state by one multiplicative Fourier tilt and control
the Gaussian residual action and tree Jacobian together. A controlled
diverging-volume sequence for the actual marginal would be an equally valid
negative disposition. Only after a one-mode result should the calculation
move to dyadic Fourier shells.

This certificate does not establish failure of the normalized low-mode
moment, failure of the interacting \(H^{-1}\) estimate, tightness, a continuum
measure, a Born rule, a Krein reconstruction, or anything
LORENTZIAN-CAUSAL.

## Verification

Run sequentially:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_boundary_curvature_obstruction.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_boundary_curvature_obstruction.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_boundary_curvature_obstruction
