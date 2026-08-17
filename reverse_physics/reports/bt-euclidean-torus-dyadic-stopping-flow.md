# BT torus dyadic stopping flow

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_DYADIC_STOPPING_FLOW_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The moderate multiband region left by the top-band theorem admits a second
transport estimate.  On the isotropic four-torus, for every $L\geq4096$,

\[
 \boxed{
 W\geq512L^{10/3}
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq{32\over\pi^4}.}
\]

Here $W$ is the largest nearest-neighbour field ratio,
$Q=\|g\|_2^2/\|r\|_2^2$, and
$\omega_L=4\sin^2(\pi/L)$.  The previous unconditional threshold was
$3072L^{11/3}$.  The new result removes one third of a power of $L$
asymptotically.  It does not prove the all-field inequality: a collapsing
family, if one exists, must now stay below $512L^{10/3}$ eventually.

## The stopping argument

Orient every unequal edge from lower to higher field value.  As in the two
predecessors, write $z_e=W\alpha_e$,

\[
 c_x=\sum_{e:x\to y}\alpha_e,
 \qquad f_e=c_x\alpha_e,
 \qquad F=\sum_xc_x^2.
\]

The total leading-flow mass is exactly

\[
                         \sum_e f_e=F.
\]

There are at most $qN/2$ oriented edges.  On an edge with $z_e<2$,
$f_e\leq2q/W$, and hence

\[
             \sum_{e:z_e<2}f_e\leq{q^2N\over W}.
\]

If $F>2q^2N/W$, more than half the flow therefore crosses edges with
$z_e\geq2$.

The orientation is acyclic, so the flow decomposes into source-to-sink paths.
If one such path has $k$ edges with $z_e\geq2$, their product is at least
$2^k$.  The ratio of the endpoint field values is at most $W^D$: connect
the same endpoints by a graph-geodesic of length at most the diameter $D$,
and every nearest-neighbour ratio is at most $W$.  Consequently

\[
                         k\leq D\log_2W.
\]

Let $S$ be the total source mass.  Counting the high-band edge mass in the
path decomposition gives

\[
 {F\over2}<SD\log_2W,
 \qquad
 \|\operatorname{div}f\|_2
 \geq{2S\over\sqrt N}
 >{F\over D\log_2W\sqrt N}.
\]

This is a stopping-time estimate: flow cannot keep crossing factor-two jumps
for more than $D\log_2W$ steps before it must terminate at a detectable
source or sink.

## Restoring the complete current

The predecessor proved the exact decomposition

\[
 g=W^2\operatorname{div}f+\operatorname{div}\epsilon
\]

and the norm bound

\[
 \|\operatorname{div}\epsilon\|_2
 \leq4q^{3/2}W\sqrt F+4q^2\sqrt N.
\]

Under

\[
                 \sqrt W\geq16\sqrt q\,D\log_2W,
\]

the two error terms consume less than one half of the leading contribution.
Indeed, $F>2q^2N/W$ makes the first relative error at most
$4/(16\sqrt2)<1/4$, while the squared stopping hypothesis implies the
second is at most $1/4$.  Therefore

\[
 \|g\|_2\geq{W^2F\over2D\log_2W\sqrt N},
 \qquad
 Q\geq{q^2\over D^2\log_2(W)^2}.
\]

## Sparse--dense closure on the four-torus

Split at $F=2q^2N/W$.

If $F\leq2q^2N/W$, the top-band theorem applies whenever

\[
                         W^3\geq512q^5D^2N^2
\]

and gives $Q\geq64q/N$.

If $F>2q^2N/W$, the stopping theorem gives the logarithmic dense bound.
For $T_L^4$, $q=8$, $N=L^4$, and $D\leq2L$.  The hypothesis
$W\geq512L^{10/3}$ clears the sparse condition because

\[
 512^3L^{10}\geq512\,8^5(2L)^2L^8.
\]

It also clears the stopping condition for $L\geq4096$.  At the endpoint,

\[
 L^{4/3}=65536
 \geq16\left(9+{10\over3}\log_2L\right)^2
 =38416,
\]

and the ratio of the two sides increases thereafter.

There are now two contrast intervals.  If
$W\geq3072L^{11/3}$, the predecessor already proves the conclusion.  In the
remaining interval, $3072<L$ implies

\[
 \log_2W<{14\over3}\log_2L
 <5\log_2L\leq{5L\over64}<{L\over8}.
\]

The dense bound is then $Q>1024/L^4$, while the sparse bound is
$Q\geq512/L^4$.  Since
$\omega_L^2\leq16\pi^4/L^4$, both branches give the displayed normalized
floor.

## Scope and next gate

This closes high polynomial contrast more tightly; it does not close the
programme goal.  The live region is now

\[
                         W=O(L^{10/3}).
\]

The next proof must use more than the total factor-two flow mass.  It should
iterate the stopping argument across nested bands and retain signed
cross-band information in the complete current.  The alternative is a
genuinely nonseparable four-torus family inside this smaller contrast window.

The result does not establish an all-field torus inequality, a collapsing
family, Witten/Poincare coercivity, the interacting $H^{-1}$ moment, a
continuum limit, Born or Krein reconstruction, or anything
`LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_dyadic_stopping_flow.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_dyadic_stopping_flow.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_dyadic_stopping_flow
```

The exact timing and tier receipt is stored in the certificate.
