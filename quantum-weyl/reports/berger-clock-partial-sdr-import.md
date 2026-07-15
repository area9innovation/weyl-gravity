# Berger clock partial-SDR import contract

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Lifecycle state: `CLASSICAL_BV` evidence import

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

The nonlinear-transfer programme now recognizes the registered classical
minimal Berger clock theorem at its exact boundary.  The immutable theorem
commit `f6e8a2b0` proves a support-local cyclic contraction of the eight rows

```text
tau, sigma, Theta, R, Theta*, R*, tau*, sigma*.
```

Thus the 34-row minimal complex retracts onto a 26-row dressed-metric and
spatial-diffeomorphism complex.  The programme registration is independently
pinned at `5530cb20`, and the setting, phase space, total-`D` boundary hash,
coverage, formulas, open flags, and the inventory and syntax of all nine
operator fingerprints are checked before the quantum receipt reproduces.  The
fingerprints are not independently recomputed because the v1 handoff lacks the
portable operator payload needed for that comparison.

## Portable-map boundary

The classical v1 certificate contains exact formulas and operator
fingerprints, but not sparse operator entries.  It also does not declare the
localized coefficient ring, derivative-to-symbol convention, suspension and
grading bridge, or the clock-block `D` action.  In particular, it does not
establish

```text
[D,q1]=0,  [D,s_cl]=0,  D pi_cl=pi_cl D,  D iota_cl=iota_cl D.
```

The new
`schema/berger-clock-partial-sdr-portable-v1.schema.json` is the receiving
contract for those objects.  It requires a 34-entry authoritative basis,
exact first-order sparse maps, canonical hashes, explicit 8/34 coverage, and
an honest `OPEN` or `VERIFIED` equivariance ledger.  Even a conforming partial
payload continues to carry `complete_classical_contraction: false`.

## ND2 boundary

The evidence receipt records

```text
partial_clock_sector_sdr = AVAILABLE_EVIDENCE_ONLY
complete_classical_contraction = NOT_AVAILABLE
physical_execution_authorized = false
```

It cannot be substituted for the ND2 `classical_contraction` artifact.  The
retained 26-row operator, nonminimal rows, complete contraction, support-local
`q2/D` export, and admissibility policy must still arrive independently.

Historical note: the later portable export at `9278ba7d` supplies exact map
entries and closes the complete 34-row minimal contraction.  This partial
evidence receipt remains the provenance record for the earlier 8-row theorem;
its original fail-closed verdict is not retroactively rewritten.

## Machine receipts

- `quantum-weyl/transfer/certificates/BERGER_CLOCK_PARTIAL_SDR_IMPORT.json`
- `quantum-weyl/transfer/certificates/BERGER_CLOCK_NONLINEAR_IMPORT.json`
- `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json`

## Verification commands

```text
python3 quantum-weyl/transfer/berger_clock_sdr_import_certificate.py --check
python3 quantum-weyl/transfer/berger_clock_import_certificate.py --check
python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_clock_sdr_import.py quantum-weyl/transfer/tests/test_berger_clock_import.py quantum-weyl/transfer/tests/test_nonlinear_transfer_certificate.py
```

The affected certificate chain and 34 focused total-`D`/SDR/ND2/aggregate
tests pass.  The complete transfer suite passes 110 tests in 70.87 seconds.
An earlier complete-suite run failed because the evolving classical aggregate
ledger was incorrectly required to retain the original theorem commit.  That
run is not counted as a pass.  The importer now reads immutable theorem and
registration blobs, and ND2 verifies every historical source artifact by its
own Git commit and SHA-256 digest.

Tier 3 is unnecessary: this imports an already-certified partial theorem,
keeps every complete-contraction and physical-execution flag false, and makes
no paper, quantum, spectral, or Lorentzian claim.
