# Six same-sign bounded witnesses

Every same-sign collision background 16--21 has an exact nonzero bounded
second-order tangent.  The positive Farkas weights cancel `H`, `P_x`, and
circle pressure; axisymmetric support cancels rotations.  Candidates 17--19
omit one resonant factor, candidates 16 and 20 use the odd-`L` axisymmetric
zero, and candidate 21 uses its certified real mixed-parity `L=4` component.
For candidate 21 the two real parity vectors are independently rescaled by
their positive action-derived absolute-current norms, so their occupations
are exactly the prescribed positive Farkas weights rather than merely
proportional to them.
The 864-defect census removes all same-fibre nonzero-frequency rows.

This proves nonemptiness, not the full geometry of the six cones or any
all-orders, causal, residual, observational, particle, or quantum claim.

The angular zero used for candidates 16 and 20 is checked exactly as
`ClebschGordan(2,0;2,0|L,0)=0` for odd `L`.  Candidate 21 uses the certified
real mixed-plus component and the common-sign axial/polar current blocks, so
the two fibre amplitudes can be rescaled independently to the prescribed
positive occupations.

## Verification receipt

- Tier 0: Python compilation and scoped `git diff --check` passed.
- Tier 1 producer: `python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_bounded_witnesses --check` -- PASS.
- Tier 1 independent verifier: `python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_collision_bounded_witnesses` -- PASS.
- Tier 1 tests: `python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_collision_bounded_witnesses` -- 3 tests PASS in 0.036 s.
- Direct consumers: atlas generation, schema validation, independent atlas verification and 86 atlas tests all PASS; Paper 13 compiled in three `pdflatex` passes with no warnings or overfull/underfull boxes.
- Tier 2 is represented by exact provenance hashes for the complete finite-harmonic cokernel theorem, scalar classifier, same-fibre census, isolated-candidate ledger and six zero-variety certificates. Tier 3 was not run because this promotes six scoped nonemptiness witnesses, not their full cone decompositions or a programme-wide freeze.
