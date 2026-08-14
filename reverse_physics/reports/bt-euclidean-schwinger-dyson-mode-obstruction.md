# BT Schwinger--Dyson mode obstruction and quartic coercivity

**Date:** 2026-08-14

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1`

**Dependency:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

Two exact facts narrow the search for an interacting, volume-uniform field
estimate.

First, the nonlinear residual gives a genuine all-volume deterministic bound:

\[
 S_\lambda(\phi)\geq
 \frac{\lambda^2}{2N}
 \left(\sum_{\{x,y\}}(\phi_y-\phi_x)^2\right)^2.
\]

In four dimensions this uniformly confines every continuum-normalized lowest
axial Fourier coefficient at the level of action sublevel sets.

Second, the most direct Schwinger--Dyson conversion of this control into the
free Fourier covariance is obstructed. An exact spatially constant
configuration on the $6^4$ lattice makes the required pointwise interaction
remainder strictly negative.

The Gibbs expectation of that remainder is not decided. Therefore the
interacting $H^{-1}$ second-moment estimate remains open.

## Exact Schwinger--Dyson identity

On the mean-zero hyperplane, let $h$ be any fixed mean-zero real direction.
Finite-volume coercivity permits integration by parts without a boundary term:

\[
 \mathbb E_\lambda\!\left[(h\!\cdot\!\phi)
                  (h\!\cdot\!\nabla S_\lambda)\right]=\|h\|_2^2.
\]

If $(-\Delta_L)h=\omega h$, split off the free action and write

\[
 R_h(\phi)=(h\!\cdot\!\phi)\,
 h\!\cdot\!(\nabla S_\lambda-\nabla S_0).
\]

Then

\[
 \omega^2\mathbb E_\lambda[(h\!\cdot\!\phi)^2]
       +\mathbb E_\lambda[R_h]=\|h\|_2^2.
\]

A pointwise theorem $R_h\geq0$ would immediately bound the interacting mode
variance by its free value. The next calculation shows that this sufficient
route is false.

## Exact lowest-mode counterexample

Use $\psi=\lambda\phi=k\log2$, constant on each spatial slice, with

\[
 k=(-8,8,-2,-8,2,8),\qquad
 h=(2,1,-1,-2,-1,1).
\]

Both vectors have zero mean, and $h$ is a lowest time-circle mode:
$(-\Delta_6)h=h$. Per spatial site, exact rational differentiation gives

\[
 k\cdot h=16,\qquad \|h\|^2=12,\qquad
 D_hA=-\frac{36885875918835948063}{2147483648},\qquad
 D_hA_0=16.
\]

At $\lambda=2/5$, the full-lattice remainder factors as

\[
 R_h=\frac{216^2\,16\log2}{\lambda^2}
       \left(D_hA-16\log2\right)<0.
\]

No numerical approximation to $\log2$ is needed: the prefactor is positive,
while $D_hA<0$ and $-16\log2<0$. The independent verifier reconstructs all
$6^4$ sites and all eight neighbors rather than using the six-site reduction.

This counterexample blocks only a pointwise sign argument. It neither computes
nor fixes the Gibbs average $\mathbb E[R_h]$.

## All-volume quartic action bound

Write

\[
 r_x=\sum_{y\sim x}\left(e^{\psi_y-\psi_x}-1\right).
\]

Pairing the two orientations of each edge gives

\[
 \sum_xr_x=2\sum_{\{x,y\}}
       \left(\cosh(\psi_y-\psi_x)-1\right)
 \geq\sum_{\{x,y\}}(\psi_y-\psi_x)^2.
\]

The scalar inequality follows directly from the nonnegative tail of the
power series for $\cosh$. Cauchy--Schwarz then gives

\[
 \sum_xr_x^2\geq \frac1N\left(\sum_xr_x\right)^2,
\]

which proves the displayed quartic bound.

For the normalized axial coefficient

\[
 \widehat\Phi_L(e_\mu)=N^{-1}\sum_x\phi_xe^{-2\pi i x_\mu/L},
\]

Parseval and the lattice eigenvalue
$\omega_L=4\sin^2(\pi/L)$ imply

\[
 E_{\rm grad}(\phi)\geq
 N\omega_L|\widehat\Phi_L(e_\mu)|^2.
\]

Since $\sin(\pi/L)\geq2/L$ for $L\geq2$, one has
$N\omega_L^2\geq256$ in four dimensions. Hence

\[
 S_\lambda(\phi)\geq
 128\lambda^2|\widehat\Phi_L(e_\mu)|^4,
\]

with exact coefficient $512/25$ at $\lambda=2/5$.

## Why this is not yet the moment bound

The deterministic inequality controls which fields can lie in a fixed action
sublevel set. A Gibbs moment is a ratio of two integrals. Bounding the action
from below on a tail event does not, by itself, control the volume-dependent
normalizing partition function or the entropy of all orthogonal modes.

The remaining analytic target is therefore precise: control the normalized
one-mode marginal, or prove a favorable annealed sign for
$\mathbb E[R_h]$, uniformly in $L$. Pointwise signs and global strong
convexity are both unavailable.

The recent
[Anderson--Bateman--Herzog--Turok result](https://arxiv.org/abs/2608.12210)
establishes perturbative all-orders infrared finiteness for Euclidean
correlators and the perfect-square renormalization structure. It does not state
this nonperturbative normalized lattice Gibbs estimate. No literature-novelty
claim is made for the present finite-lattice identities without a dedicated
review.

## Verification

Run sequentially:

```text
python3 reverse_physics/bt_euclidean_schwinger_dyson_mode_obstruction.py --check
python3 reverse_physics/verify_bt_euclidean_schwinger_dyson_mode_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_schwinger_dyson_mode_obstruction
```

The result establishes no interacting $H^{-1}$ moment bound, tightness,
continuum measure, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` statement.
