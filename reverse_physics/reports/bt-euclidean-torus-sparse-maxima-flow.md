# BT torus sparse-maxima flow theorem

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_SPARSE_MAXIMA_FLOW_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The finite-amplitude high-contrast argument can be made sensitive to how
many edges occupy its top ratio scale. Let $T_L^4$, $L\geq4$, have
$N=L^4$ vertices, degree $q=8$, and diameter
$D=4\lfloor L/2\rfloor$. Orient each unequal edge from lower to higher
field value and put

\[
 W=\max_{x\sim y}\max\left({\Omega_y\over\Omega_x},
                            {\Omega_x\over\Omega_y}\right),
 \qquad
 \alpha_e={\Omega_{\rm head}\over W\Omega_{\rm tail}},
\]

\[
 c_x=\sum_{e:x\to y}\alpha_e,
 \qquad F=\sum_xc_x^2.
\]

The new theorem is

\[
 \boxed{
 WF\geq24q^2DN
 \quad\Longrightarrow\quad
 {\|g\|_2^2\over\|r\|_2^2}\geq9q^2.}
\]

Here $r=\Delta\Omega/\Omega$ is the complete BT residual and $g$ is
the complete log-field action gradient. Since the first eigenvalue of
$-\Delta$ is at most $2q$, the conclusion is stronger than
$(9/4)\omega_L^2$.

For the four-torus, a simpler sufficient condition is

\[
                         WF\geq3072L^5.
\]

This improves the preceding size-only threshold, which was of order $L^8$,
whenever the largest ratios are spread across many edges. More importantly,
it gives a necessary geometry for any counterfamily. If

\[
 E_\theta=\#\{e:z_e\geq\theta W\},\qquad0<\theta\leq1,
\]

then

\[
 E_\theta\leq{F\over\theta^2},
 \qquad
 {E_\theta\over4L^4}
 <{768L\over\theta^2W}
\]

whenever the field lies below the theorem's quotient floor. Thus a
collapsing candidate with $W/L\to\infty$ must make every fixed relative
top-ratio band sparse. A macroscopic sea of near-maximal edges cannot be the
counterexample.

This is not the all-field theorem. A sparse hierarchy can still distribute
its mass over many lower ratio bands and arrange cancellations among their
complete currents.

## Exact finite-amplitude split

Write $z_e=W\alpha_e$ on every increasing edge. At a vertex $x$, the
outgoing ratios give

\[
                         r_x=Wc_x+h_x,
                         \qquad -q\leq h_x\leq0.
\]

For an oriented edge $e=(x,y)$, its canonical BT current is

\[
 J_e=r_xz_e-{r_y\over z_e}
    =W^2c_x\alpha_e+\epsilon_e,
\]

where

\[
 \epsilon_e=Wh_x\alpha_e-{c_y\over\alpha_e}
             -{h_y\over W\alpha_e}.
\]

Because $W^{-1}\leq\alpha_e\leq1$, $0\leq c_y\leq q$, and
$-q\leq h\leq0$,

\[
                         |\epsilon_e|\leq3qW.
\]

Equal-field edges are placed entirely in the error current and obey the same
bound. With $f_e=c_x\alpha_e$, incidence summation gives

\[
 g=W^2\operatorname{div}f+\operatorname{div}\epsilon,
 \qquad
 \|\operatorname{div}\epsilon\|_2\leq3q^2W\sqrt N.
\]

The leading flow has exact total mass

\[
             \sum_ef_e
 =\sum_xc_x\sum_{e:x\to y}\alpha_e
 =\sum_xc_x^2=F.
\]

No asymptotic limit or discarded reverse-current term occurs here.

## Band extraction and torus path geometry

Set

\[
                         \tau={F\over4q^2N}.
\]

There are at most $qN/2$ oriented edges and $c_x\leq q$. Hence the flow
mass on edges with $\alpha_e<\tau$ is at most

\[
 q\,{qN\over2}\tau={F\over8}.
\]

At least $7F/8$ of the flow therefore uses high edges. Under
$WF\geq24q^2DN$, every high edge satisfies

\[
             z_e=W\alpha_e\geq W\tau\geq6D.
\]

Consider a directed flow path containing $k$ high edges. The field grows
along the path, while a shortest path between its endpoints has at most $D$
edges whose individual ratios are at most $W$. Consequently

\[
                         (W\tau)^k\leq W^D.
\]

Moreover

\[
 {1\over\tau}={4q^2N\over F}\leq4q^2N
 =256L^4=(4L)^4,
 \qquad W\tau\geq6D\geq4L.
\]

It follows without numerical logarithms that

\[
 {\log W\over\log(W\tau)}
 =1+{\log(1/\tau)\over\log(W\tau)}\leq5,
 \qquad k\leq5D.
\]

Decompose the acyclic flow into source-to-sink paths and call their total
transported source mass $S$. The high-edge mass is at most $5DS$, so

\[
 S\geq{7F\over40D},
 \qquad
 \|\operatorname{div}f\|_2
 \geq{\|\operatorname{div}f\|_1\over\sqrt N}
 ={2S\over\sqrt N}
 \geq{7F\over20D\sqrt N}.
\]

Combining this with the complete-current error and the assumed $WF$
threshold yields

\[
 \|g\|_2\geq{7W^2F\over40D\sqrt N}.
\]

Finally $|r_x|\leq qW$, so

\[
 {\|g\|_2^2\over\|r\|_2^2}
 \geq{49W^2F^2\over1600q^2D^2N^2}
 \geq9q^2.
\]

## Density corollary

Let $k_x(\theta)$ count outgoing edges at $x$ with
$\alpha_e\geq\theta$. Then

\[
 c_x\geq\theta k_x(\theta),
 \qquad c_x^2\geq\theta^2k_x(\theta),
\]

because $k_x$ is a nonnegative integer. Summing gives

\[
                         E_\theta\leq F/\theta^2.
\]

This converts the analytic flow mass into an inspectable geometric
diagnostic for candidate families.

## Exact fixtures and independent rail

The producer evaluates two complete rational fields on $T_4^4$:

- one isolated site of height $10^6$;
- a checkerboard of heights $1$ and $10^3$.

It stores the exact residual and gradient norms, quotient, $F$, band
threshold, high/low flow masses, complete-current reconstruction, and
near-maximal edge count. Both fields satisfy the hypothesis and clear the
quotient floor.

The independent verifier does not import the producer. It rebuilds all 256
vertices and 1,024 undirected edges, reconstructs both complete residuals and
gradients through a separate adjacency implementation, and checks the
analytic constant chain and claim boundaries. Mutation tests reject changes
to a fixture norm, theorem constant, density corollary, predecessor hash,
dependency tags, or open all-field/multiband gates.

An exploratory fixed-amplitude optimizer was used only to choose this proof
route. It is not retained in the repository and supplies no evidence for the
theorem.

## What remains open

The candidate region is now more structured. A counterfamily must either
keep $W=O(L)$, or, when $W/L\to\infty$, make its top relative bands sparse
and move substantial current through a growing hierarchy of lower bands. The
next calculation is an iterative stopping-time decomposition: remove the
sparse top band, renormalize the next band, and determine whether boundary
errors can cancel across scales on $T_L^4$.

This certificate does not establish a lower bound for every positive torus
field, exclude a sparse multiband hierarchy, construct a collapsing family,
prove Witten/Poincare coercivity, decide the interacting $H^{-1}$ moment,
construct a continuum measure or Born/Krein interpretation, or establish
anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_sparse_maxima_flow.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_sparse_maxima_flow.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_sparse_maxima_flow
```

## Verification receipt

- Producer: **PASS**, 11/11 exact checks (0.07 s, 20,900 KiB maximum
  RSS).
- Independent verifier: **PASS**, 12/12 checks (0.12 s, 30,520 KiB
  maximum RSS).
- Focused and mutation tests: **PASS**, 11/11 tests (0.35 s, 30,820
  KiB maximum RSS).
- Unchanged high-contrast predecessor: **PASS**, 9/9 checks including 318
  rational fields (0.17 s, 32,172 KiB maximum RSS).
- Planning: append-only event 92 imported with 1,711 nodes, zero invalid
  items, and zero malformed events (1.36 s, 17,032 KiB maximum RSS).
- Paper: claim map verified (0.68 s, 148,136 KiB maximum RSS) and the PDF
  built twice (1.75 s, 53,904 KiB maximum RSS).
- Science Forge shadow rail: advisory exit 0 in 6.82 s, but **not** a
  scientific pass. Its bridge audit failed closed on source-current Forge
  `E9415` drift, and its census found 1,971 certificates versus the
  2026-07-19 baseline of 976.

Tier 3 was not triggered: the all-field torus theorem, a collapsing family,
Witten/Poincare transfer, interacting measure, continuum limit, freeze, and
release gates all remain open.
