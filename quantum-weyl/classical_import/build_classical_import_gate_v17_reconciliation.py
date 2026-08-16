#!/usr/bin/env python3
"""Build Gate-A v17 after the exact centered cohomology export."""

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
V16 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V16_RECONCILIATION.json"
CENTERED = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V17.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation",
        "required_hash_disposition", "minimal_missing_bundle",
        "gate_disposition", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(V16.read_text(encoding="utf-8"))
    centered = json.loads(CENTERED.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V16_RECONCILIATION" or previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V16 predecessor drift")
    required_flags = (
        "STRICT_CENTERED_C3_C4_C5_BASES_SERIALIZED",
        "STRICT_CENTERED_DIFFERENTIAL_RECONSTRUCTED",
        "STRICT_NORMALIZED_WEYL_SQUARE_REPRESENTATIVES_SERIALIZED",
        "STRICT_CENTERED_H4_COHOMOLOGY_REPLAYED",
        "M6_CENTERED_REPRESENTATIVES_COMPLETE",
    )
    if any(centered.get("claim_flags", {}).get(flag) is not True for flag in required_flags):
        raise ValueError("centered payload incomplete")
    if centered["exact_replay"]["d3_d4_nilpotency_defects"] or centered["exact_replay"]["representative_cocycle_defects"] or centered["exact_replay"]["representative_gram_defects"]:
        raise ValueError("centered payload replay defects")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v17-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V17_RECONCILIATION",
        "result_state": "M5_AND_M6_EXACT_PAYLOADS_COMPLETE_COMMON_FREEZE_AND_THREE_PACKAGES_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "0817dcbb57ee93b141649f79f4c12a95d11e8d46",
        "question": "Does the portable centered C3/C4/C5 complex and its normalized H4 basis close Gate A?",
        "answer": "No, but it closes the substantive M6 coefficient absence. Ordered centered C3, C4 and C5 bases, reconstructible d3/d4 data, and normalized W_+^2 v_- and W_-^2 v_- coordinate vectors now replay independently. Their representative hash is a valid candidate, not an accepted common-freeze hash. Gate A remains fail closed with one of seven hashes accepted; M1 common freeze, M3 support-local residual SDR and M4 full cyclic pairing remain open.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V17.md",
    })
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    exports["normalized_weyl_square_representatives"].update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*exports["normalized_weyl_square_representatives"]["evidence"], centered["result_id"]])),
        "established": "Exact sparse Q(sqrt(10)) coefficient vectors for W_+^2 v_- and W_-^2 v_- are serialized in the declared 3,084-coordinate centered C4 basis; the receiver proves cocycle status, independence, Gram I2 and parity exchange.",
        "remaining_for_gate_a": "Bind the representative payload hash to the same common support-local carrier, SDR and full cyclic pairing used by every other Gate-A object.",
        "boundary": "These are degree-four deformation/vertex classes in a finite transferred coefficient complex, not one-particle states or a full-field Lorentzian quantum construction.",
    })
    exports["centered_cohomology_bases_h3_h4_h5"].update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([*exports["centered_cohomology_bases_h3_h4_h5"]["evidence"], centered["result_id"]])),
        "established": "Ordered centered cochain bases C3, C4 and C5 of dimensions 727, 3,084 and 8,532 are serialized with coefficient actions from which the receiver rebuilds d3 and d4, proves nilpotency and exact H4 dimension two.",
        "remaining_for_gate_a": "Transport and bind this finite centered basis through the common support-local residual SDR and full cyclic contraction.",
        "boundary": "The adjacent degree-three and degree-five exports are cochain bases used to audit H4; no H3 or H5 cohomology group is claimed.",
    })
    value["required_hash_disposition"]["representative_hash"] = {
        "accepted": None,
        "candidate": centered["canonical_hashes"]["representatives_sha256"],
        "candidate_scope": "EXACT_CENTERED_C3_C4_C5_AND_NORMALIZED_H4_PAYLOAD_READY_NOT_BOUND_TO_COMMON_GATE_A_FREEZE",
    }
    value["minimal_missing_bundle"] = [
        item for item in value["minimal_missing_bundle"] if item["id"] != "M6_CENTERED_REPRESENTATIVES"
    ]
    statuses = Counter(row["status"] for row in value["export_reconciliation"])
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M5_M6_PAYLOADS_COMPLETE_COMMON_BINDING_OPEN",
        "same_theory_receiver_verified_scoped": statuses["RECEIVER_VERIFIED_SCOPED"],
        "different_theory_controls": statuses["CERTIFIED_DIFFERENT_THEORY"],
        "legacy_accepted_scoped": statuses["LEGACY_ACCEPTED_SCOPED"],
        "supporting_evidence_only": statuses["SUPPORTING_EVIDENCE_ONLY"],
        "missing_portable_objects": statuses["MISSING_PORTABLE_OBJECT"],
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["m6_centered_representatives_resolution"] = {
        "status": "PAYLOAD_COMPLETE_COMMON_FREEZE_BINDING_OPEN",
        "evidence": centered["result_id"],
        "centered_snapshot_sha256": centered["centered_snapshot"]["sha256"],
        "ordered_centered_basis_sha256": centered["canonical_hashes"]["ordered_centered_basis_sha256"],
        "representatives_sha256": centered["canonical_hashes"]["representatives_sha256"],
        "cochain_dimensions_C3_C4_C5": centered["scope"]["centered_cochain_dimensions_C3_C4_C5"],
        "differential_nonzero_coefficients": centered["centered_differential_summary"]["aggregate_nonzero_coefficients"],
        "ranks_d3_d4": centered["centered_differential_summary"]["aggregate_ranks_d3_d4"],
        "H4_dimension": centered["scope"]["cohomology_dimension_H4"],
        "normalized_gram": centered["normalized_H4_representatives"]["normalized_gram"],
        "identity_defects": sum(value_ for key, value_ in centered["exact_replay"].items() if key.endswith("defects")),
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V16.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V16), "role": "immutable Gate-A V16 predecessor"},
        {"path": str(CENTERED.relative_to(ROOT)), "result_or_artifact_id": centered["result_id"], "sha256": sha(CENTERED), "role": "portable centered cochain and normalized H4 representative payload"},
    ]
    value["claim_flags"].update({
        "STRICT_CENTERED_C3_C4_C5_BASES_SERIALIZED": True,
        "STRICT_CENTERED_DIFFERENTIAL_RECONSTRUCTED": True,
        "STRICT_NORMALIZED_WEYL_SQUARE_REPRESENTATIVES_SERIALIZED": True,
        "STRICT_CENTERED_H4_COHOMOLOGY_REPLAYED": True,
        "M6_CENTERED_REPRESENTATIVES_COMPLETE": True,
        "COMMON_GATE_A_FREEZE_BOUND": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *[item for item in previous["does_not_establish"] if "centered H3" not in item and "representative" not in item],
        "acceptance of the centered representative candidate hash in a common full Gate-A freeze",
        "H3 or H5 cohomology; C3 and C5 are adjacent cochain carriers in this certificate",
        "the common support-local residual SDR or final full cyclic contraction",
        "a one-particle interpretation for W_+^2 or W_-^2",
        "Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Construct the common support-local residual SDR and full cyclic pairing; then bind those bytes with q1/q2/q3/D, the residual zero modes and the centered payload in one freeze manifest, accepting hashes only after the final cyclic contraction replays."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v17_reconciliation.py",
        "checks": [
            "V16 predecessor and centered file pins", "independent centered payload replay",
            "two export promotions", "M6 removal and three-package remainder",
            "candidate-not-accepted representative hash firewall", "actual twenty-row status counts",
            "Gate-A and quantum fail-closed flags", "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    m6 = value["m6_centered_representatives_resolution"]
    gate = value["gate_disposition"]
    return f"""# Classical import Gate-A reconciliation v17

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `{gate['gate_a_status']}`

The finite centered coefficient package `M6` is now complete.  Its ordered
`C3/C4/C5` dimensions are `{m6['cochain_dimensions_C3_C4_C5']}`.  An
independent receiver reconstructs {m6['differential_nonzero_coefficients']:,}
nonzero differential coefficients, obtains ranks `{m6['ranks_d3_d4']}`, and
proves a two-dimensional `H4` with Gram matrix `{m6['normalized_gram']}` and
**{m6['identity_defects']}** declared identity defects.

This creates a real representative-hash candidate, but adds **zero**
accepted common-freeze hashes.  Gate A still accepts one of seven hashes.
The status totals are now {gate['same_theory_receiver_verified_scoped']} of
20 exports receiver-verified in declared scopes, with the three legacy
rows unchanged.  Three replacement packages remain: `M1`, `M3`, and `M4`.

The adjacent `C3` and `C5` bases are not claims that `H3` or `H5` cohomology
has been computed.  The two `H4` classes are deformation/vertex classes,
not one-particle states.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v17_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v17_reconciliation.py
python3 -m unittest discover -s quantum-weyl/classical_import/tests -p 'test_classical_import_gate_v17_reconciliation.py'
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
        print("CLASSICAL_IMPORT_GATE_V17_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V17_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
