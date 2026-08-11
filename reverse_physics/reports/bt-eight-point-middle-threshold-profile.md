# BT eight-point middle-threshold profile

**Certificate:** `REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The eight-point hard-profile difference survives the first **two** physical
fixed-invariant Källén reductions.  Restoring the next parent invariant
symbolically turns the outer pure-\(J_2\) direction into an exact three-row
middle profile, but its middle nonanalytic coefficient is

\[
 \boxed{\frac{334239}{313600}\ne0.}
\]

This is not yet the fourth physical factorial moment.  The final
\(\tau_2\) and \(\tau_1\) reductions, including independent inner daughter
masses, remain open.

## Complete two-invariant profiles

The complete \(34300\)-tree recursion is performed over

\[
 \mathbb Q(e_1,e_2,e_3,\tau_3,\tau_4)
\]

with the same common-scale Laurent algebra and full three-bit spectator
projector as the predecessor.  The projector is formed before any hierarchy
valuation.  On both hard fixtures:

- the amplitude begins at common mass order \(\delta^2\);
- all eight spectator masks are present; and
- the ordered hierarchy valuation is \((0,0,-1)\).

After extracting the leading \(e_3^{-1}\) coefficient, the two compact
profiles differ by

\[
 \boxed{
 \Delta F(\tau_3,\tau_4)=
 \frac{3(27213\tau_3^2-13462\tau_3+29485)}
 {156800\tau_3^2\tau_4}.}
\]

This symbolic identity independently explains two exact evaluations:

\[
 \Delta F(4,1)=\frac{246627}{501760},
 \qquad
 \Delta F(5,1)=\frac{771}{1568}.
\]

The first was computed by a separate complete-tree run at \(\tau_3=4\); the
second is the outer-threshold certificate's fixture.

## First threshold

The \(\tau_4^{-1}\) row is the pure \(J_2\) direction already identified.
Its unit \(r\log r\) coefficient removes only that profile factor:

\[
 \mathcal T_4[\Delta F](\tau_3)=
 \frac{3(27213\tau_3^2-13462\tau_3+29485)}
 {156800\tau_3^2}.
\]

Equivalently,

\[
 \mathcal T_4[\Delta F](\tau_3)
 =\frac3{156800}
 \left(27213-\frac{13462}{\tau_3}
 +\frac{29485}{\tau_3^2}\right).
\]

## Second threshold

For the next split let

\[
 \tau_3=a_3u,qquad a_3=2,qquad
 r_3=\frac{e_2\tau_2}{a_3}.
\]

The measure transforms as

\[
 \frac{\sqrt{\lambda(\tau_3,a_3,e_2\tau_2)}}{\tau_3}
 d\tau_3
 =a_3\frac{\sqrt{\lambda(u,1,r_3)}}u,du.
\]

Therefore the three Laurent rows map to

\[
 1\mapsto a_3J_1,qquad
 \tau_3^{-1}\mapsto J_2,qquad
 \tau_3^{-2}\mapsto a_3^{-1}J_3.
\]

An independent pole-derivative calculation gives unit \(r_3\log r_3\)
coefficient for \(J_1,J_2,J_3\).  The resulting difference is

\[
 \frac3{156800}\left(
 27213a_3-13462+\frac{29485}{a_3}\right)_{a_3=2}
 =\boxed{\frac{334239}{313600}}.
\]

It is strictly positive and nonzero.  Neither of the first two threshold
functionals places the hard difference in a scalar collapse kernel.

## Consequence

The scalar fourth-jump route has narrowed again.  Any successful completion
must now show one of the following at the final two thresholds:

- the surviving coefficient enters an exact pre-trace collapse direction;
- additional hard/channel profiles recombine with it before the final trace;
  or
- the fourth jump is genuinely profile-valued and the finite scalar
  branching carrier must be enlarged.

The final \(\tau_1\) step must retain independent \(a_0,a_1\).  Fixed mass
ratios cannot determine the mixed external-mass nonanalytic coefficient and
must not be used to compare with
\(P_4^{(2\text{-atom})}=73/786432\).

## Claim boundary

Established exactly:

- both complete symbolic \((\tau_3,\tau_4)\) profiles;
- their rational difference and two exact specializations;
- the outer \(J_2\) reduction;
- the middle \(J_1,J_2,J_3\) scaling map;
- the nonzero second-threshold difference \(334239/313600\).

Not established:

- the final \((\tau_2,\tau_1)\) threshold reductions;
- a fourth factorial moment or Cox decision;
- a globally derived hard-profile carrier;
- a complete \(2\to6\) probability or spacetime Møller/LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Resource disposition

The exhaustive two-profile producer ran sequentially under the \(500000\) KB
virtual-memory cap.  The final reconstruction took 6:09.98 and peaked at
\(209848\) KB RSS.  The first profile alone took 55.98 seconds and \(118180\)
KB; the second took 4:55.83 and \(204688\) KB.  The long reconstruction is an
affected-certificate rail, not the routine edit loop.  The recorded compact
profiles support a fast independent symbolic verifier and mutation suite.

## Verification receipt (2026-08-11)

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile of the outer and middle producers, verifiers, and tests; JSON parse of both work items, certificates, and schemas | PASS | at most 0.60 s wall | 15,488 KB for compile |
| 1 fast | middle certificate content/hash check | PASS | 0.03 s | 16,128 KB |
| 1 | independent symbolic verifier | PASS, 12/12 | 1.09 s | 74,384 KB |
| 1 | verifier plus eleven falsifying mutations | PASS, 12/12 | 5.48 s | 74,524 KB |
| 2 affected certificate | exhaustive two-fixture symbolic producer drift check | PASS, 12/12 | 366.95 s | 210,176 KB |
| paper | Paper V two-pass PDF build | PASS; no new overfull box or undefined reference | 0.59 / 0.47 s | 50,988 / 50,336 KB |
| paper | Paper VI final two-pass PDF build | PASS; no overfull box or undefined reference | 1.12 / 1.02 s | 50,968 / 50,700 KB |
| advisory | `ci/science-forge-shadow.sh` | INCONCLUSIVE; two capped `cbp` helpers aborted and the silent census timed out, exit 124 | 180.17 s | 59,768 KB parent RSS |

The full producer re-derived both complete symbolic profiles and matched the
recorded canonical certificate.  Paper V retains its pre-existing overfull
boxes, while Paper VI retains only pre-existing underfull boxes.  The advisory
Science Forge run is not a pass and is not used as scientific evidence.

Tier 2 stops at this certificate and its direct paper consumers.  Its inputs
are pinned by hashes, and no downstream mathematical certificate consumes the
new result yet.  Tier 3 is unnecessary because this is a fail-closed
`CLASSIFIED` preflight, not a freeze, release, shared-core-algebra change,
fourth-moment theorem, Eq. (19) proof, or lifecycle promotion.
