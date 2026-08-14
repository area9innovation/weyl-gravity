# BT bilaplacian radial reference and the missing comparison bridge

**Date:** 2026-08-14

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1`

**Dependency:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `CLASSIFIED`

## Result

The actual BT lattice action has a stronger all-volume deterministic lower
envelope than the previously certified gradient-quartic estimate.  In
bilaplacian coordinates it contains both a quadratic and a quartic radial
term.  The Gibbs measure defined by exactly this radial envelope can be solved
well enough to prove the desired uniform negative-Sobolev second-moment bound.

This does **not** yet prove the bound for the actual BT Gibbs measure.
Pointwise action domination alone does not compare normalized expectations,
and an exact Hessian witness proves that the standard convex-perturbation
comparison is unavailable.  The remaining bridge must use genuinely
nonconvex, annealed, coarea, or direct-marginal information.

## All-volume bilaplacian envelope

Put \(\psi=\lambda\phi\), let \(a=\Delta\psi\), and define

\[
 B=\sum_xa_x^2,\qquad
 r_x=a_x+\sum_{y\sim x}
 \left(e^{\psi_y-\psi_x}-1-(\psi_y-\psi_x)\right),\qquad
 A=\frac12\sum_xr_x^2.
\]

The nonlinear summand in \(r_x\) is nonnegative.  Since \(a\) has zero mean,
its positive part obeys

\[
 \sum_{a_x\geq0}a_x^2\geq \frac1N\sum_xa_x^2.
\]

Consequently \(A\geq B/(2N)\).  On a \(q\)-regular graph, the residual-sum
identity, Cauchy--Schwarz, and the spectral bound
\(B\leq2q\langle\psi,(-\Delta)\psi\rangle\) also give
\(A\geq B^2/(8q^2N)\).  Averaging the two valid bounds yields

\[
 A(\psi)\geq\frac{B}{4N}+\frac{B^2}{16q^2N}.
\]

Thus, with \(B_\phi=\sum_x(\Delta\phi_x)^2\),

\[
 S_\lambda(\phi)\geq
 \frac{B_\phi}{4N}+\frac{\lambda^2B_\phi^2}{16q^2N}.
\]

This statement is exact and holds at every finite periodic volume.

## The solved radial reference

Define a reference probability measure on the mean-zero hyperplane by

\[
 d\nu\propto
 \exp\!\left[-\frac{B_\phi}{4N}
              -\frac{\lambda^2B_\phi^2}{16q^2N}\right]d\phi.
\]

The linear change of variables \(y=\Delta\phi\) makes this a rotationally
invariant measure in \(n=N-1\) dimensions.  Radial integration by parts gives

\[
 n=\mathbb E_\nu\left[\frac{B}{2N}
       +\frac{\lambda^2B^2}{4q^2N}\right].
\]

It follows that

\[
 \mathbb E_\nu B\leq
 \frac{2q\sqrt{N(N-1)}}{|\lambda|},\qquad
 c_N=\frac{\mathbb E_\nu B}{N-1}
 \leq\frac{2q}{|\lambda|}\sqrt{\frac N{N-1}}.
\]

Combining isotropy with the certified free \(H^{-1}\) trace bound \(15/32\),
and using \(N\geq16\) in four dimensions, proves

\[
 \sup_L\mathbb E_\nu\|\Phi_L\|_{H^{-1}}^2
 \leq\frac{q\sqrt{15}}{4|\lambda|}.
\]

For \(q=8\) and \(\lambda=2/5\), the exact bound is \(5\sqrt{15}\).

## Why it does not transfer by convex comparison

Let

\[
 D(\psi)=A(\psi)-\frac{B}{4N}-\frac{B^2}{16q^2N}.
\]

On the \(6^4\) lattice, take the spatially constant center and direction

\[
 \psi=(-3,0,0,-3,3,3)\log2,
 \qquad v=(-1,-1,1,1,1,-1).
\]

Independent enumeration of all sites and all eight neighbors gives the exact
true-action directional Hessian \(D_v^2A=243\).  The quadratic reference
Hessian is \(4/3\).  The 20-term even alternating harmonic partial sum proves

\[
 \log2>\frac{155685007}{232792560}>\frac23,
\]

so the quartic reference Hessian is strictly greater than \(252\).  Therefore

\[
 D_v^2D < 243-\left(252+\frac43\right)
          =-\frac{31}{3}<0.
\]

The actual action minus the reference action is not convex.  Hence a
Brascamp--Lieb/Hargé-style convex perturbation theorem cannot supply the
missing normalized-moment comparison.

## Scientific boundary and next calculation

The reference model demonstrates that the deterministic envelope has exactly
the right volume scaling.  The obstruction identifies normalization and
nonconvex fluctuations—not radial confinement—as the remaining difficulty.

The next target is to exploit

\[
 A=\frac{U^2}{2N}+\frac12\sum_x(r_x-U/N)^2,
 \qquad U=\sum_xr_x,
\]

inside an annealed or coarea estimate, or to bound the normalized lowest-mode
marginal directly.  This result establishes no actual interacting
\(H^{-1}\) moment bound, tightness, continuum measure, Born rule, Krein
reconstruction, or `LORENTZIAN-CAUSAL` statement.

## Verification

Run sequentially:

```text
python3 reverse_physics/bt_euclidean_bilaplacian_reference_bridge.py --check
python3 reverse_physics/verify_bt_euclidean_bilaplacian_reference_bridge.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_bilaplacian_reference_bridge
```
