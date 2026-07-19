# Generic ghost n=3 barycentric factorization

## Result

The exact generic-momentum five-carrier projection has a much smaller
simplex singularity structure than its common `Delta^-4` presentation
suggests. With

```text
A = alpha1
B = alpha2
C = alpha0
Delta = C*A*x1 + A*B*x2 + B*C*x3
```

ten of the eleven raw projected numerators contain one exact factor of
`Delta`. Their pole order therefore drops from four to three before any
integration by parts or special kinematics are used. The only pole-four row
is

\[
 I_{29}^{123}:
 \qquad
 \frac{-16 A^3B^3C^3/27}{\Delta^4}.
\]

This is an exact `EUCLIDEAN-SPECTRAL` generic-kinematic integrand theorem.

## Boundary structure

After the cancellation and homogeneous barycentric lift, the edge valuations
are:

| channel | denominator | `(A,B,C)` edge orders |
| --- | ---: | --- |
| `I10_123` | `Delta^3` | `(0,0,0)` |
| `I24_123`, `I24_213`, `I24_312` | `Delta^3` | permutations of `(1,2,1)` |
| all three `I25` rows | `Delta^3` | `(1,1,1)` |
| all three `I28` rows | `Delta^3` | `(2,2,2)` |
| `I29_123` | `Delta^4` | `(3,3,3)` |

Thus `I10_123` is the only row with a nonzero direct restriction to an open
simplex edge. The other ten raw orientations, representing nine quotient
directions after the `I28` relation, vanish on every open edge.

This statement concerns the original reduced integrands. It does not prove
that a future choice of integration-by-parts primitive has zero corner flux
or that the final bubble/log coefficients vanish.

## Pointwise quotient relation

The three reduced `I28` numerators are

\[
\begin{aligned}
 \widetilde N_{28}^{123}
   &=\frac{32}{243}A^2B^2C^2(2A-B-C),\\
 \widetilde N_{28}^{132}
   &=-\frac{32}{243}A^2B^2C^2(A+B-2C),\\
 \widetilde N_{28}^{231}
   &=-\frac{32}{243}A^2B^2C^2(A-2B+C).
\end{aligned}
\]

Hence

\[
 \widetilde N_{28}^{123}
 +\widetilde N_{28}^{132}
 +\widetilde N_{28}^{231}=0
\]

as a polynomial identity, not merely after simplex integration or numerical
projection.

## Corner convergence

The certificate records the numerator order at each simplex vertex. For a
pole `Delta^-p`, the local integrability margin is stored as

\[
 m=v-p+2,
\]

where `v` is the numerator's vertex order. Every margin is positive; the
minimum is one and occurs in `I10`. This certifies convergence of the present
integrands at positive nonexceptional Euclidean kinematics. It does not
certify the corner flux of an as-yet-unconstructed rational IBP primitive.

## Consequence for the next solve

The generic integration problem now separates into two exact pieces:

1. a relative-interior IBP reduction for the ten edge-vanishing raw rows;
2. an edge-sensitive reduction for `I10`, with any bubble/log boundary data
   printed explicitly.

The next certificate must construct the rational simplex primitives, verify
their open-edge and punctured-corner fluxes, and reduce the result to the
scalar triangle plus edge-bubble masters. Until then the generic functions
remain `NOT_COMPUTED`.

## Claim boundary

This result does not compute the generic integrated form-factor functions,
edge-bubble coefficients, physical fourth-order Hessian, complete ghost
determinant, complete `Gamma1/Q1`, residual transfer, or any Lorentzian,
Hadamard, particle, positivity, scattering or unitarity theorem.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n3_barycentric_factorization --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n3_barycentric_factorization
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_ghost_n3_barycentric_factorization
```
