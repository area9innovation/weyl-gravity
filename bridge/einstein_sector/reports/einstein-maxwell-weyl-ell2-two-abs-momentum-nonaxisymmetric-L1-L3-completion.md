# Nonaxisymmetric L1/L3 branch-basis completion

## Result

The final twelve exceptional `L=1` reduced source coefficients are nonzero.
They occur on three separately tuned nonzero-momentum DIFFERENCE rows and
cover all four ordered axial/polar input-parity channels.  Every one of the
twelve corresponding branch-basis fixtures therefore has a nonzero physical
exceptional target-cokernel pairing and is `OBSTRUCTED` for bounded or finite-
quasiperiodic second-order corrections.

The same producer replays the already certified 44-coefficient `L=3`
submatrix.  Its four generic reduced tensors agree exactly with the landed
`L=3` source slice after the common `sqrt(pi)` angular normalization is
removed.  Thus all 56 odd-`L` coefficients are independently replayed, and
together with the four `L=4` matrices all 164 declared branch-basis scalar
coefficients are classified.

This is not an arbitrary-amplitude theorem.  Cancellations among simultaneous
branch amplitudes and the complete two-fibre tangent cone remain `OPEN`.
Smooth-secular correction is also `OPEN`, while a causal/retarded map remains
`NO_CERTIFIED_MAP`.

## Exact construction

The source projector evaluates the action-derived PBW `q2` on standard
normalized `Y_2m` carriers, couples the two inputs with exact Clebsch–Gordan
coefficients, and extracts the unique multiplicity-one `V_1` or `V_3`
coefficient from equatorial output jets.  Generic tensors are separated in
`k_1,omega_1,k_2,omega_2` before the isolated algebraic circumferences are
substituted.

The `L=1` target covectors are checked directly against the certified
nonzero-`k` exceptional axial and polar Hessians on
`omega^2-k^2=4/3`.  Each stored real algebraic pairing differs from the
physical complex-harmonic pairing only by the fixed nonzero phase
`sqrt(pi)` or `-i*sqrt(pi)`.  Exact rational intervals exclude zero for all
twelve new coefficients.

The independent exhaustive verifier reconstructs all 56 pairings and also
reproduces the four certified axisymmetric `L=4` source normalizations.

## Evidence

- Certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json`
- Generic slices: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_nonaxisymmetric_L1_L3_q2_slices.json`
- Projector: `bridge/einstein_sector/nonaxisymmetric_pbw_projector.py`
- Producer and independent verifier use the matching nonaxisymmetric `L1_L3` filenames under `bridge/einstein_sector/`.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_nonaxisymmetric_L1_L3_matrix --check
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix --exhaustive
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix
```
