# Natural six-block binding and rank-310 KS causal transfer

Let

\[
g_\epsilon=-dt^2+a_\epsilon(t)^2d\chi^2
 +b_\epsilon(t)^2d\Omega_2^2
\]

be a member of the certified common-slab Kantowski--Sachs Einstein family.
Thus \(\operatorname{Ric}(g_\epsilon)=g_\epsilon\), both scale factors are
positive, and the slab is globally hyperbolic.

## Fixed bundle and pairing

Write \(a_0=\cosh t\).  On covectors, define

\[
U_\epsilon(dt)=dt,
\quad
U_\epsilon(d\chi)=\frac{a_0}{a_\epsilon}d\chi,
\quad
U_\epsilon(\alpha)=\frac1{b_\epsilon}\alpha,
\quad \alpha\in T^*S^2.
\]

This is a global pointwise isometry from the \(g_\epsilon\) covector fibre to
the \(g_0\) covector fibre.  Tensor, form and tractor slots use the induced
maps.  Multiplication by

\[
\rho_\epsilon=
\left(\frac{a_\epsilon b_\epsilon^2}{a_0}\right)^{1/2}
\]

identifies the density pairings.  Hence all four cyclic fibre pairings become
the fixed unit-Nariai pairings.  Both \(U_\epsilon\) and its inverse are
pointwise and support preserving on every common slab.

## Six geometric blocks

In this fixed paired bundle, let \(L_{0,\epsilon}\) and
\(L_{1,\epsilon}\) be the natural normal-BGG splitting operators, let
\(M_\epsilon\) be the normal-tractor Yang--Mills detour middle, let
\(B_\epsilon\) be the action-normalized Bach Hessian, and let
\(K_\epsilon\) be the conformal-Killing generator.  The pointwise Kostant
maps \(p_0,J_0,r_0\) are fixed.  Define

\[
g_\epsilon=r_0(1-L_{0,\epsilon}p_0),
\qquad
k_\epsilon=K_\epsilon p_0.
\]

Relative to the unit-Nariai split differential, the complete finite
difference therefore occupies exactly

\[
\Delta g,\quad \Delta k,\quad \Delta M,\quad \Delta B,
\quad \Delta g^\sharp,\quad \Delta k^\sharp.
\]

These are not fitted coefficients.  They are the differences of the displayed
natural finite-order operators after the explicit bundle/density transport.
Consequently they determine every coordinate coefficient on demand.

This is coefficient-complete in the invariant sense: the six operators and
their domains, codomains, differential orders and adjoint partners are fixed.
It is not a claim that a component-expanded PBW table has been serialized.
The latter is useful as a regression artifact, but it is not additional
mathematical data.

The BGG splitting and Yang--Mills detour identities give

\[
p_0L_{0,\epsilon}=1,
\quad g_\epsilon J_0=1,
\quad J_0g_\epsilon=1-L_{0,\epsilon}p_0,
\]

\[
M_\epsilon L_{1,\epsilon}=\Phi_\epsilon,
\qquad
B_\epsilon k_\epsilon=0,
\]

and their pairing adjoints.  Since every Einstein metric is Bach-flat, the
normal tractor connection is Yang--Mills and these identities hold throughout
the common slab family.  They are precisely the relations assumed by the
certified six-block finite HPL theorem.

The split presentation is related to the original parent/metric graph by the
finite triangular differential automorphism

\[
 x=a-d_{{\rm aut},\epsilon}J_0s-L_{1,\epsilon}h,
 \qquad
 y=\lambda+c\Phi_\epsilon h.
\]

Its inverse changes the two signs, and its cotangent transform is the forced
formal-adjoint inverse.  Thus the transformation is BV canonical and
support-local.  In particular, proving the SDR and Green identities in split
coordinates proves them on every original field, equation, antifield and
identity row by conjugation; the curved automorphism differential and the
curved first BGG splitting have not been discarded.

## Cyclic SDR and causal transfer

Let \(\Delta=Q_{310,\epsilon}-Q_{310,0}\).  The block incidence gives

\[
(H_0\Delta)^2=(\Delta H_0)^2=0.
\]

Therefore

\[
I_\epsilon=(1-H_0\Delta)I_0,
\quad
p_\epsilon=p_0(1-\Delta H_0),
\quad
H_\epsilon=H_0-H_0\Delta H_0
\]

is a finite-order support-local cyclic SDR.  The transferred metric
differential retains the two mandatory quadratic cross terms from the
six-block theorem and is the natural four-row Bach complex at
\(g_\epsilon\).

The Einstein metric endpoint theorem supplies advanced and retarded
homotopies \(\Lambda_{{\rm met},\epsilon,\pm}\).  Set

\[
\Lambda_{310,\epsilon,\pm}
=H_\epsilon
 +I_\epsilon\Lambda_{{\rm met},\epsilon,\pm}p_\epsilon.
\]

The SDR identities imply

\[
Q_{310,\epsilon}\Lambda_{310,\epsilon,\pm}
+\Lambda_{310,\epsilon,\pm}Q_{310,\epsilon}=1.
\]

All additional maps are support local, so the homotopies retain the same
advanced or retarded support.  Cyclicity gives complementary-degree adjoint
reversal.

This is a common-slab theorem.  It does not extend a nonzero KS member across
its finite-time curvature singularity, does not cover non-Einstein Bach-flat
metric endpoints, and does not supply Hadamard or quantum data.
