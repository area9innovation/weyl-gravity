# Exact obstruction to global BT bilaplacian strong convexity

**Date:** 2026-08-14

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1`

**Dependency:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

The standard global strong-convexity route to an interacting, volume-uniform
negative-Sobolev estimate fails. On the spatially constant sector of the
periodic $6^4$ lattice, there is an exact one-parameter family for which the
directional Hessian of the nonlinear BT action becomes arbitrarily small
relative to the corresponding free bilaplacian form.

This is a proof-route obstruction. It is not an obstruction to the desired
interacting $H^{-1}$ moment bound itself.

## Exact family

Write $\psi=\lambda\phi$ and use integer coordinates $k$ through
$\psi=k\log 2$. For every positive integer $a$, take

\[
 k(a)=(-a,0,0,-a,a,a),\qquad
 v=(-1,-1,1,1,1,-1).
\]

Both profiles are mean zero and spatially constant. With

\[
 A(\psi)=\frac12\sum_x
 \left[\sum_{y\sim x}e^{\psi_y-\psi_x}-8\right]^2,
\]

exact differentiation gives, per spatial site,

\[
 \operatorname{Hess}A_{k(a)\log2}(v,v)
      =\frac{8(2^a+1)}{4^a},
 \qquad
 \sum_t(\Delta v_t)^2=16.
\]

Consequently,

\[
 \frac{\operatorname{Hess}A(v,v)}{\|\Delta v\|_2^2}
   =\frac{2^a+1}{2^{2a+1}}
   \leq 2^{-a}\longrightarrow0.
\]

Both forms acquire the same spatial-volume factor $6^3=216$ on the full
lattice. The ratio is therefore unchanged. Moreover, for
$S_\lambda(\phi)=A(\lambda\phi)/\lambda^2$, the two chain-rule factors of
$\lambda$ cancel the denominator. The statement applies in particular at
the exact coupling $\lambda=2/5$.

## Consequence

There cannot be a field-independent constant $c>0$ such that

\[
 \operatorname{Hess}S_\lambda(\phi)[v,v]
 \geq c\,\|\Delta v\|_2^2
\]

for every mean-zero field and direction. Therefore the usual uniform
Brascamp--Lieb comparison with the free bilaplacian covariance cannot provide
the interacting estimate sought by the continuum programme.

The calculation does **not** show that the full action is nonconvex: every
directional Hessian displayed here is positive. It also does not exclude a
localized, annealed, or otherwise nonuniform covariance argument.

## Independent verification

The producer reduces the spatially constant family to six time sites. The
independent verifier instead constructs all $6^4$ sites, enumerates all
eight nearest neighbors at every site, and differentiates the curvature
residual site by site using exact rational arithmetic. It reconstructs all
twelve committed fixtures and their common factor of 216.

Run sequentially under the repository memory policy:

```text
python3 reverse_physics/bt_euclidean_uniform_convexity_obstruction.py --check
python3 reverse_physics/verify_bt_euclidean_uniform_convexity_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_uniform_convexity_obstruction
```

The mutation rail rejects altered centers, ratios, method disposition,
dependency tags, provenance hashes, and undeclared fields.

## What remains open

The interacting $H^{-1}$ second-moment estimate remains the next continuum
gate. The viable analytic directions are now narrower:

1. an exact Schwinger--Dyson identity controlling Fourier modes directly;
2. an annealed inverse-Hessian or covariance estimate that tolerates rare
   weak-curvature configurations;
3. a multiscale estimate separating the global shift mode, infrared modes,
   and coercive large-field regions.

None of these routes is certified here. Tightness, a continuum Euclidean
measure, limit uniqueness, a Born rule, Krein reconstruction, and every
`LORENTZIAN-CAUSAL` claim remain unestablished.
