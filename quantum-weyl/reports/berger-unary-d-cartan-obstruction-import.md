# Berger unary D-Cartan microlocal obstruction import

Dependency tag: `LOCAL-ALGEBRAIC`.

The proof method is separately tagged `MICROLOCAL-SYMBOL`; it is not treated
as a dependency or analytic-lifecycle tag. The import pins hardened classical
commit `f6c42ce5`, including the corrected exact `alpha_B=5` specialization,
canonical hashes of all four specialized symbol matrices, and nonzero rank
minor witnesses.

The pinned import independently reconstructs the retained Douglis symbol
complex at the exact null covector `zeta=(1,1,0,0)`.  Its ranks are
`(3,1,3)` and its cohomology dimensions are `(0,6,6,0)`.  The field class
`h_hat_02` is closed, while the normalized dual functional
`coefficient(h_hat_02)-coefficient(h_hat_12)` annihilates the gauge image and
pairs to one with that class.  At the same covector the symbol of `D` is the
identity.

Consequently a finite-order support-local unary homotopy satisfying

```text
q1 iota_D^(1) + iota_D^(1) q1 = D
```

would microlocally contract a demonstrably non-acyclic symbol complex.  The
already imported 54-to-26 contraction is `D`-equivariant, so any such bare
54-row homotopy would descend to the obstructed retained complex.

This is a scoped no-go theorem.  It does not obstruct adjoining residual/BFV
rows, imposing the derived zero-charge quotient, using a causal Green
extension, or allowing a nonlocal homotopy.  It is not a quantum result.

Reproduce with:

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_unary_d_cartan_obstruction_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_unary_d_cartan_obstruction_import.py -v
```

## Verification receipt

The five scoped import/schema/mutation tests pass in 1.55 seconds with a
61,532 KiB maximum resident set.  The affected four-test nonlinear-bootstrap
rail also passes after updating the canonical question ledger.  Tier 2 is the
pinned exact symbol replay plus the already certified `D`-equivariant SDR
dependency.  Tier 3 was not run because this imports one scoped classical
no-go and does not promote an extension, causal theorem, quantum lifecycle
state, freeze, or release.
