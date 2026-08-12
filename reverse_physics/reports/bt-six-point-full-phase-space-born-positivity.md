# BT six-point full-phase-space local Born positivity

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1`

Lifecycle: `COEFFICIENT_COMPUTED`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete leading six-external-mass BT tree density is strictly positive at
every regular point of the massless physical (3\to3) phase space where the
undifferentiated local detector weight is positive. This removes the remaining
shape and orientation restrictions of the planar, diagonal, and two-angle
certificates.

It is a local tree-density theorem. Internal channel poles are excluded, not
regulated. No phase-space integral, normalized probability, Eq. (19), loop
completion, or gravity lift follows from it.

## Universal complement formula

Let (S) be one of the ten unordered partitions of six external legs into
three and three, and let

\[
 s_A=\left(\sum_{i\in A}p_i\right)^2,
 \qquad A\sim A^c,
\]

be the ten massless three-particle channel invariants. If (c_S) denotes the
coefficient of the square-free external-mass monomial (x_S) in the complete
six-point amplitude, then

\[
 c_S=c_{S^c}=\frac14\sum_{A\ne S}\frac1{s_A}. \tag{1}
\]

This is the closed form hidden inside the earlier large rational functions.
It holds before choosing planar, nonplanar, or shape coordinates.

The quickest derivation uses the auxiliary (O(1,1)) action

\[
 S_{1,1}=\int\!d^4x\left(
 \partial\Omega\,\partial\Upsilon+
 \frac{\lambda^2}{2}\Omega^2\Upsilon^2\right).
\]

At the leading six-mass order, (x_S) selects three external (Omega) legs
and three external (Upsilon) legs through the linearized Eq. (16) external-
leg map. A six-point auxiliary tree consists of two quartic vertices joined by
one cross propagator. For a proposed (3|3) channel (A), one side contains
(k=|A\cap S|) external (Omega) legs. Its three external legs can be
completed to a (2\Omega,2\Upsilon) vertex by the one internal leg exactly
when (k=1) or (k=2). The cases (k=0,3) are the single unordered channel
(A=S\sim S^c). Thus every channel except (S) occurs once. The external-leg,
vertex, and propagator normalization gives the common factor (1/4), proving
(1). An independent direct calculation sums all 220 perfect-square trees and
reproduces (1) on six exact fixtures that vary all five physical coordinates.

The three original perfect-square topology sectors are not separately
self-dual. Equation (1) is their combined cancellation, made manifest after
passing to the auxiliary quartic representation.

## Why strict positivity is now global on the regular set

Write (y_A=1/s_A). In the ten-dimensional unordered-channel basis, (1) is

\[
 4c=(J-I)y,
\]

where (J) is the all-ones matrix. Its eigenvalues are (9,-1,\ldots,-1), so

\[
 \det(J-I)=-9\ne0.
\]

Therefore all ten (c_S) can vanish simultaneously only if all ten (y_A)
vanish. That is impossible at a regular finite kinematic point. Since the
amplitude starts at mass degree three,

\[
 [x_0x_1x_2x_3x_4x_5]\,\mathcal M_6^2
 =2\sum_{S<S^c}c_S^2>0. \tag{2}
\]

This exact invertibility argument replaces the bivariate elimination that had
failed at the memory boundary. It excludes every common zero, not merely a
dense-open exception.

## Full five-dimensional physical chart

At fixed total momentum ((16/5,0,0,0)), choose planar null directions

\[
 n(r)=\left(\frac{1-r^2}{1+r^2},\frac{2r}{1+r^2},0\right)
\]

at (r=0,a,b). Their oriented cross products give the unique positive
energies that make the spatial momentum sum zero on the declared chart.
Apply the three-angle rotation (R_z(v)R_x(u)R_z(t)). The parameters
((a,b,t,u,v)) are the two final-state shape variables and three orientation
variables.

The exact Jacobian of the twelve outgoing four-vector components has rank five
at ((2,-2,0,1,0)). Rows (0,2,3,4,6) give determinant (864/3125). Hence
the chart covers an open piece of the full five-dimensional phase space. Six
positive-energy rational fixtures independently have 220 trees, 42 complete
mass-jet terms in degrees three through six, twenty middle coefficients, all
ten instances of (1), and strict positive square sums.

## Physical boundary and next gate

The theorem proves the sign of a local leading tree density on every regular
massless physical configuration. It does not define the density on the
hypersurfaces (s_A=0), where individual tree channels are singular. Squaring
creates nonintegrable-looking pole powers unless a common causal,
distributional, detector, or real-virtual prescription resolves them.

The next physical calculation is therefore no longer another angular or shape
slice. It is a common pole prescription followed by integration over the exact
five-dimensional chart. Eq. (19) remains a separate operator statement: this
amplitude theorem neither constructs (R_tP_\chi R_t^\dagger) nor proves its
weak-ghost decomposition.

## Receipts and failed routes

The exact producer recomputes the (10\times10) species-flow matrix, its
determinant, the rank-five Jacobian, and six complete-tree formula fixtures.
The method-distinct verifier explicitly enumerates all 220 labeled trees and
retains the full degree-three-through-six jet at the same six fixtures. Unit
tests cover the incidence proof, chart minor, claim boundary, verifier, and
the sparse rational arithmetic used by the exploratory three-angle rail.

Before the closed formula was found, a one-prime exact finite-field run over
(GF(1000003)(t,u,v)) verified all ten three-angle complement identities in
twenty isolated workers. It took 1511.57 seconds. It is retained only as an
independent preflight and does not establish a characteristic-zero identity.
Direct nine-invariant, three-variable square-sum, monolithic modular, and
five-variable symbolic attempts exceeded the declared memory or time bounds;
none is counted as a pass. Formula (1), not those failed brute-force routes,
supplies the theorem.

The final scoped producer passed 16/16 checks in 1.04 seconds with maximum RSS
68,620 KB. The method-distinct verifier passed 14/14 checks in 0.88 seconds
with maximum RSS 76,216 KB. Nine mutation/unit tests passed in 0.89 seconds
with maximum RSS 77,028 KB. The affected two-angle verifier passed 14/14 in
0.73 seconds with maximum RSS 73,152 KB, and the original planar explicit-tree
consumer passed 15/15 in 38.05 seconds with maximum RSS 124,604 KB. Paper V
compiled in two 0.51-second passes (50,760 KB maximum RSS); Paper VI compiled
after the final line-break repair in two 0.51-second passes (50,632 KB maximum
RSS), with no warning or overfull box in the final log. Tier 3 was not run:
this is an isolated scalar coefficient theorem, not a classical/quantum freeze,
release, shared-core-algebra change, or Lorentzian lifecycle promotion.
The advisory Science Forge shadow rail was also attempted under the same
500 MB ceiling, but its external `cbp` augmentation aborted before producing
an audit result. It is recorded as an advisory tool failure, not a pass and
not evidence for this theorem.

This certificate does not establish a regulated integral, normalized
probability, real-virtual/KLN cancellation, loops, a Møller/LSZ/S operator,
Eq. (19), a metric BV--BRST lift, anything `LORENTZIAN-CAUSAL`, or literature
priority.

CLOSE-OUT: DONE -- the complete regular physical six-point local scalar sign theorem is proved; pole regulation and integration are the next distinct work item.
EVIDENCE: reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json
