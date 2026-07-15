# Einstein--Maxwell Chevreton tangent-inclusion receipt

Date: 2026-07-15

## Result

The `LOCAL-ALGEBRAIC` certificate
`EINSTEIN_MAXWELL_CHEVRETON_TANGENT` proves the complete **on-shell linear**
statement at the certified parallel-flux product background:

> Every solution of the full linearized source-free Einstein--Maxwell
> equations maps, by the identity on `(h_mn,a_m)`, to a solution of the full
> linearized pure-Weyl--Maxwell equations before any residual quotient.

This includes curvature-dependent lower-order terms and the mixing induced by
the nonzero background Maxwell flux. It upgrades the earlier principal-symbol
inclusion, but it is a solution-tangent theorem rather than an off-shell BV
chain-map theorem.

## Exact mechanism

Bergqvist and Eriksson's four-dimensional Einstein--Maxwell identity (their
Eq. (66), translated to the repository conventions) is

```text
B_mn - (2*kappa*Lambda/3) T_mn = C_Ch_mn,
```

where `C_Ch` is the convention-adjusted trace of the Chevreton tensor and is
homogeneous quadratic in `nabla F`. On the product solution, the aligned
Maxwell field is a linear combination of parallel factor volume forms, so
`nabla Fbar=0`. Consequently both `C_Ch(gbar,Fbar)` and its first variation
vanish for arbitrary `(h,a)`.

The certified product relations

```text
k1+k2 = 2*Lambda,
alpha_B*kappa*(k1+k2) = 3
```

give `alpha_B*(2*kappa*Lambda/3)=1`. Linearizing the identity on an
Einstein--Maxwell tangent therefore gives
`alpha_B*delta B_mn-delta T_mn=0`. The Maxwell equation is the same in both
theories. A direct exact coordinate calculation independently checks a
nontrivial radion tangent
`h=2*t^2*(-dt^2+dx^2)+2*dOmega_2^2`, `delta F=0` against both complete
linearized systems.

## Interpretation and boundary

The usual two metric and two photon null-symbol classes found in the
principal preflight are not artifacts of dropping lower-order terms: their
complete Einstein--Maxwell solution tangents survive in Weyl--Maxwell before
the final quotient. Thus a vanishing closed-cylinder residual one-particle
cohomology cannot be read as local disappearance of gravitational or photon
radiation; that vanishing concerns the later global residual reduction.

Because the Chevreton defect is quadratic in `nabla F`, its first possible
obstruction occurs at second order. The result does **not** certify nonlinear
Einstein--Maxwell closure. It also does not construct the curved off-shell BV
equation and identity maps, cyclic pairing, magnetic-bundle gluing,
presymplectic comparison, quotient injection, Lorentzian causal dynamics,
observables, scattering, or a quantum equivalence.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator, verifier, and scoped test | < 0.1 s | PASS |
| 1 | exact certificate generation | 2.16 s | PASS |
| 1 | independent verifier | 0.30 s | PASS |
| 1 | scoped unit suite | 2.10 s | PASS (7 tests) |

Tier 2 was not run because this adds a new isolated theorem importing two
content-addressed certificates without changing their operators or schemas.
Tier 3 criteria were not met.

## Pre-existing shared-tree changes

The classical team had an untracked Berger gauge-fixed nonminimal completion
generator, certificate, and report during this work. They are not included in
this certificate package.
