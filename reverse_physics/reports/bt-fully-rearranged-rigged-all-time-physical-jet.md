# Fully rearranged BT all-time physical probability jet

Certificate:
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1`.

Tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The previously computed all-time coefficients are the complete selected
public-auxiliary physical probability jet through order \(\lambda^{10}\):

\[
 \boxed{
 q_{\mathrm{phys},\infty}[F]
 =\lambda^8q_{8,\infty}[F]
 +\lambda^{10}q_{10,\infty}[F]
 +O(\lambda^{12}).}
\]

Here

\[
 q_{8,\infty}[F]
 =\lVert T_{4,\infty}F\rVert_{L^2(Y)}^2>0
\]

on a nonempty real nonnegative packet class, while

\[
 q_{10,\infty}[F]
 =2\operatorname{Re}
 \langle T_{4,\infty}F,T_{6,\infty}F\rangle
\]

is finite and need not have a fixed sign.  Total-Fock parity removes every
odd probability order.  In particular, \(q_9=0\).

“Complete selected” is load-bearing.  It means that every term which can
contribute to this particular support-separated incoming-to-outgoing click
has been classified through \(\lambda^{10}\).  It does not mean that a
whole-carrier or all-channel scattering operator has been constructed.

## Why the apparently missing sectors are exactly zero

The incoming and outgoing packet supports are compact neighborhoods of the
certified fully rearranged rational centers.  They obey

\[
 P_YP_X=0.
\]

The exact external subset-sum margins for blocks of size one, two and three
are

\[
 2,\qquad {32\over625},\qquad {17794\over10625}.
\]

Every one of the 202 disconnected partitions of six external labels has a
connected component of size at most three.  That component carries its own
momentum-conservation distribution, whose support misses the selected
packet.  Consequently every disconnected identity, spectator, soft or
collinear contribution pairs to zero.

This statement is coefficientwise rather than tied to tree order.  A
distributional derivative cannot enlarge support:

\[
 \operatorname{supp}(\partial^\alpha T)
 \subseteq\operatorname{supp}(T).
\]

It therefore also covers the external-mass derivatives used by the
generalized Born prescription.  Restricting the packets before removing the
common center time makes the same zero persist in the all-time limit.  The
identity and pure forward/survival blocks are separately killed by
\(P_YP_X=0\).

Thus forward and collinear contributions have not been guessed or omitted
inside this theorem.  They are distributions on different supports and are
exactly invisible to this detector.

## Exhaustion of the surviving amplitude

Put \(g=\lambda^2\).  In the normal-ordered direct auxiliary frame the
restricted all-time amplitude is

\[
 A_{YX,\infty}
 =g^2T_{4,\infty}+g^3T_{6,\infty}+O(g^4)
 =\lambda^4T_{4,\infty}
  +\lambda^6T_{6,\infty}+O(\lambda^8).
\]

The order-\(g^3\) graph census is exhaustive.  Three quartic vertices give
four connected multigraph types.  The two tadpole types vanish in the
declared normal-ordered massless unit-residue scheme.  The remaining maps are
exactly

\[
 T_{6,\infty}
 =T_{6,\triangle,\infty}+T_{6,\mathrm{bb},\infty}.
\]

Their all-time triangle and bubble-with-bridge distributions were certified
on the same smooth packet domain.  A vacuum factor at this order would have
to be the one-vertex vacuum expectation multiplying the leading transition;
normal ordering makes it zero.  Pulling source and detector together through
the same two-sided \(R_t\) similarity creates no additional selected
coefficient: its induced \(y_5\) norm and second-order dressing cross cancel
coefficientwise.

There is therefore no unclassified selected amplitude term through
\(\lambda^6\), and squaring gives the displayed complete probability jet.

## Public and positive Born rules agree as operators

Both all-time coefficients are fixed by total ghost parity:

\[
 \alpha(T_{4,\infty})=T_{4,\infty},\qquad
 \alpha(T_{6,\infty})=T_{6,\infty}.
\]

The momentum support projectors commute with that parity.  Hence the public
Krein adjoint and positive-Hilbert adjoint agree on both coefficients.  The
effect jet is

\[
 E_8=T_{4,\infty}^*T_{4,\infty},
\]

\[
 E_{10}=T_{4,\infty}^*T_{6,\infty}
       +T_{6,\infty}^*T_{4,\infty},
\]

with exact operator identities

\[
 E_8^{\rm public}=E_8^{\rm Hilbert},\qquad
 E_{10}^{\rm public}=E_{10}^{\rm Hilbert}.
\]

This is stronger than matching one scalar matrix element.  The certificate
also includes an exact rational finite-dimensional recomputation of the
fixed-point effect algebra, and the independent verifier reconstructs it.

## Perturbative positivity

The correction \(q_{10,\infty}\) can be negative.  That does not destroy the
local perturbative physical statement.  For every fixed certified packet
and renormalization scale, \(q_{8,\infty}>0\) and
\(q_{10,\infty}\) is finite.  If the latter is negative, then

\[
 \lambda^2\leq
 {q_{8,\infty}\over2|q_{10,\infty}|}
\]

implies

\[
 q_{8,\infty}+\lambda^2q_{10,\infty}
 \geq {q_{8,\infty}\over2}>0.
\]

If \(q_{10,\infty}\geq0\), the displayed truncation is already positive.
Thus every fixed packet has a nonempty exact small-coupling positivity
neighborhood.  This is positivity of the computed truncated jet, not a claim
about the unknown \(O(\lambda^{12})\) remainder or the exact finite-coupling
probability.

## Renormalization group

The all-time identity

\[
 \partial_{\log\mu}q_{10,\infty}
 ={5\over2\pi^2}q_{8,\infty}
\]

and

\[
 \partial_{\log\mu}\lambda
 =-{5\lambda^3\over16\pi^2}
\]

give

\[
 \partial_{\log\mu}
 \left(\lambda^8q_{8,\infty}
 +\lambda^{10}q_{10,\infty}\right)
 =O(\lambda^{12}).
\]

The standalone \(q_{10}\) coordinate remains scheme dependent; the
displayed cancellation is the physical perturbative statement.

## Meaning and boundary

In ordinary language, we now have a genuine selected scattering experiment
in the BT auxiliary theory, carried to the first loop correction and to
infinite observation time at the level of smooth wave packets.  All terms at
that perturbative order either contribute through the displayed tree and
loop maps or are proved invisible by support, parity, normal ordering or
orthogonality.  The public generalized-Krein probability and the ordinary
positive-Hilbert probability agree on the resulting effect jet.

This does not establish a detector which intersects the identity, spectator,
forward or collinear strata; a canonical finite-time \(q_{10}\); an exact
finite-coupling probability; interchange of the all-time and perturbative
limits; a bounded whole-carrier Møller/LSZ/\(S\) operator; general Eq. (19);
gravity or metric BV--BRST/QME transfer; or anything `LORENTZIAN-CAUSAL`.

## Verification receipt

- Tier 0: the three new Python files compile, all four new JSON files parse,
  the strict Draft-2020-12 schema validates, an extra-property mutation is
  rejected, and the scoped diff is checked.  Papers V and VI compile twice
  under the 500 MB cap in 0.53/0.53 and 0.54/0.54 seconds, with respective
  peak resident sets of at most 50,904 and 50,760 KiB.  Paper V is 85 pages
  and Paper VI is 73 pages.  Their six and two old overfull boxes remain;
  this edit adds none.
- Tier 1: the exact producer passes 35/35 checks in 0.02 seconds at 16,652
  KiB, the method-distinct verifier passes 54/54 checks in 0.07 seconds at
  24,124 KiB, and 38 focused tests, including 36 adversarial mutations, pass
  in 2.66 seconds at 24,492 KiB.
- Tier 2: the physical-support, leading common-Born, lambda-nine parity,
  all-time q8, selected q10 assembly, all-time q10, and present physical-jet
  packages are replayed sequentially.  All fourteen producer/verifier rails
  pass, and the seven test packages run 228 tests with no failures in 10.42
  seconds.  The largest observed resident set is 69,788 KiB.
- Tier 3 is required because Papers V and VI acquire a physical theorem.  It
  remains fail-closed: 3,594 tests run in 718.439 seconds, with 31 failures
  and 9 skips, and the command exits nonzero.  The failures reproduce the
  existing certificate-drift and chain-import census; no failure is in the
  new physical-jet package.  The enclosing run takes 11:59.50 and peaks at
  391,612 KiB with no swaps.  This non-pass certifies neither a repository
  freeze nor a release; it does not erase the green scoped and transitive
  theorem rails.
- Science Forge records an append-only `DONE` transition.  The existing
  read-only coordinator folds 1,595 nodes with zero invalid items and zero
  malformed events in 5.89 seconds at 227,832 KiB.  `s-f work check` remains
  fail-closed at its existing `sfc` build failure and is not counted as a
  pass.

Every scientific process above ran sequentially under the 500 MB hard
virtual-memory cap.  The read-only Science Forge fold also ran alone; its Go
runtime is incompatible with that virtual-address cap, so its actual
resident-set receipt is recorded explicitly instead.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_rigged_all_time_physical_jet.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_rigged_all_time_physical_jet.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_rigged_all_time_physical_jet
PATH=/usr/local/bin:/usr/bin:/bin; ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -v
```

CLOSE-OUT: DONE -- the support-separated all-time q8-q10 packet jet is the
complete selected public-auxiliary physical probability jet through
\(\lambda^{10}\), with operator-level common-Born equality and a nonempty
packetwise perturbative positivity neighborhood.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PHYSICAL_JET_V1.json`
