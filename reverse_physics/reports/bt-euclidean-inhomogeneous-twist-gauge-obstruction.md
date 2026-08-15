# BT inhomogeneous-twist gauge obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_INHOMOGENEOUS_TWIST_GAUGE_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The positive uniform-twist response cannot be extended into the longitudinal
kernel needed to control scalar Fourier modes.  The longitudinal response is
exactly zero by a finite-volume gauge Ward identity.

For an antisymmetric oriented-edge field $\theta_{xy}=-\theta_{yx}$, define

\[
 r_x^\theta(\psi)
 =\sum_{y\sim x}\exp(\psi_y-\psi_x+\theta_{xy})-q.
\]

For any periodic site function $\chi$, let

\[
                  (d\chi)_{xy}=\chi_y-\chi_x.
\]

Then, pointwise,

\[
 \boxed{
 r_x^{\theta+d\chi}(\psi)=r_x^\theta(\psi+\chi),
 \qquad
 A_{\theta+d\chi}(\psi)=A_\theta(\psi+\chi).}
\]

On the mean-zero carrier, replace the translated field by
$\psi+\chi-\overline\chi$.  The constant subtraction changes no edge
difference, and Lebesgue measure is translation invariant.  Therefore

\[
                         \boxed{Z[\theta+d\chi]=Z[\theta].}
\]

This holds at every finite volume and every nonzero coupling for which the
finite integral is defined.  It is not perturbative.

## Longitudinal Ward nullspace

Let $F(\theta)=-\log Z[\theta]$.  Differentiating the exact gauge identity
gives

\[
 D F(\theta)[d\chi]=0.
\]

For the response Hessian $R_\theta=D^2F(\theta)$,

\[
                      \boxed{R_\theta d=0,
                      \qquad d^*R_\theta=0.}
\]

Thus the response factors through edge one-forms modulo exact gradients.  It
contains no longitudinal coercivity at all.

## Why the preceding uniform response survives

A spatially uniform twist along axis $\mu$ has zero plaquette curl and zero
lattice divergence, but its period around the torus is

\[
                              L\tau.
\]

Every periodic gradient has zero cycle period.  Hence a nonzero real uniform
twist is not exact: it is one of the $D$ harmonic torus representatives.

The positive $L=6,8$ response measured in the preceding checkpoint is
therefore a harmonic/topological response.  It is fully compatible with an
identically zero longitudinal response.  This is stronger than the earlier
logical two-direction non-transfer witness: the BT twist functional itself
has the wrong nullspace for a scalar $H^{-1}$ proof.

## Exact rational fixture

On the four-cycle take

\[
 \Omega=(1,2,1,1/2),
 \qquad G=(2,1,1/2,1).
\]

The gradient edge multipliers are $G_y/G_x$ and have holonomy one.  Exact
enumeration gives

\[
 r^{d\log G}(\Omega)
 =r^0(\Omega G)
 =(-3/4,-3/4,3,3),
\]

and both actions equal $153/16$.  By contrast, assigning multiplier two to
every forward edge has holonomy $2^4=16$, so it cannot be a periodic
gradient.

## Research consequence

The inhomogeneous-twist route is now closed for the scalar continuum gate.
The correct object is the sourced partition function

\[
 Z[J]=\int_H
 \exp\left[-A(\psi)/\lambda^2+\langle J,\psi\rangle\right]d\psi,
 \qquad \sum_xJ_x=0.
\]

Its second source derivative is the actual field covariance:

\[
             D_J^2\log Z[J]\big|_{J=0}
             =\operatorname{Cov}_\mu(\psi,\psi).
\]

A nonzero linear source is not removed by the edge-gauge change of variables.
Equivalent live formulations are the conditioned zero-fiber-score theorem
and the full Witten one-form Schur/resolvent problem for
$d\langle J,\psi\rangle$.

The next calculation should express this source Hessian in the certified
flat-potential/electrical coordinates, preserving the random-conductance
Green operator.  It must produce an upper bound for actual scalar Fourier
modes before the dyadic $H^{-1}$ shell sum can be attempted.

This obstruction does not show that the interacting $H^{-1}$ moment diverges
or that every source, Witten, conditioned-center, or heat-bath route fails.
It establishes no continuum limit, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` physics.  Paper 21 is unchanged because no reconstruction
or global-moment lifecycle state is promoted.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_inhomogeneous_twist_gauge_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_inhomogeneous_twist_gauge_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_inhomogeneous_twist_gauge_obstruction
```

The producer and verifier use separate exact rational enumerations of the
four-cycle fixture.  Tier 2 imports the unchanged uniform-twist certificate
by content hash.  Tier 3 is not run because this is a scoped proof-route
obstruction, not an $H^{-1}$, reconstruction, freeze, release, shared-core,
or Lorentzian lifecycle promotion.

The producer passed 16/16 checks in 0.04 s at 20,648 KiB, the non-importing
verifier passed 8/8 in 0.11 s at 30,100 KiB, and ten direct and adversarial
tests passed in 0.12 s at 30,712 KiB.  The planning importer accepted 1,682
nodes with zero invalid items and zero malformed events in 1.36 s under
`GOMEMLIMIT=300MiB` and `GOGC=50`.  The advisory Science Forge wrapper exited
zero in 3.48 s, but its bridge audit failed closed because the referenced
external `bp2transformer` verifier lacks `sympy`; it also reported corpus
drift (1,830 certificates versus baseline 976).  These findings are failures
and drift, not scientific passes.
