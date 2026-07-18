# Transverse coefficient-jet PBW requirements

The replacement PBW backend retains ordered covariant jets of every varied
normal-form coefficient.  On an independently evaluated scalar differential
operator fixture, both parenthesizations agree through coefficient-jet order
three, and every output coefficient agrees with direct symbolic
differentiation.  Point-only inputs now fail closed rather than silently
setting positive-order coefficient jets to zero.

For the Nariai triple `M_parent o L1_corrected o (K p0)`, the existing exact
curvature tower through order
`3` is sufficient.  The actual
remaining input is smaller and more precise: four positive-order coefficient
jet tables for `L0_corrected`, and fourteen for `L1_corrected`.  The current
export contains only their values at the normalization point
(`2`
and `22`
nonzero coefficients respectively).

Those values do not determine the missing jets: `a` and `a+x` agree at the
point but have normalized first-derivative difference one.  Consequently the
associative Nariai replay remains open.  Its next input must be derived from a
full perturbed covariant HPL/BGG splitting or an equivalent natural operator
formula; interpolating the point matrices is not admissible.
