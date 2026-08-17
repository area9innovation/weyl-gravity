# BT torus small-action gradient floor

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SMALL_ACTION_GRADIENT_FLOOR_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

A collapsing BT torus family cannot make its total action tend to zero.  More
precisely, there is a universal number \(\rho_*>0\), independent of the torus
side \(L\), such that every nonconstant positive field with residual norm
\(R\leq\rho_*\) obeys

\[
 {\lVert \nabla A\rVert_2^2\over R^2}\geq {\omega_L^2\over16},
 \qquad \omega_L=4\sin^2(\pi/L).
\]

Equivalently, below the universal action threshold
\(A_*=\rho_*^2/2\), the complete interacting gradient retains at least one
sixteenth of the squared free infrared scale.  A sequence whose normalized
quotient tends to zero must therefore eventually have \(A>A_*\).

In ordinary language, a proposed counterexample cannot disappear into the
zero-field or zero-action corner.  It must keep a definite amount of residual
action while also satisfying the high-field concentration conditions already
certified by the predecessor.

## Critical four-dimensional estimate

Write \(u=e^\psi>0\),

\[
 r_x=\sum_{y\sim x}(e^{\psi_y-\psi_x}-1),\qquad
 p_x=\Delta\psi_x=\sum_{y\sim x}(\psi_y-\psi_x),
\]

and set \(R=\lVert r\rVert_2\), \(P=\lVert p\rVert_2\).  The analytic input is
the volume-uniform critical discrete Sobolev estimate on four-dimensional
tori:

\[
 \left(\sum_{\text{directed }x\sim y}
 |\psi_y-\psi_x|^4\right)^{1/2}
 \leq S_4\lVert\Delta\psi\rVert_2^2,
\]

where \(S_4<\infty\) depends only on the dimension.  One obtains it by
applying the discrete \(H^1\)-to-\(L^4\) inequality to the four forward first
differences.  Each difference has mean zero, so the torus gap absorbs the
lower-order term.  Fourier symbols identify the forward Hessian-energy sum
with \(\lVert\Delta\psi\rVert_2^2\); the negative directed differences are
translates of the forward ones, and their fixed factor is absorbed into
\(S_4\).  No optimized numerical value of \(S_4\) is claimed.

## Nonlinear remainders

If \(R\leq1\), the residual formula bounds every oriented edge ratio and its
inverse by \(8+R\leq9\).  Thus every edge difference satisfies
\(|\psi_y-\psi_x|\leq\log9\).  On this interval the two scalar remainders

\[
 a(t)=e^t-1-t,
 \qquad b(t)=te^t-e^t+1
\]

obey \(0\leq a(t),b(t)\leq(9/2)t^2\).  Consequently

\[
 r=p+n,\qquad J_\psi\psi=r+d,
 \qquad \lVert n\rVert_2,\lVert d\rVert_2\leq C_4P^2,
\]

with \(C_4=(9/2)\sqrt8\,S_4\).

The estimate \(R\geq P-C_4P^2\) has a small and a large algebraic branch.
Simply choosing the small one would be invalid.  The exact additive path

\[
 u^{(s)}=u+s,\qquad
 r_x^{(s)}={\Delta u_x\over u_x+s}
\]

selects it without an assumption: \(R_s\leq R_0\), while
\(\lVert\Delta\log(u+s)\rVert_2\to0\).  Continuity forbids the path from
crossing \(P_s=1/(2C_4)\) when
\(R\leq\rho_*:=\min(1,1/(8C_4))\).  Therefore \(P\leq2R\).

## Gradient floor

For the complete logarithmic action gradient \(g=J_\psi^Tr\),

\[
 \langle g,\psi\rangle
 =\langle r,J_\psi\psi\rangle
 =R^2+\langle r,d\rangle
 \geq {R^2\over2}.
\]

After centering \(\psi\), the torus spectral gap and the branch estimate give

\[
 \lVert\psi\rVert_2\leq {P\over\omega_L}
 \leq {2R\over\omega_L}.
\]

Cauchy--Schwarz then yields

\[
 \lVert g\rVert_2\geq {\omega_LR\over4},
 \qquad
 \boxed{{\lVert g\rVert_2^2\over R^2\omega_L^2}\geq {1\over16}}.
\]

## Combined concentration alternative

The previous certificate showed that positive-action collapse requires all
of the following: residual energy escapes above every fixed field height;
the unweighted curvature \(h=r/u^2\) becomes flat relative to \(R\); and the
canonical current cancels across every fixed height cut.  The present theorem
adds action quantization:

\[
 {Q_L\over\omega_L^2}\longrightarrow0
 \quad\Longrightarrow\quad
 \liminf_L R_L\geq\rho_*,\qquad
 \liminf_L A_L\geq A_*.
\]

The only unresolved counterfamily is therefore a genuinely positive-action,
high-field, nonseparable concentration mechanism satisfying all three earlier
conditions.  The vanishing-action branch is closed.

## Exact fixture and claim boundary

The certificate reconstructs an axial rational field on \(T_4^4\), with
values \((11/10,1,9/10,1)\) in one coordinate and constant replication in the
other three.  Exact fractions verify its residual, complete action gradient,
the \(1/16\) floor, zero gradient sum, and strict residual decrease under two
additive shifts.  The independent verifier reconstructs all of these values
without importing the producer.

This result does not prove the all-field torus inequality, optimize \(S_4\) or
\(\rho_*\), or rule out the remaining positive-action concentration branch.
It establishes no Witten/Poincare transfer, interacting \(H^{-1}\) moment,
continuum measure, Born/Krein reconstruction, or LORENTZIAN-CAUSAL result.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_small_action_gradient_floor.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_small_action_gradient_floor.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_small_action_gradient_floor

The certificate records content-pinned provenance, exact commands, timings,
higher-tier disposition, and the paper and planning receipts.
