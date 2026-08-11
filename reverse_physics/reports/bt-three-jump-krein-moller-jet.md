# BT three-jump Krein--Møller coupling jet

## Result

The three amplitude-affiliated Bateman--Turok history jumps do close into one
finite reversible coupling jet on their common reduced quotient.  This is a
`LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `CLASSIFIED` result.  It constructs the
incoming Møller Taylor column through the complete available tree order.  It
also proves that this column cannot come from an ordinary bounded generator in
the additive resolution variable.

Let the rooted-comb history levels have dimensions

\[
  1\longrightarrow3\longrightarrow12\longrightarrow60
\]

and let \(B_k\) be the child--parent incidence matrix.  Exact enumeration gives

\[
 B_k^TB_k=(k+3)I,
 \qquad
 q_0=\frac1{48},\quad q_1=\frac5{64},\quad q_2=\frac{27}{400}.
\]

For equal-edge forward blocks \(F_k=\alpha_kB_k\otimes I_2\), the unique
positive weights whose constant skew exponential reproduces the physical
leading coefficient of every selected history are

\[
 \alpha_k^2=(k+1)q_k,
 \qquad
 (\alpha_0,\alpha_1,\alpha_2)
 =\left(\frac{\sqrt3}{12},\frac{\sqrt{10}}8,\frac9{20}\right).
\]

The generator \(K=F-F^\dagger\) contains every reverse block, including a
nonzero map from the three-emission level back to the two-emission level.  It
is therefore not the earlier artificial absorbing closure.

## Exact finite column

Put \(U_x=\exp(xK)\) and \(a=x^2\).  A selected level-\(k\) history has leading
amplitude

\[
 [U_x]_{h_kh_0}
 =\frac{x^k}{k!}\prod_{j=0}^{k-1}\alpha_j+O(x^{k+2}),
\]

so its leading probability is

\[
 \frac{a^k}{k!}\prod_{j=0}^{k-1}q_j.
\]

The three selected-history amplitudes are

\[
 \frac{\sqrt3}{12},\qquad
 \frac{\sqrt{30}}{192},\qquad
 \frac{\sqrt{30}}{1280},
\]

and summing respectively over 3, 12, and 60 histories gives

\[
 P_1(a)=\frac a{16}+O(a^2),\qquad
 P_2(a)=\frac{5a^2}{512}+O(a^3),\qquad
 P_3(a)=\frac{9a^3}{8192}+O(a^4).
\]

The hard amplitude begins with \(1-x^2/32\), hence its probability begins
with \(1-a/16\).  This exactly extends the certified first-jump
pseudo-unitary witness.  The two-species carrier has dimension 152, the
generator has rank 52, and its 100-dimensional kernel consists of
nondegenerate dark history combinations on the positive quotient.

Any later fourth forward block and its reverse adjoint are graph distance four
from the incoming state.  They cannot change the projections displayed above
through order \(x^3\).  This justifies the finite jet without treating the
three-emission level as physically terminal.

## Radial reduction

The normalized uniform history vector at each level spans an invariant
four-dimensional block for each quotient species.  Its edge couplings are

\[
 \beta_0=\frac14,qquad
 \beta_1=\frac{\sqrt{10}}4,qquad
 \beta_2=\frac{9\sqrt5}{20},
\]

and the radial generator is

\[
 K_{\rm rad}=
 \begin{pmatrix}
 0&-\beta_0&0&0\\
 \beta_0&0&-\beta_1&0\\
 0&\beta_1&0&-\beta_2\\
 0&0&\beta_2&0
 \end{pmatrix}.
\]

Its characteristic polynomial is

\[
 z^4+\frac{17}{10}z^2+\frac{81}{1280}.
\]

The two frequency squares are

\[
 \omega_\pm^2=\frac{68\pm\sqrt{4219}}{80}>0,
\]

because \(68^2-4219=405\).  Thus the finite witness is stable and
oscillatory; the obstruction below is not an unstable eigenvalue.

## Exact additive-resolution obstruction

The physical resolution length is \(a=x^2\).  Therefore

\[
 \|P_\perp U_{\sqrt a}e_0\|^2
 =\frac a{16}+O(a^2).
\]

If instead a bounded family on a fixed finite carrier were strongly
differentiable in additive resolution,

\[
 V(a)=I+aG+o(a),
\]

then its off-diagonal transition amplitude would be \(O(a)\) and its
probability would be \(O(a^2)\).  This contradicts the nonzero coefficient
\(1/16\).  Equivalently,

\[
 \left\|\frac{(U_{\sqrt a}-I)e_0}{a}\right\|^2
 =\frac1{16a}+O(1),
\]

which diverges as \(a\to0^+\).  Moreover \(U_{\sqrt{a+b}}\) is not
\(U_{\sqrt a}U_{\sqrt b}\).  The exact finite coupling jet is consequently
not an additive-resolution Hamiltonian or semigroup.

The next constructive alternatives are a quantum-stochastic unitary dilation,
where an Itô isometry naturally converts amplitudes of order \(\sqrt a\) to
probabilities of order \(a\), or an unbounded rigged/Jordan implementation.
Neither continuation is constructed here.

## Independent verification

The producer constructs histories by canonical leaf insertion and derives the
closed ladder formulas.  The independent verifier instead enumerates every
rooted comb by choosing its cherry and permuting the complement, reconstructs
each parent by deleting the newest leaf, and rebuilds all incidence matrices.
It imports the three rates separately from the five-, six-, and seven-point
amplitude certificates.  It then obtains the incoming Taylor column by
repeated exact matrix action, reconstructs the sparse generator and radial
block, and checks the strong-derivative scaling argument.  It does not import
the producer or its history routines.

The certificate is
`REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1`.

## Claim boundary

This result does not establish a strongly differentiable additive-resolution
generator, a time-local BT Hamiltonian, a quantum-stochastic or rigged
continuation, a fourth jump, higher-order coefficients of the finite
exponential as BT amplitudes, a complete probability, a continuum trace
domain, a global Møller/LSZ/S operator, Eq. (19), a gravitational or BRST lift,
a new spacetime dimension, anything `LORENTZIAN-CAUSAL`, or literature
priority.

## Verification receipt

All scientific Python and TeX processes run sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON/schema parse on scoped artifacts | PASS | 0.04 / 0.03 s | 15,832 / 14,012 KB |
| 0 | `git diff --check` on scoped paths | PASS | below 0.1 s | negligible |
| 1 | exact producer and certificate drift check | PASS, 34/34 | 0.80 s | 70,592 KB |
| 1 | independent history/matrix/scaling verifier | PASS, 24/24 | 0.48 s | 74,208 KB |
| 1 | producer/verifier plus eleven falsifying mutations | PASS, 13/13 | 4.07 s | 74,176 KB |
| 1 | Paper V two-pass PDF build | PASS; no new overfull box | 0.42 / 0.42 s | 50,744 / 50,904 KB |
| 1 | Paper VI two-pass PDF build | PASS; no overfull box | 0.44 / 0.44 s | 50,716 / 50,840 KB |
| advisory | Science Forge programme import | 1,397 nodes; 0 invalid items; 0 malformed events | 5.61 s | 591,352 KB |

The content-addressed five-, six-, seven-point, branching, and pseudo-unitary
inputs are unchanged.  Tier 2 is therefore unnecessary: this certificate is a
new consumer of their pinned outputs and does not change any mathematical
input used by those chains.  Tier 3 is unnecessary because there is no freeze,
release, shared-core change, lifecycle promotion beyond `CLASSIFIED`, complete
probability, Eq. (19), gravitational transfer, or Lorentzian theorem.  No
skipped rail is counted as a pass.

The Science Forge shadow rail exited zero only in advisory mode.  Its bridge
audit failed on the pre-existing Forge binary/stdlib mismatch and compiler
diagnostic E9118; its coverage census reported drift from the 976-certificate
baseline to 1,535 certificates.  These are recorded findings, not successful
verification of this result.

## Next gate

Construct the minimal quantum-stochastic Krein-unitary dilation of the three
quotient jump blocks in additive resolution, with both creation and reverse
annihilation terms.  Verify its vacuum Itô table against the certified
branching instrument and compare its domain with the existing rigged
Jordan/Abel carrier.  A pass would supply an additive-resolution Møller
cocycle; a failure would isolate the remaining domain or trace obstruction.

CLOSE-OUT: DONE — the three amplitude-affiliated jumps close into an independently verified finite reversible coupling jet, while an ordinary bounded additive-resolution generator is exactly obstructed and every higher claim remains fail-closed
EVIDENCE: reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_JUMP_KREIN_MOLLER_JET_V1.json
