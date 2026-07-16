# Periodic Einstein--Maxwell gravitational mode: second-order obstruction

Date: 2026-07-16

## Result

The `LOCAL-ALGEBRAIC`, `REDUCED-MODE` certificate
`EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER` proves a fixed-charge
second-order obstruction for a smooth periodic `l=2` gravitational harmonic.

Let

```text
Y_20=(3 cos(theta)^2-1)/2,
X_phi=-sin(theta) partial_theta Y_20=3 sin(theta)^2 cos(theta).
```

The odd-parity metric mode and its magnetic-flux-forced Maxwell dressing are

```text
h1=2 H(t) X_phi dx dphi,
a1=q(t) Y_20 dx.
```

The complete linearized Einstein--Maxwell equations reduce exactly to

```text
H''+6H+2q=0,
q''+6q+6H=0.
```

Thus `omega_+^2=6+2 sqrt(3)`, `q=+sqrt(3)H` and
`omega_-^2=6-2 sqrt(3)`, `q=-sqrt(3)H`. The certificate tests the plus branch
with `H=cos(omega_+ t)`. Every component of the full linearized Einstein and
Maxwell residual vanishes.

This is not pure gauge. For `l=2`, Regge--Wheeler gauge fixes the axial angular
diffeomorphism, and the invariant base curl is proportional to `H'(t)X_phi`,
which is not identically zero. Both first-order Maxwell charge variations
vanish.

## Second-order pairing

At `t=0`, the convention-adjusted Chevreton tensor is nonzero and

```text
<C_Ch^(2)_tt>_S2 = -(36/5)(1+sqrt(3)).
```

The exact quadratic Weyl--Maxwell source has

```text
S2_tt|t=0 = (9/2) [(-101+45 sqrt(3)) sin(theta)^4
                    +(109-52 sqrt(3)) sin(theta)^2
                    -22+8 sqrt(3)],

<S2_tt>_S2 = -(12/5)(6+5 sqrt(3)) != 0.
```

After averaging a hypothetical correction over `S1 x SO(3)`, the linearized
`tt` row pairs to zero with the constant lapse at fixed electric and magnetic
charges. Its source pairing instead equals

```text
-48 pi L (6+5 sqrt(3))/5.
```

Therefore no smooth periodic second-order correction exists for the certified
plus branch. Evaluating one Cauchy slice is sufficient because a correction
would have to satisfy the averaged constraint on every slice.

## Interpretation

The compact obstruction now reaches a genuine gravitational multipole, not
only radion, duality, or photon directions. The linear gravitational state is
still present before the residual quotient; it is its nonlinear integrability
inside the fixed-charge Weyl--Maxwell solution locus that fails.

On this curved compact background, the precise statement is an odd-parity
`l=2` representative of the local metric/helicity-two sector with unavoidable
Maxwell dressing. It is not an asymptotic scattering-helicity theorem. Only
the plus normal branch is classified at second order, so the result is not a
no-go for every graviton harmonic or every boundary condition.

## Verification

Because exhaustive fourth-order regeneration exceeds the preferred 60-second
feedback loop, it is separated from the fast invariant rail.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compilation, JSON parsing, scoped `git diff --check` | < 0.1 s | PASS |
| 1 fast | generator/schema/input-hash verification | 0.31 s | PASS |
| 1 fast | independent eigenmode, charge, average, and provenance verifier | 0.78 s | PASS |
| 1 fast | scoped unit suite | 0.87 s | PASS (7 tests) |
| 1 exhaustive | exact fourth-order certificate generation | 77.50 s | PASS |
| 1 exhaustive | byte-for-byte tensor certificate regeneration | 79.57 s | PASS |

Tier 2 was not run because the imported certificates and tensor helper are
unchanged content-addressed inputs; this adds a direct reduced-mode consumer.
Tier 3 criteria were not met: no freeze, lifecycle promotion, shared-core
change, or release is involved.
