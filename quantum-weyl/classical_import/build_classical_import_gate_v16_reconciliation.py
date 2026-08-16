#!/usr/bin/env python3
"""Build Gate-A v16 after the exact residual zero-mode export."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V15 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V15_RECONCILIATION.json"
RESIDUAL = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V16.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation",
        "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m5_residual_exact_payload_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(V15.read_text())
    residual = json.loads(RESIDUAL.read_text())
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V15_RECONCILIATION" or previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V15 predecessor drift")
    required_flags = (
        "STRICT_PRIMAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_DUAL_FIFTEEN_MODE_BASIS_SERIALIZED",
        "STRICT_SO42_STRUCTURE_CONSTANTS_SERIALIZED",
        "STRICT_RESIDUAL_REPRESENTATION_MATRICES_SERIALIZED",
        "STRICT_Q_RES_0_SERIALIZED",
        "STRICT_RESIDUAL_ZERO_MODE_IDENTITIES_REPLAYED",
        "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE",
    )
    if any(residual.get("claim_flags", {}).get(flag) is not True for flag in required_flags):
        raise ValueError("residual zero-mode payload incomplete")
    if any(residual["exact_replay"].values()):
        raise ValueError("residual zero-mode replay defects")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v16-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V16_RECONCILIATION",
        "result_state": "RESIDUAL_M5_EXACT_PAYLOAD_COMPLETE_COMMON_FREEZE_AND_FOUR_PACKAGES_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "be886d401f450636443a37cfb8d6ddaa2048d79b",
        "question": "Does the portable exact fifteen-mode residual payload close Gate A?",
        "answer": "No, but it closes the substantive M5 coefficient absence. Exact primal and dual fifteen-mode bases, SO(4,2) structure constants, all residual adjoint/cotangent representation matrices, and q_res^(0) are now independently replayable. Their zero-mode hash is a valid candidate, not an accepted common-freeze hash: the support-local residual SDR, full cyclic contraction, centered H3/H4/H5 representatives and one all-object manifest remain open. Gate A stays fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V16.md",
    })

    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    updates = {
        "conformal_killing_zero_modes_15": (
            "The canonical CE ordering now has exact 65-by-15 primal and dual coefficient matrices, coordinate maps and idempotent projectors; the receiver proves KZ=0 and normalized primal-dual pairing.",
            "Bind the residual snapshot hash to the same versioned full support-local Gate-A manifest as q0/q2/q3/D, the pairing and SDR.",
            "A finite polynomial zero-mode chart is not itself a support-local residual SDR or a common freeze.",
        ),
        "residual_representation_matrices": (
            "All fifteen exact adjoint, coadjoint and 30-by-30 cotangent representation matrices are serialized and the receiver proves every representation commutator.",
            "Bind these matrices to the common residual carrier and its support-local inclusion and projection.",
            "An exact finite residual representation does not construct the full-field intertwining maps.",
        ),
        "so42_structure_constants": (
            "The complete ordered 15-by-15-by-15 SO(4,2) tensor is serialized with 120 nonzero entries; antisymmetry, unimodularity and every Jacobi identity replay exactly.",
            "Pin the tensor in the common Gate-A freeze manifest.",
            "The Lie algebra payload does not establish analytic group integration or a Hadamard representation.",
        ),
        "residual_differential_q_res_0": (
            "The zero unary q_res^(0) matrix on Z[1] plus Z^*[-1] is serialized, squared and linked to the separately exported nonabelian CE structure tensor.",
            "Replay q0/iota_cl and pi_cl/q0 intertwiners against this exact residual matrix on the common support-local SDR.",
            "The unary zero matrix does not replace the nonlinear CE/BFV differential or the missing residual SDR.",
        ),
    }
    for export_id, (established, remaining, boundary) in updates.items():
        row = exports[export_id]
        row.update({
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": list(dict.fromkeys([*row["evidence"], residual["result_id"]])),
            "established": established,
            "remaining_for_gate_a": remaining,
            "boundary": boundary,
        })

    value["required_hash_disposition"]["zero_mode_basis_hash"] = {
        "accepted": None,
        "candidate": residual["canonical_hashes"]["zero_mode_basis_sha256"],
        "candidate_scope": "EXACT_PRIMAL_DUAL_RESIDUAL_PAYLOAD_READY_NOT_BOUND_TO_COMMON_GATE_A_FREEZE",
    }
    value["minimal_missing_bundle"] = [
        item for item in value["minimal_missing_bundle"] if item["id"] != "M5_RESIDUAL_EXACT_PAYLOAD"
    ]
    statuses = Counter(row["status"] for row in value["export_reconciliation"])
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M5_RESIDUAL_PAYLOAD_COMPLETE_COMMON_BINDING_OPEN",
        "same_theory_receiver_verified_scoped": statuses["RECEIVER_VERIFIED_SCOPED"],
        "different_theory_controls": statuses["CERTIFIED_DIFFERENT_THEORY"],
        "legacy_accepted_scoped": statuses["LEGACY_ACCEPTED_SCOPED"],
        "supporting_evidence_only": statuses["SUPPORTING_EVIDENCE_ONLY"],
        "missing_portable_objects": statuses["MISSING_PORTABLE_OBJECT"],
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["m5_residual_exact_payload_resolution"] = {
        "status": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
        "evidence": residual["result_id"],
        "residual_snapshot_sha256": residual["residual_snapshot"]["sha256"],
        "zero_mode_basis_sha256": residual["canonical_hashes"]["zero_mode_basis_sha256"],
        "structure_constants_sha256": residual["canonical_hashes"]["structure_constants_sha256"],
        "representation_matrices_sha256": residual["canonical_hashes"]["representation_matrices_sha256"],
        "q_res_0_sha256": residual["canonical_hashes"]["q_res_0_sha256"],
        "primal_modes": residual["scope"]["primal_dimension"],
        "dual_modes": residual["scope"]["dual_dimension"],
        "structure_nonzero_entries": residual["so42_structure_constants"]["nonzero_entries"],
        "representation_matrices": len(residual["residual_representation"]["matrices"]),
        "identity_defects": sum(residual["exact_replay"].values()),
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V15.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V15), "role": "immutable Gate-A V15 predecessor"},
        {"path": str(RESIDUAL.relative_to(ROOT)), "result_or_artifact_id": residual["result_id"], "sha256": sha(RESIDUAL), "role": "portable exact residual zero-mode, Lie and representation payload"},
    ]
    value["claim_flags"].update({
        "STRICT_PRIMAL_FIFTEEN_MODE_BASIS_SERIALIZED": True,
        "STRICT_DUAL_FIFTEEN_MODE_BASIS_SERIALIZED": True,
        "STRICT_SO42_STRUCTURE_CONSTANTS_SERIALIZED": True,
        "STRICT_RESIDUAL_REPRESENTATION_MATRICES_SERIALIZED": True,
        "STRICT_Q_RES_0_SERIALIZED": True,
        "STRICT_RESIDUAL_ZERO_MODE_IDENTITIES_REPLAYED": True,
        "M5_RESIDUAL_EXACT_PAYLOAD_COMPLETE": True,
        "COMMON_GATE_A_FREEZE_BOUND": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *[item for item in previous["does_not_establish"] if "residual payload" not in item and "zero-mode" not in item],
        "acceptance of the residual zero-mode candidate hash in a common full Gate-A freeze",
        "the support-local residual SDR or final full cyclic contraction",
        "centered H3, H4 and H5 representative coefficient vectors",
        "Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Construct the exact centered H3/H4/H5 representative payload and the common support-local residual SDR; then bind those bytes with the already compatible 386-row q1/q2/q3/D/pairing carrier and this residual snapshot in one freeze manifest, accepting hashes only after the final cyclic contraction replays."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v16_reconciliation.py",
        "checks": [
            "V15 predecessor and residual file pins", "independent residual payload replay",
            "four export promotions", "M5 removal and four-package remainder",
            "candidate-not-accepted zero-mode hash firewall", "actual twenty-row status counts",
            "Gate-A and quantum fail-closed flags", "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    m5 = value["m5_residual_exact_payload_resolution"]
    gate = value["gate_disposition"]
    return f"""# Classical import Gate-A reconciliation v16

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`
**Gate A:** `{gate['gate_a_status']}`

The substantive residual coefficient package `M5` is now complete.  The
receiver independently replays {m5['primal_modes']} primal modes,
{m5['dual_modes']} normalized dual modes, {m5['structure_nonzero_entries']}
nonzero ordered SO(4,2) structure coefficients, all
{m5['representation_matrices']} residual representation matrices and
`q_res^(0)`, with **{m5['identity_defects']}** identity defects.

This creates a real zero-mode hash candidate, but adds **zero** accepted
common-freeze hashes.  Candidate coefficients do not become a common Gate-A
snapshot merely because they are exact.  The candidate must still be bound
to the support-local full carrier, residual SDR, cyclic pairing and centered
representatives.

The status totals are now recomputed from the twenty export rows:
{gate['same_theory_receiver_verified_scoped']} receiver-verified scoped,
{gate['legacy_accepted_scoped']} legacy scoped, and
{gate['supporting_evidence_only']} supporting-only.  Four replacement
packages remain: `M1`, `M3`, `M4`, and `M6`.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v16_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v16_reconciliation.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_classical_import_gate_v16_reconciliation.py'
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V16_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V16_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
