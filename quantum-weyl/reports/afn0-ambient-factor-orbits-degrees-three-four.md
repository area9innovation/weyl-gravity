# AFN0 ambient signed factor orbits in total degrees three and four

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`SIGNED_FACTOR_ORBITS_COMPLETE_IDENTITY_QUOTIENT_OPEN`.

The factored ambient tensor realization contains 2,860,932,903 raw graphs, so
the production path must not materialize the full space.  Total degrees three
and four form a bounded validation slice: 144 refined signatures split into
192 derivative-distribution profiles and exactly 388,011 raw epsilon/metric
contraction graphs.

The machine now constructs the direct product of the symmetric groups acting
on identical factors at fixed derivative order.  Exchanges of odd Weyl and
Diff ghost factors carry their exact Koszul sign, and movement of slots inside
the epsilon carrier contributes the induced orientation sign.  Every raw
graph is assigned to exactly one signed orbit.  The result is:

```text
signed factor orbits          139,889
surviving signed orbits       130,937
odd-stabilizer zero orbits      8,952
```

Each of the 192 profile receipts stores the factor-action order, action hash,
orbit-size histogram, surviving and zero representative-manifest hashes, and
the identity

```text
sum(orbit_size * orbit_count) = raw_graph_count.
```

This is not yet the canonical local-form quotient.  Intrinsic Riemann
symmetries, algebraic and differential Bianchi identities, covariant-jet
commutators, horizontal-form antisymmetry, integration by parts, and
four-dimensional antisymmetrization remain explicit `NOT_COMPUTED` seams.
Consequently the production `Q` and `d_h` matrices and total-complex
exhaustiveness also remain open.  Degrees five and six stay in factored form;
none of their billion-scale raw graph sets was materialized.

The machine-readable receipt is
[`AFN0_AMBIENT_FACTOR_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json`](../local_bv/certificates/AFN0_AMBIENT_FACTOR_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json).

## Next gate

Implement intrinsic Riemann symmetries and horizontal-form antisymmetry on
these signed orbit representatives, then add Bianchi/jet relations and
integration by parts.  Exact `Q` and `d_h` matrices may be assembled only
after that identity quotient is stable.

## Verification receipt

```text
Tier 0
python3 -m py_compile quantum-weyl/local_bv/ambient_factor_orbits.py \
  quantum-weyl/local_bv/ambient_factor_orbit_certificate.py \
  quantum-weyl/local_bv/tests/test_ambient_factor_orbits.py
python3 -m json.tool quantum-weyl/local_bv/schema/afn0_ambient_factor_orbit.schema.json
python3 -m json.tool quantum-weyl/local_bv/schema/afn0_ambient_factor_orbit_bundle.schema.json

Tier 1
PYTHONPATH=quantum-weyl python3 -m unittest \
  local_bv.tests.test_ambient_factor_orbits
Result: 3 passed in 14.219 s

PYTHONPATH=quantum-weyl python3 -m \
  local_bv.ambient_factor_orbit_certificate --check
Result: PASS

Draft 2020-12 validation
jsonschema.Draft202012Validator.check_schema and iter_errors
Result: certificate PASS; bundle PASS
```

Tier 2 is limited to the unchanged ambient-signature and tensor-realization
consumer tests because this certificate adds a downstream quotient layer and
does not modify their algebra.  Tier 3 was not run: no classical/quantum
freeze, paper theorem, shared-core algebra, or lifecycle promotion is made.
