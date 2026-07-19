# Relative charge/Koszul receiver preflight

The direct full-domain Einstein--Weyl morphism is obstructed at arity two,
but the obstruction does not justify deleting the offending linear mode.  The
relative Taub map is quadratic, so its zero locus is a derived quadratic locus,
not a linear subcomplex.

The certified unary carrier remains the support-local noncyclic mapping
cofiber.  Its six residual endpoints map identically and have zero endpoint
cone cohomology.  Five endpoints are connected product isometries,

\[
H,\quad P_x,\quad J_1,\quad J_2,\quad J_3,
\]

and define the relative moment maps

\[
\mu_{\mathrm{rel},X}(u)
=\frac12(\iota^*\Omega_{\mathrm{WM}}-\Omega_{\mathrm{EM}})
(u,\mathcal L_Xu).
\]

The sixth endpoint is constant (U(1)) reducibility.  Since
(d\lambda=0), its fundamental vector field vanishes; it is not a sixth Taub
charge.

On the standard radiative branches,

\[
w_\pm=1\pm\frac32\sqrt{2\ell(\ell+1)},\qquad
\mu_{\mathrm{rel},X}=(w_\pm-1)\mu_{\mathrm{EM},X}.
\]

The derived zero locus is represented, at this reduced-mode stage, by

\[
\mathcal O(\mathrm{Sol}_{\mathrm{std}})\otimes
\Lambda(\kappa_H,\kappa_{P_x},\kappa_{J_1},\kappa_{J_2},\kappa_{J_3}),
\qquad d_K\kappa_X=\mu_{\mathrm{rel},X}.
\]

With the repository's action-derived Taylor convention, the symmetric
polarization and charge-row bracket are

\[
B_X(u,v)=\left\langle\zeta_X,\frac12\Delta_2(u,v)\right\rangle,
\qquad
q^{\rm charge}_{2,X}(u,v)=2B_X(u,v)
=\langle\zeta_X,\Delta_2(u,v)\rangle.
\]

The exact exterior-algebra check gives (d_K^2=0) on all 32 monomials.
Because each moment map is homogeneous quadratic,
(\mu_{\mathrm{rel}}(0)=d\mu_{\mathrm{rel}}|_0=0): the full radiative
tangent survives at unary order and the Taub condition first appears at
quadratic order.

This selects the architecture but does not yet build its off-shell local BV
lift.  The next gate is the complete five-charge polarization of the exact
PBW defect, including exceptional and global rows as required, or a typed
obstruction to such a lift.  The original (f_2) remains obstructed and arity
three remains closed.
