# Complete ordered cross-parity L=4 source matrices

## Result

Both ordered cross-parity parts of the axisymmetric two-absolute-momentum
workload are classified:

- axial first and polar second;
- polar first and axial second.

Each matrix contains twelve separately tuned resonance rows, twenty input
branch-basis fixtures and twenty-seven scalar target-adjoint coefficients.
All 54 scalar coefficients are nonzero by exact rational interval witnesses,
and every one of the forty ordered branch-basis fixtures has a nonzero
complete axial target-cokernel vector. Every declared fixture is therefore
`OBSTRUCTED` in the bounded or finite-quasiperiodic correction class.

Together with the same-parity matrices, this closes all 108 axisymmetric
`L=4` basis coefficients. It does not classify the common zero variety for
arbitrary amplitudes.

## Shared action-derived source

One content-addressed generic `q2` slice retains arbitrary signed
`k_1,k_2`, arbitrary `omega_1,omega_2`, one arbitrary axial gauge-slice
vector and one arbitrary polar gauge-slice vector. It includes both PBW input
orders explicitly: 832 axial-then-polar terms and 832 polar-then-axial terms.
The axial action-row normalization is fixed by exact agreement with the
previous direct four-dimensional axial-plus-polar-minus source.

The reverse workload is not inferred by matching carrier names. It is
computed from the shared bilinear slice by an explicit role substitution:
the axial role receives the workload's second branch and momentum, while the
polar role receives its first. The two ordered matrices retain their separate
branch, signed-momentum, frequency and circumference labels.

## Exact witnesses

Every stored radical coefficient carries an outward rational interval
strictly excluding zero. The independent verifiers do not import either
producer. They replay the interval arithmetic, target-shell identities,
source and schema hashes, the direct source calibration, and the explicit
reverse-role audit.

## Workload disposition

The axisymmetric `L=4` basis workload is complete: 108 of 108 scalar
coefficients are classified. The remaining finite-harmonic source workload
contains 56 nonaxisymmetric `L=1,3` coefficients. Cancellations among
arbitrary amplitudes, smooth-secular correction and the full two-fibre
tangent cone remain `OPEN`; causal/retarded correction remains
`NO_CERTIFIED_MAP`.

## Evidence

- Forward certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json`
- Reverse certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json`
- Shared slice: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_polar_L4_q2_slice.json`
- Forward producer: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix.py`
- Reverse producer: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix.py`
- Independent verifiers and scoped tests use the matching filenames under `bridge/einstein_sector/`.

## Verification commands

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix
```
