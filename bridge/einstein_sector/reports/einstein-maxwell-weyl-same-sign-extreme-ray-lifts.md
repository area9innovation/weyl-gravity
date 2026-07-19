# Same-sign scalar extreme-ray lifts

All four scalar extreme-ray supports lift to a bounded second-order point on
each of candidates 16--21.  Among the 24 lifts, ten omit a resonant factor,
ten use an axisymmetric odd-`L` zero, two use candidate 19's real regular-
pencil `L=4` component, and two use candidate 21's real scalar mixed-parity
`L=4` component.  Every lift has `m=0`, so the three rotation moment maps
vanish.

This saturates the scalar cone at the level of extreme rays.  It does not
classify arbitrary nonnegative sums: their phase and parity cross terms can
reactivate the bilinear resonance map.

## Verification receipt

- Tier 0: Python/JSON parsing and scoped `git diff --check` passed.
- Tier 1 producer, independent verifier and 2 unit tests passed; the test rail took 0.034 s.
- Direct consumers: generated atlas schema, independent verifier and 88 tests passed; Paper 13 compiled in three `pdflatex` passes without warnings or box errors.
- Tier 2 is content-addressed to the universal scalar rays, complete finite-harmonic cokernel theorem, same-fibre census, isolated-candidate ledger and exact candidate-19/21 zero varieties. Tier 3 was not run because arbitrary sums, full cones and higher lifecycles remain open.
