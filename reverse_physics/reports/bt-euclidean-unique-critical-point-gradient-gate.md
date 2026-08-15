# BT unique critical point and nonlinear gradient gate

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The finite-volume BT action has exactly one stationary point.  On every
finite connected undirected graph, put

\[
 \Omega_x=e^{\psi_x}>0,\qquad
 r_x={\Delta\Omega_x\over\Omega_x},\qquad
 A(\psi)={1\over2}\sum_xr_x^2 .
\]

Modulo the irrelevant constant shift of \(\psi\), the equation
\(\nabla A=0\) has only the vacuum \(\psi=0\).  Thus the Witten barrier is
not caused by additional finite-volume wells or false vacua.

The strongest gradient consequence one might guess is nevertheless false.
If \(\omega_G\) is the smallest positive eigenvalue of \(-\Delta\), the
global inequality

\[
             \|\nabla A\|_2^2\geq\omega_G^2\|r\|_2^2
\]

does not retain the sharp free coefficient.  An exact rational field on the
\(4^4\) torus has quotient

\[
 {\|\nabla A\|_2^2\over\|r\|_2^2}
 ={1994522814988163335078911851405560366405233608338391351
   \over
   565547202042256176363769851231265478188203144178190400}
 <4=\omega_4^2 .
\]

This is a sharp-constant obstruction, not an obstruction to every positive
constant at the correct \(L^{-4}\) scale.

## Why the critical point is unique

Let \(K=-\Delta+\operatorname{diag}(r)\).  Direct differentiation gives

\[
 Dr=-\operatorname{diag}(\Omega)^{-1}
       K\operatorname{diag}(\Omega),
 \qquad K\Omega=0.
\]

The positive-ground-state transform of the symmetric graph operator \(K\)
is the exact edge-square identity

\[
 f^TKf=\sum_{\{x,y\}\in E}\Omega_x\Omega_y
 \left({f_x\over\Omega_x}-{f_y\over\Omega_y}\right)^2.
\]

Connectedness therefore makes its kernel exactly
\(\operatorname{span}\{\Omega\}\).  It follows that

\[
             \ker Dr^T=\operatorname{span}\{\Omega^2\}.
\]

At a critical point, \(Dr^Tr=0\), so \(r=c\Omega^2\).  But the residual also
obeys the exact graph identity

\[
 0=\sum_x(\Delta\Omega)_x=\sum_x\Omega_xr_x
   =c\sum_x\Omega_x^3.
\]

Positivity of \(\Omega\) forces \(c=0\).  Hence \(r=0\), so \(\Omega\) is
harmonic and therefore constant on a connected finite graph.  Fixing the
mean-log gauge gives \(\psi=0\).

## Exact sharp-constant fixture

On a \(4\times4\) periodic square take \(\Omega=10^{-3}\) times

\[
\begin{pmatrix}
2021&1265&954&1265\\
1265&954&784&954\\
954&784&676&784\\
1265&954&784&954
\end{pmatrix}.
\]

All entries are positive rationals.  Computing \(r=\Delta\Omega/\Omega\)
and the log-coordinate gradient \(Dr^Tr\) with exact fractions gives a
strictly positive gap

\[
 4\|r\|_2^2-\|\nabla A\|_2^2
 ={267665993180861370376167553519501546347578968374370249
   \over
   131476141037613429305460659960135236883776349082240000}>0.
\]

Repeating this pattern constantly in the other two coordinates embeds it in
the physical \(4^4\) BT torus.  Both squared norms acquire the same factor
\(16\), while the lowest eigenvalue remains \(\omega_4=2\).

## Meaning for the reconstruction programme

The landscape is simpler than a generic nonconvex theory: it has negative
curvature regions but no extra stationary wells.  Consequently an eventual
small Witten eigenvalue cannot be explained by tunnelling between distinct
finite-volume vacua.  It would have to come from a delocalized or
growing-volume almost-stationary valley.

The next precise quantity is

\[
 \gamma_L=\inf_{\psi\ \mathrm{nonconstant}}
 {\|\nabla A(\psi)\|_2^2
  \over\omega_L^2\|r(\psi)\|_2^2}.
\]

The live fork is exact: prove \(\inf_L\gamma_L>0\) using the special relation
\(r=\Delta\Omega/\Omega\), or construct a growing-volume sequence for which
\(\gamma_L\to0\).  Even the positive outcome would still require a separate
bridge from deterministic gradient domination to the Gibbs Poincare/Witten
estimate.

## Boundaries

This certificate does not establish a positive volume-uniform gradient
constant, a Poincare inequality, Witten one-form coercivity, an interacting
\(H^{-1}\) bound, a continuum measure, a Born rule, a Krein reconstruction,
or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_unique_critical_point_gradient_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_unique_critical_point_gradient_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_unique_critical_point_gradient_gate
```
