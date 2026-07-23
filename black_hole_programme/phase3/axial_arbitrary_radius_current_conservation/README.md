# Exact arbitrary-radius axial-current conservation

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This package closes the provenance gap between the literal Lee--Wald action
current and the repaired axial six-state flow.  The prior null-trace
certificate stored the exact current only at `r=4` and stated, but did not
prove, its radial conservation equation.

The producer evaluates the literal action current at the 30 exact radii
`3,...,32`, retaining `omega` as an indeterminate.  A localized-ring audit
proves that every entry has denominator dividing

```text
r^7 (r-2)^6 (omega*r-2*I)^4 (omega*r+2*I)^4
```

and that the cleared numerator has radial degree at most 29.  The 30 values
therefore recover the arbitrary-`r` matrix uniquely over `QQ(I)(omega)`.
The independent verifier parses that matrix and the frozen repaired flow,
differentiates independently, and checks all 36 entries of

```text
dJ/dr + A(r,-omega)^T J + J A(r,omega) = 0
```

as exact zero rational functions.

Commands:

```bash
python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify
python3 -m pytest -q black_hole_programme/phase3/axial_arbitrary_radius_current_conservation/tests
python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.produce --check
python3 -m black_hole_programme.phase3.axial_arbitrary_radius_current_conservation.verify --replay-literal-samples
```

The last two commands are exhaustive reproduction/provenance rails.  They are
kept separate from the fast independent verifier.

This result does not establish horizon regularity, endpoint trace limits, a
global connection/scattering matrix, stability, or a quantum statement.
