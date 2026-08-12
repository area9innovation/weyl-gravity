# BT crossed detector orientation no-go

Certificate: REVERSE_PHYSICS_BT_CROSSED_DETECTOR_ORIENTATION_NO_GO_V1

Lifecycle: CLASSIFIED

Dependencies: LOCAL-ALGEBRAIC, REDUCED-MODE

## Result

The two standard momentum-crossing orientations cannot repair the negative
six-point crossed quotient on the certified factorized strongly ordered
carrier. Momentum crossing sends \(p\) to \(-p\), but the external
virtuality is \(p^2\). It therefore acts trivially on the constant/linear
external-virtuality jet. Both crossing orientations carry the same negative
rank-two species Gram, up to phase.

A positive detector mixture of those orientations remains negative
semidefinite. The missing sign is not an orientation interference effect.

There is a unique algebraic repair among real unit relative signs. The
physical collapse must change from

\[
 R_+=[I_2,I_2]
\]

to

\[
 R_-=[I_2,-I_2].
\]

This selects the complementary quotient, whose fixed-Hilbertized Gram is
positive. But the required operation is the internal dual-number parity
\(\epsilon\mapsto-\epsilon\), not ordinary momentum crossing. It is
anti-Krein on the parent jet and has not been derived from the public BT
asymptotic map or generalized-Born adjoint.

The physical barrier has consequently narrowed again. The next question is
not which momentum orientation to choose; neither works. It is whether BT
dynamics supplies this internal dipole-jet parity, or a genuinely
nonfactorizing crossed \(3\to3\) pre-trace term with the same effect.

## Why ordinary crossing does not flip the jet

The parent external-mass carrier is the dual-number algebra

\[
 \mathbb Q[\epsilon]/(\epsilon^2),
\]

where \(\epsilon\) records the first external-virtuality coefficient. In the
basis \((1,\epsilon)\), its cross pairing is

\[
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

For a scalar leg, standard momentum crossing is \(p\mapsto-p\). Since
\((-p)^2=p^2\), it acts on the virtuality jet as

\[
 C_{\rm mom}=I_2,\qquad C_{\rm mom}^TJC_{\rm mom}=J.
\]

The operation needed to change the relative constant/linear sign is instead

\[
 S_\epsilon=\begin{pmatrix}1&0\\0&-1\end{pmatrix},
 \qquad S_\epsilon^T J S_\epsilon=-J.
\]

Thus \(S_\epsilon\) is anti-Krein. It is additional internal data; it cannot
be inferred from moving a scalar momentum between the incoming and outgoing
sides.

## Positive detector mixtures cannot help

On the crossed sheet write \(q_x>0\) and \(v=a_2/2>0\). The certified
one-branch species block is

\[
 H_\times=-6q_xv I_2.
\]

The two real tree orientations can differ by a relative phase. Their
amplitude vector can be written

\[
 u_\theta=(1,e^{i\theta})^T,
\]

with orientation Gram

\[
 M_\theta=u_\theta u_\theta^\dagger
 =\begin{pmatrix}
 1&e^{-i\theta}\\e^{i\theta}&1
 \end{pmatrix}.
\]

This has eigenvalues \(2,0\), so it is positive semidefinite. The complete
factorized detector block is

\[
 M_\theta\otimes H_\times.
\]

Its only nonzero eigenvalues are negative, with multiplicity two. More
generally, for every positive two-orientation detector density \(M\),

\[
 M\otimes(-6q_xvI_2)\preceq0.
\]

The negative rank is \(2\,\operatorname{rank}(M)\). A positive detector
recombination cannot manufacture a positive species direction from a common
negative block.

This theorem assumes that both orientations restrict to the same certified
strongly ordered species block up to phase. A new nonfactorizing crossed
pre-trace term is not known and is not ruled out.

## Classification of coherent collapses

Retain the crossed diagonal amplitude coefficients

\[
 D=\operatorname{diag}(-q_x,-q_x,v,v)
\]

on the four-component parent/profile carrier with
\(\eta=J\otimes3J\). The species-uniform real coherent-collapse family is

\[
 R_t=[I_2,tI_2],\qquad t\neq0.
\]

The raised pullback

\[
 A_t=\eta^{-1}D^TR_t^T(3J)R_tD
\]

has characteristic polynomial

\[
 z^2(z+2q_xtv)^2.
\]

Its only nonzero eigenvalue is

\[
 \lambda_t=-2q_xtv.
\]

Because \(q_x,v>0\), positivity requires \(t<0\). If crossing is allowed to
change only a real unit relative sign, \(|t|=1\), the repair is unique:
\(t=-1\).

For the outgoing-style continuation \(R_+\), the selected image is

\[
 N_+=\begin{pmatrix}
 v&0\\0&v\\-q_x&0\\0&-q_x
 \end{pmatrix}
\]

with eigenvalue \(-2q_xv\). Its complement

\[
 N_-=\begin{pmatrix}
 v&0\\0&v\\q_x&0\\0&q_x
 \end{pmatrix}
\]

is killed. For the repaired collapse \(R_-\), this disposition reverses:

\[
 R_-DN_+=0,\qquad R_-DN_-=2q_xvI_2,
\]

and the selected complementary quotient obeys

\[
 (N_-^T\eta N_-)J=+6q_xvI_2.
\]

The repair does not take an absolute value of the same negative quotient. It
changes the physical collapse and selects the already existing orthogonal
complement. The relation

\[
 R_-=R_+\operatorname{diag}(I_2,-I_2)
\]

is exactly the internal parity \(S_\epsilon\) on the second block.

## Relation to BT ghost parity

The algebraic sign repair resembles the kind of extra branch operation hidden
ghost parity might supply, but the certificate does not identify them. The
independent perturbative unit-status theorem already shows that a regular
same-chart local-symbol automorphism cannot exchange the two public BT target
fields on the perturbative vacuum. Singular, localized, doubled, nonlocal or
unbounded implementations remain possible.

A physical derivation must show that the regulated crossed five-to-four
amplitude ratio, including the incoming Wightman dual and physical adjoint,
acts as \(S_\epsilon\) on the external-virtuality jet. If it does, the
positive complementary quotient can be composed with the already constructed
bilateral Källén range to affiliate all twelve reversed histories.

If it does not, the only remaining escape inside this route is a
nonfactorizing crossed \(3\to3\) pre-trace term that invalidates the tensor
product \(M\otimes H_\times\).

## Claim boundary

Established exactly:

- ordinary scalar momentum crossing acts trivially on the \(p^2\)
  constant/linear dual-number jet;
- every positive two-orientation detector mixture remains negative
  semidefinite on the factorized crossed species block;
- the complete real species-uniform collapse family has nonzero eigenvalue
  \(-2q_xtv\);
- the unique real unit-sign repair is \(R_-=[I_2,-I_2]\);
- this repair selects the positive complementary quotient;
- its inducing dual-number parity is anti-Krein and distinct from ordinary
  momentum crossing;
- the same classification applies to all twelve reversed histories.

Not established:

- physical BT derivation of \(S_\epsilon\);
- the complete nonfactorizing crossed \(3\to3\) amplitude;
- a positive crossed probability or the twelve physical intertwiners;
- the 300 crossed seven-point sheets or spectator sectors;
- Eq. (19), a spacetime Møller/LSZ/S operator, a gravity/BRST lift, or
  anything LORENTZIAN-CAUSAL.

## Verification receipt

- Exact producer: 26/26 checks passed in 0.52 s with 68,740 KiB peak RSS.
- Independent verifier: 32/32 checks passed in 0.45 s with 72,192 KiB peak
  RSS.
- Mutation suite: 19/19 tests passed in 7.33 s (7.36 s including timing
  overhead) with 72,648 KiB peak RSS.
- Python byte compilation passed in 0.03 s with 15,128 KiB peak RSS; all four
  new JSON files parsed in 0.02 s with 13,180 KiB peak RSS.
- Paper V rebuilt in two passes at 0.46 s and 0.47 s; only its four
  pre-existing overfull boxes remain. Paper VI rebuilt in 0.48 s and 0.49 s
  with no warnings. PDF text extraction found the new theorem in both.
- `git diff --check` passed with index preloading disabled.
- The narrow Science Forge programme import produced 1,439 nodes with zero
  invalid items and zero malformed events in 7.71 s with 247,720 KiB peak RSS.
- Tier 3 is not required: this is an isolated reduced-mode certificate, not a
  freeze, lifecycle promotion, shared core change, or release.
