#!/usr/bin/env python3
"""Build Gate-A v22 after the residual odd-pairing rank obstruction."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V21 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V22_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V22.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m3r_typed_residual_comparison_resolution", "m4_typed_local_cyclicity_resolution",
        "residual_cyclic_carrier_obstruction_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def one(items: list[dict[str, Any]], key: str, wanted: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == wanted]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={wanted}, got {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    previous = json.loads(V21.read_text(encoding="utf-8"))
    obstruction = json.loads(OBSTRUCTION.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V21_RECONCILIATION":
        raise ValueError("Gate V21 predecessor drift")
    if previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V21 was not fail closed")
    if obstruction.get("result_id") != "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1":
        raise ValueError("residual cyclic obstruction identity drift")
    flags = obstruction["claim_flags"]
    if (
        flags["CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO"] is not True
        or flags["FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE"] is not True
        or flags["FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING"] is not False
        or flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False
    ):
        raise ValueError("residual cyclic obstruction firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v22-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V22_RECONCILIATION",
        "result_state": "M3R_PRIMAL_COMPLETE_CURRENT_470_M4R_RANK_ZERO_M3RC_M4R_M1_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "6395898920233872342d9f24757d5c7406f5db05",
        "question": "Can M4R be replayed directly on the current 470-mode M3R target, and what exact prerequisite remains if not?",
        "answer": "No. The receiver finds that all 470 M3R synthesis columns land in degree-zero metric slots, while the authoritative degree-minus-one BV form has no metric-metric block. The induced odd form is therefore exactly zero, with rank defect 470. The older symmetric cross-energy cohomology form is not a field-theoretic BV antibracket and cannot repair the mismatch. A finite 940-coordinate shifted-cotangent carrier and its canonical rank-940 odd pairing are constructed as a preflight, but the degree-one dual inclusion, projection and homotopy into the authoritative endpoint complex remain absent. Gate A now records M3RC cyclic residual carrier completion as a prerequisite to M4R; M1 remains last.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V22.md",
    })
    value["minimal_missing_bundle"] = [
        {
            "id": "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION",
            "object": "Extend the 470-coordinate primal M3R target by degree-one dual residual representatives on the same endpoint domain, with exact dual inclusion/projection and an identified action-derived odd pairing.",
            "unlocks": ["nondegenerate induced residual BV pairing", "well-typed M4R replay"],
        },
        {
            "id": "M4R_TYPED_RESIDUAL_CYCLICITY",
            "object": "On the M3RC-complete carrier, replay q_res cyclicity, p=iota-sharp, homotopy skew-adjointness and residual-transfer cyclic side conditions exactly.",
            "unlocks": ["cyclic_compatibility", "final full cyclic contraction", "residual transfer premise"],
        },
        {
            "id": "M1_COMMON_STRICT_SNAPSHOT",
            "object": "One versioned strict pure-Weyl manifest and commit containing every Gate-A carrier, map and ordered basis, including both residual primal and dual maps, with no Berger or compensator rows.",
            "unlocks": ["all seven accepted top-level hashes", "independent common-domain replay"],
        },
    ]

    cyclic = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic.update({
        "status": "BLOCKED_RESIDUAL_CARRIER_RANK_ZERO_MISSING_M3RC",
        "evidence": list(dict.fromkeys([*cyclic["evidence"], obstruction["result_id"]])),
        "established": "M4L closes the local pairing identities and M3R fixes the primal 470-mode comparison. Exact receiver replay shows the literal induced odd form on that target has rank zero. A canonical rank-940 cotangent preflight exists but is not identified with the endpoint/action pairing.",
        "remaining_for_gate_a": "Construct M3RC dual representatives and comparison maps, identify their pairing with the action-derived BV form, then replay M4R.",
        "boundary": "The rank-zero result obstructs only direct M4R on the one-sided 470-mode carrier. It does not obstruct a dual-complete residual carrier.",
    })
    value["m3r_typed_residual_comparison_resolution"].update({
        "status": "M3R_PRIMAL_RECEIVER_VERIFIED_M3RC_REQUIRED_FOR_CYCLIC_COMPLETION",
        "target_category": "finite primal W+/W- residual coefficient space concentrated in degree zero",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC_RANK_ZERO",
    })
    value["m4_typed_local_cyclicity_resolution"].update({
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC_RANK_ZERO",
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "OPEN",
    })
    replay = obstruction["obstruction_replay"]
    preflight = obstruction["cotangent_preflight"]
    value["residual_cyclic_carrier_obstruction_resolution"] = {
        "status": "RECEIVER_VERIFIED_RANK_ZERO_OBSTRUCTION_AND_940_COTANGENT_PREFLIGHT",
        "evidence": obstruction["result_id"],
        "certificate_sha256": sha(OBSTRUCTION),
        "current_primal_coordinates": replay["m3r_residual_coordinates"],
        "current_induced_odd_pairing_rank": replay["pulled_back_odd_pairing_rank"],
        "current_induced_odd_pairing_nullity": replay["pulled_back_odd_pairing_nullity"],
        "current_nondegeneracy_rank_defect": replay["nondegeneracy_rank_defect"],
        "cotangent_preflight_coordinates": preflight["total_dimension"],
        "cotangent_preflight_pairing_rank": preflight["constructive_exact_rank"],
        "cotangent_pairing_action_identified": False,
        "M3RC_CYCLIC_RESIDUAL_CARRIER_COMPLETION": "OPEN",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "BLOCKED_BY_M3RC",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M3L_M3R_PRIMAL_M4L_COMPLETE_M3RC_M4R_M1_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(V21.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(V21),
            "role": "immutable Gate-A V21 predecessor",
        },
        {
            "path": str(OBSTRUCTION.relative_to(ROOT)),
            "result_or_artifact_id": obstruction["result_id"],
            "sha256": sha(OBSTRUCTION),
            "role": "receiver-verified rank-zero M4R obstruction and finite cotangent preflight",
        },
    ]
    value["claim_flags"].update({
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": True,
        "M3R_PRIMAL_ONLY_FOR_CYCLIC_PURPOSES": True,
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_RANK_ZERO": True,
        "CURRENT_470_MODE_INDUCED_ODD_PAIRING_NONDEGENERATE": False,
        "FINITE_940_SHIFTED_COTANGENT_CARRIER_CONSTRUCTED": True,
        "FINITE_940_CANONICAL_ODD_PAIRING_NONDEGENERATE": True,
        "FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING": False,
        "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED": False,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
        "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED": False,
        "COMMON_GATE_A_FREEZE_BOUND": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "nonexistence of every possible cyclic residual completion; only the direct one-sided 470-mode pullback is rank-zero obstructed",
        "dual residual representatives, dual comparison maps or action-pairing transport for the 940-coordinate cotangent preflight",
        "M3RC, M4R, a new accepted Gate-A hash or the M1 common freeze",
    ]))
    value["next_gate"] = "Construct M3RC dual residual representatives and comparison maps on the same endpoint domain, identify the action-derived odd pairing, then replay M4R and bind M1 before any Hadamard or QME promotion."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v22_reconciliation.py",
        "checks": [
            "V21 predecessor and obstruction content pins",
            "independent rank-zero and 940-cotangent receiver replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M3RC, M4R and M1 retained in dependency order",
            "cyclic check blocked on the exact rank defect rather than marked ready",
            "even-form/BV-pairing category firewall",
            "Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    resolution = value["residual_cyclic_carrier_obstruction_resolution"]
    return f"""# Classical import Gate-A reconciliation v22

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

Direct M4R on the current 470-mode M3R target is obstructed.  All synthesis
columns land in degree-zero metric slots, so the degree-minus-one local BV
form pulls back to rank {resolution['current_induced_odd_pairing_rank']} with
nullity {resolution['current_induced_odd_pairing_nullity']}.

The exact 940-coordinate shifted-cotangent preflight has pairing rank
{resolution['cotangent_preflight_pairing_rank']}, but its degree-one dual
comparison maps and action-pairing identification are not constructed.  Gate
A therefore inserts M3RC before M4R.  M1 remains the final common freeze; no
new top-level hash is accepted.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v22_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v22_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v22_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V22_RECONCILIATION: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V22_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
