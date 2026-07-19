# Complete axial--axial cross-momentum L=4 source matrix

## Result

The complete axial--axial part of the axisymmetric two-absolute-momentum
workload is now classified.  It contains twelve separately tuned resonance
rows, twenty input branch-basis fixtures and twenty-seven scalar target
adjoint coefficients.  The input branches are the Einstein `q_minus` and
`q_plus` primaries and both `p_extra` basis representatives on each retained
momentum fibre.

Exactly one scalar coefficient vanishes: the first component of the already
known candidate-4 two-dimensional p-primary cokernel vector.  The other
twenty-six coefficients have exact rational intervals excluding zero.
Consequently every one of the twenty declared branch-basis fixtures has a
nonzero complete target-cokernel vector and is `OBSTRUCTED` in the bounded or
finite-quasiperiodic correction class.

This is a basis-fixture theorem, not yet the zero variety of the full
quadratic matrix.  Cancellations among arbitrary linear combinations of
axial amplitudes remain open.

## Exact source slice

The calculation extracts a 7.3 KiB bilinear source slice from the certified
Weyl--Maxwell product `q2` payload.  It retains arbitrary signed
`k_1,k_2`, arbitrary `omega_1,omega_2`, and two arbitrary axial gauge-slice
vectors in the order `(H_t,H_x,Q_t,Q_x)`.  The four output rows are the
action-normalized polar `L=4` rows.

The independent verifier specializes this generic slice to the axial
Einstein-minus representative and reproduces the previously certified narrow
q-minus/q-minus slice symbolically.  It also verifies the q2, action and row
layout hashes.

## Nonvanishing proof

Each stored radical pairing is evaluated by exact rational interval
arithmetic.  Square-root endpoints are bounded using integer square roots at
a declared decimal scale; additions, products and reciprocals use rational
outward bounds.  Every nonzero coefficient has a stored interval lying
strictly on one side of zero.  This replaces slow algebraic-number
factorization with a reproducible exact witness; no floating-point sign test
supports the theorem.

The fast rail rebuilds the generic q2 slice and independently replays every
stored rational interval in about eight seconds.  The exhaustive producer
re-specializes and contracts all twenty-seven coefficients and is retained
as a separate roughly 161-second Tier-2 rail.

## Workload disposition

The resolved axisymmetric `L=4` count is now 27 of 108.  The remaining 81
axisymmetric coefficients consist of polar--polar and the two ordered
cross-parity matrices.  All 56 nonaxisymmetric `L=1,3` coefficients also
remain open.

Smooth-secular correction is `OPEN`; causal/retarded correction is
`NO_CERTIFIED_MAP`.  The twelve circumference rows remain distinct.  No
complete tangent-cone, residual, observable or quantum claim is inferred.

## Evidence

- Certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json`
- Generic q2 slice: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_axial_L4_q2_slice.json`
- Generator: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix.py`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.py`
- Scoped tests: `bridge/einstein_sector/tests/test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.py`

## Verification commands

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix --recompute-exhaustive
```
