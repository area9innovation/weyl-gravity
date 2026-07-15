# Classical import and cylinder bootstrap report

## Outcome

The first quantum import snapshot is pinned to classical commit
`a3fc926cc289e5a545933a43331e395328580e0e` and tagged
`LOCAL-ALGEBRAIC`.  The verifier confirms that all 17 referenced artifacts
match both that commit and the current working tree.

This is an integrity result, not the classical freeze:

```text
artifact_integrity_status           VERIFIED
gate_a_status                       FAIL_CLOSED
claim_state                         CLASSICAL_IMPORT_PENDING
publishable_quantum_results_allowed false
```

The checked-in machine result is
[`certificates/CLASSICAL_IMPORT_CERTIFICATE.json`](certificates/CLASSICAL_IMPORT_CERTIFICATE.json).
Its source snapshot is
[`snapshots/bootstrap-v1.json`](snapshots/bootstrap-v1.json).  Their SHA-256
digests at this bootstrap are respectively
`3c6f540286ca0cda0e4c6663d31f68bf66a8a7cea40891dc65b60c43f4673213`
and
`01e4b2188695f901a77a5bd1921454dc57c19b2d8047c835a83646cbabd74a26`.

## Required export ledger

`AVAILABLE` means that a portable exact ledger exists within its explicitly
stated classical scope.  It does not by itself pass Gate A.  `INCOMPLETE`
means useful content-addressed evidence exists but the complete portable
payload required by the quantum brief does not.  `NOT_AVAILABLE` means no
such payload was found and no substitute was reconstructed.

| Required classical export | Status | Fail-closed boundary |
|---|---|---|
| Complete field, ghost, and antifield dictionary | `INCOMPLETE` | Existing dictionaries are finite D-eigenmode cylinder dictionaries. |
| All field gradings | `INCOMPLETE` | No export has form degree and parity together with every other required grading. |
| Complete local classical BV differential `Q0` | `INCOMPLETE` | The imported tangent certificate explicitly excludes nonlinear terms. |
| Gauge-fixed and nonminimal contractions | `INCOMPLETE` | Identities and internal map hashes exist, not a complete portable map payload. |
| Trace-sector contraction | `INCOMPLETE` | The finite-buffer certificate does not export the local projector/homotopy. |
| Fifteen conformal-Killing zero modes | `INCOMPLETE` | Labels, gradings, and matrix digests exist; basis vectors are not serialized. |
| Residual representation matrices `rho(G_a)` | `NOT_AVAILABLE` | No portable full residual representation payload was found. |
| Structure constants `f^a_bc` | `INCOMPLETE` | Jacobi is certified, but the tensor is constructed in code rather than exported. |
| Classical inclusion `iota_cl` | `NOT_AVAILABLE` | Only finite-mode internal hashes are reported. |
| Classical projection `pi_cl` | `NOT_AVAILABLE` | Only finite-mode internal hashes are reported. |
| Classical homotopy `S_cl` | `NOT_AVAILABLE` | Only finite-mode internal hashes are reported. |
| Cyclic pairing | `INCOMPLETE` | Exact identities and normalization exist, but not the complete portable pairing. |
| Taub/moment-map normalization | `AVAILABLE` | Exact D-finite E/A/L normalization ledger, with its own scope guards. |
| BFV suspension convention | `AVAILABLE` | Selected closed-cylinder convention with `lambda=+1`; uniqueness is not claimed. |
| Positive-frequency state ledger | `AVAILABLE` | Selected algebraic polarization; analytic completion is outside this import. |
| Normalized representatives `W_\pm^2 v_-` | `INCOMPLETE` | Names, parity, and Gram data exist; normalized coefficient vectors do not. |
| Centered bases in degrees 3, 4, and 5 | `INCOMPLETE` | The H4 basis and C3/C4/C5 dimensions exist; H3 and H5 bases do not. |
| Residual differential `Q_res^(0)` | `INCOMPLETE` | The finite-window transfer is certified; a full portable action payload is absent. |

Consequently every independent freeze identity remains
`BLOCKED_MISSING_EXPORT`: `Q0^2=0`, `pi_cl iota_cl=1`, the contraction
identity, both chain-map identities, and cyclic compatibility.  The required
top-level dictionary, differential, zero-mode, pairing, and representative
hash fields are present but null.  A null is not a hash of absence; it means
there is no accepted complete payload to hash yet.

## Antifield/Koszul--Tate handoff contract

The required shape of the local antifield export is now executable rather
than implicit.  The schema
[`schema/antifield_export.schema.json`](schema/antifield_export.schema.json)
and fail-closed preflight
[`verify_antifield_export.py`](verify_antifield_export.py) require the metric,
diffeomorphism-ghost, and Weyl-ghost antifields, as well as every retained
nonminimal or auxiliary antifield.  Every generator carries tensor type,
all gradings, exact mass dimension and Weyl weight, its complete `Q_image`,
canonical index symmetry, and the equation or Noether-identity row from
which its Koszul--Tate image arises.

The preflight also requires the explicit split

```text
Q = delta + gamma + Q_gt0
```

with antifield-number shifts `-1`, `0`, and positive, respectively.  It
rejects floating-point data, missing minimal roles, unsafe proof paths,
unverified filtration identities, and non-reproducing canonical hashes.
Proof artifacts are required for `delta^2=0`,
`delta gamma + gamma delta=0`, and `Q^2=0`.

The receipt
[`certificates/ANTIFIELD_EXPORT_CONTRACT.json`](certificates/ANTIFIELD_EXPORT_CONTRACT.json)
is deliberately `CONTRACT_READY_AWAITING_CLASSICAL_EXPORT`.  It certifies the
handoff format and preflight behavior, not the absent classical rows and not
their independent quantum-side verification.

## Cylinder branch

[`../cylinder/bootstrap.json`](../cylinder/bootstrap.json) imports only this
ledger.  It records the 15-generator and centered-H4 evidence but does not
recompute it.  The local-to-cylinder map is `NOT_COMPUTED`; projection is
blocked at the absent `pi_cl`, and the adjacent-degree ledger records H3 and
H5 as `NOT_AVAILABLE`.  The even/odd basis formula is recorded as a
convention, while the parity operator and Ward identity remain unavailable
or uncomputed.

## Verification receipts

Run from `physics/symplectic-reconstruction/` on 2026-07-15:

| Tier | Command | Elapsed | Status |
|---|---|---:|---:|
| 0 | `python3 -m py_compile quantum-weyl/classical_import/verify_snapshot.py quantum-weyl/classical_import/tests/test_verify_snapshot.py` | 0.03 s | pass |
| 0 | Parse every JSON file below `quantum-weyl/classical_import` and `quantum-weyl/cylinder` with Python `json` | 0.02 s | pass (4 files) |
| 0 | Scoped Python EOF/trailing-whitespace check over all eight new text files | 0.02 s | pass |
| 0 | `git diff --check -- quantum-weyl/classical_import quantum-weyl/cylinder` | <0.01 s | pass; integration staging remains with the root agent |
| 1 | `python3 quantum-weyl/classical_import/verify_snapshot.py --check` | 0.12 s | pass |
| 1 | `python3 -m unittest discover -s quantum-weyl/classical_import/tests -v` | under 1 s | pass (13 tests, including 9 antifield-contract tests) |

The tests include attempted false promotion of Gate A and an artifact-hash
mutation; both fail closed.  Tier 2 was not triggered because no classical
mathematical input or certificate chain changed: the imported inputs are
unchanged and content-addressed.  Tier 3 was not triggered because this work
does not freeze a theorem, promote a lifecycle state, alter shared core
algebra, or prepare a release.  No full classical or repository-wide suite
was run or represented as passing.

## Next classical handoff

The next snapshot should replace partial evidence with versioned portable
payloads, run the antifield preflight, populate the five required top-level
hashes, and let the quantum verifier independently execute the filtration and
six freeze identities.  Until then, the correct state is a verified import
inventory with Gate A closed.
