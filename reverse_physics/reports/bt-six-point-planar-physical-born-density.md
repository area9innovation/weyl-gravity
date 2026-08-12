# BT six-point planar physical Born density

Certificate:
`REVERSE_PHYSICS_BT_SIX_POINT_PLANAR_PHYSICAL_BORN_DENSITY_V1`

Lifecycle: `COEFFICIENT_COMPUTED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete BT six-point tree amplitude has a strictly positive local
six-delta-prime Born density on an exact continuous nonforward physical
\(3\to3\) family, away from ordinary internal-propagator poles.

This is the first positive physical result after leaving the correlated
crossed cylinder.  It does not contradict the negative crossed quotient on
that cylinder.  The quotient keeps only a two-profile boundary block.  The
complete physical external-mass projector instead retains twenty middle-
degree amplitude coefficients.  On the family below they form ten equal
complement pairs, so the complete six-derivative coefficient is twice a sum
of ten squares.

The result is a local phase-space density on a one-parameter planar slice.  It
is not yet an integral over the complete nonplanar six-body phase space and is
not a proof of Bateman--Turok Eq. (19).

## Exact physical family

Use signature \((+---)\).  Three future-null incoming momenta are

\[
 p_0=(6/5,6/5,0,0),\qquad
 p_1=(1,-3/5,4/5,0),\qquad
 p_2=(1,-3/5,-4/5,0).
\]

They have total momentum \((16/5,0,0,0)\).  Rotate all three spatial
directions in their plane by

\[
 c(t)=\frac{1-t^2}{1+t^2},\qquad
 s(t)=\frac{2t}{1+t^2},
\]

and call the resulting future-null vectors \(q_3,q_4,q_5\).  The all-incoming
six-tuple

\[
 (p_0,p_1,p_2,-q_3,-q_4,-q_5)
\]

is exactly massless and conserves four-momentum for every real \(t\).  It is a
continuous physical scattering family, not a formal invariant fixture.  The
producer reconstructs its six adjacent and three complementary-triple
invariants as exact rational functions of \(t\).

## Complete external-mass jet

Let \(x_i=m_i^2\) be the six independent BT external mass-square variables and
work in

\[
 J_6=\mathbb Q(t)[x_0,\ldots,x_5]/(x_0^2,\ldots,x_5^2).
\]

A cached subset recursion evaluates all 220 trees:

\[
 10\,V_4^2+105\,V_3^2V_4+105\,V_3^4.
\]

The resulting amplitude has 42 nonzero square-free slots, of degrees
\(3,4,5,6\).  In particular it has no term below degree three.  Write its
middle part as

\[
 \mathcal M_6^{[3]}=\sum_{|S|=3}c_S(t)x_S.
\]

For all ten unordered three--three partitions,

\[
 c_S(t)=c_{S^c}(t).
\]

This equality is not imposed and is not true separately in any one of the
three topology sectors.  Each topology has a nonzero complement-antisymmetric
part.  The three parts cancel only with the complete perfect-square relative
coupling.  The identity is therefore dynamical information from the full BT
tree sum, not a generic property of the square-free algebra.

## Positive six-derivative coefficient

Because the amplitude starts at degree three, the top coefficient of its
square receives only complementary degree-three products:

\[
 [x_0x_1x_2x_3x_4x_5]|\mathcal M_6|^2
 =2\sum_{S<S^c}c_S(t)c_{S^c}(t)
 =2\sum_{S<S^c}c_S(t)^2.
\]

The exact rational result is

\[
 \frac{625N(t)}{
 4718592\,t^2(3t-4)^2(3t+4)^2
 (7t-24)^2(7t+24)^2(t^2-8)^2},
\]

where

\[
\begin{split}
 N(t)={}&1031139585t^{14}-20590848176t^{12}
 +217036944448t^{10}-686772590592t^8\\
 &+258054111232t^6+2900547862528t^4\\
 &+5406222974976t^2+2087354105856.
\end{split}
\]

The expanded numerator is not used as a positivity shortcut.  Positivity
comes from the ten-square representation.  The reduced numerator polynomials
of the ten \(c_S\) have gcd one, so they have no common complex zero.  Hence
their real square sum never vanishes simultaneously.  Every displayed pole
has even multiplicity.  The coefficient is therefore strictly positive for
every real \(t\) away from

\[
 t=0,\quad t=\pm4/3,\quad t=\pm24/7,\quad t=\pm\sqrt8.
\]

These exclusions are ordinary tree propagator poles; this certificate does
not regulate or integrate them.

## Why the local phase-space weight does not change the sign

BT's six external delta-prime factors give sign \((-1)^6=+1\).  Let \(K(x)\)
be a regular analytic local phase-space and detector weight.  Since
\(\mathcal M_6\) begins at mass degree three, \(|\mathcal M_6|^2\) begins at
degree six, which is already the full mask in \(J_6\).  Therefore

\[
 [x_0\cdots x_5]\,K(x)|\mathcal M_6(x)|^2
 =K(0)[x_0\cdots x_5]|\mathcal M_6(x)|^2.
\]

Mass derivatives of \(K\) cannot mix into this leading coefficient.  At a
regular interior point with \(K(0)>0\), the local generalized-Born density is
strictly positive.

This statement does not include integration over the full phase space,
detector normalization, pole regulation, or endpoint distributions.

## Meaning for the crossed barrier

The finite-hierarchy no-go remains correct on its declared correlated
boundary carrier: its coherent fixed-sharp two-profile quotient is negative.
The present calculation proves that this reduced block is not the complete
physical Born density.  Away from that singular reduction, the complete
external-mass projector recombines ten middle-degree pairs into a positive
sum.

The barrier has therefore changed form.  We no longer need an ad hoc parity to
make this planar local density positive.  We must determine whether the
complement self-duality persists on genuinely nonplanar physical kinematics
and whether the resulting density has a finite positive regulated integral.

## Claim boundary and next gate

This certificate does not establish:

- positivity on the complete nonplanar \(3\to3\) phase space;
- an integrated or normalized six-point probability;
- regulation or cancellation of the propagator poles;
- twelve separately positive reversed-history intertwiners;
- a Moller, LSZ, or \(S\) operator;
- Eq. (19), beyond-tree positivity, or KLN cancellation;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`;
- a new physical dimension or literature priority.

The next direct physical calculation is a nonplanar two-parameter family,
followed by a common regulated six-body integration if complement self-duality
survives.

## Verification receipts

All exact symbolic commands ran sequentially under a 500 MB virtual-memory
limit.

| Tier | Check | Result | Elapsed / peak RSS |
|---|---|---:|---:|
| 0 | Python compile, JSON parse, schema parse, scoped `git diff --check` | PASS | under 1 s |
| 1 | producer, 20 exact checks | PASS | 16.10 s / 80,912 KB |
| 1 | independent explicit-tree verifier, 15 checks | PASS | 38.27 s / 124,648 KB |
| 1 | 10-test mutation suite | PASS | 41.36 s / 124,712 KB |
| 1 | Paper V, two sequential `pdflatex` passes | PASS; no new overfull box | 0.48 / 0.53 s; 50,840 KB max |
| 1 | Paper VI, two sequential `pdflatex` passes | PASS; no warning or overfull box | 0.55 / 0.53 s; 50,828 KB max |
| affected planning rail | Science Forge import, 1,447 nodes, zero invalid items and zero malformed events | PASS | 14.85 s / 279,900 KB |
| 2 | predecessor hashes and direct tree/quotient interfaces | checked by producer and verifier | included above |
| 3 | not run: no freeze, lifecycle promotion, shared-core change, or release | NOT APPLICABLE | -- |

Two exploratory attempts to retain nine fully symbolic independent invariant
coordinates at once were killed by the 500 MB cap at 458,248 KB and 460,560 KB
RSS.  They are failures, not verification results.  The successful exact
physical-family calculation retains one rational continuum parameter and the
complete 64-slot mass jet; the independent rail retains all 220 trees
explicitly.
