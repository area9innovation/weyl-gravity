# Transverse Nariai PBW curvature-jet gate

The transverse Kantowski--Sachs tangent changes the Levi--Civita connection
and the normal-tractor curvature.  At the normalized point the fixed-frame
connection-difference tensor is nonzero, while the moving coframe has three
nonzero boost-connection variations.  More decisively,

\[
(\nabla_0\,\delta C)_{0202}=-\sqrt2.
\]

Thus the tangent is not a parallel-curvature perturbation.  The existing
`FibrePBW` backend was designed for locally symmetric backgrounds and omits
Leibniz terms in which outer derivatives hit the varied curvature.

As a diagnostic, freezing the curvature variation at the point gives exact
first responses with `2` BGG-0,
`21` BGG-1,
`126` parent-middle, and
`130` compressed-middle
coefficients.  Its varied normal-tractor square agrees exactly with the
independent curvature-incidence reconstruction.  Those middle coefficients
are deliberately **not** promoted: the nonzero curvature jet proves that the
parallel substitution omits required terms.

The next implementation gate is a jet-aware PBW normal form carrying
covariant derivatives of curvature through the Leibniz rule, followed by the
middle/Schur and full rank-310 SDR variations.  This is a scoped backend
obstruction, not a no-go theorem for transverse causal transfer.
