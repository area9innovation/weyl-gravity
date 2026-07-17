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
`eb48675fb36489e7d33724b2d06f1f0ebfe6867d043bf71d1536015f9862b2d6`
and
`459f46e3a8d233754ceec2593c858b1996ead38ec52622678bf5a7c7ec3a61e9`.

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
| Support-local classical BV `q2` | `NOT_AVAILABLE` | No arbitrary-support local-polydifferential payload with complete field, ghost, and antifield rows was found. |
| Local `D` action on all BV generators | `NOT_AVAILABLE` | No portable support-local action covering fields, ghosts, and antifields was found. |
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
`BLOCKED_MISSING_EXPORT`.  In addition to the free contraction identities,
the ledger now names arity-two nilpotency, `[D,q1]=0`, the full `D` derivation
identity for `q2`, and `q2` cyclicity explicitly.  The required top-level
dictionary, `q1`, `q2`, `D`-action, zero-mode, pairing, and representative
hash fields are present but null.  A null is not a hash of absence; it means
there is no accepted complete payload to hash yet.

## Support-local `q2` handoff contract

The former generic sparse-tensor schema was insufficient to distinguish an
arbitrary-support local bidifferential operator from a finite-mode matrix.
The executable contract now consists of
[`schema/support_local_q2_export.schema.json`](schema/support_local_q2_export.schema.json),
[`verify_support_local_q2_export.py`](verify_support_local_q2_export.py), and
the machine receipt
[`certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json`](certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json).

It requires the metric, Diff/Weyl ghosts, and all three minimal antifield
roles; complete output-row ledgers for `q1`, `q2`, and the local `D` action;
the suspended factorial convention; exact local-expression payloads and jet
bounds; and a declared support/test-function category.  It rejects endpoint
or finite-mode locality labels, floating-point coefficients, parity-degree
violations, incomplete rows, unknown generators, unverified proof receipts,
and non-reproducing canonical hashes.  When a repository root is supplied,
every proof artifact must match both the working tree and the pinned classical
commit.

The seven required proof receipts are `q1^2=0`, arity-two nilpotency,
Koszul symmetry, row completeness, `[D,q1]=0`, the `D`-derivation identity for
`q2`, and BV cyclicity of `q2`.  The contract is
`CONTRACT_READY_AWAITING_CLASSICAL_EXPORT`; it does not certify any missing
coefficient or replace independent quantum-side evaluation of the expressions.

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

with antifield-number shifts `-1`, `0`, and zero or more distinct positive
components, respectively.  It
rejects floating-point data, missing minimal roles, unsafe proof paths,
unverified filtration identities, and non-reproducing canonical hashes.
Proof artifacts are required for `delta^2=0`,
`delta gamma + gamma delta=0`, reconstruction of the complete `Q_image` from
the filtration components, and `Q^2=0`.
When supplied a repository root, it also verifies every proof digest against
both the working-tree bytes and the pinned `classical_commit` Git blob.

The receipt
[`certificates/ANTIFIELD_EXPORT_CONTRACT.json`](certificates/ANTIFIELD_EXPORT_CONTRACT.json)
is deliberately `CONTRACT_READY_AWAITING_CLASSICAL_EXPORT`.  It certifies the
handoff format and preflight behavior, not the absent classical rows and not
their independent quantum-side verification.

### Executable v2 receiving gate

The v1 receipt remains historical metadata preflight. The active receiving
gate is now
[`ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT.json`](certificates/ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT.json).
Version 2 replaces opaque expression objects with exact rational canonical
superpolynomials over a finite, grading-bounded atom dictionary. It requires
the complete minimal field/ghost/antifield dictionary and content-addressed
field, action, Euler--Lagrange, Noether, atom-basis, and canonicalization
manifests.

The consumer reconstructs `Q` from `delta`, `gamma`, and all positive
filtration components, independently evaluates the filtration identities on
every atom, closes the admitted monomials, and dry-runs exact sparse blocks
through `FilteredLocalComplex` and its AFN0 view. Producer proof booleans are
retained only as pinned provenance. The receiver now enforces the declared
graded scope, and the real classical export has passed it independently in
[`CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json`](certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json).
That import closes the handoff gate but does not compute the minimal-BV
relative cohomology.

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
| 0 | `python3 -m py_compile` on the changed classical-import and nonlinear-consumer Python files | 0.03 s | pass |
| 0 | Parse all classical-import and transfer certificate/schema JSON files with Python `json` | 0.02 s | pass (17 files) |
| 0 | Parse `.github/workflows/conformal-bridge.yml` with Python `yaml.safe_load` | <0.01 s | pass |
| 1 | `python3 quantum-weyl/classical_import/support_local_q2_contract_certificate.py --check` | 0.04 s | pass |
| 1 | `python3 quantum-weyl/classical_import/verify_snapshot.py --check` | 0.14 s | pass |
| 1 | `python3 -m unittest discover -s quantum-weyl/classical_import/tests -v` | 0.46 s | pass (28 tests) |
| 2 | `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check` | 0.04 s | pass |
| 2 | Focused ND1 and nonlinear aggregate consumer tests | 8.08 s | pass (11 tests) |
| 2 | `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 47.76 s | pass (42 tests) |

The tests include attempted false promotion of Gate A, finite-mode
substitution, missing antifield roles, incomplete rows, parity and exactness
violations, unverified identities, hash mutations, and proof-artifact drift;
all fail closed.  The affected nonlinear chain was regenerated after its
first run correctly detected the changed snapshot dependency, and the final
full transfer suite passes.  Tier 3 was not triggered because no classical
mathematical tensor was imported, no shared algebra changed, and no complete
interacting, quantum, Lorentzian, or paper lifecycle state was promoted.

## Next classical handoff

The next snapshot should replace partial evidence with versioned portable
payloads, run both executable preflights, populate the seven required
top-level hashes, and let the quantum verifier independently execute the
filtration and ten freeze identities.  Until then, the correct state is a
verified import inventory with Gate A closed.
