# BT complete connected order-lambda4 packet column

Certificate:
`REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

For the declared timelike three-particle source, the complete connected
order-`lambda^4` BT output is a three-particle tree output in the same positive
ghost-even species sector. There is no connected particle-number leakage and
no connected negative-parity leakage at this order.

Moreover, the actual public ten-channel tree amplitude—not a
detector-partitioned surrogate—defines a bounded positive finite-time effect
on every common compact regular packet acceptance. Its channel terms enter
with their physical unit weights:

\[
 A_{{\rm full},C}=16\lambda^4
 \sum_{B=0}^{9}K_{B,T}\otimes R_B.
\]

The exact bound is

\[
 \|A_{{\rm full},C}\|^2
 \le12960\lambda^8
 \frac{T^2\mu(X)\mu(Y)}{d^2}.
\]

Thus `A_full,C^* A_full,C` and its operational complement form a positive
normalized binary detector on the corresponding contraction domain.

This is stronger than the preceding coherent square-partition detector. That
construction was a valid detector model but multiplied each channel amplitude
by a subordinate `chi_B`. The present column uses one common detector cutoff
`chi_C` and leaves all ten public tree coefficients equal to one. It is the
actual connected tree amplitude restricted to the detector acceptance.

## Complete graph-order classification

The perfect-square cubic and quartic vertices carry coupling degrees

\[
 d(V_3)=1,\qquad d(V_4)=2.
\]

For any connected graph, half-edge counting gives

\[
 d_\lambda=\sum_v(n_v-2)=E+2L-2,
\]

where `E` is the number of external legs and `L` the loop number. At
`d_lambda=4`, the complete list is

\[
 (E,L)=(6,0),(4,1),(2,2),(0,3).
\]

The producer enumerates all twelve `(V3,V4,I,E,L)` rows. The independent rail
derives them a second time using `I=L+V-1` rather than importing that list.

For a three-particle input:

- `(0,3)` is a vacuum graph and does not attach the source;
- `(2,2)` has fewer external legs than incoming particles;
- `(4,1)` would be a `3 -> 1` process; and
- `(6,0)` is the `3 -> 3` tree.

The declared phase chart has

\[
 P=(16/5,0,0,0),\qquad P^2=256/25.
\]

A sole massless output would obey `p^2=0`, so energy-momentum conservation
excludes the `(4,1)` process exactly. The only source-connected type is
therefore `(6,0)`. Its three vertex topologies are precisely

\[
 V_4^2,\qquad V_3^2V_4,\qquad V_3^4,
\]

the three public six-point tree families.

This is a theorem about the connected column. Lower-order connected processes
composed with spectators are disconnected contributions to the full
three-particle evolution and retain a separate ledger.

## Complete species closure

On the eight three-particle species strings, complement parity is

\[
 \kappa_3|x\rangle=|7-x\rangle.
\]

The public six-point Choi coefficient obeys, at arbitrary kinematics,

\[
 \kappa_3A_6\kappa_3=A_6.
\]

The independent verifier reconstructs the generic `8 x 8` coefficient
placement directly from the ten channel masks and their complements. It
checks coefficientwise that

\[
 U_+^TA_6U_-=0,
 \qquad U_-^TA_6U_+=0.
\]

The even basis

\[
 u_x=\frac{|x\rangle+|7-x\rangle}{\sqrt2},
 \qquad x=0,1,2,3,
\]

has Krein Gram `I_4`. Hence the complete connected tree maps the positive
even source sector into the positive even output sector at every momentum.
The negative block exists for a negative-parity input, but it is not reached
from the declared source.

Combining graph order and parity therefore closes the *type* of the connected
output:

\[
 \boxed{\text{three-body momentum}\ \otimes\ \mathbb C^4_{\kappa=+1}}.
\]

## The unpartitioned finite-time column

Let `C` be one common compact subset of incoming/outgoing three-body phase
space. Use a single detector cutoff `chi_C` with `|chi_C|<=1`. For each
unordered channel choose its future orientation and write

\[
 \delta_B=q_B^0-|\mathbf q_B|,
 \qquad D_B=q_B^0+|\mathbf q_B|\ge d>0
\]

on `C`. Define

\[
 \beta_{B,T}(y,x)=\chi_C(y,x)
 \frac{F_T(\delta_B(y,x))}{D_B(y,x)}.
\]

Every channel uses the same acceptance and retains its unit tree coefficient.
There is no square partition `sum |chi_B|^2=1` in this amplitude.

The exact ten-residue interference Gram is

\[
 H=\frac{I+8J}{16},\qquad \lambda_{\max}(H)=\frac{81}{16}.
\]

Since all ten coefficients obey `|beta_B,T|<=T/d`,

\[
 \sum_B|\beta_{B,T}|^2\le\frac{10T^2}{d^2},
\]

and therefore

\[
 \left\|\sum_B\beta_{B,T}R_B\right\|_{\rm HS(species)}^2
 \le\frac{405T^2}{8d^2}.
\]

After integrating over `X x Y` and restoring the common `16 lambda^4`
multiplier,

\[
 \|A_{{\rm full},C}\|^2
 \le\|A_{{\rm full},C}\|_{\rm HS}^2
 \le12960\lambda^8
 \frac{T^2\mu(X)\mu(Y)}{d^2}.
\]

The factor `12960` is ten times the predecessor's `1296`: the predecessor used
the square-partition identity to bound the channel coefficient norm by one,
whereas the actual unit-weight tree sum has ten bounded entries. This is a
sufficient bound, not claimed optimal.

On

\[
 12960\lambda^8\frac{T^2\mu(X)\mu(Y)}{d^2}\le1,
\]

the effects

\[
 E_{\rm click}=A_{{\rm full},C}^*A_{{\rm full},C},\qquad
 E_{\rm no}=I-E_{\rm click}
\]

are positive and sum to the identity.

## Dressed scalar source

For `Psi_in=F tensor u0`, the hard channel remains dark and the other nine
residue images coincide:

\[
 R_0u_0=0,\qquad R_Bu_0=u_0/4\quad(B=1,\ldots,9).
\]

Consequently the actual connected compact-tree probability is

\[
 q_{\rm click}=16\lambda^8
 \left\|\sum_{B=1}^{9}K_{B,T}F\right\|^2,
 \qquad q_{\rm no}=1-q_{\rm click}.
\]

All coherent channel interference is retained. Positivity follows from the
single norm squared, not from deleting its cross terms.

## What remains of outside leakage

The previous survival/leakage theorem left `B_out` abstract. For the connected
order-`lambda^4` column, the present result reduces it to

\[
 B_{\rm out}:\quad
 \text{three-body positive-even momentum states outside }C.
\]

There are no other connected particle numbers and no negative-parity output
from the declared source at this order. This is a substantial closure of the
output ledger, but it is not yet a global operator theorem.

The remaining connected boundary is the set where one or more `q_B=0`. The
compact proof uses `D_B>=d>0`; it does not decide whether the exact phase-space
measure makes the finite-time kernel square integrable as `d -> 0`. That is
now the next calculation.

Disconnected spectator terms are a separate issue. They arise from lower
connected blocks composed with identity particles and are required for the
complete order-`lambda^4` three-particle evolution, but not for the connected
six-point column certified here.

## Verification receipts

All scientific commands ran sequentially under `ulimit -v 500000` with
Python `/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer: `25/25`, pass, `0.04 s`, `16892 KB` maximum RSS;
- independent graph/Choi/Fraction verifier: `24/24`, pass, `0.10 s`,
  `23648 KB` maximum RSS;
- eleven tests, including ten decisive mutations: pass, `0.17 s`, `24752 KB`
  maximum RSS.

Papers 5 and 6 compiled twice with `pdflatex -interaction=nonstopmode
-halt-on-error` under the same memory cap. Their final passes took `0.48 s`
and `0.51 s`, at `50824 KB` and `50560 KB` maximum RSS; no new overfull boxes
were introduced. The append-only planning fold imported `1489` nodes with
zero invalid items and zero malformed events in `6.00 s` at `255772 KB`
maximum RSS.

Tier 0 covers Python/JSON parsing, TeX compilation, exact staged-diff
inspection and `git diff --check`. Tier 1 is the scoped producer, independent
verifier and mutation suite. The mathematical predecessors are unchanged,
content-pinned and checked passing, which supplies the affected Tier-2 import
gate. Tier 3 is not required because this is a reduced-mode coefficient
theorem, not a freeze, shared-core change, QME promotion or Lorentzian
theorem.

## Boundaries and next gate

This result does not establish the disconnected spectator contribution, a
bounded global soft-complete kernel, an integrated cross section, the forward
graph, an all-orders finite-time probability, an all-time operator, general
Eq. (19), loops/KLN completion, gravity, BV/BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

The next connected calculation is exact and local: classify every `q_B=0`
stratum in the five-dimensional phase chart and determine the measure power
of

\[
 \left|F_T(\delta_B)/D_B\right|^2.
\]

That will prove either square integrability of the actual finite-time column
or the first precise infrared divergence. No particle-number or species
classification remains open for this connected order.

CLOSE-OUT: DONE — the complete source-connected order-`lambda^4` codomain is
positive-even three-body phase space, and the actual unpartitioned ten-channel
tree amplitude gives a positive normalized compact finite-time packet effect;
only its soft/global momentum domain and disconnected spectator completion
remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json`
