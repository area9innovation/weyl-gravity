# BT full-phase current-g6 / score-g4 reconciliation

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G6_CURRENT_RECONCILIATION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The cubic-current obstruction belongs to order \(g^6\) in the current
variance but to order \(g^4\) in the corresponding score variance.  The next
calculation is therefore a complete full-phase \(M_4\) Wick sum—not a new
order-\(\lambda^6\) score expansion.

The older complete \(M_4\) theorem does not answer this version of the
question.  It removes one real cosine mode, leaving a rank-one,
non-translation-invariant covariance.  The live current-susceptibility gate
removes the complete cosine-sine plane.  Its Gaussian background covariance
is translation invariant and simply deletes the conjugate Fourier modes
\(+p\) and \(-p\).  The old connected-diagram architecture can be reused, but
its negative coefficient cannot be transferred across this conditioning
change.

## Exact current-to-score order map

Rescale \(\psi=g\phi\) and write

\[
 S_g(\phi)=\frac{A(g\phi)}{g^2}
 =S_0+gS_1+g^2S_2+g^3S_3+\cdots
\]

and

\[
 J(g\phi)=gJ^{(1)}+g^2J^{(2)}+g^3J^{(3)}+\cdots.
\]

For any real direction \(h\), the exact action-gradient identity is

\[
 D_hS_g=\frac1g\sum_{\{x,y\}}(h_y-h_x)J_{xy}(g\phi).
\]

Matching powers gives

\[
 D_hS_0=\sum dh\,J^{(1)},\qquad
 D_hS_1=\sum dh\,J^{(2)},\qquad
 D_hS_2=\sum dh\,J^{(3)}.
\]

Thus the newly certified cubic current is exactly the quartic-score
coefficient \(B=D_hS_2\), before multiplication by the external lattice
difference.  Its positive third-chaos square is the \(|B|^2\) summand of
\(M_4\).

An independent exact enumeration on the \(5^4\) compact motif, using a
nontrivial rational direction, gives respectively

\[
 (D_hS_0,D_hS_1,D_hS_2)
 =\left(493,\frac{689}{2},\frac{5107}{6}\right),
\]

and obtains the same three values from the \(J^{(1)},J^{(2)},J^{(3)}\) edge
fluxes.

For the full axial phase pair the exact identity

\[
 |s_c|^2+|s_s|^2=\frac{\omega_p}{g^2}|\widehat J_0(p)|^2
\]

then implies

\[
 [g^6]\,\mathbb E_{\nu_g}|\widehat J_0(p)|^2
 =\frac1{\omega_p}M_4^{\mathrm{full}}.
\]

## Complete full-phase coefficient

Let

\[
 A=(D_{h_c}S_1,D_{h_s}S_1),\quad
 B=(D_{h_c}S_2,D_{h_s}S_2),\quad
 C=(D_{h_c}S_3,D_{h_s}S_3).
\]

Integrating the two-dimensional free fiber gives
\(W_g=W_0+gW_1+g^2W_2+O(g^3)\).  Put
\(R_0=W_1^2/2-W_2\) and \(z_2=\mathbb E_0R_0\).  Expansion of both the
observable and normalized background density yields

\[
 \boxed{
 M_4^{\mathrm{full}}=\mathbb E_0\left[
 |B|^2+2A\!\cdot\!C-2W_1A\!\cdot\!B
 +|A|^2\left(\frac{W_1^2}{2}-W_2-z_2\right)
 \right]. }
\]

The independent square-root-density form is

\[
 \left\|B-\frac{W_1A}{2}\right\|_0^2
 +2\left\langle A,
 C-\frac{W_1B}{2}
 +\left(\frac{W_1^2}{8}-\frac{W_2}{2}-\frac{z_2}{2}\right)A
 \right\rangle_0.
\]

An exact two-state vector fixture gives \(z_2=4/3\) and \(M_4=26/3\) in
both forms.

## Conditioning boundary and next calculation

For the live background,

\[
 C_{\mathrm{full}}(k)=
 \begin{cases}
  0,&k\in\{0,+p,-p\},\\
  \omega(k)^{-2},&\text{otherwise}.
 \end{cases}
\]

This covariance is diagonal in momentum and translation invariant.  The next
exact calculation is to expand the two-dimensional fiber contributions to
\(W_1,W_2\), enumerate the connected Wick contractions with this deleted-mode
propagator, and evaluate \(M_4^{\mathrm{full}}\) first at \(L=4\) or \(L=5\).
Only then can its large-volume kernels be compared with the extensive cubic
current block.

No sign or scaling of the full-phase coefficient, nonperturbative current
susceptibility, interacting \(H^{-1}\) theorem, continuum measure, Born rule,
Krein reconstruction, or `LORENTZIAN-CAUSAL` physics is established.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_g6_current_reconciliation.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_g6_current_reconciliation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_g6_current_reconciliation
```

## Verification receipt

- Tier 0 passed: all three Python files compile, the schema, certificate, and
  sequence-36 planning event parse, and the scoped diff check is clean.  Python
  ran under a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.12 s with 21 MB maximum
  resident memory.  The non-importing independent verifier passed in 0.18 s
  with 30 MB maximum resident memory.
- Fourteen direct and adversarial mutation tests passed in 0.66 s with 32 MB
  maximum resident memory.
- The cubic-current, full-phase weighted-current, connected-normalization, and
  one-cosine lower-loop predecessor verifiers passed in 0.20 s, 0.11 s,
  1.13 s, and 0.22 s respectively.  The last input is checked as a scope
  contrast, not transferred as a full-phase sign theorem.
- The append-only planning import read 1,639 nodes with zero invalid items and
  zero malformed events in 7.45 s under a 300 MiB Go memory limit.
- The 2.36 s advisory Science Forge shadow rail failed closed on the existing
  Forge binary/standard-library mismatch (`E9118`) and reported corpus
  baseline drift (1,753 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 remains deferred because its independent foundations
  authority/claim-map rail is stale at the unchanged parent (`authority hash
  drift: explorer_snapshot`).  This result is published through its
  certificate and report without taking ownership of that overlapping work.
- Tier 3 was not run because this is an exact scope/order reconciliation and
  formula, not a continuum, reconstruction, freeze, or shared-core lifecycle
  promotion.
