# Adaptive chart-separation obstruction

Dependency tag: `REDUCED-MODE`.

## Midpoint-derived candidate

At the first obstruction after the nine content-addressed shared-reciprocal
substeps, the raw Taylor state is finite.  Rounding its dominant midpoint
direction to half-integers gives the determinant-one chart row

\[
m=(0,0,1,-1/2).
\]

Its midpoint denominator is nonzero, but its complete ball has modulus lower
bound zero.  The chart is therefore refused.  The finite deterministic atlas
\(\{m,e_2,e_3,e_2-e_3,e_2+e_3\}\) likewise contains no separating row.

## Sharp universal result for this enclosure

Every base-component rectangle contains zero.  Consequently the Cartesian
product enclosure contains the zero vector.  For any fixed complex row
\(u\),

\[
0=u\,0\in u(B).
\]

Thus no fixed \(GL(4,\mathbb C)\)/Möbius denominator can be certified nonzero
from the current rectangular enclosure.  This is stronger than failure of a
particular finite atlas.

A mutation that accepts a chart solely because its midpoint denominator is
nonzero is killed by the full-ball test.

The result is deliberately scoped to the current Cartesian enclosure.  A
stronger affine or Taylor-model set may retain enough correlation to exclude
the zero vector.  No successor checkpoint, \(r=4\), \(H_4\), \(T_+\), Gram,
or Stokes claim is made.
