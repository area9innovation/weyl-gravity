# BT torus extensive-action gradient floor

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_EXTENSIVE_ACTION_GRADIENT_FLOOR_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The unresolved BT torus family cannot hide its gradient in an extensive or
superextensive residual action.  On the isotropic four-torus, let

\[
 r_x={\Delta\Omega_x\over\Omega_x},\qquad
 A={1\over2}\sum_xr_x^2,\qquad
 Q={\|g\|_2^2\over\|r\|_2^2},
\]

where $g$ is the complete log-field action gradient and
$\omega_L=4\sin^2(\pi/L)$.  For every $L\geq4$,

\[
 \boxed{
 A\geq{488\over5}L^4
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq{61\over320\pi^4}.}
\]

Consequently, every field below this certified normalized floor satisfies

\[
 \boxed{
 A<{488\over5}L^4,
 \qquad
 W<16L^2,}
\]

where $W$ is the maximum nearest-neighbour field ratio.  This improves the
live contrast window from the preceding $O(L^{10/3})$ stopping-flow cutoff
to $O(L^2)$, and simultaneously forces bounded action density.

This is not the all-field theorem.  The low-action, sub-$16L^2$ sector
remains open.

## From affine virial to a pointwise gradient floor

The certified affine virial theorem gives, with $N$ vertices and
$C=488/5$,

\[
             \langle\psi,g\rangle\geq2A-CN.
\]

Hence $A\geq CN$ implies

\[
                         \langle\psi,g\rangle\geq A.
\]

Every oriented edge ratio $z=\Omega_y/\Omega_x\geq1$ is one positive
summand in

\[
                         q+r_x=\sum_{y\sim x}{\Omega_y\over\Omega_x},
\]

so on a $q$-regular graph

\[
                         W\leq q+\sqrt{2A}.
\]

Fix the mean-log gauge $\sum_x\psi_x=0$, and let $D$ be the graph
diameter.  A shortest path and the edge-ratio bound give

\[
 \max\psi-\min\psi
 \leq D\log(q+\sqrt{2A}).
\]

Since zero lies between the minimum and maximum,

\[
 \|\psi\|_2
 \leq D\sqrt N\log(q+\sqrt{2A}).
\]

Cauchy--Schwarz now yields

\[
 \|g\|_2
 \geq{A\over D\sqrt N\log(q+\sqrt{2A})},
\]

and therefore

\[
 \boxed{
 Q\geq{A\over
 2ND^2\log(q+\sqrt{2A})^2}.}
\]

No convexity of the BT action, Hessian positivity, current-sign assumption,
or asymptotic expansion is used.

## Why the threshold is the worst large-action value

Put $s=\sqrt{2A}$.  The logarithmic derivative of

\[
                 {A\over\log(q+\sqrt{2A})^2}
\]

is positive whenever

\[
                         (q+s)\log(q+s)>s.
\]

For $q=8$, $\log(q+s)>1$, so this is immediate.  Thus the displayed
quotient floor is weakest at $A=CN$; arbitrarily large action only
strengthens it.

## Four-torus constants

For $T_L^4$,

\[
 N=L^4,\qquad q=8,\qquad D=4\lfloor L/2\rfloor\leq2L.
\]

The exact rational comparison

\[
                         2C={976\over5}<14^2
\]

gives, at $A=CN$,

\[
 8+\sqrt{2C}\,L^2<8+14L^2<16L^2.
\]

For $L\geq4$, $\log16<4$ and $2\log L\leq L$, hence

\[
 \log(8+\sqrt{2C}\,L^2)<\log(16L^2)<2L.
\]

Substitution into the graph theorem gives

\[
                         Q\geq{C\over32L^4}
                         ={61\over20L^4}.
\]

Finally, $\sin x\leq x$ gives

\[
                         \omega_L^2\leq{16\pi^4\over L^4},
\]

which proves the normalized constant $61/(320\pi^4)$.

If a field lies below that floor, the contrapositive gives $A<CL^4$.
The edge-ratio estimate then gives directly

\[
                         W<8+14L^2<16L^2.
\]

This last conclusion does not depend on the sparse/dense flow split.

## Exact fixture and independent rail

The producer evaluates a rational $T_4^4$ field with one site of height
$1000$ and every other site of height one.  Its complete residual, gradient,
action, quotient, and maximum edge ratio are stored as exact fractions.  It
lies above the extensive-action threshold and clears every theorem
inequality.

The independent verifier does not import the producer.  It reconstructs all
256 vertices and their periodic neighbours with a separately written
adjacency loop, recomputes the exact rational residual and gradient, and
re-derives the constant chain $488/5\to61/20\to61/320$.  Mutation tests
reject changes to the virial constant, graph quotient, torus floor,
contrast necessity, fixture, input hashes, dependency tags, or open gates.

## What remains

The possible counterfamily has now been forced into the joint sector

\[
                         A=O(L^4),\qquad W=O(L^2).
\]

The next positive route is a critical-dimension compactness or localized
band theorem inside this bounded-action-density sector.  The negative route
is a genuinely nonseparable family satisfying both restrictions and driving
$Q/\omega_L^2$ to zero.

The certificate does not establish the all-field torus inequality,
Witten/Poincare coercivity, the interacting $H^{-1}$ moment, a continuum
measure, Born or Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_extensive_action_gradient_floor.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_extensive_action_gradient_floor.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_extensive_action_gradient_floor
```

The exact timing and tier disposition are stored in the certificate.
