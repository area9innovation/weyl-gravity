# BT bounded-oscillation gradient coercivity

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_BOUNDED_OSCILLATION_GRADIENT_COERCIVITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The nonlinear BT action-gradient quotient cannot collapse while the positive
field stays in a fixed bounded-oscillation sector. On every finite connected
undirected graph, let

\[
 \Omega_x=e^{\psi_x}>0,\qquad
 r_x={\Delta\Omega_x\over\Omega_x},\qquad
 A={1\over2}\sum_xr_x^2,
\]

and put \(m=\min_x\Omega_x\), \(M=\max_x\Omega_x\). If \(\omega_G\)
is the smallest positive eigenvalue of \(-\Delta\), then

\[
 \boxed{\|\nabla A\|_2^2\geq
 \omega_G^2\left({m\over M}\right)^{12}\|r\|_2^2.}
\]

The coefficient is independent of the number of vertices. In particular,
for any sequence of graphs and nonconstant fields,

\[
 {\|\nabla A\|_2^2\over\omega_G^2\|r\|_2^2}\longrightarrow0
 \quad\Longrightarrow\quad {M\over m}\longrightarrow\infty.
\]

This is a genuine positive part of the deterministic volume-uniform gate. It
does not settle the gate, because the Gibbs field is not yet known to remain
in a uniformly bounded-oscillation sector.

## Ground-state spectral estimate

Write \(D=\operatorname{diag}(\Omega)\) and

\[
 K=-\Delta+\operatorname{diag}(r).
\]

The exact factorization imported from the unique-critical-point certificate is

\[
 Dr=-D^{-1}KD,\qquad K\Omega=0,
\]

with ground-state identity

\[
 f^TKf=\sum_{\{x,y\}\in E}\Omega_x\Omega_y
 \left({f_x\over\Omega_x}-{f_y\over\Omega_y}\right)^2.
\]

For \(f\perp\Omega\), write \(f=\Omega h\). Then
\(\sum_x\Omega_x^2h_x=0\). The left side above is bounded below by
\(m^2\sum_{\{x,y\}}(h_x-h_y)^2\). Weighted mean zero also gives

\[
 \|f\|_2^2=\sum_x\Omega_x^2h_x^2
 =\min_c\sum_x\Omega_x^2(h_x-c)^2
 \leq M^2\sum_x(h_x-\bar h)^2.
\]

The ordinary graph Poincare inequality therefore yields

\[
 f^TKf\geq\omega_G\left({m\over M}\right)^2\|f\|_2^2.
\]

Because \(K\) is symmetric and positive semidefinite with kernel
\(\operatorname{span}\{\Omega\}\), its first positive eigenvalue has the
same lower bound. Hence

\[
 \|Kf\|_2\geq\omega_G(m/M)^2\|f\|_2
 \qquad(f\perp\Omega).
\]

## The residual cannot align with the bad kernel

Set \(q=D^{-1}r\). The action gradient is

\[
                         \nabla A=-DKq.
\]

The only direction killed by \(K\) is \(\Omega\), but \(q\) obeys a second,
different orthogonality relation:

\[
 \langle\Omega^2,q\rangle
 =\langle\Omega,r\rangle
 =\sum_x(\Delta\Omega)_x=0.
\]

Let \(f\) be the orthogonal projection of \(q\) onto
\(\Omega^\perp\). Elementary two-vector geometry gives

\[
 {\|f\|_2\over\|q\|_2}\geq
 {\langle\Omega,\Omega^2\rangle
  \over\|\Omega\|_2\|\Omega^2\|_2}
 \geq\left({m\over M}\right)^3.
\]

Combining the spectral estimate, this angle, and
\(\|DKq\|\geq m\|Kq\|\), \(\|q\|\geq M^{-1}\|r\|\), gives

\[
 \|\nabla A\|_2
 \geq\omega_G\left({m\over M}\right)^6\|r\|_2.
\]

Squaring proves the theorem. The exponent twelve is deliberately conservative;
no optimality is claimed.

## Meaning for the barrier

The earlier exact work ruled out extra finite-volume critical points, purely
axial collapse, repaired finite bubble collections, a synchronized growing
bubble crystal, and the canonical round two-scale tower. This theorem removes
the entire remaining bounded-amplitude sector at once. A counterexample must
now escape to the boundary of positive-field space: its log-field oscillation
must diverge.

The lattice pilot already gives the deterministic range bound

\[
 A\geq {1\over2}\left(e^{R/D_G}-q_G\right)^2,
 \qquad R=\log(M/m),
\]

once the bracket is positive. The next question is probabilistic and
volume-sensitive: does that energy penalty beat the entropy of large-range
configurations uniformly as the graph diameter and volume grow? If it does,
the bounded-sector theorem becomes an input to a Witten estimate. If it does
not, the escaping sector is the now sharply localized place to construct an
actual low-Rayleigh sequence.

## Boundaries

This certificate does not establish an all-field volume-uniform gradient
constant, a Poincare inequality, Witten one-form coercivity, an interacting
\(H^{-1}\) bound, a continuum measure, a Born rule, Krein reconstruction, or
anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_bounded_oscillation_gradient_coercivity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_bounded_oscillation_gradient_coercivity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_bounded_oscillation_gradient_coercivity
```
