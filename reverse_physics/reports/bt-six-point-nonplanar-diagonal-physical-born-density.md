# BT six-point nonplanar diagonal physical Born density

Certificate:
`REVERSE_PHYSICS_BT_SIX_POINT_NONPLANAR_DIAGONAL_PHYSICAL_BORN_DENSITY_V1`

Lifecycle: `COEFFICIENT_COMPUTED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The positive six-point BT local Born density is not a consequence of planar
kinematics.  It remains strictly positive on an exact continuous family where
the outgoing three-particle plane is generically different from the incoming
plane.

Begin with the certified physical incoming null triple.  Rotate the outgoing
triple in the original plane with stereographic parameter \(t\), then rotate
it out of that plane about an independent spatial axis with stereographic
parameter

\[
 u=\frac t2.
\]

Both rotations are rational.  The resulting six all-incoming momenta remain
exactly null and conserve four-momentum.  For generic \(t\), the outgoing
momenta have nonzero \(z\)-components while the incoming momenta lie in
\(z=0\), so this is genuinely nonplanar.

The complete 220-tree amplitude in the 64-slot external-mass jet again begins
at mass degree three.  Its twenty degree-three coefficients form ten equal
complement pairs.  Consequently the six-delta-prime coefficient is twice a
sum of ten rational squares.  Their numerator gcd is one and all ten
propagator-pole factors have even multiplicity, proving strict positivity for
every regular real \(t\).

This is a theorem on a nonplanar one-parameter diagonal, not yet on the full
two-independent-parameter family and not an integrated probability.

## Exact nonplanar construction

The first rotation has

\[
 c_t=\frac{1-t^2}{1+t^2},\qquad s_t=\frac{2t}{1+t^2}.
\]

For an intermediate spatial vector \((x,y,0)\), the tilt uses

\[
 c_u=\frac{1-u^2}{1+u^2},\qquad s_u=\frac{2u}{1+u^2},
 \qquad u=\frac t2,
\]

and sends it to \((x,c_uy,s_uy)\).  Applied uniformly to the outgoing triple,
this preserves every energy, nullness, and total spatial momentum.  The
producer records all six adjacent and three complementary-triple invariants
as exact rational functions of \(t\).

## Ten-square mechanism

In

\[
 J_6=\mathbb Q(t)[x_0,\ldots,x_5]/(x_i^2),
\]

the exact amplitude has 42 nonzero terms of degrees \(3,4,5,6\).  Its middle
part is

\[
 \mathcal M_6^{[3]}=\sum_{|S|=3}c_S(t)x_S,
\]

and the complete tree sum obeys

\[
 c_S(t)=c_{S^c}(t)
\]

for all ten unordered partitions.  Each of the \(V_4^2\), \(V_3^2V_4\), and
\(V_3^4\) sectors has a nonzero complement-antisymmetric part separately.
Their cancellation depends on the complete BT perfect-square relative
coupling.

It follows exactly that

\[
 [x_0\cdots x_5]|\mathcal M_6|^2
 =2\sum_{S<S^c}c_S(t)^2.
\]

The ten reduced numerator polynomials have gcd one, so their common zero set
is empty even over the complex numbers.  The denominator factors as ten
polynomials, each squared.  Therefore the coefficient is strictly positive
on every real point where the tree amplitude is regular.

As in the planar predecessor, the amplitude starts at degree three, so its
square starts at the full six-mass degree.  Derivatives of a regular analytic
local phase-space weight cannot enter the top coefficient.  A positive
undifferentiated interior weight preserves its sign.

## What changed

The progression is now:

1. The correlated two-profile crossed quotient is negative.
2. The complete planar local Born density is positive.
3. The complete nonplanar diagonal local Born density is also positive.

Thus neither the hierarchy limit nor coplanarity explains the positive
completion.  The relevant structure is complement self-duality of the full
middle-degree external-mass jet after all tree topologies are combined.

## Boundary and next gate

This certificate does not establish:

- positivity for two independent nonplanar rotation parameters or the full
  six-body phase space;
- an integrated or normalized probability;
- regulation or cancellation of internal propagator poles;
- separately positive reversed-history channels;
- a Moller, LSZ, or \(S\) operator;
- Eq. (19), beyond-tree positivity, or KLN cancellation;
- a Weyl-gravity/BRST lift or anything `LORENTZIAN-CAUSAL`;
- a new physical dimension or literature priority.

The direct \(\mathbb Q(t,u)\) calculation was safely interrupted after 310 s
because rational-function cancellation was too slow, not because of memory:
peak RSS was 171,696 KB.  Five independent exact \((t,u)\) fixtures all obeyed
the complement identities and positive square sum.  The next proof should use
degree-bounded modular evaluation and interpolation rather than repeat that
backend.

## Verification receipts

All symbolic jobs ran sequentially under the 500 MB memory cap.

| Tier | Check | Result | Elapsed / peak RSS |
|---|---|---:|---:|
| 0 | Python compile, JSON parse, schema parse, scoped diff check | PASS | under 1 s |
| 1 | cached exact continuum producer, 22 checks | PASS | 71.03 s / 116,972 KB |
| 1 fast | two independent exact nonplanar fixtures | PASS | 0.66 s / 73,252 KB |
| 1 | 10-test mutation suite on fast independent rail | PASS | 4.904 s |
| 2 | independent explicit enumeration of all 220 symbolic tree values, 16 checks | PASS | 188.47 s / 184,924 KB |
| 2 consumer | planar predecessor independent verifier after shared helper extension | PASS | 40.98 s / 124,356 KB |
| 1 | Paper V, two sequential builds | PASS; no new overfull box | 0.48 / 0.50 s; 50,584 KB max |
| 1 | Paper VI, two sequential builds | PASS; no warning or overfull box | 0.49 / 0.49 s; 50,928 KB max |
| planning | Science Forge import, 1,449 nodes, zero invalid items and zero malformed events | PASS | 15.26 s / 279,488 KB |
| 3 | not run: no freeze, shared-core change, lifecycle promotion, or release | NOT APPLICABLE | -- |

After adding the fast rational-fixture interface, the first affected-chain
replay failed immediately because the exact rational domain and the rational-
function field require different coercion constructors.  That attempt is not
counted as a pass.  The domain-specific coercion was corrected, the fast rail
replayed, and the full symbolic explicit-tree rail then passed as recorded.
