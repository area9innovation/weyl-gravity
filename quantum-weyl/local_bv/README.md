# Local BV bootstrap

Dependency tag: `LOCAL-ALGEBRAIC`.

This directory is the first exact substrate for Branch A of the quantum
programme.  It implements a four-dimensional supercommutative coordinate-jet
algebra over rational coefficients, metadata for the minimal fields
`g`, `xi`, and `omega`, deterministic canonical serialization/hashing, and
the three minimal Diff x Weyl BRST rows stated in the brief.  The checked-in
certificate verifies nilpotency on every independent minimal generator,
commutation with coordinate total derivatives, and the odd graded Leibniz
rule.

The second scoped layer is an exact abstract-index tensor quotient.  It
implements signed Riemann and epsilon slot symmetries, graded factor order,
dummy-index renaming without erasing free-index order, exact rational relation
reduction, algebraic Bianchi identities, covariant total derivatives,
integration by parts, and an explicit spacetime-parity involution.  Exhaustive
generation of all 105 pairings of two Riemann tensors produces four canonical
symmetry orbits; the generated Bianchi relation has rank one, leaving a
three-dimensional parity-even quadratic curvature quotient.  The conventional
`Riemann_squared`, `Ricci_squared`, and `scalar_curvature_squared`
representatives independently span it.

This is not Gate A or Gate B.  In particular, the classical commit is
`NOT_FROZEN`; antifield and nonminimal rows have not been imported; and
general covariant curvature reduction remains incomplete.  Only the generated
two-Riemann algebraic-Bianchi quotient and an exact total-divergence/IBP rail
are certified.  Differential Bianchi identities, derivative commutators,
Hodge-star normalization, descent, and both `H^{0,4}(s|d)` and
`H^{1,4}(s|d)` remain unavailable.  The curvature certificate must not be
cited as a complete covariant jet normal form or cohomology calculation.

Run the exact tests and reproduce the receipt from the repository root:

```bash
PYTHONPATH=quantum-weyl python -m unittest discover -s quantum-weyl/local_bv/tests -v
PYTHONPATH=quantum-weyl python -m local_bv.certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.curvature_certificate --check
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_CURVATURE_CANONICALIZATION.json
```

The certificate is
[`certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Its repository-wide result-schema envelope is
[`../../quantum-weyl/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](../certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Running `python -m local_bv.certificate` without `--check` prints the
canonical regenerated JSON for review; it does not overwrite the receipt.

The detailed curvature receipt is
[`certificates/LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json`](certificates/LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_CURVATURE_CANONICALIZATION.json`](../certificates/LOCAL_CURVATURE_CANONICALIZATION.json).

Next admissible local steps are the differential Bianchi/derivative-commutator
relations, Hodge/chiral normalization, Weyl BRST curvature rows, and a
derivative-bounded invariant ansatz.  The antifield and relative-cohomology
layers still wait for the frozen classical schema.
