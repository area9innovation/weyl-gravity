# BT off-diagonal two-angle detector through lambda six

Certificate:
REVERSE_PHYSICS_BT_TWO_ANGLE_COHERENT_Q6_DETECTOR_V1.

Dependencies: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE.

Lifecycle: COEFFICIENT_COMPUTED.

## Result

The record of two distinct hard Bateman--Turok scattering-angle modes can be
erased by a genuinely off-diagonal positive detector without changing the
complete probability through \(\lambda^6\).

Let the two orthogonal output modes have equal leading normalization and
centres \(c_1,c_2\in(-1,1)\).  The fixed-\(s\) four-point BT density is
angle independent.  After aligning the conventional phases of the two output
kets, its angle-record vector is therefore

\[
 X_2=x_2\binom{1}{1}.
\]

On the two-angle record space define

\[
 P_+={1\over2}\begin{pmatrix}1&1\\1&1\end{pmatrix},
 \qquad
 P_-={1\over2}\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\]

For \(0<\epsilon\leq1\), the click effect and its binary complement are

\[
 E_\epsilon=P_++(1-\epsilon)P_-
 =\begin{pmatrix}
 1-\epsilon/2&\epsilon/2\\
 \epsilon/2&1-\epsilon/2
 \end{pmatrix},
\]

\[
 E_{\rm no}=I-E_\epsilon=\epsilon P_-.
\]

Thus \(E_\epsilon\) has eigenvalues \(1\) and \(1-\epsilon\), while
\(E_{\rm no}\) has eigenvalues \(0\) and \(\epsilon\).  Both are positive,
they sum to the identity, and the click effect has nonzero off-diagonal
entries whenever \(\epsilon>0\).  At \(\epsilon=1\), the click is the pure
symmetric projection \(P_+\): it records a coherent angle mode and contains
no information saying which of the two angles occurred.

The decisive identity is

\[
 E_\epsilon X_2=X_2.
\]

For the arbitrary complete order-\(\lambda^4\) output \(X_4\), self-adjointness
then gives

\[
 \langle X_2,E_\epsilon X_4\rangle
 =\langle E_\epsilon X_2,X_4\rangle
 =\langle X_2,X_4\rangle.
\]

Consequently both the leading norm and the complete \(X_2\)--\(X_4\) cross
are identical to their recorded \(I_2\) values.  If \(q_4\) is the common
one-mode leading probability and \(R_6(c_i)\) the certified complete
fibrewise coefficient, then

\[
 \boxed{
 q_\epsilon(c_1,c_2;f,T)
 =2q_4\left[
 1+\lambda^2\,{R_6(c_1;f,T,\mu)+R_6(c_2;f,T,\mu)\over2}
 \right]+O(\lambda^8).}
\]

This expression is independent of \(\epsilon\).  In particular, the recorded
two-angle effect, every partially coherent effect above, and the pure
coherent symmetric click give exactly the same \(q_4\) and \(q_6\)
coefficients.

## Exact rational two-mode fixture

The construction is not restricted to an abstract pair of labels.  Choose

\[
 c_1=0,\qquad c_2={3\over5},
\]

and keep the common incoming momenta

\[
 p_0=k_0=(6/5,6/5,0,0),\quad
 p_1=(1,-3/5,4/5,0),\quad
 p_2=(1,-3/5,-4/5,0).
\]

The two outgoing active pairs are

\[
 \begin{array}{c|cc}
 c&k_1&k_2\\ \hline
 0&(1,-3/5,0,4/5)&(1,-3/5,0,-4/5)\\
 3/5&(1,-3/5,12/25,16/25)&
      (1,-3/5,-12/25,-16/25).
 \end{array}
\]

Every vector is exactly null and both rows conserve the same momentum.  Their
active invariants are

\[
 (t,u)_{c=0}=(-32/25,-32/25),
 \qquad
 (t,u)_{c=3/5}=(-64/125,-256/125).
\]

After one common scale by \(25\), every spatial component lies on one integer
momentum lattice.  Thus the two reduced modes have a common finite-box
realization and can be treated as orthogonal output modes with equal
normalization.

## Why the equality stops at the next order

Write the complete order-\(\lambda^4\) correction as

\[
 Y_4=\binom{Y_4(c_1)}{Y_4(c_2)}.
\]

The recorded identity effect assigns its known squared-norm term

\[
 \|Y_4(c_1)\|^2+\|Y_4(c_2)\|^2.
\]

The off-diagonal effect instead gives

\[
 \langle Y_4,E_\epsilon Y_4\rangle
 =\|Y_4(c_1)\|^2+\|Y_4(c_2)\|^2
 -{\epsilon\over2}\|Y_4(c_1)-Y_4(c_2)\|^2.
\]

The difference is the negative angle variance

\[
 \boxed{
 -{\epsilon\over2}\|Y_4(c_1)-Y_4(c_2)\|^2\leq0.}
\]

It enters probability at order \(\lambda^8\), because \(Y_4\) is an
order-\(\lambda^4\) amplitude.  For the exact complex test

\[
 \epsilon={2\over5},\qquad
 Y_4(c_1)=1+2i,\qquad Y_4(c_2)=-3+i,
\]

the recorded norm is \(15\), the coherent norm is \(58/5\), and the
difference is \(-17/5\).

This does not compute the full \(q_8\) coefficient.  The \(X_2\)--\(X_6\)
cross and every other allowed object in the order-\(\lambda^8\) ledger must
be assembled with the same effect.  The result only proves that:

1. coherence cannot change the known probability through \(\lambda^6\); and
2. the first known detector-sensitive term is the displayed
   order-\(\lambda^8\) variance.

## Boundedness and transport

On a common compact hard interval, the predecessor gives
\(|R_6(c)|\leq M_R\).  Hence

\[
 \left|{R_6(c_1)+R_6(c_2)\over2}\right|\leq M_R.
\]

The same condition \(\lambda^2M_R<1\) therefore makes the truncated coherent
probability positive uniformly for every \(0<\epsilon\leq1\).

The two-angle effect can be tensored with any of the nine certified
spectator-label record blocks.  This erases the two-angle record inside a
chosen spectator cylinder; it does not coherently erase the spectator label
itself.

## Independent rail

The producer uses symbolic projectors and an arbitrary complex correction
split into real and imaginary parts.  The independent verifier uses only
exact Fraction arithmetic.  It reconstructs \(P_\pm\), checks four
nonzero rational values of \(\epsilon\), and exhausts a finite separating
family of complex corrections.  For every case it independently verifies
the cross invariance and variance identity.  It also reconstructs the two
rational momentum modes, their null conditions, conservation laws,
Mandelstam invariants and common integer-lattice scaling.

## Exact boundary

Established:

- an explicit off-diagonal two-angle click effect;
- a positive binary complement and exact normalization;
- complete erasure of the angle label at the coherent endpoint
  \(\epsilon=1\);
- exact equality of recorded and coherent probabilities through
  \(\lambda^6\);
- the average \(R_6(c_1),R_6(c_2)\) coefficient and its compact bound;
- an exact rational common-box two-mode fixture;
- the first known detector-sensitive order; and
- the negative order-\(\lambda^8\) variance term in the \(Y_4\) norm.

Not established:

- the full order-\(\lambda^8\) probability;
- a continuum-angle coherent detector;
- unequal mode normalizations;
- a BT apparatus interaction that dynamically selects \(\epsilon\) and the
  relative phase;
- either forward endpoint or real--virtual/KLN completion;
- an all-order probability or all-time Møller/LSZ/S operator;
- the standard scalar projector or general Eq. (19);
- gravity, metric BV--BRST, QME or residual transfer;
- anything LORENTZIAN-CAUSAL; or
- literature priority.

## Meaning

The previous barrier was phrased too strongly.  Angle coherence is not
already an obstruction at \(q_6\).  Because the leading fixed-\(s\) output is
symmetric, every positive off-diagonal detector in the family acts exactly
like the recorded detector on all terms that contain that leading amplitude.
The first place coherence can see angular variation is the norm of the next
amplitude, at \(q_8\).

This is still an operational reduced-mode detector.  The public BT Hamiltonian
does not select this measurement, and the result does not establish an
all-time scattering theory.  It nevertheless converts the vague
two-angle-coherence barrier into a concrete next calculation:
the complete \(q_8\) ledger on this same two-mode carrier.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.03 s, 15,416 KB peak RSS.
- Exact producer replay: PASS 35/35, 0.34 s, 68,524 KB peak RSS.
- Independent `Fraction`/spectral verifier: PASS 38/38, 0.07 s,
  24,304 KB peak RSS.
- Scoped tests: PASS 27/27 in 0.17 s, 24,812 KB peak RSS.  These include
  26 adversarial certificate mutations.
- Papers V and VI: PASS under the same cap.  The final builds took 0.49 s
  and 0.51 s, with peak RSS below 52 MB.  The resulting PDFs have 61 pages
  (666,238 bytes) and 57 pages (648,545 bytes), respectively.
- Tier 3: FAIL-CLOSED, 2,292 tests in 688.312 s, with 31 failures and 9
  skips; the enclosing timed process took 689.33 s and peaked at 391,644 KB.
  The new two-angle producer, verifier, schema, mutation and paper-facing
  tests all passed.  The failures are in older content-addressed producer,
  verifier and chain-import rails and do not establish a pass for the full
  repository.
- The advisory Science Forge wrapper exited zero in 3.83 s with 59,388 KB
  peak RSS, but its bridge audit is recorded as FAIL: the Go runtime could
  not reserve page-summary memory under the 500 MB cap.  Its independent
  coverage census reported drift, 1,602 certificates versus the 976-certificate
  2026-07-19 baseline.  Neither advisory finding promotes this certificate.

Tier 3 was required because Papers V and VI promote the complete two-angle
through-\(q_6\) statement.  The failed older rails are not reclassified as
passes and the certificate remains scoped to its independently passing
chain.

Commands:

    ulimit -v 500000; python3 reverse_physics/bt_two_angle_coherent_q6_detector.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_coherent_q6_detector.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_coherent_q6_detector
