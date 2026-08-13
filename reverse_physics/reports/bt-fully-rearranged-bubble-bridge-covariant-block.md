# Fully rearranged BT bubble-with-bridge covariant block

**Certificate:**
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
**Lifecycle:** `COEFFICIENT_COMPUTED` for the isolated covariant block.

## Result

The only direct-auxiliary connected six-leg loop left by the frame-typed
ledger is now computed covariantly.  Write one labelled graph as

\[
 R=(a;bc;def).
\]

The external leg (a) is attached to the degree-three junction, (bc) to
the bubble leaf, and (def) to the tree leaf.  There are

\[
 6\binom52=60
\]

such roles.  Equivalently, there are six insertions over each of the ten
unordered (3|3) bridge channels.

Put (g=\lambda^2).  Each neutral auxiliary vertex contributes (2g), and
the two parallel bubble edges have symmetry factor (1/2).  With
(\lambda^6) outside the coefficient, the common-phase-stripped answer is

\[
 \boxed{
 T_{6,\mathrm{bb}}^{\mathrm{cov}}
 ={4\over16\pi^2}\sum_R
 {B_{\overline{\mathrm{MS}}}(Q_R^2)\over K_R^2+i0}\,W_R ,}
\]

where (Q_R=p_b+p_c), (K_R=p_d+p_e+p_f), and

\[
 B_{\overline{\mathrm{MS}}}(Q^2)
 =\log{\mu^2\over -Q^2-i0}+2.
\]

The real dispersive part is the already certified
(\log(\mu^2/|Q^2|)+2).  The displayed complex master keeps the timelike
boundary rather than deleting it before this six-point block is assembled.

Together with the finite covariant triangle predecessor, this closes the
connected covariant six-leg loop list in the selected normal-ordered
auxiliary scheme.  It does not yet close the finite-time list.

## Exact species tensor

For every role, orient the two parallel bubble edges and the bridge.  Each
edge joins opposite auxiliary species, while all three vertices must contain
two Ω and two Υ fields.  On the twenty neutral three-Ω/three-Υ external
assignments, every (W_R) has

- two zero entries;
- six entries equal to one;
- twelve entries equal to two; and
- squared Hilbert--Schmidt norm (6+4(12)=54).

Every neutral assignment has total routing weight ninety after summing all
sixty roles.  On the declared source

\[
 u_0={|000\rangle+|111\rangle\over\sqrt2},
\]

the role weights have multiplicities (6,18,36) at values (0,1,2).

The independent verifier does not enumerate the eight internal edge
orientations.  If (n_B) is the number of external Ω legs at the bubble
leaf and (n_C) that at the three-leg leaf, direct solution of the three
neutrality constraints gives

\[
 W_R(m)=
 \begin{cases}
 \binom2{n_B},&n_C=1\text{ or }2,\\
 0,&n_C=0\text{ or }3.
 \end{cases}
\]

This reconstructs the complete tensor independently.

Species complementation maps every allowed routing to another allowed
routing, so

\[
 \kappa_3W_R\kappa_3=W_R
\]

coefficientwise.

## The forty-to-one forest identity

Let (R_C) denote the certified tree residue for bridge channel (C).
Grouping the six roles whose bridge is (C) gives the exact matrix identity

\[
 \boxed{\sum_{R:\,C_R=C}W_R=40R_C.}
\]

Both sides vanish on the two complementary species masks defining (C),
and both equal ten on each of the other eighteen neutral assignments.

The full tree--bubble-bridge cross Gram has entries

\[
 {13\over2},\qquad 7,\qquad {15\over2},
\]

with multiplicities (360,180,60).  Every tree row sums to (405), every
graph-role column to (135/2), and the sixty same-bridge entries are exactly
(15/2).  Restriction to the positive four-frame divides these values by
two.  This is a carrier statement, not a sign evaluation of the momentum
integral.

## Renormalization and an exact RG check

The complete graph has overall degree

\[
 \omega=4L-2I=-2.
\]

It therefore needs no primitive six-point counterterm.  Its two parallel
edges form one logarithmic four-point bubble subdivergence.  Renormalizing
that subgraph in the same MSbar quartic-coupling convention as the active
four-point predecessor is sufficient.

The forest identity fixes the counterterm normalization without fitting a
six-point result.  Since

\[
 {\partial B_{\overline{\mathrm{MS}}}\over\partial\log\mu}=2
\]

and the tree coefficient is

\[
 T_4^{\mathrm{cov}}=16\sum_C{R_C\over K_C^2+i0},
\]

we obtain

\[
 \boxed{
 {\partial T_{6,\mathrm{bb}}^{\mathrm{cov}}
  \over\partial\log\mu}
 ={5\over4\pi^2}T_4^{\mathrm{cov}}.}
\]

The independently certified beta function is

\[
 {d\lambda\over d\log\mu}=-{5\lambda^3\over16\pi^2}.
\]

Consequently

\[
 {d\over d\log\mu}(\lambda^4T_4)
 =-{5\lambda^6\over4\pi^2}T_4,
\]

which cancels the explicit scale derivative of
(\lambda^6T_{6,\mathrm{bb}}) exactly.  This agreement simultaneously checks
the vertex factor, bubble symmetry factor, six insertions per bridge channel,
and local counterterm coefficient.

The identity also survives finite switching at the local level.  In time
space, differentiating the renormalized bubble distribution gives
(2\delta(t_A-t_B)).  Collapsing the bubble endpoints turns the graph into
the same switched tree kernel (T_{4,T}), again with coefficient
(5/(4\pi^2)).  Thus the finite-time forest term is fixed before the finite
nonlocal remainder is evaluated.

## Exact packet margins

At the fully rearranged rational center, all sixty bubble momenta obey

\[
 \min_R|Q_R^2|={32\over625},
 \qquad
 \min_R|\mathbf Q_R|^2={32\over625}.
\]

The bubble subgraph is therefore separated from its external soft and
collinear loci on a sufficiently small compact neighborhood.

Six roles have (K_R^2=0).  These are genuine bridge-shell graphs and must
be handled by a finite-time kernel; the covariant pole cannot be frozen at
the packet center.

The only bridge with zero spatial momentum is the hard channel formed by all
three incoming or all three outgoing legs.  Its six tensors annihilate
(u_0) coefficientwise.  Every role that survives on the selected source
satisfies

\[
 |\mathbf K_R|^2\ge {7169\over10625}.
\]

This proves a nonempty selected-source domain on which all surviving bridge
energies are nonzero.  It is not a full-carrier zero-mode theorem.

## Why the existing finite-time bubble is not enough

The predecessor's

\[
 B_{T,\overline{\mathrm{MS}}}(P)
\]

is an energy-diagonal four-point tree--loop interference: the ordered
second-Dyson cross is divided by the one-vertex tree duration.  Inside the
present six-point graph, the bubble exchanges energy with the third vertex
before the total-energy projection.  There are two independent intermediate
defects.

Therefore multiplying the finite-time tree bridge by the displayed
energy-diagonal (B_T) would not be a derivation.  The required successor is
the full renormalized off-diagonal bubble time distribution convolved with
the bridge on ([0,T]), or equivalently the subtracted three-vertex spatial
integral with all six chronological orderings.  The local subtraction is now
fixed by the forty-to-one identity, but its finite nonlocal transient has not
yet been computed.

## Common-Born boundary

The scalar bubble and bridge distributions commute with total species
parity, while every (W_R) is κ-fixed.  Hence the isolated covariant
interference obeys

\[
 T_4^\sharp T_{6,\mathrm{bb}}
 +T_{6,\mathrm{bb}}^\sharp T_4
 =T_4^*T_{6,\mathrm{bb}}
 +T_{6,\mathrm{bb}}^*T_4.
\]

Its public-Krein and positive-Hilbert operator coefficients coincide.  The
sign is not fixed because the complex momentum kernel and its future
finite-time transient remain coherent.

## Claim boundary

This certificate does not establish:

- the off-diagonal finite-time bubble-with-bridge kernel;
- permission to insert the energy-diagonal (B_T) multiplicatively;
- the finite-time interference value or sign;
- a full-carrier treatment of the zero-spatial hard bridge;
- the complete finite-time connected (T_6);
- (y_5), source/detector dressing, or vacuum/survival normalization;
- complete (q_{10}), Eq. (19), gravity, or anything
  `LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific Python and TeX commands ran sequentially below the 500 MB
virtual-memory cap.

- Tier 0 passes in `0.12 s` at `15332 KiB`: the three new Python files
  compile, the work item, append-only event, strict schema and certificate
  parse, and the final scoped diff has no whitespace error.  The verifier
  applies Draft-2020-12 validation, while the mutation suite rejects an
  injected top-level property.
- The exact producer passes `38/38` checks in `0.05 s` at `17984 KiB`.  The
  method-distinct verifier passes `52/52` in `0.13 s` at `24660 KiB`.  It
  generates roles from the ten unordered bridge cuts and uses the closed
  binomial contraction rather than the producer's internal-edge orientation
  enumeration.  The focused suite contains `48` tests: one positive check and
  `47` adversarial mutations.  All pass in `3.240 s` (`3.31 s` enclosing wall
  time) at `25840 KiB`.
- The affected Tier-2 chain runs `95` predecessor tests and six independent
  verifiers for the frame ledger, active MSbar loop, ten-channel instrument,
  connected tree column, fully rearranged physical packet and UV hard law.
  It passes in `1.91 s` at `73552 KiB`.
- Papers V and VI compile twice with no undefined citation or reference and
  no new overfull box.  Their PDFs are `81` and `69` pages and contain
  `748913` and `705908` bytes, with SHA-256
  `e8769046b2a817ff50789be27e306d97c1d6aa0204238fdb8fd1e96fd181d594`
  and
  `1c2be7887e0afb8f630e5c958317b173aeb9a15b83ca03e870c7ab6bebea6b2f`.
  The final four-pass build took `2.12 s` at `50992 KiB`.  Paper V retains six
  known overfull boxes and Paper VI two.
- Tier 3 is fail-closed, not a repository-wide pass.  With system tools ahead
  of semantic-search shims, `3325` tests ran in `707.684 s` (`708.73 s`
  enclosing wall time) at `391636 KiB`, with the established `31` failures
  and `9` skips.  All `48` new tests pass.  The failures remain older
  certificate drift and the fifteen-path `chain_imports` policy list; none is
  counted as a pass.
- The append-only planning fold accepts `1579` nodes with zero invalid items
  and zero malformed events in `1.47 s` at `14188 KiB`.
- The advisory Science Forge shadow wrapper exits zero by design in `2.03 s`
  at `335808 KiB`, but its bridge audit remains fail-closed at the known
  toolchain/standard-library `E9118` mismatch.  Its read-only census finds
  `1629` certificates and `1410` verifier files.  This advisory exit is not
  theorem evidence.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` covariant loop theorem.  No classical freeze, QME
state, residual transfer, release or `LORENTZIAN-CAUSAL` state changed.  The
final certificate SHA-256 before staging is
`6aecc094f44505270c66b919bd8d44e58ac6faaf42ac61d7f263da79928b33e6`.

CLOSE-OUT: DONE -- the last direct-auxiliary covariant connected six-leg loop
is computed, its forest subtraction and RG normalization are exact, and the
remaining finite-time object is isolated as an off-diagonal third-Dyson
kernel rather than the already known energy-diagonal (B_T).

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1.json`
