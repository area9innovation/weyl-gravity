# Global five-charge current replay

The local Laurent superpotential is not promoted to a global tensor.  Instead,
the invariant current comparison is globalized at the correct level.  The
Lee--Wald current is natural, while covariant integration by parts supplies a
global Green current for the global formally self-adjoint relative Hessian.
Their closed difference has vertical degree two and horizontal degree three.
The positive-contact row of the global variational bicomplex of the affine
metric/connection field bundle is exact below top horizontal degree, so a
smooth global bilinear horizontal two-form exists with

\[
\omega_{\rm LW}-\omega_{G,\rm cov}=d_HU_{\rm global}.
\]

The proof uses no polar-coordinate regularity assumption.  Choose a global
connection on the metric/connection variation bundle and integrate the global
relative Hessian covariantly by parts; this constructs a global Green form.
Formal self-adjointness makes its difference from the natural Lee--Wald form
`d_H`-closed.  Locally, the algebraic Poincare homotopy contracts every
positive-contact row below horizontal degree four.  These rows are fine
sheaves of modules over smooth jet functions, so the local contractions patch
to global exactness.  The affine fibres contribute no additional vertical
cohomology.  This proves existence of `U_global` independently of the local
Laurent representative.

Because the Cauchy surface is the closed manifold `S1_L x S2`, Stokes' theorem
removes this improvement.  The resulting integral is the polarized relative
moment-map Hessian.  The already-certified complete standard decomposition
then replays the generic radiative, physical `ell=1`, homogeneous and axial
twist blocks, with output basis `(H,P_x,J_1,J_2,J_3)` and no constant-`U(1)`
charge.

This closes the local-to-global five-charge receiver.  It does not turn the
global integration into a support-local map, repair the direct `f2`
obstruction, add target-only extra-Weyl inputs or authorize arity three.
