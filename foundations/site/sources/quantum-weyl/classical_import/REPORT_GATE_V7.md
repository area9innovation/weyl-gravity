# Classical import Gate-A reconciliation v7

**Result:** `CLASSICAL_IMPORT_GATE_V7_RECONCILIATION`

**Lifecycle:** `CLASSIFIED`

**Gate A:** `FAIL_CLOSED`

## Outcome

The strict minimal q2 has an exact cyclic trivial stabilization on the full
**386**-row carrier.  Its graph-coordinate action DAG
has **140** ordered-component channels,
**68** block triples and
**110 / 110**
input/output row envelopes.  Candidate q1/q2, q2 cyclicity and D/q2 defects are
**0 / 0 / 0**.

## The remaining M2 obstruction

The construction is internally valid, but it was made by the quantum receiver.
No authoritative classical export or source-certified cyclic L-infinity
equivalence says that the intended nonminimal and generalized-auxiliary theory
is this trivial stabilization.  The candidate q2 hash is therefore recorded
but not accepted.

The old Berger D/q2 control is no longer the closest evidence.  It is replaced
by strict-carrier supporting evidence, still below a Gate-A freeze check because
the theory-identity link is missing.

## Gate verdict

Gate A remains fail closed with **0**
accepted hashes.  The export/check counts are unchanged at
**11 / 20**
scoped exports and **8 / 10**
scoped checks.  One check is supporting evidence and one remains blocked.
M1 and M3-M6 are independent blockers.

## Provenance drift

The V6 input ledger contains **23** records; **5**
current files differ from those historical hashes.  Every difference is
recorded and none is silently rebound.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v7_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v7_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v7_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v7_reconciliation.py
```
