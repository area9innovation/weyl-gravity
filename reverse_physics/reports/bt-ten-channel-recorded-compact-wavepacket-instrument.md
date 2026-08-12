# BT ten-channel recorded compact-wavepacket instrument

Certificate:
`REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

All ten finite-time BT six-point channel kernels can be combined into one
positive compact-packet instrument if the detector retains the intermediate
channel as an orthogonal record.  A smooth square partition of unity assigns
the compact acceptance to the channel records.  Where shell neighborhoods
overlap, several records may fire at amplitude level, but their orthogonality
removes signed cross terms from the recorded probability.

For the normalized dressed scalar packet `F tensor u0`, one channel is dark
and nine are visible.  The leading probability is

\[
 q_{\rm click}=16\lambda^8
 \sum_{B=1}^{9}\|K_{B,T}F\|^2,
 \qquad q_{\rm no}=1-q_{\rm click}.
\]

The ten partitions comprise one hard total-momentum record and nine mixed
exchange records that may reach shell.  This closes ten-channel gluing for a
declared channel-resolving detector on a
compact regular acceptance.  It does not give the coherent probability of a
detector that forgets the channel record.

## The ten residue matrices

The positive three-particle frame has ten public Choi coefficient positions:

\[
 (0,0),(1,3),(2,3),(1,2),(2,2),
 (3,1),(1,1),(2,1),(3,2),(3,3).
\]

For intermediate channel `B`, the exact residue `R_B` is zero at position `B`
and equals `1/4` at the other nine positions.  Thus every residue obeys

\[
 \|R_B\|_{\rm HS}^2=\operatorname{tr}(R_B^TR_B)=\frac9{16}.
\]

Channel zero, with representative mask `7`, is exceptional.  It is the
incoming-versus-outgoing partition, so its intermediate momentum is the fixed
total momentum and

\[
 q_0=P,\qquad q_0^2=P^2=\frac{256}{25}.
\]

It is hard and off resonance throughout the physical chart, not a tenth shell
pole.  Its residue algebra is

\[
 \operatorname{spec}(R_0^TR_0)
 =\left\{0,0,0,\frac9{16}\right\},
 \qquad \operatorname{rank}R_0=1.
\]

The other nine are the mixed incoming/outgoing exchange channels.  They form
the physical shell-capable family and are related by row and column
permutations.  Combinatorially there are
`binom(3,2) binom(3,1)=9` such unordered splits, and the incoming/outgoing
label group `S3 times S3` acts transitively on them; the exact channel-11 shell
witness therefore supplies a relabeled witness for every member.  Their common
Gram spectrum is

\[
 \operatorname{spec}(R_B^TR_B)
 =\left\{0,\frac1{16},
 \frac{2-\sqrt3}{8},\frac{2+\sqrt3}{8}\right\},
 \qquad \operatorname{rank}R_B=3.
\]

For `u0=(1,0,0,0)` in this frame,

\[
 \|R_0u_0\|^2=0,
 \qquad
 \|R_Bu_0\|^2=\frac1{16},\quad B=1,\ldots,9.
\]

Stacking all ten residue matrices has rank four.  The detector therefore sees
the whole positive source space even though each individual channel has a
kernel.

The independent verifier does not import the listed coefficient positions.
It reconstructs the `8 x 8` Choi placement directly from the ten six-bit
representative masks and their complements, performs the positive complement-
pair projection, and obtains all ten stored `4 x 4` residues over exact
fractions.

## Smooth square gluing

Let `C` be a compact detector acceptance in `X times Y`.  It is covered by ten
regular oriented channel neighborhoods `U_B`: one for the hard channel and
nine around the exchange-shell family.  Every neighborhood avoids the soft
point `q_B=0` and has

\[
 D_B=q_B^0+|\mathbf q_B|\ge d>0
\]

after choosing the positive-energy orientation.

Choose smooth functions `psi_B` supported in `U_B` with no common zero on
`C`, and set

\[
 \chi_B=\frac{\psi_B}
 {\sqrt{\sum_A\psi_A^2}}.
\]

Then

\[
 \sum_B|\chi_B|^2=1
\]

on `C`.  This is an amplitude partition, rather than an ordinary linear
partition, because probabilities are quadratic.  It remains valid on every
pairwise or higher overlap stratum; no choice of a preferred channel is
needed there.

## Direct-sum packet operator

For every channel define

\[
 \beta_{B,T}(y,x)=
 \chi_B(y,x)\frac{F_T(\delta_B(y,x))}{D_B(y,x)},
 \qquad
 (K_{B,T}F)(y)=\int_X\beta_{B,T}(y,x)F(x)d\mu(x).
\]

Because `|F_T|<=T`, the square partition gives the joint pointwise bound

\[
 \sum_B|\beta_{B,T}(y,x)|^2\le\frac{T^2}{d^2}.
\]

After integrating over `X times Y`,

\[
 \sum_B\|K_{B,T}\|_{\rm HS}^2
 \le\frac{T^2\mu(X)\mu(Y)}{d^2}.
\]

The recorded amplitude maps into ten orthogonal output copies:

\[
 A_{\rm rec}=16\lambda^4
 \bigoplus_{B=0}^{9}(K_{B,T}\otimes R_B).
\]

Consequently

\[
 \|A_{\rm rec}\|^2
 \le\|A_{\rm rec}\|_{\rm HS}^2
 \le144\lambda^8
 \frac{T^2\mu(X)\mu(Y)}{d^2}.
\]

The factor `144` is exact: `16^2` from the tree multiplier times `9/16`
from every residue Gram trace.

## Positive normalized effects

Set

\[
 E_{\rm click}=A_{\rm rec}^*A_{\rm rec}
 =256\lambda^8\sum_B
 K_{B,T}^*K_{B,T}\otimes R_B^TR_B,
\]

and `E_no=I-E_click`.  The click effect is positive.  Both effects are
positive and complete on the sufficient domain

\[
 144\lambda^8\frac{T^2\mu(X)\mu(Y)}{d^2}\le1.
\]

At a simultaneous-shell intersection the direct-sum norm is the sum of the
record norms.  There is no term
`K_A^* K_B tensor R_A^T R_B` for `A != B`.  A rational two-record fixture with
weights `3/5` and `4/5` independently confirms this Gram identity.

## What was and was not glued

The construction glues all ten channel-resolved records on the declared
compact regular acceptance.  It is a legitimate finite-time measurement in
which an apparatus or environment preserves which sequential channel was
resolved.

If the record is erased coherently, amplitudes must instead be summed before
squaring.  The cross terms then reconstruct the already certified indefinite
`J-I` interference structure.  This certificate neither discards those terms
nor proves that virtual contributions make their coherent sum positive.  It
therefore does not claim an unobserved cross section or a global `S`-matrix.

The scalar pullback remains the selected dressed, shift-breaking preparation
on the compact Gaussian detector ideal.  Since the amplitude starts at
`lambda^4`, unknown order-`lambda` source corrections first change the
probability at order `lambda^9`.

## Verification receipts

All scientific commands ran sequentially under `ulimit -v 500000` with
Python `/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer: `28/28`, pass, `0.31 s`, `66940 KB` maximum RSS;
- independent Fraction/Choi verifier: `28/28`, pass, `0.08 s`, `23944 KB`
  maximum RSS;
- ten tests, including nine decisive mutations: pass, `0.19 s`, `24180 KB`
  maximum RSS;
- final Paper 6 TeX pass: pass, `0.55 s`, `51112 KB` maximum RSS, with no new
  overfull boxes;
- Science Forge `import-program`: pass with `1483` nodes, `0` invalid items and
  `0` malformed events, `6.65 s`, `255460 KB` maximum RSS.  As in the
  predecessor, this Go planning check ran without the Python symbolic
  virtual-address cap while resident memory was measured.

Tier 0 includes Python and JSON parsing, TeX compilation, duplicate-key
checks, exact staged-diff inspection and `git diff --check`.  Tier 1 is the
three scoped rails above.  The predecessors are unchanged and content-pinned;
their hashes and `checks.ok` fields supply the affected Tier-2 import gate.
Tier 3 is not required because this is a reduced-mode scalar coefficient and
instrument result, not a freeze, shared-core change, QME promotion or
Lorentzian theorem.

The external Science Forge shadow audit retains the same Forge-binary/stdlib
`E9118` mismatch and stale corpus baseline recorded by the predecessor.  It is
advisory and is not counted as a pass.

## Open gates

The next physical gate is the coherent collapse: sum the ten packet amplitudes
into one unrecorded output and include the BT virtual term before testing
positivity.  The soft `q_B=0` limit is a separate infrared gate.  The Eq. (19)
route remains separate and needs a nonregular ghost-conjugate source/projector
branch.

This result does not establish:

- that an internal channel record is an asymptotic particle or a
  detector-independent observable;
- the unobserved coherent BT probability or a detector-independent cross
  section;
- a canonical packet, detector partition, duration, or acceptance;
- the soft internal-zero or ordinary-Fock infrared limit;
- the complete connected finite-time amplitude or any exact all-order
  probability;
- an all-time Møller, LSZ, or `S` operator;
- the standard scalar projector or general Eq. (19);
- loops, KLN completion, gravity, BV/BRST transfer, or anything
  `LORENTZIAN-CAUSAL`;
- literature priority.

CLOSE-OUT: DONE — all ten finite-time compact packet channel records form one positive normalized dressed-scalar detector instrument across overlap strata, while coherent unobserved scattering remains open.
EVIDENCE: reverse_physics/certificates/REVERSE_PHYSICS_BT_TEN_CHANNEL_RECORDED_COMPACT_WAVEPACKET_INSTRUMENT_V1.json
