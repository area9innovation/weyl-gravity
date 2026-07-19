# Same-sign collision same-fibre census

For each distinct collision background 16--21, all 18 nonzero-frequency
same-fibre temporal channels have been compared with all eight physical target
shell conditions.  All 864 exact defects exclude zero.  The `ell=0` sum and
difference channels use the separately certified empty nonzero-Fourier and
homogeneous nonzero-frequency quotients.

Therefore no same-fibre source matrix is needed.  The remaining bounded gate
on these six backgrounds is exactly the candidate-specific cross-fibre
resonance ideal joined to the scalar Farkas common zero and rotations.  This
certificate does not perform that join or make higher-lifecycle claims.

## Verification receipt

- Tier 0: Python compilation and scoped `git diff --check` passed.
- Tier 1 producer: `python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_same_fibre_census --check` -- PASS.
- Tier 1 independent verifier: `python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_collision_same_fibre_census` -- PASS.
- Tier 1 tests: `python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_collision_same_fibre_census` -- 2 tests PASS in 16.656 s on the final rail.
- Direct consumers: atlas generation, schema validation, independent atlas verification and 86 atlas tests all PASS; Paper 13 compiled in three `pdflatex` passes with no warnings or overfull/underfull boxes.
- Tier 2 was discharged through the content-addressed imported certificates checked by the producer and verifier. Tier 3 was not run because this classifies a scoped derived shell census and does not promote a programme-wide freeze or shared core algebra.
