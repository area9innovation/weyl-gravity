# Retained Berger minimal-q1 import

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Lifecycle layer: `CLASSICAL_BV`

Result state: `RETAINED_26_ROW_MINIMAL_Q1_IMPORTED_ND2_INPUT_INCOMPLETE`

## Result

The complete 26-row retained minimal Berger differential is now imported as
an independently checked prerequisite for nonlinear homological transfer.
The import pins three immutable classical layers separately:

```text
mathematical theorem    b37bf3bd504a7745fbe80448cd0ab578a3a135ea
classical promotion     d4b4fbdad2e0fff4aebf670df66f8c813a39e340
portable schema repair  e703df6d6f58c7e2592c7d01d1e452e919cd9923
```

The theorem certificate has SHA-256
`296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77`.
The repaired schema has SHA-256
`de48f6f69f068ec3f1ca58e33346bc99810ebf49e70d4944289e2c95e355ab6e`.
The importer verifies that the schema-only repair did not change the theorem
blob.

## Independent PBW reconstruction

The quantum consumer does not import the classical producer.  It parses the
declared exact polynomial coefficient language over `Q(alpha_B,u,v)`, rejects
unknown tokens and floating point, and independently implements the Berger
invariant-frame commutators

```text
[e1,e2]=u e3,  [e2,e3]=v e1,  [e3,e1]=v e2,  [e0,ei]=0.
```

It reconstructs:

| Block | Shape | Nonzero entries | PBW terms | Maximum order |
|---|---:|---:|---:|---:|
| `K_spatial` | 10 x 3 | 14 | 14 | 1 |
| `H_retained` | 10 x 10 | 100 | 863 | 4 |
| `minus_K_spatial_sharp` | 3 x 10 | 14 | 14 | 1 |

Exact PBW composition reproduces

```text
H_retained^sharp = H_retained
minus_K_spatial_sharp = -K_spatial^sharp
H_retained K_spatial = 0
minus_K_spatial_sharp H_retained = 0
q1_retained^2 = 0
```

Mutation tests reject the original impossible-schema form, record-hash drift,
undeclared expression tokens after rehashing, and a broken Noether row after
rehashing.

## Fail-closed boundary

This result supplies the complete retained minimal `q1` only.  The existing
clock theorem remains a separate 8-of-34 partial SDR import whose portable
maps and `D`-equivariance are absent.  Nonminimal rows, the complete all-row
contraction, `q2`, the `D` action, admissibility, causal Green theory, and all
interacting and quantum verdicts remain open.  Consequently

```text
retained_minimal_q1 = AVAILABLE_VERIFIED_PREREQUISITE
support_local_q1_q2_D = NOT_AVAILABLE
classical_contraction = NOT_AVAILABLE
physical_execution_authorized = false
```

## Machine receipt

- `quantum-weyl/transfer/certificates/BERGER_RETAINED_MINIMAL_Q1_IMPORT.json`

## Verification commands

```text
python3 quantum-weyl/transfer/berger_retained_q1_import_certificate.py --check
python3 -m unittest quantum-weyl.transfer.tests.test_berger_retained_q1_import
python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check
python3 -m unittest quantum-weyl.transfer.tests.test_nonlinear_transfer_certificate
```

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Retained-`q1` certificate reproduction | 11.30 | PASS | 1 |
| AJV strict Draft-2020-12 validation of the quantum receipt | 2.03 | PASS | 0 |
| Retained-`q1` and nonlinear-aggregate focused tests | 13.07 | PASS (10 tests) | 2 |
| Nonlinear aggregate certificate reproduction | 0.03 | PASS | 2 |
| Transfer suite excluding the independently stale ND1 reproduction receipt | 72.64 | PASS (108 tests) | 2 |
| Remaining ND1 semantic and mutation tests | 9.05 | PASS (7 tests) | 2 |
| ND1 checked-in certificate reproduction | 3.43 | FAIL: pre-existing classical-status dependency hash drift | 2 |

The ND1 reproduction failure is not counted as a pass and was not repaired in
this commit.  Its only differences are the dependency hash and manifest hash
of `d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json`, which
changed in the concurrent classical programme.  The retained-`q1` import does
not consume or modify that ND1 certificate.  The complete transfer suite is
therefore recorded as affected-suite coverage rather than a clean full-suite
pass.

Tier 3 is unnecessary because this imports one content-addressed
`LOCAL-ALGEBRAIC` prerequisite, keeps every nonlinear, contraction, causal,
and quantum gate false, and changes no shared transfer algebra.
