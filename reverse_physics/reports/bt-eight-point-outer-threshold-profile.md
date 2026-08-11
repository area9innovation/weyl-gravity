# BT eight-point outer-threshold profile

**Certificate:** `REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The correct outer fixed-invariant Källén integration does not remove the
eight-point hard-profile obstruction.  It identifies the obstruction as one
exact \(J_2\) moment direction and increases the difference between the two
declared fixtures from \(257/1568\) at the previously fixed outer invariant
to \(771/1568\) in the threshold coefficient.

This is an outer-threshold result, not yet the physical fourth factorial
moment.  Three nested threshold reductions and their scale Jacobians remain.

## Complete retained outer profiles

The predecessor summed all \(34300\) eight-point trees and proved that the
complete spectator-projected square is hard-dependent at fixed outer
invariant.  Here the outer parent invariant is retained as

\[
 u=\tau_4.
\]

After the common external-mass limit and the first two ordered hierarchy
limits, each exact fixture gives a Laurent polynomial

\[
 F_i(u,e_3)=\sum_{n=0}^{3}c_{i,n}(e_3)u^{-n}.
\]

The full expressions, their lengths, and their content hashes are stored in
the certificate.  Both complete amplitudes begin at \(\delta^2\), contain all
eight square-free spectator masks, and have zero \((e_1,e_2)\) valuations.

Their leading \(e_3\) profiles are

\[
 e_3F_{33}\big|_{e_3=0}
 =\frac{4687916142u^2-5080002355u-13749551400}
 {3073280000u^2},
\]

\[
 e_3F_{34}\big|_{e_3=0}
 =\frac{4687916142u^2-6591162355u-13749551400}
 {3073280000u^2}.
\]

Their exact difference collapses to

\[
 \boxed{
 e_3(F_{33}-F_{34})\big|_{e_3=0}
 =\frac{771}{1568u}.}
\]

Thus the hard deformation occupies one Laurent-profile direction, rather
than changing every moment row.

## Exact outer Källén functional

At the outer split the daughter-mass ratio is

\[
 r=\frac{e_3\tau_3}{a_4}=5e_3
\]

on the declared soft fixture.  The phase-space measure multiplies the square
by

\[
 \frac{\sqrt{\lambda(u,1,r)}}u,du.
\]

Define the fixed-invariant finite-part moments

\[
 J_n(r)=\operatorname{FP}_{\Lambda\to\infty}
 \int_{(1+\sqrt r)^2}^{\Lambda}
 \frac{\sqrt{\lambda(u,1,r)}}{u^n},du.
\]

The four profile rows map as

\[
 1\mapsto J_1,qquad u^{-1}\mapsto J_2,qquad
 u^{-2}\mapsto J_3,qquad u^{-3}\mapsto J_4.
\]

An independent rationalized-pole calculation verifies

\[
 [r\log r]J_1=[r\log r]J_2=[r\log r]J_3=[r\log r]J_4=1.
\]

Consequently the outer nonanalytic functional is simply

\[
 \mathcal T_{\rm out}[F](e_3)=\sum_{n=0}^{3}c_n(e_3)
 =F(1,e_3).
\]

The fixture difference is a pure \(u^{-1}\) row, so it passes through \(J_2\)
with unit coefficient:

\[
 \boxed{
 \lim_{e_3\to0}e_3\left(
 \mathcal T_{\rm out}[F_{33}]
 -\mathcal T_{\rm out}[F_{34}]
 \right)=\frac{771}{1568}.}
\]

At the predecessor's fixed value \(u=3\), the same profile gives

\[
 \frac1{3}\frac{771}{1568}=\frac{257}{1568},
\]

which exactly replays the earlier certificate.  This explains the factor of
three without introducing another fit.

Multiplying by \(r=5e_3\), the actual leading outer logarithms on the two
fixtures differ by

\[
 \boxed{\frac{3855}{1568}\log r.}
\]

The fixed-invariant threshold integration therefore amplifies rather than
cancels the hard-profile distinction.

## Meaning for the physical route

The direct scalar branching architecture cannot yet be extended by one
number \(q_3\).  At this stage the smallest observed difference carrier is
the one-dimensional \(J_2\) profile direction.  Calling that a BT dynamical
degree of freedom would be premature: it is an exact two-fixture quotient
direction, not a globally constructed asymptotic carrier.

The remaining question is sharper.  Retain \(\tau_3\) symbolically, include
the \(e_3\) scale Jacobian, and perform the next fixed-invariant threshold
reduction.  The \(J_2\) difference may:

- land in a collapse kernel of the middle pre-trace quotient;
- survive as a genuine hard-profile-valued fourth jump; or
- combine with additional channel profiles before becoming scalar.

Only after all remaining thresholds produce a hard-independent scalar may a
fourth factorial moment be compared with the two-atom Cox prediction

\[
 P_4^{(2\text{-atom})}=\frac{73}{786432}.
\]

## Claim boundary

Established exactly:

- both complete retained outer profiles;
- the pure \(J_2\) difference \(771/(1568u)\);
- the predecessor replay at \(u=3\);
- the independent \(J_1,\ldots,J_4\) unit nonanalytic coefficients;
- the surviving threshold-pole and physical-log differences.

Not established:

- the remaining three nested threshold reductions;
- a final fourth factorial moment;
- exclusion of the two-atom Cox law;
- a global or dynamically derived hard-profile carrier;
- a complete \(2\to6\) probability or spacetime Møller/LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Resource disposition

The exhaustive producer ran both full rational-function profiles sequentially
under the \(500000\) KB virtual-memory cap.  It completed in 3:30.99 with peak
RSS \(142044\) KB.  Routine checking is split into a content-addressed fast
rail and an independent verifier.  The verifier reconstructs the threshold
functional by pole derivatives and replays both complete finite-hierarchy
tree values using the alternative triangle form of the cubic vertex.

## Verification receipt (2026-08-11)

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile of the outer and middle producers, verifiers, and tests; JSON parse of both work items, certificates, and schemas | PASS | at most 0.60 s wall | 15,488 KB for compile |
| 1 fast | outer certificate content/hash check | PASS | 0.03 s | 16,284 KB |
| 1 | method-distinct outer verifier | PASS, 12/12 | 5.09 s | 78,940 KB |
| 1 | verifier plus twelve falsifying mutations | PASS, 13/13 | 22.11 s | 79,220 KB |
| 2 affected certificate | exhaustive two-fixture outer-profile producer | PASS, 12/12 | 210.99 s | 142,044 KB |
| paper | Paper V two-pass PDF build | PASS; no new overfull box or undefined reference | 0.59 / 0.47 s | 50,988 / 50,336 KB |
| paper | Paper VI final two-pass PDF build | PASS; no overfull box or undefined reference | 1.12 / 1.02 s | 50,968 / 50,700 KB |
| advisory | `ci/science-forge-shadow.sh` | INCONCLUSIVE; two capped `cbp` helpers aborted and the silent census timed out, exit 124 | 180.17 s | 59,768 KB parent RSS |

Paper V retains its pre-existing overfull boxes.  The inserted passages create
no new box warning.  Paper VI retains only pre-existing underfull boxes.  The
advisory Science Forge run is not a pass and is not used by the certificate.

Tier 2 stops at the outer and middle profile certificates and their direct
paper consumers.  All predecessor artifacts are imported by unchanged content
hashes.  Tier 3 is unnecessary because these are fail-closed `CLASSIFIED`
preflights, not a freeze, release, shared-core-algebra change, fourth-moment
theorem, Eq. (19) proof, or lifecycle promotion.
