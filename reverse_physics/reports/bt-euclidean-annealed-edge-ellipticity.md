# BT annealed edge ellipticity

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The actual normalized BT Gibbs law suppresses every individual local
peak-to-valley jump uniformly in lattice volume. On the four-dimensional
periodic lattice at \(\lambda=2/5\), put

\[
 w_{xy}=e^{\psi_y-\psi_x},\qquad d_{xy}=\psi_y-\psi_x,
 \qquad r_x=\sum_{z\sim x}w_{xz}-8.
\]

For every directed nearest-neighbor edge,

\[
 \mathbb E w_{xy}^2\leq {8088\over25},
\]

and for the corresponding unoriented log jump,

\[
 \boxed{\mathbb E e^{2|d_{xy}|}\leq {16176\over25}.}
\]

Consequently,

\[
 \mu_{2/5}(|d_{xy}|\geq u)
 \leq {16176\over25}e^{-2u},\qquad u\geq0.
\]

The canonical weighted current

\[
 J_{xy}=r_xw_{xy}-r_yw_{yx}
\]

also has the volume-uniform first-moment estimate

\[
                         \mathbb E|J_{xy}|\leq {8932\over25}.
\]

These are actual interacting Gibbs estimates, not sampler observations or
reference-Gaussian estimates.

## Proof from the action-density theorem

The affine virial theorem already proves

\[
 {1\over N}\mathbb E A\leq {1222\over25},
 \qquad A={1\over2}\sum_xr_x^2.
\]

Translation invariance therefore gives

\[
                         \mathbb E r_x^2\leq {2444\over25}.
\]

All directed ratios leaving \(x\) are positive and sum to \(r_x+8\).
Hence

\[
 w_{xy}\leq r_x+8\leq |r_x|+8,
 \qquad
 w_{xy}^2\leq2r_x^2+128.
\]

Taking expectations gives \(8088/25\). Since

\[
 e^{2|d_{xy}|}=\max(w_{xy}^2,w_{yx}^2)
 \leq w_{xy}^2+w_{yx}^2,
\]

the exponential jump moment follows.

For the current, use

\[
 |r_x|w_{xy}
 \leq r_x^2+8|r_x|
 \leq {3\over2}r_x^2+32.
\]

Adding the reverse endpoint and averaging yields \(8932/25\).

## Sparse-edge consequences

There are \(4N\) undirected edges. If \(B_u\) counts those with
\(|d|\geq u\), then

\[
 {\mathbb E B_u\over N}
 \leq {64704\over25}e^{-2u},
\]

and for every \(\rho>0\),

\[
 \mu_{2/5}(B_u\geq\rho N)
 \leq {64704\over25\rho}e^{-2u}.
\]

The maximum edge jump satisfies

\[
 \mu_{2/5}(\max_e|d_e|\geq u)
 \leq {64704\over25}N e^{-2u}.
\]

Thus the unbounded global oscillation left open by the preceding gradient
theorem cannot normally be attributed to a positive density of arbitrarily
large single-edge jumps.

## What remains

This result controls local amplitudes but not their correlations. A field can
accumulate a large global change along a long path of moderate jumps, and a
low-frequency current can be built from many individually controlled blocks
whose phases add coherently. Neither possibility contradicts any bound above.

This identifies the next mathematical object more sharply: a multiscale
path/block extraction theorem under the integrated background marginal. It
must show that a large corrector forces many separated resampleable blocks,
or exhibit a coherent-path family that survives the Gibbs cost and has a low
full-Witten Rayleigh quotient. Merely strengthening a one-edge moment cannot
supply the missing Fourier factor.

The full-Gibbs theorem also does not automatically transfer to the zero-fiber
background marginal used by the center-score reduction. That transfer must be
proved rather than assumed.

## Boundaries

This certificate establishes no independence or correlation decay, current
hyperuniformity, all-field gradient constant, Poincare inequality, Witten
coercivity, interacting \(H^{-1}\) bound, continuum measure, Born rule, Krein
reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_edge_ellipticity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_edge_ellipticity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_edge_ellipticity
```
