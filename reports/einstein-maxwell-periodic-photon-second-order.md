# Periodic Einstein--Maxwell photon: second-order obstruction

Date: 2026-07-16

## Result

The `LOCAL-ALGEBRAIC`, `REDUCED-MODE` certificate
`EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER` closes the first physical-mode
gate left open by the earlier second-order inclusion test.

On the certified `R_t x S1_L x S2` product background, consider

```text
a1 = cos(2t) cos(theta) dx,
h1 = 2 cos(2t) sin(theta)^2 dx dphi.
```

Here `cos(theta)` is the smooth `l=1` scalar harmonic and
`sin(theta)^2 dphi` is the smooth axial Killing one-form. The exact coupled
linear equations reduce to

```text
H''+2H+2q=0,
q''+2q+2H=0.
```

The physical eigenvector is `H=q` with `omega^2=4`. The complete linearized
Einstein and Maxwell residuals vanish. Both first-order Maxwell charge
variations vanish, so this is a genuine periodic photon--metric normal mode,
not the global duality direction tested previously.

## Quadratic tensors

The convention-adjusted Chevreton coefficient is nonzero. Its `tt` component
can be written

```text
C_Ch^(2)_tt = 8(sin(theta)^2-1)
              +(8-12 sin(theta)^2) sin(2t)^2,
```

and its normalized sphere average is `-8/3`.

The exact affine quadratic Weyl--Maxwell source projection is

```text
S2_tt = 1-(19/2)sin(theta)^2
        +((63/2)sin(theta)^2-21)sin(2t)^2.
```

Its normalized sphere average is the time-independent value `-16/3`.

## Adjoint-cokernel obstruction

Average any hypothetical second-order correction over `S1 x SO(3)`. The
linearized operator is equivariant, so the averaged correction must solve the
averaged equation. In invariant Diff x Weyl gauge, the spatially averaged
linearized `tt` row consists of spatial total derivatives and the second-order
magnetic-flux coefficient `p`. Fixed electric and magnetic charges set `p=0`;
an averaged electric correction has zero linear stress pairing with the purely
magnetic background.

The linear-row pairing with the constant lapse is therefore zero, while the
source pairing is

```text
<1,S2_tt>_(S1 x S2) = -(64 pi L)/3 != 0.
```

Hence no smooth periodic second-order Weyl--Maxwell correction exists for
this declared tangent at fixed charges. Only this projected source is needed:
one nonzero adjoint-cokernel pairing already proves the no-solution result.

## Interpretation

The compact fixed-charge obstruction is not confined to zero modes. It occurs
for a real, nonzero-frequency photon harmonic that is present in the complete
linear Einstein--Maxwell tangent space before the residual quotient. This does
not remove the linear photon; it says that this tangent is not integrable to
second order inside the fixed-charge compact Weyl--Maxwell solution locus.

The result is not a no-go for all photon harmonics, does not yet treat a
periodic helicity-two mode, and makes no asymptotically flat, causal,
observable, scattering, or quantum claim. The next discriminating gate is one
periodic helicity-two harmonic.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator, verifier, and tests; schema/certificate JSON parse | < 0.1 s | PASS |
| 1 | exact tensor certificate generation | 26.49 s | PASS |
| 1 | independent charge, harmonic, average, and provenance verifier | 0.51 s | PASS |
| 1 | scoped unit suite | 26.34 s | PASS (7 tests) |

Tier 2 was not run because the three imported certificates are unchanged,
content-addressed inputs and this theorem adds a new isolated reduced-mode
fixture. Tier 3 criteria were not met: no freeze/tag, lifecycle promotion,
shared-core algebra change, or release is involved.
