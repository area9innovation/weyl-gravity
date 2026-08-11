# BT eight-point \(\tau_2\)-threshold profile

**Certificate:** `REVERSE_PHYSICS_BT_EIGHT_POINT_TAU2_THRESHOLD_PROFILE_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete eight-point hard-profile difference survives the first
**three** fixed-invariant Källén coefficient functionals.  After the first
two functionals are evaluated, the exact retained profile is

\[
 \Delta F(\tau_2)=
 \frac{3(2090\tau_2^2+1146\tau_2+981)}
 {12800\tau_2^2}.
\]

At the third threshold its three Laurent rows give

\[
 \boxed{\frac{23229}{6400}\ne0}.
\]

Only the inner \(\tau_1\) reduction remains.  It must keep the daughter
masses \(a_0,a_1\) independent and restore every nonzero mass-ratio
prefactor before a physical fourth moment is assigned.

## Complete retained profiles

The first two threshold functionals have unit \(r\log r\) coefficients for
every Laurent row they encounter.  Their coefficient-sum actions may
therefore be evaluated at

\[
 \tau_4=a_4=1,\qquad \tau_3=a_3=2,
\]

before retaining \(\tau_2\).  The complete tree recursion then runs over

\[
 \mathbb Q(e_1,e_2,e_3,\tau_2).
\]

No \(\tau_2\) interpolation is used.  On both hard fixtures all \(34300\)
trees are summed, the amplitude begins at \(\delta^2\), all eight spectator
masks are present, and the ordered hierarchy valuation is \((0,0,-1)\).
The two leading profiles are

\[
 F_{33}=-\frac{
 4914140\tau_2^4+33538836\tau_2^3+48409686\tau_2^2
 +33726780\tau_2+14435415}
 {2560000\tau_2^4},
\]

\[
 F_{34}=-\frac{
 6168140\tau_2^4+34226436\tau_2^3+48998286\tau_2^2
 +33726780\tau_2+14435415}
 {2560000\tau_2^4}.
\]

Their \(\tau_2^{-4}\) and \(\tau_2^{-3}\) rows cancel in the difference,
leaving only the three rows displayed in \(\Delta F\).

## Predecessor replay

The middle-threshold certificate retained \(\tau_3,\tau_4\) and fixed
\(\tau_2=7\).  Substituting \(\tau_2=7\) in the new raw difference gives

\[
 \Delta F(7)=\frac{334239}{627200}.
\]

The middle measure scale is \(a_3=2\), so

\[
 2\Delta F(7)=\frac{334239}{313600},
\]

exactly reproducing the independently recorded predecessor result.  Each
individual hard profile also agrees with the corresponding predecessor
profile at \((\tau_3,\tau_4)=(2,1)\).

## Third threshold

After the first two coefficient functionals, the difference is

\[
 2\Delta F(\tau_2)=\frac3{6400}left(
 2090+\frac{1146}{\tau_2}+\frac{981}{\tau_2^2}
 \right).
\]

For \(\tau_2=a_2u\) with \(a_2=3\), the measure sends

\[
 1\mapsto a_2J_1,\qquad
 \tau_2^{-1}\mapsto J_2,\qquad
 \tau_2^{-2}\mapsto a_2^{-1}J_3.
\]

An independent rationalized-pole calculation gives unit \(r\log r\)
coefficient for \(J_1,J_2,J_3\).  Hence

\[
 \frac3{6400}\left(
 2090a_2+1146+\frac{981}{a_2}
 \right)_{a_2=3}
 =\boxed{\frac{23229}{6400}}.
\]

The coefficient is strictly positive.  The third functional does not place
the declared hard difference in a scalar collapse kernel.

## Physical normalization ledger

The coefficient above is the exact profile-functional comparison required
to test collapse.  It is not yet a normalized fourth-event probability.
At each nested threshold, the physical nonanalytic term contains the
daughter-mass ratio multiplying \(r\log r\), in addition to the measure
scale encoded by the coefficient functional.  Those factors are nonzero and
therefore cannot change this non-collapse result, but they must be assembled
with the inner residue, external distribution signs, phase-space factors,
history count, and ordered simplex before a fourth factorial moment is named.

## Consequence

Three successive physical coefficient functionals have failed to erase the
hard-profile distinction.  The final inner calculation now has a sharp task:

- retain independent \(a_0,a_1\) rather than fixing their ratio;
- derive the invariant-cutoff \(\tau_1\) logarithmic residues;
- determine whether those residues annihilate or retain the two-fixture
  profile difference; and
- only on a scalar result, assemble the physical normalization and compare
  with the two-atom Cox prediction.

If the inner functional also retains the difference, the scalar fourth-jump
architecture is obstructed on the declared fixtures and a channel/profile
carrier is required.  That conclusion is not promoted before the final
residue calculation.

## Claim boundary

Established exactly:

- both complete symbolic \(\tau_2\) profiles;
- their three-row rational difference;
- individual and difference replays of the middle-threshold certificate;
- the \(J_1,J_2,J_3\) scaling map and unit nonanalytic coefficients; and
- the nonzero third-threshold profile-functional difference
  \(23229/6400\).

Not established:

- the independent-mass \(\tau_1\) threshold reduction;
- a fully assembled physical normalization;
- a fourth factorial moment or Cox decision;
- a globally derived hard-profile carrier;
- a complete \(2\to6\) probability or spacetime Møller/LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Resource disposition

The complete profiles were generated sequentially under the \(500000\) KB
virtual-memory cap.  The first isolated fixture took 37.27 seconds and
94,036 KB RSS; the second took 105.39 seconds and 125,320 KB.  The combined
certificate reconstruction took 147.58 seconds and peaked at 126,528 KB.
The compact certificate supports a fast content-addressed check and an
independent symbolic verifier for routine work.

## Verification receipt (2026-08-11)

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile of producer, verifier, and tests; JSON parse of work item, certificate, and schema | PASS | at most 0.60 s wall | 15,740 KB for compile |
| 1 fast | certificate content/hash check | PASS | 0.03 s | 16,192 KB |
| 1 | independent symbolic verifier | PASS, 13/13 | 3.19 s | 74,044 KB |
| 1 | verifier plus eleven falsifying mutations | PASS, 13/13 | 18.30 s | 73,744 KB |
| 2 affected certificate | exhaustive two-fixture symbolic producer and certificate generation | PASS, 13/13 | 147.58 s | 126,528 KB |
| paper | Paper V two-pass PDF build | PASS; no new overfull box or undefined reference | 0.57 / 0.51 s | 50,296 / 50,836 KB |
| paper | Paper VI two-pass PDF build | PASS; no overfull box, warning, or undefined reference | 0.53 / 0.52 s | 50,616 / 50,388 KB |

Paper V retains four pre-existing overfull boxes; the inserted passage creates
none.  The Science Forge shadow rail was not rerun for this successor because
the immediately preceding same-session capped attempt was already
inconclusive: two `cbp` helpers aborted and the silent census timed out after
180.17 seconds.  That advisory result is not a pass and is not used as
scientific evidence.

Tier 2 stops at this new certificate and its direct paper consumers.  The
middle profile input is pinned by content hash.  Tier 3 is unnecessary because
this is a fail-closed `CLASSIFIED` preflight, not a freeze, release,
shared-core-algebra change, fourth-moment theorem, Eq. (19) proof, or lifecycle
promotion.
