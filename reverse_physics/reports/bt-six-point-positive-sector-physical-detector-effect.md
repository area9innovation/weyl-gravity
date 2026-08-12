# BT six-point positive-sector physical detector effect

Certificate:
`REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

There is a positive, normalized leading click/no-click probability jet for an
explicit three-particle source prepared directly in the public BT
\(\mathrm{O}(1,1)\) theory.  Its click coefficient comes from the complete six-point
tree and the BT Hamiltonian cut.  Pseudo-unitarity fixes the complementary
no-click coefficient; it is not supplied by the earlier operational rotation
and is not fitted.

This bypasses the obstructed regular Eq. (19) route by changing the
preparation: the source is already a positive ghost-even public auxiliary
state.  It is not claimed to be the transported perfect-square scalar
projector.

## Positive three-particle source sector

On the eight three-particle species strings, ghost parity acts by bitwise
complement,

\[
 \kappa_3|x\rangle=|7-x\rangle.
\]

Its positive even frame is

\[
 u_x=\frac{|x\rangle+|7-x\rangle}{\sqrt2},
 \qquad x=0,1,2,3.
\]

Because the three-particle Krein metric is the same complement exchange,

\[
 \langle u_x,u_y\rangle_K=\delta_{xy}.
\]

The complete Choi coefficient commutes with \(\kappa_3\), so it has separate
positive-even and negative-odd \(4\times4\) blocks.  In the positive frame,

\[
 A_+=\begin{pmatrix}
 c_0&0&0&0\\
 0&c_6&c_3&c_1\\
 0&c_7&c_4&c_2\\
 0&c_5&c_8&c_9
 \end{pmatrix}.
\]

This is a restriction of the actual public transition coefficient, not a new
detector Hilbert space.

## Fixed-shell click effect

At the isolated channel \(B=1\) pole, \(c_B=0\) and all other residues are
\(1/4\).  Therefore

\[
 R_+=\frac14
 \begin{pmatrix}
 1&0&0&0\\
 0&1&1&0\\
 0&1&1&1\\
 0&1&1&1
 \end{pmatrix}.
\]

The leading click effect is the ordinary positive Gram

\[
 G=R_+^TR_+.
\]

Its exact characteristic polynomial is

\[
 x\left(x-\frac1{16}\right)
 \left(x^2-\frac{x}{2}+\frac1{64}\right),
\]

and hence

\[
 \operatorname{spec}G=\left\{
 0,\frac1{16},\frac{2-\sqrt3}{8},
 \frac{2+\sqrt3}{8}\right\}.
\]

Every eigenvalue is nonnegative.  The effect has rank three and trace
\(9/16\).  The negative-parity block has the same squared singular values and
trace \(9/16\); their sum is the previously certified full residue norm
\(9/8\).

## Detector normalization and positivity interval

Write

\[
 D=\pi^4\kappa^4L_xL_y^2L_z^2.
\]

The full detector rate was

\[
 \Gamma_\Xi=\frac{9\lambda^8}{1024D}.
\]

Dividing by the full coefficient norm \(9/8\) gives the rate per unit
coefficient norm,

\[
 \gamma_0=\frac{\lambda^8}{128D}.
\]

For observation time \(T\) and dimensionless tangential volume
\(\Delta\Xi\), set

\[
 \zeta=\gamma_0T\Delta\Xi.
\]

The leading two-outcome effects on the positive public source space are

\[
 E_{\rm click}=\zeta G,
 \qquad
 E_{\rm no}=I_4-\zeta G.
\]

They sum to \(I_4\).  Since the largest eigenvalue of \(G\) is
\((2+\sqrt3)/8\), both are positive throughout the exact uniform interval

\[
 0\leq\zeta\leq
 \frac8{2+\sqrt3}=16-8\sqrt3.
\]

Thus every normalized state in the positive even four-plane has nonnegative
click and no-click weights on this declared leading-shell domain.

For the particularly simple source

\[
 u_0=\frac{|\Upsilon\Upsilon\Upsilon\rangle
              +|\Omega\Omega\Omega\rangle}{\sqrt2},
\]

\(G u_0=u_0/16\).  Its two probabilities are

\[
 q_{\rm click}=\frac\zeta{16},
 \qquad q_{\rm no}=1-\frac\zeta{16},
\]

and its click rate is

\[
 \boxed{\Gamma_{u_0,\Xi}
 =\frac{\lambda^8}
 {2048\pi^4\kappa^4L_xL_y^2L_z^2}}.
\]

## Why the no-click coefficient is dynamical

Let the transition amplitude be \(\sqrt\zeta\,R_+\).  The minimal skew block

\[
 K=\begin{pmatrix}0&-R_+^T\\R_+&0\end{pmatrix}
\]

obeys \(K^T=-K\).  Expanding a pseudo-unitary completion gives the source
virtual-amplitude Hermitian coefficient

\[
 B_{\rm source}=-\frac12R_+^TR_+=-\frac G2.
\]

Consequently the survival/no-click probability coefficient is

\[
 2B_{\rm source}=-G,
\]

which cancels the transition coefficient \(R_+^TR_+=G\).  An arbitrary
anti-Hermitian virtual phase drops out of the probability.  This is the same
order-by-order pseudo-unitarity mechanism that fixes an optical-theorem
survival term, now applied after the actual BT transition has been restricted
to a positive invariant public sector.

The earlier \(J\)-unitary boost counterexample is not contradicted.  It showed
that pseudo-unitarity alone does not make an arbitrary Krein transition
positive.  Here positivity comes first from the ghost-even Choi restriction;
pseudo-unitarity then fixes its complement.

## What is physical, and what is not

This is a physical probability statement inside the public auxiliary BT
theory in the following precise sense:

- the preparation is a normalized positive ghost-even public Fock state;
- the click block is the complete BT six-point tree residue;
- its time kernel is derived from the BT interaction-picture cut;
- the finite-volume characteristic supplies the detector normalization; and
- the leading complementary weight is fixed by pseudo-unitarity.

It is still a probability **jet**: the leading duration-growing isolated-shell
coefficient is retained, while smooth \(O(1)\) terms and higher perturbative
orders are not resummed.  It is not an exact all-time probability.

Most importantly, this preparation is not
\(R_tP_\chi^{(\phi)}R_t^\dagger\).  The regular same-chart Eq. (19) route is
already obstructed at order \(\lambda\), and this calculation does not repair
it.  A direct intertwiner from a physical perfect-square scalar preparation
to the \(u_x\) sector would promote the result to the scalar theory; none is
constructed here.

The result does not establish global ten-shell gluing, a Møller/LSZ/\(S\)
operator, all-order Eq. (19), loops, gravity/BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipt

- Tier 0: all new Python and JSON artifacts parse; the scoped diff passes
  `git diff --check`.  Papers 5 and 6 are rebuilt twice before commit.
- Tier 1: the exact producer passes 32/32 checks with peak resident memory
  68,956 KB; the independent fraction/algebraic verifier passes 24/24 checks
  below 24 MB; eight tests, including six decisive claim mutations, pass
  below 25 MB.  Every scientific command is sequential under the 500 MB hard
  cap.
- Tier 2: the affected chain from complete full-phase-space positivity through
  shell normalization, detector cell, Hamiltonian cut, public-Fock history
  embedding and this effect passes sequentially.  Producers report 16/16,
  19/19, 27/27, 26/26, 31/31 and 32/32 checks; independent verifiers report
  14/14, 21/21, 26/26, 23/23, 24/24 and 24/24 checks.  The combined 43-test
  chain passes in 1.07 seconds with peak resident memory 78,124 KB; the
  verifier chain peaks at 76,068 KB.
- Tier 3 is unnecessary because there is no shared-core change, freeze,
  release, lifecycle promotion, QME state or Lorentzian claim.
- The programme-wide Science Forge bridge audit remains unavailable because
  the cached Forge 0.0.2 binary and current `FORGE_LIB` mismatch at substrate
  error `E9118`; this is not counted as a pass.  The append-only event is
  authored manually, independently of the scientific verifier.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_six_point_positive_sector_physical_detector_effect.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_positive_sector_physical_detector_effect.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_six_point_positive_sector_physical_detector_effect
```

CLOSE-OUT: DONE -- an explicitly positive public BT three-particle source has
a BT-affiliated leading click effect and a pseudo-unitarity-fixed positive
no-click complement; the physical-scalar source, complete finite-time
probability and Eq. (19) remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_SECTOR_PHYSICAL_DETECTOR_EFFECT_V1.json`
