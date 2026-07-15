# AFN0 lower-form carrier precertificate

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`CANDIDATE_AND_EXACT_BOUNDARY_CARRIERS_COMPLETE_AMBIENT_BASIS_OPEN`

## Outcome

The production run now has a single lower-form inventory joining the three
previously separate sources:

1. universal Diff completions from the descent database;
2. the nonzero intrinsic Euler components and their Diff completions; and
3. the explicit primitive/current carriers proving `Box R` and
   `omega Box R` exact.

The exact counts are:

```text
universal candidate carriers   40
intrinsic Euler carriers       11
exact boundary carriers        13
all carriers                   64
strict lower-form carriers     55
structurally zero Euler tail    2
```

Every carrier records its source, bidegree, parity, contraction order,
universal rational coefficient, and reproducible hash. The generator checks
the candidate set and every universal tower row against the descent database,
and independently checks the Euler and exact-boundary source certificates.

The initial implementation replayed the expensive Euler tensor audit in each
consumer process. The optimized consumer instead reads the exact ordinary
bidegree expansion embedded in the byte-hashed Euler certificate. This
preserves the dependency proof while reducing the standalone lower-form
certificate build from tens of seconds to below one second on the recorded
machine.

## Claim boundary

`COMPLETE` applies only to the declared candidate and exact-boundary carrier
algebra. It does not yet apply to the unrestricted ambient local-form basis.
Mixed Weyl--Diff monomials, unrestricted ghost derivatives, additional
generalized-connection signatures are now exhaustive at the integer grading
level: 2,480 coarse and 720 refined signatures in total degrees three through
six. Their tensor realizability, tensor identities, and production `Q`/`d_h`
matrices remain open. Therefore no relative class or complete dual
nontriviality witness is promoted.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m local_bv.lower_form_basis_certificate --check
PYTHONPATH=quantum-weyl python3 -m local_bv.lower_form_ambient_certificate --check
pytest -q quantum-weyl/local_bv/tests/test_lower_form_basis.py
pytest -q quantum-weyl/local_bv/tests/test_lower_form_ambient.py
```

| Rail | Result |
|---|---:|
| lower-form, ambient-signature, basis-gap, and AFN0 consumers | 20 pass in 12.92 s |
| complete local-BV suite | 199 pass, 125 subtests in 54.07 s |
| standalone lower-form carrier build | 0.61 s |
| standalone ambient signature build | 0.43 s |
| carrier and ambient certificates under hash seeds `1,7,123` | byte-identical |
| changed Python compile, schemas, reproduction, and diff check | pass |
