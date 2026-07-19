# Berger recoil numerical-input contract v2

## Result

The v2 schema and translator now map every declaration-controlled input exactly
to `run_reality_folded_shell_stream`: mass or mass-squared intervals, two
nonzero couplings, a positive inverse Berger-volume interval, a contiguous
shell extension, four tail radii after every shell, interval precision, a zero
initial-partial origin, and one of the four runtime stopping goals.

The old v1 schema is retained as an auditable
`OBSTRUCTED_SCHEMA_RUNTIME_MISMATCH`. It omitted six runtime input classes and
used the incompatible goal names `interval_tolerance`, `nonzero`, and `sign`.

## Independent rail

The verifier independently parses and squares the rational mass domains,
reconstructs shell and tail maps, and compares all serialized runtime arguments
for `entry_tolerance`, `entry_nonzero`, `entry_sign`, and `rank_two`. Mutation
tests reject the legacy goal shape, missing inverse volume, missing, duplicate
or noncontiguous shells, incomplete tails, nonpositive mass or volume, zero
coupling, and absent provenance.

## Boundary

All replay values are marked `VALIDATION_ONLY`; they are neither physical data
nor recommendations. The translator does not activate a stream. A separate
gate must receive and verify a provenance-complete `EXPLICIT_EXTERNAL_VALUES`
declaration before any physical recoil interval or recoil-corrected rank claim
can be made. The hashed exact-T carrier remains `NO_CERTIFIED_MAP`, and the
tangent-cone, physical-branch, nonlinear-stability, and quantum gates remain
inactive.
