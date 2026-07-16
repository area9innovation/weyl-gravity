# Compact Einstein--Maxwell polar master complex

Date: 2026-07-16

## Theorem

`COMPACT_EM_POLAR_MASTER_COMPLEX` promotes the polar preflight to an exact
arbitrary-harmonic theorem for every periodic `S1` momentum and every
`(ell,m)` with `ell>=2` on the fixed compact `U(1)` bundle. Its generality is
`G2_POLAR_ALL_N_ELL_M_ELL_GE2`, with dependency tags `LOCAL-ALGEBRAIC` and
`REDUCED-MODE`.

The exceptional `ell=0,1` complexes and covariant symplectic normalization
remain open and are not included in this theorem.

## Full tensor identity

The generator uses an abstract axisymmetric eigenfunction satisfying only

```text
Y''+cot(theta)Y'+lambda Y=0
```

and its differentiated identity. It constructs the complete linearized
Einstein tensor and Maxwell density separately for each gauge-fixed
coefficient `(A,B,C,K,U)`. All Einstein components, all four Maxwell density
components, and every unlisted tensor component agree exactly with the
declared `8 x 5` harmonic matrix.

The Maxwell calculation retains the perturbed `sqrt(-g)`. This is essential
for the row

```text
(A-C)/2+K+(omega^2-k^2-lambda)U=0.
```

No fixed-`ell` interpolation is used in this promotion.

## Gauge theorem and all `m`

Before gauge fixing, the metric coefficients include `h_A D_aY` and the
tracefree tensor coefficient `G`. For a polar diffeomorphism
`(xi_A Y,xi D_aY)`, the relevant transformations are

```text
delta G=2xi,
delta h_A=xi_A+partial_A xi,
delta K=-lambda xi,
delta U=-xi.
```

The last transformation is induced by contraction of the diffeomorphism with
the background magnetic flux. The squared-norm factor of the tracefree
tensor harmonic is

```text
lambda(lambda-2)/2.
```

It is nonzero for `ell>=2`, where `lambda>=6`. Consequently `G=0` fixes `xi`
uniquely and `h_A=0` then fixes `xi_A` uniquely; no smooth residual polar
gauge remains.

The product metric and magnetic volume form are `SO(3)`-invariant, and the
linearized equations are natural and equivariant. Each `ell` eigenspace is an
irreducible `SO(3)` representation. The coefficient matrix computed on one
nonzero representative therefore acts as that same multiplicity-space matrix
tensored with the identity on every `m`.

## Singular reconstruction audit

For `s=omega^2-k^2` nonzero, the constraints reconstruct

```text
R=K-2U,
A=C=-(omega^2+k^2)R/s,
B=2k omega R/s.
```

The apparent singularity at `s=0` is checked independently rather than
divided away. The five-row minor using

```text
E00,E01,E11,sphere tracefree,Maxwell axial density
```

is exactly

```text
lambda^3(lambda-2)/8.
```

It is nonzero for every `ell>=2`, including `omega=k=0`. Hence the
gauge-fixed `s=0` matrix has full column rank and only the zero solution. No
lightlike constraint mode or zero-block solution was lost in the master
reconstruction.

## Master system and interpretation

The remaining polar masters `(K,U)` have

```text
K_polar=[[lambda,-2lambda],[-1,lambda]],
omega_+^2=k_n^2+lambda+sqrt(2lambda),
omega_-^2=k_n^2+lambda-sqrt(2lambda).
```

For `ell>=2`, both mass-squared values are positive. They coincide exactly
with the axial spectrum for every `(n,ell,m)`, although the two parity sectors
have different reconstruction maps.

This completes both radiative parity towers before the residual quotient.
It is direct evidence that the ordinary local gravitational-wave modes have
not disappeared. A vanishing final residual one-particle cohomology on the
closed cylinder concerns the subsequent global quotient, not the existence
of these linearized solutions.

The reduced master matrix is symmetrized by `W=diag(1,2lambda)`. Matching its
current, and the axial current, to the covariant Einstein--Maxwell
presymplectic form is still required before assigning physical norms or
normalizing the adjoint/Taub coefficient table.

## Next gate

The next theorem should classify the exceptional polar `ell=0` and `ell=1`
complexes without extrapolating the `ell>=2` gauge. After that, axial and
polar reduced currents can be matched to the covariant symplectic current,
followed by the remaining fourth-order adjoint blocks.

## Verification

The generator performs five arbitrary-harmonic full-tensor column checks and
the exact singular-rank audit. An independent verifier reconstructs all eight
equations, the master reduction, characteristic polynomial, symmetrizer,
gauge-fixing rank, and `s=0` minor without importing the generator. Ten scoped
tests cover the theorem and its fail-closed boundaries. Generator verification
passed in `22.58 s`, the independent verifier in `0.61 s`, and the ten-test
suite in `23.27 s`. This promotion changes a mathematical input used by the
compact programme, so the affected programme certificate chain is run during
registration. Tier 3 criteria are not met because exceptional modes,
symplectic matching, and the full adjoint theorem remain explicitly open.
