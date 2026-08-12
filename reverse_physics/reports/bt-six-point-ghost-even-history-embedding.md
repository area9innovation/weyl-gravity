# BT six-point ghost-even history embedding

Certificate:
`REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The complete six-point BT tree coefficient and every fixed-channel
nine-history output range lie exactly in the positive ghost-even plane of the
public neutral six-leg Fock carrier.  This closes the output-history embedding
gate left by the finite-time Hamiltonian-cut calculation.  It does not push
the physical scalar input projector through (R_t), derive the virtual
survival block, or prove Eq. (19).

## The public neutral carrier

Label a six-leg species assignment by a six-bit mask, with a one for an
(Omega) leg and a zero for an (Upsilon) leg.  The neutral sector has three
of each species, hence dimension

\[
 {6\choose3}=20.
\]

The ten unordered (3|3) representatives in the complete phase-space
certificate are

\[
 7,11,19,13,21,25,14,22,26,28.
\]

Their bitwise complements supply the other ten assignments.  Order the basis
as representatives followed by complements.  The cross-Krein metric induced
from the public (Omega,Upsilon) pairing and the ghost-parity exchange are
then the same matrix,

\[
 \eta=\kappa=
 \begin{pmatrix}0&I_{10}\\I_{10}&0\end{pmatrix}.
\]

This is a nondegenerate Krein space of inertia ((10,10)).  The associated
fundamental positive metric is (etakappa=I_{20}).  Its even and odd frames
are

\[
 U_+=\frac1{\sqrt2}\binom{I_{10}}{I_{10}},\qquad
 U_-=\frac1{\sqrt2}\binom{I_{10}}{-I_{10}},
\]

and exact multiplication gives

\[
 U_+^T\eta U_+=I_{10},\qquad
 U_-^T\eta U_-=-I_{10},\qquad
 U_+^T\eta U_-=0.
\]

Thus this positive carrier is not an abstract Hilbert space adjoined for the
detector.  It is the (+1) ghost-parity eigenspace already present in the
public six-leg Fock sector.

## Complete coefficient and Choi form

The complete tree calculation previously proved

\[
 c_S=c_{S^c}=\frac14\sum_{A\ne S}\frac1{s_A}.
\]

Writing (c=(c_0,\ldots,c_9)^T), its full twenty-component coefficient is

\[
 a=\binom cc=\sqrt2,U_+c.
\]

Consequently

\[
 \kappa a=a,qquad
 a^T\eta a=2\sum_{S=0}^9c_S^2.
\]

The right-hand side is exactly the certified complete local Born density.  If
(y_A=1/s_A) and (M=J-I), then (c=My/4) and

\[
 2\left(\frac M4\right)^T\left(\frac M4\right)
 =J+\frac18I,
\]

recovering the complete ten-channel Gram independently from the public Fock
pairing.

There is also an operator formulation.  Use three bits for the incoming
species string and three for the outgoing string, and arrange the twenty
neutral coefficients as an (8\times8) matrix (A).  Let
(kappa_3|x\rangle=|7-x\rangle).  Complement equality becomes

\[
 \kappa_3A\kappa_3=A.
\]

Therefore the Krein adjoint simplifies:

\[
 A^\sharp=\kappa_3A^T\kappa_3=A^T,
\]

and the generalized Born trace is

\[
 \operatorname{tr}(A^\sharp A)
 =\operatorname{tr}(A^TA)
 =2\sum_Sc_S^2\ge0.
\]

This proves strong ghost symmetry for the complete tree coefficient itself,
not merely positivity after a scalar contraction.  It remains a coefficient-
level statement; it does not construct an all-order scattering operator.

## Fixed-shell histories

Fix an intermediate channel (B).  The predecessor has precisely the nine
histories ((S,B)) with (S\ne B), with resolved-history metric (2I_9).
After normalizing the raw history basis by (1/\sqrt2), define

\[
 E_B f_{(S,B)}=U_+e_S.
\]

Then

\[
 E_B^T\eta E_B=I_9,qquad \kappa E_B=E_B.
\]

The fixed-pole residue has normalized history coordinates
(h_S=1/(2\sqrt2)).  Its image has coefficient (1/4) on both (S) and
(S^c), and zero on (B,B^c).  Its two norms agree exactly:

\[
 h^Th=(E_Bh)^T\eta(E_Bh)=\frac98.
\]

This is the same (9/8) multiplying the BT-derived finite-time shell kernel.
The positive fixed-shell history range used in the detector calculation is
therefore affiliated with an actual public Fock subspace.

## Why ninety histories still need a record

The ten fixed-channel embeddings cannot be combined into an isometry from all
ninety resolved histories to the ten-dimensional positive species plane.  The
only simultaneous restriction with the displayed fixed-channel action sends

\[
 f_{(S,A)}\longmapsto U_+e_S.
\]

It has rank ten and an eighty-dimensional kernel.  Histories with the same
final species assignment but different intermediate channels collapse
coherently.  This is the exact distinction between the public species carrier
and the detector's channel record.

There is no inconsistency: a detector can retain the record in an additional
positive channel-label ancilla.  What is ruled out is silently identifying the
ninety orthogonal resolved histories with only ten public species directions.

## Consequence for Eq. (19) and the physical route

The finite-time calculation left two logically separate tasks:

1. embed the positive output-history range into the BT Krein carrier;
2. show that the transported physical input projector and its survival
   complement enter the same weakly ghost-symmetric process.

The first task is now complete for each fixed shell, and the complete six-point
transition coefficient is itself strongly ghost symmetric.  The second task is
not implied by this fact.  Eq. (19) concerns
(R_tP_\chi^{(\phi)}R_t^\dagger), including the source projector, vacuum and
zero-mode structure, trace domain, and higher orders.  None of those objects is
reconstructed by reorganizing an already computed output coefficient.

The next calculation should therefore hold this positive output plane fixed
and compute the leading finite-time pushforward of the incoming scalar
three-particle projector.  Success would give a derived positive survival
column on this shell.  Failure would identify the first source component that
cannot land in the positive even plane.  Global shell gluing must carry an
explicit channel-record ancilla.

This certificate does not establish a complete inclusive probability,
Møller/LSZ/(S) operator, all-order Eq. (19), loops, gravity/BRST transfer, or
anything `LORENTZIAN-CAUSAL`.

## Verification receipt

- Tier 0: the producer, independent verifier, tests, schema, certificate and
  work item parse; the scoped diff is checked before commit.  Papers 5 and 6
  compile twice with no undefined control sequence, reference or citation
  warning; their pre-existing box warnings remain outside this claim.
- Tier 1: the exact producer passes 31/31 checks, the method-distinct verifier
  passes 24/24 checks, and seven mutation tests pass.  The producer peaks at
  66,840 KB resident memory; the verifier and tests remain below 25 MB.  Every
  scientific process runs under the 500 MB hard cap.
- Tier 2: the affected chain from complete full-phase-space Born positivity
  through shell normalization, detector cell, Hamiltonian cut and this
  embedding passes sequentially.  Producers report 16/16, 19/19, 27/27,
  26/26 and 31/31 checks; independent verifiers report 14/14, 21/21, 26/26,
  23/23 and 24/24 checks.  The combined 35-test chain passes in 1.06 seconds
  with peak resident memory 78,612 KB; the independent-verifier chain peaks
  at 75,860 KB.
- Tier 3 is not required because no shared core algebra, freeze, release,
  lifecycle promotion, QME state or Lorentzian claim changes.
- The read-only Science Forge shadow command exits advisory-success and writes
  its corpus census, but its bridge audit is **not a pass**: the cached Forge
  0.0.2 binary and current `FORGE_LIB` hashes differ, and compilation stops at
  substrate error `E9118`.  The scoped `s-f work check` is unavailable for the
  same build failure.  The append-only `DONE` event is therefore authored
  manually; this coordination-tool failure is kept separate from the passing
  exact scientific rails.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_six_point_ghost_even_history_embedding.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_ghost_even_history_embedding.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_six_point_ghost_even_history_embedding
```

CLOSE-OUT: DONE -- the complete six-point tree coefficient and every fixed-
shell positive history range are embedded in the public neutral ghost-even
Fock sector; the physical input-projector pushforward, survival block and
global channel record remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_GHOST_EVEN_HISTORY_EMBEDDING_V1.json`
