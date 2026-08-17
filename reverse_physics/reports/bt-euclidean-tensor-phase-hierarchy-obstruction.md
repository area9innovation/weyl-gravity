# BT independent tensor-phase hierarchy obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_TENSOR_PHASE_HIERARCHY_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

Lifecycle:
`INDEPENDENT_TENSOR_PHASE_ROUTE_RULED_OUT_NONSEPARABLE_CORRECTOR_GATE_OPEN`

## Result in ordinary language

Giving the polynomial-contrast cycle hierarchy two, three, or four
independent coordinates does not make it a four-dimensional low-gradient
configuration.

Let (u) be the certified positive hierarchy on
(C_L), with (L=4m^4+2), and put

\[
  \Omega(x)=\prod_{a=1}^k u(x_a),\qquad 2\leq k\leq4.
\]

This field no longer factors through one cyclic phase. Nevertheless, a
macroscopic part of every ramp has a fixed sign pattern: the cycle residual
is positive, while both the reverse-residual difference and the complete
cycle gradient are negative. All multidimensional cross terms reinforce the
gradient there instead of cancelling it. Exact counting gives

\[
 \boxed{
 \frac{\|g\|_2^2}{\|r\|_2^2}
 \geq \frac{1}{256\,40^k m^6}}
 \qquad(m\geq4,\ 2\leq k\leq4).
\]

Since the free bilaplacian scale is of order (L^{-4}=m^{-16}),

\[
 \boxed{
 \frac{\|g\|_2^2}{\omega_L^2\|r\|_2^2}
 \geq \frac{m^{10}}{16\,40^k\pi^4}
 \longrightarrow\infty.}
\]

Independent tensor phases therefore fail by ten powers of (m). A genuine
negative construction must couple its phases so that the cross terms change
sign across a macroscopic region; merely multiplying independently varying
profiles is insufficient.

## 1. Exact tensor identity

On the cycle define

\[
 \rho_i=\frac{u_{i+1}}{u_i}+\frac{u_{i-1}}{u_i}-2,
 \qquad
 \bar\rho_i=\frac{u_i}{u_{i+1}}+\frac{u_i}{u_{i-1}}-2,
 \qquad
 \delta_i=\bar\rho_i-\rho_i,
\]

and

\[
 J_i=\rho_i\frac{u_{i+1}}{u_i}
       -\rho_{i+1}\frac{u_i}{u_{i+1}},
 \qquad h_i=J_{i-1}-J_i.
\]

For the tensor field, inactive-coordinate contributions cancel exactly and

\[
                         r(x)=\sum_{a=1}^k\rho_{x_a}.
\]

Expanding the complete degree-eight log-field action gradient, including all
reverse-neighbour terms, gives

\[
 \boxed{
 g(x)=\sum_{a=1}^k h_{x_a}
       +\sum_{a\ne b}\delta_{x_a}\rho_{x_b}.}
\]

The second sum is load-bearing. It is precisely what a product of independent
profiles adds beyond a one-phase pullback. The certificate evaluates all
tensor norms from exact one-dimensional mixed moments. The independent rail
uses a separately derived closed combinatorial formula and also enumerates a
complete two-phase tensor directly.

## 2. Same-sign block on the hierarchy

Write (R=m^4), (s=(m-1)/R), and on the increasing ramp put
(z_i=1+si). Take

\[
 B=\{\lceil R/2\rceil+1,\ldots,\lfloor3R/4\rfloor\}.
\]

For (m\geq4), this block has at least (R/8) sites. Direct substitution
shows

\[
 \rho_i>0,\qquad \delta_i<0\qquad(i\in B).
\]

The current on the increasing ramp is (J_i=F_s(z_i)), where

\[
 F_s(z)=z^2+\frac{z}{z-s}-2z-1-\frac{s}{z}
        -\frac1{z^2}+\frac2z.
\]

On the displayed bulk, elementary differentiation gives

\[
 F_s'(z)\geq z-1.
\]

The mean-value theorem therefore yields

\[
 h_i=F_s(z_i-s)-F_s(z_i)
 \leq-\frac{1}{8m^2}.
\]

If every active coordinate lies in (B), every term in the tensor-gradient
identity is negative. Hence

\[
                         |g(x)|\geq\frac{k}{8m^2}.
\]

There are (|B|^kL^{4-k}) such four-torus sites, so

\[
 \|g\|_2^2\geq
 |B|^kL^{4-k}\frac{k^2}{64m^4}.
\]

Every directed cycle ratio and its inverse is at most (m), giving
(|\rho_i|\leq2m) and

\[
                         \|r\|_2^2\leq4k^2m^2L^4.
\]

Finally, (|B|/L\geq1/40), which proves the stated quotient bound.

## 3. Exact fixtures and independent rail

The producer reconstructs the complete rational cycle at (m=4) and
(m=5). For every (k=2,3,4), it stores the exact residual norm, gradient
norm, quotient, (m^6)-scaled quotient, and analytic floor. The observed
scaled quotients are already of ordinary size:

| (m) | (k=2) | (k=3) | (k=4) |
|---:|---:|---:|---:|
| 4 | 4.7200 | 5.3434 | 6.0907 |
| 5 | 4.7815 | 5.4600 | 6.2586 |

These decimals are only readable renderings of stored exact fractions; the
theorem uses the analytic rational floor.

The independent verifier does not import the producer. It reconstructs both
cycles, checks the complete bulk sign/floor statement, evaluates the tensor
norms through a closed mixed-moment formula, and directly enumerates every
site of a separate (m=2, k=2) tensor to challenge that formula.

Exploratory fixed-RMS optimization and additional sum, harmonic-mean, folded-
phase, and random-walk screens also found no collapsing branch. Those screens
are deliberately not certificate evidence and are not used in this theorem.

## 4. What remains open

The result removes two superficially different but mathematically low-rank
ways of recycling the cycle obstruction:

1. the predecessor removes every linear axial, diagonal, or helical
   single-phase pullback;
2. this theorem removes every independent multiplicative tensor of two to
   four copies of the hierarchy.

The remaining negative branch is narrower and genuinely nonlinear. It must
couple its phases so that (delta_a\rho_b) changes sign and cancels the cycle
gradients on a macroscopic set. The positive branch is the corresponding
localized weighted Rellich/Hodge theorem: combine the exact additive pairing
with four-torus cut geometry without inserting a global min/max condition
number.

This certificate does not establish an all-field torus lower bound, exclude
additive or genuinely coupled phase fields, prove Witten coercivity, decide
the interacting (H^{-1}) moment, construct a continuum measure or a
Born/Krein interpretation, or establish anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_tensor_phase_hierarchy_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tensor_phase_hierarchy_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tensor_phase_hierarchy_obstruction
```

## Verification receipt

- Producer: **PASS**, 10/10 exact checks (0.95 s, 22,660 KiB maximum
  RSS).
- Independent verifier: **PASS**, 11/11 checks (0.64 s, 32,756 KiB
  maximum RSS).
- Focused and mutation tests: **PASS**, 10/10 tests (5.25 s, 32,616
  KiB maximum RSS).
- Unchanged phase-pullback predecessor: **PASS**, 11/11 checks (0.19 s,
  30,960 KiB maximum RSS).
- Planning: append-only event 91 imported with 1,710 nodes, zero invalid
  items, and zero malformed events (1.42 s, 17,020 KiB maximum RSS).
- Paper: claim map verified (0.60 s, 148,408 KiB maximum RSS) and the PDF
  built twice (1.90 s, 53,700 KiB maximum RSS).
- Science Forge shadow rail: advisory exit 0, but **not** a scientific
  pass. Its bridge audit failed closed on source-current Forge `E9415`
  drift, and its read-only census found 1,970 certificates versus the
  2026-07-19 baseline of 976.

Tier 3 was not triggered: this result neither promotes a lifecycle state nor
claims the all-field torus theorem, interacting measure, continuum limit,
freeze, or release boundary.
