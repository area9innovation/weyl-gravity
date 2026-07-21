# Compact-product polar direct Lee--Wald completion

Date: 2026-07-21  
Team: Einstein/nonlinear bridge  
Science Forge item: `bridge-compact-product-polar-direct-lee-wald-completion`

## Outcome

The generic polar parity gap is closed before final residual descent. The
literal four-dimensional Weyl--Maxwell curvature-momentum potential produces
the polar current independently of the reduced Hessian. Exact coordinate
samples at `ell=2,3,4`, divided by their scalar harmonic norms and promoted by
the proved degree-two spectral bound, give

```text
field order: (A_t, B, C_t, U)

J_01 = -i k (k^2+lambda)/2
J_02 = -i (2k^2-lambda)(omega_1+omega_2)/8
J_11 = -i (4k^2+3lambda)(omega_1+omega_2)/4
J_12 =  i k (lambda-omega_1^2-omega_1 omega_2-omega_2^2)/2
J_22 =  i (omega_1+omega_2)(2lambda-omega_1^2-omega_2^2)/4
J_33 = -i lambda(omega_1+omega_2)
```

with the symmetric off-diagonal entries and all other entries zero. Only
after this direct interpolation is complete is the older reduced
Green/Hessian gate imported as a comparator; its remainder is the zero
`4x4` matrix.

## Load-bearing variation term

The complete `delta(nabla C)` contribution is retained. In the exact
`ell=2`, `(A_t,B)` entry its two pieces are

```text
nabla(delta C):                 -i*pi*k*(k^2+4)/5
delta Gamma acting on C_bar:    -2*i*pi*k/5
complete delta(nabla C):        -i*pi*k*(k^2+6)/5.
```

At `k=1`, omitting this term leaves the nonzero remainder `-7*i*pi/5`.
The independent verifier rejects this omission, an overall sign/content
mutation, and a factor-two normalization mutation.

## Shell pullback

Pulling the direct current to the two exact `p`-primary representatives gives

```text
det G_X^pol =
  9 lambda^2 (lambda-2) (9lambda-2)
    (3k^2+3lambda-2) (6k^2+3lambda-2)^2.
```

The formal collision locus consists of the zeros of the displayed factors,
together with `omega_e=0`. It has empty intersection with
`lambda=ell(ell+1)>=6` and real allowed compact momentum. Consequently:

- the polar extra block has radical dimension zero and inertia `(2,0)`;
- the exact Einstein `q`-primary image is orthogonal to it;
- the Einstein image has inertia `(1,1)`;
- the complete generic polar target has inertia `(3,1)`.

The axial completion has the same block inertias, but no representatives or
carrier languages are identified across parity.

## Controls and scope

The Maxwell `U-U` entry is exactly
`-i*lambda*(omega_1+omega_2)`. The existing independent
Einstein--Maxwell curvature-momentum fixture and flat constant-metric control
remain passing. The action convention is `alpha_B=3` and `-F^2/4`.

This is a `LOCAL-ALGEBRAIC/REDUCED-MODE` theorem for generic polar
`ell>=2`, all `m`, and every allowed compact `k`, including zero. It is before
the final residual quotient. Exceptional `ell<2`, causal evolution,
asymptotic scattering, particles, Hilbert norms, quantum ghosts, positivity
and unitarity are not established.

## Evidence

- certificate:
  `bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json`;
- independent verifier:
  `bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_direct_lee_wald_completion.py`;
- fail-closed atlas row:
  `einstein.ph.wm.polar.generic.direct_lee_wald`;
- paper update: `paper/92-extra-axial-lee-wald-bridge.md`.

The next gate is the polar ungauged BV/Noether lift and final residual descent.

## Verification timing

The exhaustive, independent coordinate replay passed all three interpolation
nodes: `ell=2` in 99.874 s, `ell=3` in 114.845 s, and `ell=4` in 191.541 s;
total 406.260 s. This long rail is Tier 2. The ordinary generator, independent
verifier and five mutation/scoped tests remain on the fast rail.
