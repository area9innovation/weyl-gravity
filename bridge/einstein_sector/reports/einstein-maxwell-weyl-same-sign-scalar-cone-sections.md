# Same-sign scalar-cone amplitude sections

Every point of each complete four-ray scalar occupation cone on candidates
16--21 has at least one bounded second-order amplitude lift.  Four candidates
use a universal all-axial `m=0` section because their cross-fibre resonance
has odd output `L`.  Candidate 19 uses one real regular-pencil `L=4`
eigenline, and candidate 21 uses its real scalar mixed-parity `L=4`
component.  Homogeneity permits independent fibre rescaling to arbitrary
prescribed occupations, including all faces.

This proves surjectivity of the bounded cone onto the scalar cone.  It does
not classify the entire phase/parity fibre: another amplitude with the same
occupations can still excite the bilinear resonance.

## Verification receipt

- Tier 0: Python/JSON parsing and scoped `git diff --check` passed.
- Tier 1 producer, independent verifier and 2 unit tests passed; the final test rail took 0.024 s.
- Direct consumers: generated atlas schema, verifier and 89 tests pass; Paper 13 compiles in three `pdflatex` passes without warnings or box errors.
- Tier 2 is content-addressed to the universal scalar cone, 24 extreme-ray lifts, complete cokernel theorem, current forms, same-fibre census and exact candidate-19/21 real zero varieties. Tier 3 was not run because phase/parity fibres, full components and higher lifecycles remain open.
