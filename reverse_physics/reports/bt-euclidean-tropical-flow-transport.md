# BT tropical flow transport and the remaining multiscale gate

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TROPICAL_FLOW_TRANSPORT_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

Lifecycle:
`SINGLE_SCALE_TROPICAL_COEFFICIENT_SHARPENED_MULTISCALE_UNIFORM_GATE_OPEN`

## Result

The leading coefficient in the BT maximal-jump theorem has a substantially
stronger universal lower bound than the earlier counting estimate. Let (G)
be a finite connected undirected graph, let

\[
                   \Omega_x(t)=t^{a_x},
                   \qquad t\longrightarrow\infty,
\]

and assume that the exponent profile is nonconstant. If

\[
 D=\max_{x\sim y}(a_y-a_x),
\]

then the predecessor proves

\[
 \lim_{t\to\infty}t^{-2D}
 {\|\nabla A\|_2^2\over\|r\|_2^2}
 ={\sum_xd_x^2\over\sum_xc_x^2}>0.
\]

The new theorem is

\[
 \boxed{
 {\sum_xd_x^2\over\sum_xc_x^2}
 \geq {2\over\operatorname{diam}(G)}.}
\]

The previous general-purpose floor was (1/(Nq^2)). On a four-dimensional
periodic (L)-torus, the new floor is at least (1/L), rather than order
(L^{-4}). After division by the free bilaplacian scale,

\[
 \boxed{
 \lim_{t\to\infty}t^{-2D}
 {\|\nabla A\|_2^2
  \over\omega_L^2\|r\|_2^2}
 \geq {L^3\over16\pi^4}.}
\]

This rules out a small leading coefficient on every exact one-scale power
ray. It does not give a remainder uniform in both (t) and (L). A bad
joint sequence could still keep many edge-ratio scales comparable while the
number of scales grows. That dense multiscale regime is now the precise
deterministic branch left open.

## 1. The maximal-jump coefficients are an integer flow

Orient every edge attaining the maximum jump (D) from lower to higher
exponent, and put

\[
                   c_x=\#\{y:a_y-a_x=D\}.
\]

The predecessor calculation gives

\[
 r_x=c_xt^D+o(t^D),
\]

and

\[
 (\nabla A)_x=d_xt^{2D}+o(t^{2D}),
 \qquad
 d_x=\sum_{y\to x}c_y-c_x^2.
\]

Assign flow (c_x) to each of the (c_x) edges leaving (x). Its total
outflow at (x) is (c_x^2), while its total inflow is
(sum_{y\to x}c_y). Therefore (d_x) is exactly inflow minus outflow.
In particular,

\[
                         \sum_xd_x=0.
\]

All capacities and divergences are integers. This integrality is important;
it is what upgrades a transport (L^1) estimate to the required squared
coefficient estimate.

## 2. Every flow path is geodesically short

The maximal-jump graph is acyclic because the exponent increases by (D>0)
on every oriented edge. More quantitatively, a directed path of length (k)
has endpoint exponent difference (kD).

On the other hand, (D) is the largest absolute exponent difference across
any graph edge. Along a shortest path between the same endpoints,

\[
 |a_{\rm end}-a_{\rm start}|
 \leq D\,\operatorname{dist}(\rm start,end)
 \leq D\,\operatorname{diam}(G).
\]

Hence

\[
                         k\leq\operatorname{diam}(G).
\]

This is stronger than acyclicity alone: maximal-jump flow cannot wind through
an arbitrarily large fraction of a graph whose metric diameter is small.

## 3. Flow decomposition proves the coefficient bound

Decompose the nonnegative acyclic flow into paths from vertices with net
outflow to vertices with net inflow. Let

\[
 F=\sum_xc_x^2
\]

be the total edge-flow mass and

\[
 S=\sum_{d_x>0}d_x
  =\sum_{d_x<0}(-d_x)
  ={1\over2}\sum_x|d_x|
\]

the transported mass. Every decomposed path has length at most the graph
diameter, so

\[
 F\leq\operatorname{diam}(G)S
 ={\operatorname{diam}(G)\over2}\sum_x|d_x|.
\]

Because every (d_x) is an integer,

\[
                         d_x^2\geq|d_x|.
\]

Consequently,

\[
 \sum_xd_x^2
 \geq\sum_x|d_x|
 \geq {2F\over\operatorname{diam}(G)},
\]

which proves the theorem after dividing by (F=sum c_x^2).

## 4. Four-torus scaling

For the nearest-neighbor four-torus,

\[
 \operatorname{diam}(T_L^4)=4\lfloor L/2\rfloor\leq2L.
\]

Therefore the leading coefficient is at least (1/L). Also

\[
 \omega_L=4\sin^2(\pi/L)\leq {4\pi^2\over L^2},
 \qquad
 \omega_L^2\leq {16\pi^4\over L^4}.
\]

Combining the two estimates yields the displayed normalized
(L^3/(16\pi^4)) floor.

This is a leading-coefficient statement. It does not say that there is one
value of (t) beyond which the asymptotic approximation is accurate for all
graphs and all exponent profiles. If successive edge jumps approach the
maximum ever more closely as (L) grows, the onset of the maximal-jump
asymptotic can be delayed. Such a construction uses a growing hierarchy of
scales and is not covered by a one-ray coefficient theorem.

## 5. Exact computational rails

The producer reconstructs the integer flow and gives a complete path
decomposition for three graph geometries:

- the four-cycle bowl;
- the six-cycle plateau;
- the (3\times3) torus single peak.

For every fixture, path mass reconstructs every edge capacity, transported
mass equals half the divergence (L^1) norm, every path respects the graph
diameter, and the coefficient satisfies the theorem.

The independent verifier does not import the producer. It rebuilds graph
distances, maximal-jump edges, capacities, divergence, and every stored path.
It additionally exhausts 636 normalized nonconstant exponent classes on
(C_4), (C_6), and (T_{3\times3}). This finite rail challenges the
implementation; the analytic flow proof supplies the universal theorem.

## 6. Meaning for the continuum programme

In ordinary language, a single dominant hierarchy cannot make the BT
landscape anomalously flat. Its leading residual behaves like flow along a
directed uphill network. That flow has to enter and leave somewhere, and the
finite graph diameter prevents it from hiding its boundary cost for too
long. On the four-torus, the resulting coefficient becomes larger relative
to the free continuum scale as the box grows.

The negative branch is therefore narrower. A genuine countersequence must
avoid having one asymptotically dominant edge scale. It must distribute the
field variation over a growing, densely spaced scale hierarchy, or it must
act directly through the full connection-corrected Witten form rather than
through the deterministic action-gradient quotient.

This is real progress toward the volume-uniform gate, but it does not meet
the work item's stop condition. No complete finite-amplitude (L)-uniform
PL bound, Witten/Poincare estimate, actual interacting (H^{-1}) moment,
controlled divergence, tightness, or continuum measure is established. The
finite-volume ordinary Osterwalder--Schrader obstruction remains unchanged.
There is no Born, Krein, or `LORENTZIAN-CAUSAL` promotion. Paper 21 is not
updated because no reconstruction or continuum lifecycle state changes.

## Next calculation

The next deterministic calculation is a quantitative finite-(W) scale
decomposition. Either:

1. sum the divergence cost across edge-ratio bands with constants uniform in
   (L), producing the first full quotient bound; or
2. construct an explicit hierarchy of increasingly close edge-ratio bands
   whose complete normalized quotient collapses.

Neither outcome can be transferred to the actual Gibbs (H^{-1}) moment
without the separately required Witten/annealed bridge.

## Verification

Run sequentially under the 500 MB cap:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_tropical_flow_transport.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tropical_flow_transport.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tropical_flow_transport
```

Tier 2 uses the unchanged predecessor by its recorded content hash. Tier 3 is
not triggered because this checkpoint does not promote the actual interacting
moment, continuum, reconstruction, freeze, release, or shared-core lifecycle.

The producer passed in 0.04 seconds at 20,684 KiB peak RSS. The independent
verifier passed in 0.12 seconds at 30,832 KiB and checked all 636 exponent
classes. All nine focused and adversarial-mutation tests passed in 0.88
seconds at 31,232 KiB. Python compilation passed in 0.04 seconds at 15,684
KiB. Strict JSON parsing and Draft 2020-12 schema validation passed under the
same memory ceiling.

The append-only sequence-87 planning event validated, and the independent
programme import folded 1,706 nodes with zero invalid items and zero malformed
events in 8.02 seconds at 201,944 KiB peak RSS. The advisory Science Forge
wrapper exited zero after 3.26 seconds at 341,952 KiB. Its underlying bridge
audit failed closed on the pre-existing Forge/stdlib revision drift and
missing SymPy in the bp2 environment, while the census reported the stale
July baseline (1,935 certificates versus 976). Those findings are recorded as
drift/failures, not as scientific passes.
