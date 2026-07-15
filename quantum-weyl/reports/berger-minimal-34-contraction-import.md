# Berger complete minimal contraction import

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`COMPLETE_34_ROW_MINIMAL_UNARY_CONTRACTION_IMPORTED_ND2_NONLINEAR_INPUT_BLOCKED`

## Result

The portable classical export at `9278ba7d` is independently imported.  It
combines the retained PBW-valued unary differential with the eight clock rows
and supplies exact order-zero maps

```text
iota_cl : C_retained -> C_minimal
pi_cl   : C_minimal -> C_retained
S_cl    : C_minimal -> C_minimal[-1].
```

The quantum consumer independently parses every sparse map entry and verifies
the 34-row unary nilpotency and cyclicity, both chain-map identities,
`pi_cl iota_cl=1`, the complementary projectors, the full SDR identity, all
three side conditions, nondegeneracy of the 34- and 26-row pairings, and
projection/pairing compatibility.  The SDR therefore preserves the cohomology
of the retained unary complex.

This satisfies ND2's standalone `classical_contraction` artifact.  It does
not satisfy the other physical-run artifacts: support-local `q2/D`, local
`D`-equivariance, an admissibility policy, and a coefficient-domain-compatible
Cartan assembly remain absent.  Nonminimal gauge-fixing rows, causal Green
operators, Hadamard data, and every quantum lifecycle claim also remain open.

## Machine receipt

- `quantum-weyl/transfer/certificates/BERGER_MINIMAL_34_CONTRACTION_IMPORT.json`

## Verification commands

```text
python3 quantum-weyl/transfer/berger_minimal_contraction_import_certificate.py --check
python3 -m unittest quantum-weyl.transfer.tests.test_berger_minimal_contraction_import
python3 quantum-weyl/transfer/nd2_physical_run_certificate.py --check
python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check
```

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Classical producer guards, independent verifier, and focused tests | 4.21 | PASS (3 tests) | 1 |
| Contraction, ND2, ND1, and nonlinear aggregate certificate checks | 34.39 | PASS | 2 |
| Strict AJV Draft-2020-12 validation of contraction and ND2 receipts | 4.44 | PASS (2 receipts) | 0 |
| Focused contraction, ND2, and aggregate tests | 27.93 | PASS (15 tests) | 2 |
| ND1 provenance-only refresh after the classical status commit | 3.77 | PASS | 2 |
| Complete transfer suite | 109.19 | PASS (125 tests) | 2 |
| Python compile, JSON parsing, and scoped `git diff --check` | 0.12 | PASS | 0 |

The first exhaustive complete-suite run exposed only the previously recorded
stale ND1 dependency hash.  After the classical status stabilized, that
quantum-owned provenance receipt was regenerated without changing its
analysis payload; the final complete suite is clean.

Tier 3 is unnecessary unless this import is used to promote the full
classical freeze or a physical ND2 execution.  This receipt closes one exact
minimal-unary prerequisite and keeps all nonlinear, causal, and quantum gates
false.
