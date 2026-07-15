# AFN0 ambient lower-form signature certificate

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `AMBIENT_GRADING_EXHAUSTIVE_TENSOR_QUOTIENT_OPEN`

## Outcome

The integer solver covers every bidegree needed by the AFN0 relative complexes:

```text
H04: incoming total degree 3, cocycle degree 4, outgoing degree 5
H14: incoming total degree 4, cocycle degree 5, outgoing degree 6
```

For both spacetime parities it solves

```text
ghost_number + form_degree = total_degree
2 n_R + n_dR + n_domega + n_dxi - n_xi - form_degree = 0
```

over nonnegative integers. The second equation uses `[dx]=-1`, Weyl-ghost
dimension zero, and Diff-ghost dimension minus one. Since total degree is at
most six, it also proves the finite bound `n_R <= 3`.

| Parity | Total degree | Coarse | Refined |
|---|---:|---:|---:|
| even | 3 | 80 | 22 |
| even | 4 | 190 | 51 |
| even | 5 | 360 | 105 |
| even | 6 | 610 | 183 |
| odd | 3 | 80 | 20 |
| odd | 4 | 190 | 51 |
| odd | 5 | 360 | 105 |
| odd | 6 | 610 | 183 |
| total | | 2,480 | 720 |

Refinement rejects seedless derivatives, derivatives of absent ghost species,
products of two or more undifferentiated scalar Weyl ghosts, odd scalar-index
counts, and parity-odd signatures without four epsilon slots. Every retained
and rejected row carries a reproducible hash.

## Claim boundary

This is an exhaustive integer-signature theorem under the declared generator
algebra, not a tensor-basis theorem. Raw tensor graphs, Bianchi and Grassmann
relations, integration by parts, dimension-specific antisymmetrization, and
the production matrices remain open. No cohomology dimension is emitted.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m local_bv.lower_form_ambient_certificate --check
pytest -q quantum-weyl/local_bv/tests/test_lower_form_ambient.py
```

The focused ambient suite passes 5 tests in 0.35 seconds. The complete
local-BV rail passes 199 tests and 125 subtests in 54.07 seconds. The large
full rail remains a release gate; the standalone signature certificate builds
in 0.43 seconds for the ordinary edit loop.
