# BT torus top-band flow and the unconditional high-contrast cutoff

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_TOP_BAND_FLOW_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The sparse near-maximum sector left open by the preceding density theorem
also has a free-scale lower bound once its local contrast is sufficiently
large. With the same notation

\[
 W=\max_e z_e,
 \qquad \alpha_e=z_e/W,
 \qquad c_x=\sum_{e:x\to y}\alpha_e,
 \qquad F=\sum_xc_x^2,
\]

the top-band theorem is

\[
 \boxed{
 W^2\geq256q^3D^2NF
 \quad\Longrightarrow\quad
 Q={\|g\|_2^2\over\|r\|_2^2}
 \geq{W^2\over4q^2D^2N^2}
 \geq{64qF\over N}.}
\]

Since $F\geq1$, this is already at the free four-torus scale $L^{-4}$.
Combining it with the dense-band predecessor at the split
$F=N^{1/3}$ gives the unconditional corollary

\[
 \boxed{
 W\geq3072L^{11/3}
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq{32\over\pi^4}.}
\]

The previous size-only finite-amplitude theorem required contrast of order
$L^8$; the density-sensitive theorem improved dense configurations; the new
dichotomy lowers the unconditional exponent to $11/3$.

This still does not settle the all-field problem. A collapsing family, if it
exists, must now remain within

\[
                         W<3072L^{11/3}
\]

eventually and arrange its current through a moderate sparse hierarchy of
ratio bands.

## Refined complete-current error

The predecessor decomposition is exact:

\[
 r_x=Wc_x+h_x,
 \qquad
 J_e=W^2c_{\rm tail}\alpha_e+\epsilon_e,
 \qquad
 g=W^2\operatorname{div}f+\operatorname{div}\epsilon,
\]

where $-q\leq h_x\leq0$, $f_e=c_{\rm tail}\alpha_e$, and, on an
increasing edge $x\to y$,

\[
 \epsilon_e=Wh_x\alpha_e-{c_y\over\alpha_e}
             -{h_y\over W\alpha_e}.
\]

The earlier pointwise estimate summed a worst-case $O(W)$ error over all
$N$ sites. The three pieces can instead be squared and summed using $F$.
First,

\[
 \sum_{x\to y}(Wh_x\alpha_e)^2
 \leq q^2W^2\sum_e\alpha_e^2
 \leq q^2W^2F.
\]

Second, because $\alpha_e\geq W^{-1}$ and each vertex has at most $q$
incoming edges,

\[
 \sum_{x\to y}\left({c_y\over\alpha_e}\right)^2
 \leq qW^2F.
\]

Third, $W\alpha_e=z_e\geq1$ gives

\[
 \sum_{x\to y}\left({h_y\over W\alpha_e}\right)^2
 \leq{q^3N\over2}.
\]

For equal-field edges, use
$\epsilon_e=r_x-r_y=W(c_x-c_y)+(h_x-h_y)$ and the graph energy
ceilings

\[
 \sum_{x\sim y}(c_x-c_y)^2\leq2qF,
 \qquad
 \sum_{x\sim y}(h_x-h_y)^2\leq2q^3N.
\]

After the elementary three-term square bound, and then the incidence bound,

\[
 \boxed{
 \sum_e\epsilon_e^2\leq7q^2W^2F+6q^3N,}
\]

\[
 \boxed{
 \|\operatorname{div}\epsilon\|_2^2
 \leq14q^3W^2F+12q^4N.}
\]

Thus

\[
 \|\operatorname{div}\epsilon\|_2
 \leq4q^{3/2}W\sqrt F+4q^2\sqrt N.
\]

This is the key improvement: the contrast-enhanced error is proportional to
$\sqrt F$, not $\sqrt N$.

## The top edge supplies a flow path

Let $H=\{e:\alpha_e\geq1/2\}$. At least one edge has $\alpha_e=1$.
At its tail, $c_x\geq1$, so that edge carries flow
$f_e=c_x\alpha_e\geq1$. Therefore the total flow mass through $H$ is at
least one.

Along a directed path with $k$ top-band edges,

\[
                         (W/2)^k\leq W^D.
\]

For $W\geq4$, this gives $k\leq2D$. Decomposing the acyclic flow into
source-to-sink paths therefore yields transported source mass at least
$1/(2D)$ and

\[
                         \|\operatorname{div}f\|_2
                         \geq{1\over D\sqrt N}.
\]

Under $W^2\geq256q^3D^2NF$, each of the two terms in the refined error
bound consumes at most one quarter of this leading contribution. Hence

\[
                         \|g\|_2
                         \geq{W^2\over2D\sqrt N}.
\]

Together with $\|r\|_2\leq qW\sqrt N$, this proves the displayed
top-band quotient bound.

## Dense--sparse dichotomy

Assume the common contrast condition

\[
                         W\geq24q^2DN^{2/3}.
\]

If $F\geq N^{1/3}$, then

\[
                         WF\geq24q^2DN,
\]

so the density-sensitive predecessor gives $Q\geq9q^2$.

If $F<N^{1/3}$, squaring the common contrast condition gives more than

\[
                         256q^3D^2NF,
\]

so the new top-band theorem gives $Q\geq64q/N$. On $T_L^4$,
$N=L^4$, $q=8$, $D\leq2L$, and
$\omega_L^2\leq16\pi^4/L^4$. Therefore

\[
 24q^2DN^{2/3}\leq3072L^{11/3},
 \qquad
 {64q/N\over16\pi^4/L^4}={32\over\pi^4}.
\]

This proves the unconditional corollary.

## Exact fixture and independent rail

The producer evaluates the complete single-spike field of height $10^6$ on
$T_4^4$. It stores exact rational residual, gradient, leading flow, edge
error, error divergence, norms, theorem conditions, and floors. The complete
gradient reconstructs exactly as $W^2\operatorname{div}f+
\operatorname{div}\epsilon$.

The independent verifier rebuilds the 256-site field and all 1,024 edges
without importing the producer. It separately checks the refined summation
constants, top-band theorem, dense--sparse dichotomy, predecessor hashes, and
claim boundaries. Mutation tests reject altered error norms, thresholds,
normalized floors, hashes, dependency tags, and false all-field promotions.

## What remains open

The live interval is now moderate polynomial local contrast,
$W=O(L^{11/3})$, combined with a sparse multiband current architecture. The
next useful object is a stopping-time forest over decreasing ratio bands. It
must either sum the source mass that survives each peel, producing the full
free-scale bound, or expose a compatible nonseparable hierarchy whose
cross-band errors cancel it.

This certificate does not prove the all-field torus inequality, exclude the
remaining moderate sector, construct a collapsing family, prove a
Witten/Poincare theorem, decide the interacting $H^{-1}$ moment, construct a
continuum measure or Born/Krein interpretation, or establish anything
`LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_top_band_flow.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_top_band_flow.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_top_band_flow
```

## Verification receipt

- Producer: **PASS**, 10/10 exact checks (0.05 s, 20,788 KiB maximum
  RSS).
- Independent verifier: **PASS**, 10/10 checks (0.12 s, 30,044 KiB
  maximum RSS).
- Focused and mutation tests: **PASS**, 11/11 tests (0.27 s, 30,968
  KiB maximum RSS).
- Unchanged sparse-maxima predecessor: **PASS**, 12/12 checks (0.13 s,
  30,504 KiB maximum RSS).
- Planning: append-only event 93 imported with 1,712 nodes, zero invalid
  items, and zero malformed events (1.77 s, 16,900 KiB maximum RSS).
- Paper: claim map verified (1.05 s, 148,360 KiB maximum RSS) and PDF
  built twice (2.49 s, 53,844 KiB maximum RSS).
- Science Forge shadow rail: advisory exit 0 in 8.05 s, but **not** a
  scientific pass. Its bridge audit failed closed on source-current Forge
  `E9415` drift, and its census found 1,972 certificates versus the
  2026-07-19 baseline of 976.

Tier 3 was not triggered: the all-field torus theorem, a collapsing family,
Witten/Poincare transfer, interacting measure, continuum limit, freeze, and
release gates remain open.
