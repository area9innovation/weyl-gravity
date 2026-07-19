# Universal same-sign scalar extreme rays

After positive column rescaling, the six `H/P_x/R_c` receiver columns lie on
the moment curve `(x^2,x,1)`.  Their node order is independent of `rho>0`, and
their current signs in that order are `(-,+,+,-,+,+)`.  Every circuit has
four nodes and alternating moment-curve signs.  Exactly four supports match
the current signs: both `q_minus` nodes together with one of `p_extra` or
`q_plus` on each momentum fibre.

Thus the scalar-null occupation cone has exactly four extreme rays for every
same-sign `n=(1,2)` background.  This classifies the scalar projection only;
rotations, resonance amplitudes and arbitrary sums of lifted rays remain the
next gate.

## Verification receipt

- Tier 0: Python/JSON parsing and scoped `git diff --check` passed.
- Tier 1 producer, independent verifier and 2 unit tests passed; the test rail took 0.235 s.
- Direct consumers: generated atlas schema, independent verifier and 88 tests passed; Paper 13 compiled in three `pdflatex` passes without warnings or box errors.
- Tier 2 is content-addressed to the all-collision scalar classifier and isolated-candidate ledger. Tier 3 was not run because the result does not freeze arbitrary amplitude sums, full cones or a release.
