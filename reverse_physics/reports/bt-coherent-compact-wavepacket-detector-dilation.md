# BT coherent compact-wavepacket detector dilation

Certificate:
`REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

Erasing the ten BT channel records coherently does not destroy positivity of
the finite-time compact-packet click probability. It changes the amplitude:
the ten channel kernels must be summed before squaring, so all interference
terms return. The resulting effect is nevertheless the adjoint square of one
bounded operator,

\[
 A_{\rm coh}=16\lambda^4\sum_{B=0}^{9}K_{B,T}\otimes R_B,
 \qquad E_{\rm click}=A_{\rm coh}^*A_{\rm coh}.
\]

On the explicit contraction domain, `E_no=I-E_click` is also positive and the
two effects sum to the identity. An exact Julia unitary supplies a normalized
click/no-click detector realization.

This closes the coherent finite-time *measurement* problem at leading order.
It does not close the BT *dynamics* problem. The detector dilation fixes the
Hermitian virtual coefficient that any pseudo-unitary BT completion would
have to reproduce at order `lambda^8`, but the public calculation contains no
such virtual graph. That object remains explicitly missing.

## Exact interference Gram

The predecessor reconstructed ten real `4 x 4` positive-frame residues. Each
`R_B` is zero at one of the ten public coefficient positions and equals `1/4`
at the other nine. Their Hilbert--Schmidt interference Gram is

\[
 H_{AB}=\operatorname{tr}(R_A^TR_B)
 =\begin{cases}9/16,&A=B,\\1/2,&A\ne B,\end{cases}
 \qquad H=\frac{I+8J}{16}.
\]

Thus its spectrum is

\[
 \operatorname{spec}H=\left\{\frac{81}{16},
 \underbrace{\frac1{16},\ldots,\frac1{16}}_{9}\right\}.
\]

The Gram is strictly positive. Signed interference can occur because the
finite-time channel coefficients are complex and their relative phases enter
the cross terms. It is not a negative outcome probability: the complete sum
is the squared norm of the coherent amplitude.

The independent verifier rebuilds the residues from the ten six-bit channel
masks and their complement pairs. It then recomputes all 100 Gram entries over
exact fractions; it does not trust the stored matrix or call the producer.

## Compact packet bound

On the compact regular acceptance of the recorded instrument, let

\[
 \beta_{B,T}(y,x)=\chi_B(y,x)
 \frac{F_T(\delta_B(y,x))}{D_B(y,x)},
 \qquad \sum_B|\chi_B|^2=1,
 \qquad D_B\ge d>0.
\]

The largest eigenvalue of `H` and `|F_T|<=T` give the pointwise estimate

\[
 \left\|\sum_B\beta_{B,T}R_B\right\|_{\rm HS(species)}^2
 \le \frac{81}{16}\sum_B|\beta_{B,T}|^2
 \le \frac{81T^2}{16d^2}.
\]

After integration over the finite incoming and outgoing phase regions,

\[
 \|A_{\rm coh}\|^2\le\|A_{\rm coh}\|_{\rm HS}^2
 \le1296\lambda^8\frac{T^2\mu(X)\mu(Y)}{d^2}.
\]

The coefficient `1296` is exact: `16^2` from the common two-quartic tree
multiplier times the coherent Gram eigenvalue `81/16`. It is nine times the
recorded bound `144`, as expected when the nine aligned exchange images may
add coherently.

Hence

\[
 E_{\rm click}=A_{\rm coh}^*A_{\rm coh},\qquad
 E_{\rm no}=I-E_{\rm click},\qquad
 E_{\rm click}+E_{\rm no}=I
\]

are positive and complete on the sufficient domain

\[
 1296\lambda^8\frac{T^2\mu(X)\mu(Y)}{d^2}\le1.
\]

## Selected scalar source

For the normalized dressed scalar packet `F tensor u0`, the hard channel is
dark and the nine mixed exchange channels have the same species image:

\[
 R_0u_0=0,\qquad R_Bu_0=\frac{u_0}{4},\quad B=1,\ldots,9.
\]

Therefore

\[
 A_{\rm coh}(F\otimes u_0)
 =4\lambda^4\left(\sum_{B=1}^{9}K_{B,T}F\right)\otimes u_0,
\]

and the coherent leading probability is

\[
 q_{\rm click}=16\lambda^8
 \left\|\sum_{B=1}^{9}K_{B,T}F\right\|^2,
 \qquad q_{\rm no}=1-q_{\rm click}.
\]

Unlike the recorded probability, this formula contains every channel cross
term. Their phases can enhance or suppress a particular packet. The total is
nonnegative because it is one norm squared. Unknown order-`lambda` corrections
to the prepared source first affect this probability at order `lambda^9`.

## Exact operational completion

For any contraction `A=A_coh`, define the defect operators

\[
 D_X=(I-A^*A)^{1/2},\qquad D_Y=(I-AA^*)^{1/2}.
\]

Continuous functional calculus gives `D_Y A=A D_X`. Consequently the Julia
operator

\[
 U_J=\begin{pmatrix}D_X&-A^*\\A&D_Y\end{pmatrix}
\]

is exactly unitary. Its first column is a detector isometry,

\[
 \Psi\longmapsto(D_X\Psi,A\Psi),\qquad
 \|D_X\Psi\|^2+\|A\Psi\|^2=\|\Psi\|^2.
\]

The producer checks an exact algebraic diagonal fixture. The independent rail
checks the corresponding rational defect-square identities and, separately,
a two-channel rational compression whose `A^*A` differs from its incoherent
diagonal part. Thus normalization is not obtained by deleting interference.

## What BT dynamics must still supply

Write a hypothetical BT completion on the same positive source/output sector
as

\[
 S=I+\lambda^4L_4+\lambda^8M_8+\cdots,
 \qquad
 L_4=\begin{pmatrix}0&-A_4^*\\A_4&0\end{pmatrix}.
\]

Order-by-order pseudo-unitarity gives

\[
 M_8+M_8^*+L_4^*L_4=0,
\]

so its source block must satisfy

\[
 \operatorname{Herm}(M_8)_{\rm source}=-\frac12A_4^*A_4.
\]

The anti-Hermitian part is not fixed, but it drops out of the order-`lambda^8`
survival probability. This is a sharp testable target, not a derivation of the
target. The available public Hamiltonian calculation supplies the
order-`lambda^4` transition/cut kernel only. It does not supply an
order-`lambda^8` forward/virtual graph or a common-domain finite-time BT
evolution. The Julia complement is therefore an exact operational detector
completion, not the asserted BT time evolution.

## Verification receipts

The scientific Python commands ran sequentially under `ulimit -v 500000`
with Python
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer: `24/24`, pass, `0.27 s`, `65964 KB` maximum RSS;
- independent Fraction/Choi verifier: `24/24`, pass, `0.07 s`, `23488 KB`
  maximum RSS;
- ten tests, including nine decisive mutations: pass, `0.12 s`, `24616 KB`
  maximum RSS;
- final Paper 6 TeX pass: pass, `0.54 s`, `50768 KB` maximum RSS, with no new
  overfull boxes;
- Science Forge `import-program`: pass with `1485` nodes, `0` invalid items
  and `0` malformed events, `6.02 s`, `226028 KB` maximum RSS. As in the
  predecessor, this Go planning check ran without the Python symbolic
  virtual-address cap while resident memory was measured.

Tier 0 covers Python and JSON parsing, TeX compilation, exact diff inspection
and `git diff --check`. Tier 1 is the three scoped rails above. The predecessor
inputs are unchanged, content-pinned and checked passing, which is the affected
Tier-2 import gate. Tier 3 is not required because this is a reduced-mode
scalar coefficient/detector result, not a freeze, shared-core change, QME
promotion or Lorentzian theorem.

## Boundaries and next gate

This result constructs a coherent finite-time click/no-click probability for
the declared compact detector and selected dressed scalar source. It does not
establish:

- the order-`lambda^8` BT virtual graph or its anti-Hermitian phase;
- that the Julia dilation equals public BT evolution;
- the complete connected finite-time amplitude beyond the leading residues;
- a canonical packet, partition, duration or compact acceptance;
- a soft internal-zero or ordinary-Fock infrared limit;
- a detector-independent cross section or exact all-orders probability;
- an all-time Møller, LSZ or `S` operator;
- the standard scalar projector or general Eq. (19);
- loops, KLN completion, gravity, BV/BRST transfer or anything
  `LORENTZIAN-CAUSAL`;
- literature priority.

The next calculation is the explicit order-`lambda^8` BT forward/virtual
packet kernel on this same compact positive sector. Its Hermitian part must
equal `-A_4^*A_4/2`. Agreement would dynamically affiliate the leading
probability identity; disagreement would be an obstruction. General Eq. (19)
remains a separate projector route.

CLOSE-OUT: DONE — coherent finite-time compact-packet detection and its exact
operational dilation are constructed; the matching BT virtual graph is a
precisely specified missing dynamical object.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_COHERENT_COMPACT_WAVEPACKET_DETECTOR_DILATION_V1.json`
