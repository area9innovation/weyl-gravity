# BT six-point history incidence isometry

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The six-point factorization residue has a canonical positive history carrier
once its two kinds of labels are kept distinct. The final auxiliary-species
assignment (S) and the intermediate channel (A) are not two copies of the
same physical state space. They form ninety allowed histories

\[
 {cal H}=\{(S,A):S\ne A\}.
\]

This carrier supports an exact isometry, a normalized detector POVM, and a
finite probability-conserving channel-label instrument with survival. The
time scale and momentum-wave-packet embedding remain to be derived from BT
dynamics.

## The typed incidence lift

Let (B:\mathbb R^{10}\to\mathbb R^{90}) lift an intermediate-channel vector
to histories, and let (C:\mathbb R^{90}\to\mathbb R^{10}) coherently sum
histories with the same final species assignment:

\[
 B_{(S,A),B'}=\frac14\delta_{A B'},qquad
 C_{S',(S,A)}=\delta_{S'S},qquad S\ne A.
\]

Every channel has nine allowed histories, hence

\[
 B^TB=\frac9{16}I_{10},qquad
 W_{\rm hist}=\frac43B,qquad W_{\rm hist}^TW_{\rm hist}=I_{10}.
\]

Coherent collapse reconstructs the complete residue:

\[
 CB=\frac14(J-I).
\]

The normalized collapse (ar C=C/3) is a coisometry. Moreover
(ar C W_{m hist}=(J-I)/9) is invertible, so the history range has zero
intersection with the collapse kernel.

The incidence graph is invariant under simultaneous permutations of (S)
and (A). The physical crossing group is the induced (S_6) subgroup on the
ten unordered three-particle channels. An equal nonnegative weight (w) on
every allowed edge is isometric exactly when (9w^2=1), fixing (w=1/3).
Thus this symmetry class has no remaining normalization choice.

## Where interference comes from

With the common reduced Born factor two, fully resolved histories use
(E_{m res}=2I), while coherent species detection uses
(E_{m coh}=2C^TC). Their pullbacks are

\[
 B^TE_{m res}B=\frac98I,qquad
 B^TE_{m coh}B=J+\frac18I.
\]

Their difference is the signed interference matrix:

\[
 B^T(E_{m coh}-E_{m res})B=J-I.
\]

The interference is therefore a difference between positive detector
quadratic forms. It is not a negative-probability outcome. Partial coherence
is described by

\[
 E_\mu=2\big[(1-\mu)I+\mu C^TC\big],\qquad0\le\mu\le1,
\]

whose pullback is

\[
 G_\mu=\frac98I+\mu(J-I).
\]

Its singlet eigenvalue is (9/8+9\mu), and the other nine eigenvalues are
(9/8-\mu). Local positivity persists throughout the resolution interval.

## Normalized history detector

The unnormalized Born weight is eighteen times the effect

\[
 P_\mu=\frac{(1-\mu)I+\mu C^TC}{9}.
\]

On the ten-dimensional coherent subspace its eigenvalue is
((1+8\mu)/9); on the eighty-dimensional complement it is
((1-\mu)/9). Therefore (0\le P_\mu\le I), and
({P_\mu,I-P_\mu}) is a normalized two-outcome POVM on the finite history
label space. This is a history-sector detector, not yet a spacetime detector.

## Exact finite channel instrument

Because (W_{m hist}) is isometric, the block

\[
 K=\begin{pmatrix}0&-W_{m hist}^T\\W_{m hist}&0\end{pmatrix}
\]

obeys (K^T=-K) and (K^3=-K). Its exact rotation is

\[
 U_\theta=I+\sin\theta K+(1-\cos\theta)K^2.
\]

The source column is

\[
 U_\theta I_{\rm source}
 =\binom{\cos\theta I_{10}}{\sin\theta W_{m hist}}.
\]

Combining the survival branch with the two history-detector outcomes gives

\[
 E_{\rm surv}=\cos^2\theta I,
\]

\[
 E_{\rm det}=\sin^2\theta W_{m hist}^TP_\mu W_{m hist},
 \qquad
 E_{\rm unres}=\sin^2\theta
 W_{m hist}^T(I-P_\mu)W_{m hist}.
\]

All three are positive and

\[
 E_{\rm surv}+E_{\rm det}+E_{\rm unres}=I_{10}.
\]

This is an exact normalized finite instrument on the channel labels. It fixes
the finite equal-edge incidence part of the Møller defect action, including a
survival branch.

## Remaining physical gate

The parameters (	heta) and (mu) have not been derived from BT dynamics.
The calculation also lacks the finite-time phase/energy kernel, the embedding
of momentum wave packets into the actual incoming and outgoing defect
continua, and a crossing-compatible extension away from the factorization
subspace. Consequently it does not fix the global defect partial unitary or
construct a finite inclusive BT probability.

The next calculation must tensor the incidence isometry with the finite-time
quartic BT kernel and prove that its induced survival and detector effects
agree with the normalized label instrument. No complete Møller/LSZ/S
operator, Eq. (19), loop theorem, gravity/BRST lift, or
`LORENTZIAN-CAUSAL` result follows here.

## Verification receipt

All scientific and TeX processes ran sequentially under `ulimit -v 500000`.

- The producer passed 25/25 exact checks in 1.52 s with 70,768 KB maximum RSS.
- The independent verifier rebuilt the history graph, checked two generators of the simultaneous permutation symmetry, reconstructed both projections, the POVM and the skew instrument, and passed 23/23 checks. The five-verifier affected chain took 3.67 s with 75,780 KB maximum RSS.
- The affected positivity-to-incidence suite passed 28 tests in 4.10 s with 85,664 KB maximum RSS.
- Papers V and VI passed two `pdflatex -interaction=nonstopmode -halt-on-error` runs each. Their second passes took 0.47 s with 50,456 KB and 0.49 s with 50,712 KB maximum RSS.
- Science Forge conformance reports the new work item and event as `OK`; the full planning scan still refuses on ten unrelated pre-existing nonconformances, which are neither repaired nor counted as a pass here.
- The non-certifying prose advisory leaves Paper V's pre-existing parenthetical/abstract findings and Paper VI's pre-existing abstract finding; emphasis, dash, and Paper VI parenthetical budgets remain within their advisory limits.
- Tier 0 includes Python compilation, structured-data parsing, exact staged-diff inspection and `git diff --check`. Tier 2 was required and run because the content-addressed Bateman note and predecessor certificates changed. Tier 3 was not run because this is a scalar reduced-mode coefficient/instrument result, not a freeze, release, shared-core change, or Lorentzian lifecycle promotion.

CLOSE-OUT: DONE -- the ninety-history isometry, normalized history POVM and finite channel-label instrument with survival are exact; BT time/momentum affiliation remains open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_HISTORY_INCIDENCE_ISOMETRY_V1.json`
