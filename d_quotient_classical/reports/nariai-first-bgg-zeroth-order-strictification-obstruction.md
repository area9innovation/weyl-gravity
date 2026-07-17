# Nariai first-BGG zeroth-order strictification obstruction

This report supersedes certificate hash
`c4738c825fd1814962d4970e62341f0399fafb08331fe9b57bc25958b1fadbcc`,
whose producer assigned the wrong sign to the temporal Schouten component.

On unit Nariai, the Schouten tensor has orthonormal components
\((-1/6,+1/6,+1/6,+1/6)\).  The form indices carry the covector curvature
action while the middle standard-tractor slot carries its dual vector action.
With all three conventions enforced, the normal tractor exterior square is
nonzero, as it must be on this non-conformally-flat Einstein background.

We tested the complete zeroth-order correction ansatz

\[
d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K=0,
\]

where \(\Delta L_0\) is an arbitrary \(15\times4\) bundle map and
\(\Delta L_1\) is an arbitrary \(60\times9\) bundle map.  For each one-form
row, the three derivative axes transverse to its form slot have coefficient
rank `9` and uniquely determine that row of
\(\Delta L_1\).  The remaining axis then determines a candidate row of
\(\Delta L_0\).

The derivative equations are mutually compatible across all four form slots:
they fix \(\Delta L_0=0\) and a rank-`9` correction
\(\Delta L_1\).  But the remaining algebraic coefficient has rank
`4` and
`12` nonzero entries.  A normalized
witness is

\[
\frac32\bigl(d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K\bigr)_{4,1}=1.
\]

Both harmonic projection defects remain rank zero, so the failure is not a
normalization artifact.  Thus zeroth-order corrections cannot strictify this
first square with the conformal-Killing operator fixed.  Genuinely
derivative-dependent corrections and homotopy-coherent curved transfer remain
open; this is not a no-go theorem for the Nariai Yang--Mills detour
compression or its Green theory.
