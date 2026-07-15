# Einstein--Maxwell second-order registration receipt

The programme imports `EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST` from
commit `05695ffe3b4082c629e3e632ac5f53e8b70e8601` by its committed SHA-256
digest.

The result is deliberately split into two phase-space rows:

- `compact_einstein_maxwell_second_order_fixed_flux` records the adjoint
  obstructions for the constant radion and Maxwell duality tangent on the
  periodic compact product at fixed magnetic flux.
- `universal_cover_einstein_maxwell_second_order_null_extension` records the
  explicit removable nonzero-Chevreton fixture on `R^(1,1) x S2`.

Neither row is allowed to imply the other. In particular, the compact
fixed-charge obstructions are not a universal nonlinear no-go, and the
universal-cover extension is not general nonlinear closure.

## Verification

The source certificate passed exact regeneration (34.22 s), an independent
adjoint/reduced-equation verifier (0.50 s), and eight scoped tests (35.86 s).
The programme registration passed JSON parsing, scoped diff checks, exact
programme regeneration, and mutation guards. Higher tiers were not required
because no shared mathematical operator or schema changed.
