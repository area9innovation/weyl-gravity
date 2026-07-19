# Complete polar--polar cross-momentum L=4 source matrix

## Result

The complete polar--polar part of the axisymmetric two-absolute-momentum
workload is classified. It contains twelve separately tuned resonance rows,
twenty input branch-basis fixtures and twenty-seven scalar target-adjoint
coefficients. The input branches are the Einstein `q_minus` and `q_plus`
primaries and both `p_extra` basis representatives on each retained momentum
fibre.

Exactly one scalar coefficient vanishes and the other twenty-six have exact
rational intervals excluding zero. Every one of the twenty declared polar
branch-basis fixtures therefore has a nonzero complete target-cokernel vector
and is `OBSTRUCTED` in the bounded or finite-quasiperiodic correction class.

This is a basis-fixture theorem, not the zero variety of the full bilinear
matrix. Cancellations among arbitrary polar linear combinations remain
`OPEN`.

## Action-derived source and calibration

The calculation extracts a content-addressed bilinear source slice from the
certified Weyl--Maxwell product `q2` payload. It retains arbitrary signed
`k_1,k_2`, arbitrary `omega_1,omega_2`, and two arbitrary polar gauge-slice
vectors in the order `(A_t,B,C_t,U)`. The 1,576 retained PBW terms produce the
four action-normalized polar `L=4` rows.

The slice is independently calibrated by specializing both inputs to the
previously certified opposite-momentum Einstein-minus representatives. It
reproduces the older direct four-dimensional polar--polar source exactly.
Every input branch representative is also checked directly against the polar
action Hessian on its declared shell.

## Nonvanishing proof

Each stored radical pairing is evaluated by exact outward rational interval
arithmetic. Square-root endpoints use integer square roots at a declared
decimal scale; additions, products and reciprocals remain rational. Every
nonzero coefficient has a stored interval strictly on one side of zero. No
floating-point sign test supports the obstruction theorem.

The independent verifier does not import the producer. It checks the q2,
action and row-layout hashes, reconstructs the earlier direct calibration,
replays every rational interval and independently checks all target-shell
relations.

## Workload disposition

Together with the axial--axial matrix, 54 of 108 axisymmetric `L=4`
coefficients are now resolved. The remaining 54 are the two ordered
cross-parity matrices. All 56 nonaxisymmetric `L=1,3` coefficients remain
open.

Smooth-secular correction is `OPEN`; causal/retarded correction is
`NO_CERTIFIED_MAP`. The twelve circumference rows remain distinct. No
complete tangent-cone, residual, observational or quantum claim is inferred.

## Evidence

- Certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json`
- Generic q2 slice: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_polar_polar_L4_q2_slice.json`
- Generator: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix.py`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.py`
- Scoped tests: `bridge/einstein_sector/tests/test_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.py`

## Verification commands

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix --recompute-exhaustive
```
