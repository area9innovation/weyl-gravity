# BT tropical gradient escape and fixed-graph PL theorem

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TROPICAL_GRADIENT_ESCAPE_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

Lifecycle:
FIXED_GRAPH_PL_PROVED_VOLUME_UNIFORM_CONSTANT_OPEN

## Result

Large field amplitude cannot make the BT residual-gradient quotient collapse
on a fixed finite graph. Let \(G\) be a finite connected \(q\)-regular
undirected graph and put

\[
 r_x={(\Delta\Omega)_x\over\Omega_x},\qquad
 A={1\over2}\sum_xr_x^2.
\]

On any nonconstant power ray

\[
                     \Omega_x(t)=t^{a_x},\qquad t\longrightarrow\infty,
\]

there is an explicit constant \(C(a)>0\) and a largest oriented edge jump

\[
 D=\max_{x\sim y}(a_y-a_x)>0
\]

such that

\[
 \boxed{\displaystyle
 {\|\nabla A\|_2^2\over\|r\|_2^2}
 =C(a)t^{2D}+o(t^{2D})\longrightarrow\infty.}
\]

The result is not restricted to the three certified fixtures. It follows
from the acyclic graph formed by all edges attaining the maximum exponent
jump.

Combining this boundary theorem with the certified unique-vacuum result and
the free bilaplacian expansion proves that every fixed connected graph has a
positive, graph-dependent Polyak--Lojasiewicz constant:

\[
 \boxed{\displaystyle
   \|\nabla A(\psi)\|_2^2\geq c_G\|r(\psi)\|_2^2
                         =2c_GA(\psi),\qquad c_G>0.}
\]

This is the strongest global fixed-volume action-gradient statement in the
BT programme so far. It does **not** prove that
\(c_G/\omega_G^2\) stays positive as the graph grows. That volume-uniform
constant, its transfer to the full Witten operator, and the interacting
\(H^{-1}\) moment remain open.

## 1. Exact maximal-jump graph

For each vertex define

\[
 c_x=\#\{y\sim x:a_y-a_x=D\}.
\]

Since every directed edge ratio is a monomial in \(t\), the residual has the
exact leading form

\[
                         r_x=c_xt^D+o(t^D).
\]

At least one \(c_x\) is nonzero. Therefore

\[
              \|r\|_2^2=t^{2D}\sum_xc_x^2+o(t^{2D}).
\]

Orient every edge whose exponent jump is exactly \(D\) from its lower to its
higher endpoint. Exponents strictly increase along every oriented edge, so
this maximal-jump graph is acyclic.

The log-coordinate action gradient is

\[
 (\nabla A)_x
 =\sum_{y\sim x}r_y t^{a_x-a_y}
   -r_x\sum_{y\sim x}t^{a_y-a_x}.
\]

Its coefficient at degree \(2D\) is

\[
 d_x=\sum_{\substack{y\sim x\\a_x-a_y=D}}c_y-c_x^2.
\]

Choose a minimum-exponent vertex among the tails of the maximal-jump edges.
It has \(c_x>0\), but it cannot have an incoming maximal-jump edge: such an
edge would have a still lower tail. Hence

\[
                         d_x=-c_x^2\ne0.
\]

This single source vertex prevents leading-order cancellation. Consequently,

\[
 \|\nabla A\|_2^2=t^{4D}\sum_xd_x^2+o(t^{4D})
\]

and

\[
 \boxed{\displaystyle
 C(a)=\frac{\sum_xd_x^2}{\sum_xc_x^2}>0.}
\]

Since the \(c_x\) are integers between zero and \(q\), the elementary bound

\[
                         C(a)\geq{1\over Nq^2}
\]

also holds. It is not claimed to be sharp.

## 2. From fixed rays to every fixed-graph escape

A general unbounded sequence need not lie on one preselected power ray. For
each field put

\[
 W=\max_{x\sim y}e^{\psi_y-\psi_x}.
\]

On a fixed connected graph, the field oscillation is at most the graph
diameter times the largest edge jump. Thus
\(\operatorname{osc}\psi\to\infty\) implies \(W\to\infty\).

Suppose a sequence escaped but its gradient quotient did not diverge. Pass to
a subsequence on which every normalized directed edge ratio

\[
                 \alpha_{xy}={e^{\psi_y-\psi_x}\over W}
\]

converges in \([0,1]\). At least one limit equals one. The positive limiting
edges cannot contain a directed cycle: every such edge has log ratio
\(\log W+O(1)\), while the log ratios around a cycle sum to zero.

Put \(c_x=\sum_y\alpha_{xy}\) using the limiting weights. Direct division of
the exact residual and gradient formulas gives

\[
 {r_x\over W}\longrightarrow c_x,\qquad
 {(\nabla A)_x\over W^2}\longrightarrow
 d_x:=\sum_yc_y\alpha_{yx}-c_x^2.
\]

The positive limiting graph has a source tail with at least one outgoing
edge. At that vertex \(c_x>0\), the incoming sum vanishes, and
\(d_x=-c_x^2\ne0\). Consequently

\[
 {1\over W^2}{\|\nabla A\|_2^2\over\|r\|_2^2}
 \longrightarrow{\sum_xd_x^2\over\sum_xc_x^2}>0.
\]

Since \(W\to\infty\), this contradicts boundedness. Hence

\[
 {\|\nabla A(\psi_n)\|_2^2\over\|r(\psi_n)\|_2^2}
 \longrightarrow\infty
\]

on every fixed graph whenever \(\operatorname{osc}\psi_n\to\infty\). This
maximum-normalized edge-ratio argument is the step that promotes the
displayed power-ray formula from a family calculation to a fixed-graph
boundary theorem.

## 3. Fixed-graph Polyak--Lojasiewicz consequence

Define, away from the constant field,

\[
 Q_G(\psi)={\|\nabla A(\psi)\|_2^2\over\|r(\psi)\|_2^2}.
\]

Near the vacuum,

\[
 r=\Delta\psi+O(\|\psi\|^2),\qquad
 \nabla A=\Delta^2\psi+O(\|\psi\|^2).
\]

If \(\omega_G\) is the first positive eigenvalue of \(-\Delta\), spectral
decomposition gives

\[
 \liminf_{\psi\to0}Q_G(\psi)\geq\omega_G^2.
\]

At the other end, the tropical theorem gives \(Q_G\to\infty\) as the field
oscillation tends to infinity. Between those two regions, the mean-zero
carrier contains only a compact annulus. The predecessor theorem proves that
the vacuum is the only critical point, so both the numerator and denominator
are nonzero throughout that annulus. Continuity therefore gives a strictly
positive minimum \(c_G\).

This proves

\[
             \|\nabla A\|_2^2\geq c_G\|r\|_2^2=2c_GA.
\]

The proof is nonconstructive in its compact-annulus step. More importantly,
it gives one number for each fixed graph, not a common lower bound for a
growing sequence of tori.

## 4. Exact rails

The producer constructs the complete integer Laurent polynomials for three
different profiles:

- a bowl on \(C_4\);
- a plateau on \(C_6\);
- a single peak on the \(3\times3\) torus.

For each profile it verifies that the residual degree is \(D\), the gradient
degree is \(2D\), the source coefficient is a negative square, the leading
quotient coefficient is positive, and direct exact evaluation at \(t=2\)
agrees with the polynomial construction.

The independent verifier does not import the producer. It reconstructs the
positive field, residual, and oriented-edge action gradient directly with
rational arithmetic. It also exhausts 621 nonconstant exponent classes:

\[
 124\text{ on }C_4,\qquad
 242\text{ on }C_6,\qquad
 255\text{ on }T_{3\times3}.
\]

Every class has an acyclic maximal-jump source, a nonzero negative-square
gradient coefficient, and the declared \(1/(Nq^2)\) coefficient floor. This
finite audit is an adversarial rail for the universal proof; it is not used
as a replacement for that proof.

## 5. Meaning for the continuum barrier

In ordinary language, sending some positive lattice fields to enormous
values and others to tiny values does not make the BT action flat on a fixed
lattice. The residual grows once with the largest local ratio, while the
action gradient feels that ratio twice. The field becomes steeper, not more
stationary.

This rules out a hidden fixed-volume escape mechanism and strengthens the
earlier observation that the exact additive contraction can become slow even
when the ordinary Euclidean action gradient becomes very large. The two
flows must not be confused.

The result also identifies the remaining negative branch more sharply. A
counterexample must use \(L\to\infty\) and distribute its structure across
growing scales. It cannot be obtained by taking a fixed finite pattern and
only increasing its amplitude. The live quantity is

\[
 \gamma_L=\inf_{\psi\ne0}
 {\|\nabla A(\psi)\|_2^2
  \over\omega_L^2\|r(\psi)\|_2^2}.
\]

The next theorem must prove \(\inf_L\gamma_L>0\), then supply a valid
Lyapunov/Witten transfer, or construct a genuinely growing-volume sequence
for which the normalized gradient or full-Witten Rayleigh quotient collapses
with nonzero lowest-mode overlap.

This certificate does not prove either branch. It establishes no global
Poincare theorem, no full Witten coercivity, no interacting \(H^{-1}\)
moment, no tightness or continuum measure, no Born rule, and no Krein or
LORENTZIAN-CAUSAL reconstruction. The existing finite-volume ordinary-OS
obstruction remains unchanged. Paper 21 is not updated because no
reconstruction or continuum lifecycle state is promoted.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_tropical_gradient_escape.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tropical_gradient_escape.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tropical_gradient_escape

Tier 3 is not triggered: the graph-size-uniform PL constant, its Witten
bridge, the actual interacting \(H^{-1}\) moment, and all continuum and
reconstruction lifecycle states remain open.

The deterministic producer passed in 0.04 seconds at 20,740 KiB peak RSS.
The nonimporting verifier, including all 621 exponent classes, passed in 0.10
seconds at 30,216 KiB. All fourteen focused and adversarial-mutation tests
passed in 0.17 seconds at 30,616 KiB. Python compilation, strict JSON parsing,
and Draft 2020-12 schema validation also passed under the same memory ceiling.

The append-only sequence-86 planning event passed in 6.37 seconds at 188,416
KiB peak RSS. The independent programme import folded 1,705 nodes with zero
invalid items and zero malformed events in 6.65 seconds at 208,272 KiB. The
read-only Science Forge wrapper exited zero in advisory mode after 3.17
seconds at 333,392 KiB; its bridge audit failed closed on the pre-existing
Forge/stdlib revision drift and missing SymPy in the bp2 bridge verifier, and
its census reported the stale July baseline (1,930 certificates versus 976).
Those findings are recorded as drift/failures, not scientific passes.
