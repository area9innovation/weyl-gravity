# Berger A104 endpoint completion

The exact classical endpoint export closes the last two diagonal slots in the
frozen Cauchy ordering:

| block | coordinates | nonzero sparse entries |
| --- | ---: | ---: |
| `ghost_A12` | 144 | 27 |
| `identity_A12` | 144 | 27 |

The global `104 x 104` operator now has all 10,816 coordinates determined and
470 nonzero sparse entries.
All 10,528 previously certified coordinates are preserved.

This completes the finite coefficient table only.  The next gate is the
degree-plus-one companion/Cauchy BRST operator together with the nondegenerate
Cauchy/Krein form and real structure.  Closedness, the zero-frequency
Riesz/Jordan ledger and a Hadamard covariance remain open.

Verification uses the deterministic producer replay, completion replay,
independent sparse-entry verifier, strict Draft 2020-12 validation and the
ten scoped unit tests.  Tier 3 is not run because this closes one affected
finite carrier chain without promoting a Hadamard, QME, theorem-freeze or
release lifecycle.
