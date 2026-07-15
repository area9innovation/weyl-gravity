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

This is not Gate A or Gate B.  In particular, the classical commit is
`NOT_FROZEN`; antifield and nonminimal rows have not been imported; and
covariant curvature reduction, integration by parts, Bianchi identities,
Hodge duality, descent, and both `H^{0,4}(s|d)` and `H^{1,4}(s|d)` are
`NOT_COMPUTED`.  The coordinate-jet normal form must not be cited as a
canonical form modulo those relations.

Run the exact tests and reproduce the receipt from the repository root:

```bash
PYTHONPATH=quantum-weyl python -m unittest discover -s quantum-weyl/local_bv/tests -v
PYTHONPATH=quantum-weyl python -m local_bv.certificate --check
```

The certificate is
[`certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Its repository-wide result-schema envelope is
[`../../quantum-weyl/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](../certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Running `python -m local_bv.certificate` without `--check` prints the
canonical regenerated JSON for review; it does not overwrite the receipt.

Next admissible steps are to import the frozen classical schema, extend the
same exact differential with certified antifield rows, and only then add the
covariant and relative-cohomology quotients.
