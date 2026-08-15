# Strict universal cylinder Bach-Hessian export v1

**Result:** `STRICT_CYLINDER_BACH_UNIVERSAL_EXPORT_V1`

**State:** `UNIVERSAL_CYLINDER_TABLE_FAST_RECEIVER_READY_GLOBAL_AST_AND_DIFF_IDENTITY_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The full second-order geometric pipeline has now been differentiated as a
universal local operator at a homogeneous unit-cylinder frame. The compact
table names all **700** symmetric-metric four-jet basis
inputs, all ten contravariant density outputs, and
**19,401** nonzero exact symmetric coefficients.
Input-slot symmetry is checked before compression rather than assumed.

This closes the coefficient-enumeration problem at the chosen frame. It does
not yet close the portable `h_star` row: SO(4) isotropy-covariant globalization,
the differentiated Diff identity, the HT1B adapters and the metric-antifield
cotangent terms remain separate gates.

## Row sizes

| Output | Unary terms | Ordered bilinear terms | Symmetric stored terms |
|---|---:|---:|---:|
| `(0, 0)` | 75 | 4117 | 2121 |
| `(0, 1)` | 50 | 3618 | 1809 |
| `(0, 2)` | 50 | 3632 | 1816 |
| `(0, 3)` | 49 | 3614 | 1807 |
| `(1, 1)` | 69 | 4065 | 2094 |
| `(1, 2)` | 52 | 3682 | 1841 |
| `(1, 3)` | 51 | 3684 | 1842 |
| `(2, 2)` | 73 | 4108 | 2116 |
| `(2, 3)` | 52 | 3688 | 1844 |
| `(3, 3)` | 72 | 4097 | 2111 |

The table uses a shared rational coefficient dictionary and a shared 700-entry
input basis. That basis uses normalized Taylor coordinates
`partial^alpha h / alpha!`; the producer explicitly inserts the factorial
shift when a coordinate derivative raises `alpha`. Each bilinear entry is
`[left_basis, right_basis, coefficient]` with `left_basis <= right_basis`;
evaluation restores the swapped term when the two basis indices differ.

## Exact checks

- zero input-swap defects on the unreduced ordered table;
- zero background, unary and quadratic defects in `g_ab E^ab=0`;
- maximum total input derivative order four;
- three independent concrete-jet comparisons in which the universal table,
  compact table and earlier point evaluator agree exactly.

## Remaining gates

| Gate | Status | Required evidence |
|---|---|---|
| `DIFFERENTIATED_DIFF_NOETHER` | `OPEN` | derive the order-five divergence test with connection and density variations |
| `HT1B_MODE_ADAPTERS` | `OPEN` | evaluate and integrate the two named nonzero cylinder channels |
| `TENSOR_NATURAL_GLOBALIZATION` | `OPEN` | certify SO(4) isotropy covariance and portable coordinate/tensor AST semantics |
| `STRICT_HSTAR_ROW_INTEGRATION` | `OPEN` | combine the metric Hessian with Diff/Weyl cotangent terms and replay the complete q2 receiver |

## Production and replay

The exhaustive producer is intentionally Tier 2 and takes minutes. The
`fast independent checker` replays the checked-in table in seconds and is the
routine per-commit rail.

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_bach_universal_export.py
python3 quantum-weyl/classical_import/check_strict_cylinder_bach_universal_export.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_bach_universal_export.py
```

## Does not establish

- an SO(4)-isotropy-covariant tensor-natural globalization of the basepoint table.
- the differentiated diffeomorphism Noether identity or its fifth-jet cancellation.
- the two nonzero HT1B mode densities or their exact S3 integrations.
- the metric-antifield Diff and Weyl cotangent terms.
- a portable complete h-star row or suspended six-row q2.
- the q1q2, D-derivation or BV-cyclicity receiver identities.
- a passed Gate A, causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory.
