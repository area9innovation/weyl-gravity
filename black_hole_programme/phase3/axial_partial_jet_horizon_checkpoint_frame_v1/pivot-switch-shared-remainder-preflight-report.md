# Shared-reciprocal projective preflight

Dependency tag: `REDUCED-MODE`.

## One repaired radial step

The source of truth is the corrected finite panel-30 checkpoint at

\[
\rho=\frac{95}{268435456}.
\]

The next Taylor step is finite and its \(e_2\) pivot excludes zero.  The old
eager dual normalization nevertheless forms the rectangular product \(s^2\).
That enclosure contains zero, so every eager tangent quotient becomes
non-finite.

The repaired representation computes the reciprocal once and reuses the
same node:

\[
b_i^{\rm new}=b_i\,s^{-1},\qquad
t_i^{\rm new}=(t_i-b_i^{\rm new}t_s)s^{-1}.
\]

The selected base and tangent pivots are retained exactly as \(1\) and \(0\).
All post-normalization base, tangent, amplitude, and amplitude-tangent balls
are finite.  This certifies one new radial step to panel 31,
\(\rho=3/8388608\), in a resumable shared-reciprocal dual-projective chart.

## Mutation witness and boundary

A mutation restoring the eager squared-denominator evaluation is killed:
its denominator enclosure contains zero and its normalized tangent is
non-finite.

This is one bounded representation preflight.  It does not reach the next
dyadic shell, \(r=4\), \(H_4\), \(T_+\), or the global Stokes identity.
