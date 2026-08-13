# Compact-sphere BT dark-port probability at order lambda eight

Certificate:
`REVERSE_PHYSICS_BT_COMPACT_SPHERE_DARK_PORT_ABSOLUTE_Q8_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED` on a nonempty compact fixed-total-momentum
packet class.  Finite invariant-mass and total-momentum bandwidth remains
`NOT_CONSTRUCTED`.

## Result

The positive absolute dark-port coefficient is not an artifact of two
zero-width angular modes.  It survives on two orthogonal, equal-area compact
packets of the invariant fixed-(P) two-body sphere, together with compact
incoming and positive spectator packets.

The certified strict bound is

\[
 \boxed{
 {Q_{8,-}\over\bar q_{4,\mathrm{pkt}}}
 >{2401\over2284119687168}>{1\over10^9}.}
\]

Here (ar q_{4,\mathrm{pkt}}>0) is the leading one-packet coefficient and

\[
 q_-(\lambda)=\lambda^8Q_{8,-}+O(\lambda^{10}).
\]

The packet class has positive measure in every angular direction on the
fixed-(P) sphere.  The result is not yet a packet across different total
momenta or invariant masses.

## Invariant packet geometry

For fixed timelike two-body momentum (P), parameterize the massless shell by

\[
 n=(x,\sqrt{1-x^2}\cos\varphi,
       \sqrt{1-x^2}\sin\varphi).
\]

Up to a common positive (P^2)-dependent factor, the invariant measure is

\[
 d\Omega=dx\,d\varphi.
\]

This measure matters.  The earlier equal-lab-energy family is the equator
(x=0), whose invariant angular factor is (d\varphi), not
(dc) for (c=\cos\varphi).

Put

\[
 \delta={1\over10000},\qquad
 \alpha=\arccos{3\over5},
\]

and choose the equal-width azimuth bins

\[
 I_0=[\pi/2-\delta,\pi/2+\delta],\qquad
 I_1=[\alpha-\delta,\alpha+\delta].
\]

Exact alternating bounds for (sin\delta) and (cos\delta) give disjoint
rational enclosures for their (c)-ranges.  For every sufficiently small
positive latitude thickness (epsilon), define

\[
 B_j(\epsilon)=\{|x|\leq\epsilon,\ \varphi\in I_j\}.
\]

Both cells have invariant measure (4\epsilon\delta).  Therefore

\[
 h_j={\mathbf1_{B_j}\over\sqrt{4\epsilon\delta}}
\]

are normalized, orthogonal and equal-area packet modes.  The leading
four-point BT kernel is angle-independent at fixed (P^2), so the two
projected leading amplitudes agree, including their phase.

## Exact equatorial margins

At (kappa T=1), only two terms of the connected tree bracket depend on
(c):

\[
 {10\sin a_t(c)\over32(1-c)/25}
 +{10\sin a_u(c)\over32(1+c)/25},
\]

where

\[
 a_t(c)={2\over5}(\sqrt{17-8c}-3),\qquad
 a_u(c)={2\over5}(\sqrt{17+8c}-3).
\]

The common resonant and fixed-gap terms cancel between packet cells.  Rational
square-root enclosures followed by alternating sine bounds prove uniformly
for every equatorial (arphi_0\in I_0) and
(arphi_1\in I_1) that

\[
 \boxed{W(\cos\varphi_1,1)-W(\cos\varphi_0,1)>{1\over20}.}
\]

The loop simplifies further.  Define

\[
 H(y)=\sum_{n\geq1}{(-1)^{n+1}y^n
 \over2n(2n+1)(2n)!},
\]

so that

\[
 C(\sqrt y)=1-\gamma-\frac12\log y+H(y).
\]

For

\[
 y_t(c)={32(1-c)\over25},\qquad
 y_u(c)={32(1+c)\over25},
\]

one has

\[
 y_t(c)y_u(c)=\left({32\over25}\right)^2(1-c^2).
\]

This identity cancels the explicit (-\log(1-c^2)) in the loop against the
two logarithms coming from (C).  The scale, finite local constant and all
remaining common terms cancel between cells.  Thus the complete angular
dependence is

\[
 B(c)=\text{common}-2[H(y_t(c))+H(y_u(c))].
\]

Termwise interval evaluation of the even lower and odd upper partial sums
then proves

\[
 \boxed{B(\cos\varphi_1)-B(\cos\varphi_0)>{1\over225}}
\]

uniformly on the two equatorial bins.  The certificate stores the complete
rational endpoints and canonical hashes; no floating-point number enters the
claim.

## Thickening all fixed-P packet variables

The equatorial bins alone still have zero sphere measure.  The hard finite-time
kernel supplies the missing transverse step.

For the tree, (F_T(\Delta)) is entire in the energy mismatch and every
oriented denominator (D_A) stays nonzero on a sufficiently small hard tube.
The compact tree kernel is therefore jointly continuous in output latitude,
incoming active variables and spectator variables.  The renormalized
finite-time loop kernel is likewise continuous while both light-cone gaps
remain nonzero.

The equatorial product (I_1\times I_0) is compact and has strict rational
margins.  Joint continuity therefore supplies one common open product
neighborhood in:

- output latitude;
- incoming fixed-(P) active variables; and
- the positive spectator momentum.

The neighborhood can be chosen so that its pointwise tree-kernel contrast is
greater than (1/40), while the loop contrast is greater than (1/230).
Choose nonzero, nonnegative normalized compact packets inside it.

The tree packet functional is then strictly positive.  Its magnitude is not
claimed to exceed (1/40): normalized double integration carries the packet
measure, and shrinking the spectator support shrinks that matrix element.
The (1/40) number belongs only to the pointwise kernel.  This distinction is
explicit in the certificate and verifier.

The loop contributes through the normalized spectator identity and retains
its averaged lower bound.  Consequently the complete packet contrast obeys

\[
 \Delta R_6={2\sqrt2\over3}\Delta C_{\rm tree}
 +{5\over24\pi^2}\Delta B_{\rm pkt},
\]

with

\[
 \Delta C_{\rm tree}>0,qquad
 \Delta B_{\rm pkt}>{1\over230}.
\]

Dropping the positive tree functional and using (pi<22/7) gives

\[
 \boxed{\Delta R_6>{49\over534336}.}
\]

The proof establishes that suitable transverse and incoming radii exist.  It
does not assign fabricated numerical values to them.

## Absolute dark-port coefficient

On the two output packet modes, write

\[
 X(\lambda)=\lambda^2X_2+\lambda^4X_4+lambda^6X_6
 +O(\lambda^8),\qquad
 X_2=x_{2,\mathrm{pkt}}(1,1).
\]

The antisymmetric effect

\[
 P_-={1\over2}\begin{pmatrix}1&-1\\-1&1\end{pmatrix}
\]

annihilates (X_2).  Hence the complete (X_2)-(X_6) cross is absent and

\[
 Q_{8,-}=\langle X_4,P_-X_4\rangle
 ={1\over2}\|X_4(1)-X_4(0)\|^2.
\]

The packetwise (q_6) identities imply

\[
 \operatorname{Re}\langle x_{2,\mathrm{pkt}},X_4(1)-X_4(0)\rangle
 ={\bar q_{4,\mathrm{pkt}}\Delta R_6\over2}.
\]

Cauchy--Schwarz therefore gives

\[
 {Q_{8,-}\over\bar q_{4,\mathrm{pkt}}}
 \geq{(\Delta R_6)^2\over8}
 >{2401\over2284119687168}>{1\over10^9}.
\]

This coefficient is absolute for the dark outcome.  The recorded and
symmetric bright-port coefficients remain unknown because their
(X_2)-(X_6) cross does not vanish.

## Physical boundary

The output modes are genuine positive-measure (L^2) packets on the invariant
two-body sphere.  The incoming active and spectator modes are also compact
packets on their fixed-(P) hard carriers.  This removes the zero-angle and
single-box-mode artifacts from the dark-port theorem.

The total active momentum and invariant mass remain exact fibre labels.  The
result is therefore not yet a globally normalizable direct-integral
wavepacket.  It also does not construct a local finite-derivative Hamiltonian
which selects these exact indicator packets, compute a numerical continuity
radius, determine either bright/recorded absolute (q_8) coefficient, control
the (O(\lambda^{10})) remainder, provide forward/collinear/KLN completion,
prove Eq. (19), construct a positive full BT Hilbert space, transfer to metric
BV--BRST gravity, restore a QME, transfer to residual cohomology, or establish
anything `LORENTZIAN-CAUSAL`.  No literature-priority claim is made.

## Independent rail

The producer uses 30-decimal rational square-root enclosures, sine/cosine
partial sums through orders 7/6 and (H)-series bounds through orders 10/9.
The independent verifier uses 36-decimal enclosures, recurrence-generated
trigonometric sums through orders 9/8 and (H) bounds through orders 12/11.
It proves that every independently generated interval lies inside the stored
one.  A separate exact complex-amplitude grid verifies the dark projection,
half-difference norm and Cauchy factor.  It also rejects replacing the
invariant (d\varphi) measure by (dc), inventing a transverse radius, or
promoting the point-kernel margin to a packet-functional bound.

## Verification receipt

All scientific processes ran sequentially.  Python and TeX processes used
`ulimit -v 500000`.

- Tier 0 Python compilation and JSON parsing: PASS in 0.04 s at 15,416 KB
  peak RSS.
- Exact producer replay: PASS 32/32 in 0.03 s at 16,828 KB peak RSS.
- Method-distinct verifier: PASS 43/43 in 0.11 s at 24,680 KB peak RSS.
- Scoped tests: PASS 51/51 in 0.291 s (0.39 s enclosing wall time) at 25,000
  KB peak RSS.  These include 50 adversarial mutations.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each and a
  final post-audit rebuild after boundary-wording cleanup.  The latest passes
  took 0.50 s and 0.51 s at 50,756 KB and 50,828 KB peak RSS.  The PDFs have
  69 pages (694,254 bytes) and 60 pages (664,610 bytes), with SHA-256
  hashes
  `206c984419aa76f94bcd65344e0e4bb1b8c4245fcc8d3851a3ec02a9499e3be1`
  and
  `888266e2faf019a272bced8d03d5c3535df8c781d74d07a56a03917d6cf4bc05`.
  No overfull box occurs at either inserted compact-packet theorem.
- The paper-prose shadow rail remains advisory and non-certifying.  It flags
  the papers' pre-existing ledger-style abstract length and parenthetical
  density; emphasis, em-dash, sentence-length and vocabulary checks remain
  within its budgets.
- Tier 3: FAIL-CLOSED, 2,638 tests in 799.672 s (800.71 s enclosing wall
  time) at 391,492 KB peak RSS, with 32 failures and 9 skips.  Every one of
  the 51 new tests passed.  The increase from the preceding 2,587-test run is
  exactly those 51 tests, and the set of 32 failure names is identical.  The
  final chain-import grep again reached its 120 s timeout late in the capped
  full suite.  A scoped rerun under the same cap completed the scan in 18.809
  s (18.86 s enclosing wall time) at 391,496 KB: its scan-executed test passed
  and the same two older outside-reference findings remained failures.  This
  is not a repository-wide pass and supports no freeze.
- The Science Forge planning fold accepted 1,543 nodes with zero invalid
  items and zero malformed events in 5.86 s at 244,876 KB peak RSS.  It ran
  outside the virtual-address cap because the Go runtime reserves a larger
  virtual page arena before execution.
- The advisory Science Forge shadow script exited zero by design in 2.10 s at
  343,340 KB, but its bridge audit is a fail-closed finding: the available
  Forge 0.0.2 binary has a standard-library hash mismatch and rejects the
  current prelude with `E9118`.  The independent coverage census reports
  1,611 certificates against the old 976-certificate baseline.  Neither
  finding is evidence for this theorem.

Tier 3 was required because Papers V and VI acquire a compact-packet
coefficient theorem.  Tier 2 is the content-addressed six-predecessor chain
rechecked by both exact implementations.  No classical input, shared
operator, quantum schema or quantum lifecycle claim changed, so unrelated
classical and quantum freeze chains were not rebuilt separately.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_compact_sphere_dark_port_absolute_q8.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_compact_sphere_dark_port_absolute_q8.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_sphere_dark_port_absolute_q8
```
