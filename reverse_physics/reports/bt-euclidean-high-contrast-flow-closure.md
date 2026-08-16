# BT finite-amplitude high-contrast flow closure

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_HIGH_CONTRAST_FLOW_CLOSURE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`HIGH_CONTRAST_SECTOR_CLOSED_MODERATE_MULTISCALE_GATE_OPEN`

## Result

An increasingly large nearest-neighbor field spike cannot hide in the
finite-amplitude remainder of the BT tropical flow theorem.  Let (G) be a
finite connected simple (q)-regular graph with (N) vertices, let
(Omega_x>0) be nonconstant, and put

\[
 r_x={\Delta\Omega_x\over\Omega_x},\qquad
 A={1\over2}\sum_xr_x^2,
\]

with (g=\nabla_{\log\Omega}A).  Define the largest unoriented edge ratio

\[
 W=\max_{\{x,y\}\in E}
 \max\left({\Omega_y\over\Omega_x},{\Omega_x\over\Omega_y}\right)>1.
\]

The new finite-amplitude theorem is

\[
 \boxed{
 W\geq3q^2N(N-1)
 \quad\Longrightarrow\quad
 {\|g\|_2^2\over\|r\|_2^2}\geq9q^2.}
\]

Every eigenvalue of the graph Laplacian lies in ([0,2q]).  If
(omega_G) is its smallest positive eigenvalue, the conclusion is therefore
stronger than

\[
             {\|g\|_2^2\over\|r\|_2^2}
             \geq {9\over4}\omega_G^2.
\]

Thus a sequence whose quotient collapses relative to the free infrared scale
must obey

\[
                         W<3q^2N(N-1).
\]

This converts the open dense-hierarchy branch from an unrestricted edge-ratio
range to only (O(\log N)) multiplicative bands.

## 1. Exact residual split

Orient each unequal edge from its lower to its higher endpoint.  On an
oriented edge (e=(x,y)), write

\[
 z_e={\Omega_y\over\Omega_x},\qquad
 \alpha_e={z_e\over W}\in[W^{-1},1].
\]

Equal-field edges are left unoriented for the moment.  At each vertex define

\[
                         c_x=\sum_{e:x\to y}\alpha_e.
\]

Every incoming ratio and every equal-edge ratio is at most one, so the exact
residual decomposition is

\[
                         r_x=Wc_x+h_x,
             \qquad -q\leq h_x\leq0.
\]

Some edge attains (z_e=W).  Its tail has (c_x\geq1), and hence

\[
                         F:=\sum_xc_x^2\geq1.
\]

No limiting argument has been used: these identities hold at the original
finite field amplitude.

## 2. The exact current is a large acyclic flow plus an error

The canonical oriented current is

\[
                         J_e=r_xz_e-{r_y\over z_e},
\]

and its graph divergence is exactly (g).  Substitution of (r=Wc+h)
gives

\[
 J_e=W^2c_x\alpha_e+\epsilon_e,
 \qquad
 \epsilon_e=Wh_x\alpha_e-{c_y\over\alpha_e}
                         -{h_y\over W\alpha_e}.
\]

Since (0\leq c_y\leq q), (|h|\leq q), and
(W^{-1}\leq\alpha_e\leq1),

\[
                         |\epsilon_e|\leq3qW.
\]

On an equal edge, put the complete current (r_x-r_y) into
(epsilon_e); the same bound remains valid.  The graph incidence estimate
then gives

\[
                     \|\operatorname{div}\epsilon\|_2
                     \leq3q^2W\sqrt N.
\]

For the leading term put flow

\[
                         f_e=c_x\alpha_e
\]

on every increasing edge, and let (d=\operatorname{div}f).  Its total
edge-flow mass is exactly

\[
              \sum_ef_e=\sum_xc_x\sum_{e:x\to y}\alpha_e
                         =\sum_xc_x^2=F.
\]

Because the scalar field strictly increases on every oriented edge, this
flow graph is acyclic.  Decompose it into source-to-sink paths.  Every path is
simple and has length at most (N-1).  The total transported source mass is
(|d|_1/2), while (F) counts that mass once per traversed edge.  Therefore

\[
                F\leq{N-1\over2}\|d\|_1,
 \qquad
                \|d\|_2\geq{2F\over(N-1)\sqrt N}.
\]

The full finite-amplitude gradient is

\[
                         g=W^2d+\operatorname{div}\epsilon.
\]

At (W\geq3q^2N(N-1)), the error is at most half the transport lower
bound, so

\[
                         \|g\|_2
                         \geq{W^2\over(N-1)\sqrt N}.
\]

Every directed neighbor ratio lies in ([W^{-1},W]), hence
(|r_x|\leq q(W-1)\leq qW) and

\[
                         \|r\|_2\leq qW\sqrt N.
\]

Division proves

\[
 {\|g\|_2^2\over\|r\|_2^2}
 \geq{W^2\over q^2N^2(N-1)^2}
 \geq9q^2.
\]

## 3. Actual interacting Gibbs consequence

The predecessor edge-ellipticity certificate is an actual interacting theorem
at (lambda=2/5), not a reference-Gaussian or sampler statement.  On every
undirected nearest-neighbor edge of the four-torus it gives

\[
          \mathbb E\exp(2|\psi_y-\psi_x|)\leq{16176\over25}.
\]

There are (4N) undirected edges and (q=8).  A union bound followed by
Markov's inequality at the deterministic threshold

\[
                       3q^2N(N-1)=192N(N-1)
\]

therefore gives the exact probability estimate

\[
 \boxed{
 \mu_{2/5}\!\left(W\geq192N(N-1)\right)
 \leq {337\over4800N(N-1)^2}.}
\]

The bound is (O(N^{-3})=O(L^{-12})).  In particular, the sequence of these
one-volume exceptional probabilities is summable.  On its complement,
(log W=O(\log N)), so only logarithmically many dyadic ratio bands remain.
No independence between edges was assumed.

This is the first place where the tropical transport calculation and an
actual normalized Gibbs estimate meet.  It closes the enormous-local-spike
branch, but it does not control correlations among the remaining moderate
bands.

## 4. Exact rails

The producer stores three rational finite-amplitude fields: a single-band
four-cycle, a two-band five-cycle, and a (3\times3) pyramid.  It records
the residual, full gradient, normalized outgoing masses, bounded remainder,
main flow divergence, edge currents, error currents, and all relevant norms.

The independent verifier does not import the producer.  It reconstructs all
three fixtures directly from their adjacency lists and positive rational
fields, performs an independent rational path decomposition, and checks 318
nonconstant rational fields on the four- and five-cycles.  It also re-derives
the constants (9q^2) and (337/4800) from the pinned predecessor.

## Meaning for the continuum barrier

The previous tropical theorem ruled out one exact asymptotic scale.  The new
theorem closes a different loophole: taking the largest edge ratio so large
that the asymptotic onset might depend badly on volume.  Such fields are both
deterministically strongly coercive and summably rare under the actual Gibbs
law.

The unresolved branch is now genuinely moderate and collective.  A bad
sequence must keep every local ratio below (O(N^2)), distribute its current
over (O(\log N)) ratio bands, and arrange cancellations or transverse
correctors across growing distances.  The next calculation is a band-to-block
transport estimate on this polynomial-contrast sector, followed by a Witten
or conditional-center transfer.  Alternatively, one must construct an actual
polynomial-contrast low-Rayleigh sequence.

## Boundaries

This result does not establish an all-field volume-uniform Polyak--Lojasiewicz
constant, a Poincare inequality, Witten one-form coercivity, boundedness or
divergence of the actual interacting (H^{-1}) moment, tightness, a continuum
measure, or a continuum Osterwalder--Schrader theorem.  It supplies no Born
rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` claim.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_high_contrast_flow_closure.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_high_contrast_flow_closure.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_high_contrast_flow_closure
```
