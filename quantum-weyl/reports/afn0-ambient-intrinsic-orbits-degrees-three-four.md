# AFN0 ambient intrinsic signed orbits in total degrees three and four

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`INTRINSIC_SIGNED_ORBITS_COMPLETE_LINEAR_RELATIONS_OPEN`.

The degree-three/four ambient slice contains 388,011 raw epsilon/metric
contractions.  Expanding the full product of tensor symmetry groups for every
graph would repeat work unnecessarily.  The machine instead applies a
minimal signed generator set and computes connected components with a signed
disjoint-set structure.

The implemented generators are:

- adjacent identical-factor transpositions, including Koszul signs;
- antisymmetry in each Riemann index pair;
- exchange of the two Riemann index pairs;
- adjacent horizontal-form transpositions;
- the epsilon-orientation sign induced by every slot permutation.

The exact result is:

```text
raw contraction graphs          388,011
signed generator edges        3,277,285
intrinsic signed orbits            9,534
surviving orbits                   5,637
odd-stabilizer zero orbits         3,897
```

Every generator image remains inside its profile's raw graph space.  Each raw
graph belongs to one signed component, and every profile histogram exactly
reconstructs its raw count.  The detailed content-addressed bundle stores 192
profile receipts with generator manifests, orbit histograms, surviving and
zero representative hashes, and explicit open-relation ledgers.

This is not a canonical local-form basis.  Algebraic and differential Bianchi
relations, covariant-jet commutators, integration by parts, and
four-dimensional antisymmetrization relate different surviving orbits and
remain `NOT_COMPUTED`.  Hence the production `Q` and `d_h` matrices and the
total-complex quotient remain fail-closed.  No degree-five/six raw graph set
was materialized.

The machine-readable receipt is
[`AFN0_AMBIENT_INTRINSIC_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json`](../local_bv/certificates/AFN0_AMBIENT_INTRINSIC_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR.json).

## Next gate

Generate exact Bianchi and jet-commutator relation rows on the 5,637 surviving
representatives, followed by integration-by-parts and four-dimensional
relations.  Assemble `Q` and `d_h` only after the resulting basis is stable.

## Verification receipt

```text
Tier 0
python3 -m py_compile quantum-weyl/local_bv/ambient_intrinsic_orbits.py \
  quantum-weyl/local_bv/ambient_intrinsic_orbit_certificate.py \
  quantum-weyl/local_bv/tests/test_ambient_intrinsic_orbits.py

Tier 1
PYTHONPATH=quantum-weyl python3 -m unittest \
  local_bv.tests.test_ambient_factor_orbits \
  local_bv.tests.test_ambient_intrinsic_orbits
Result: 8 passed in 27.628 s

PYTHONPATH=quantum-weyl python3 -m \
  local_bv.ambient_intrinsic_orbit_certificate --check
Result: PASS

Draft 2020-12 validation
jsonschema.Draft202012Validator.check_schema and validate
Result: certificate PASS; bundle PASS
```

Tier 3 was not run because this result does not freeze the classical or
quantum programme, promote a paper theorem, modify shared core algebra, or
advance a QME lifecycle state.
