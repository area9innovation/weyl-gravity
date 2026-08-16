#!/usr/bin/env python3
"""Build Gate-A v20 after typed local cyclic-pairing closure."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V19 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V20.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m4_typed_local_cyclicity_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()


def one(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={value}, got {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    previous = json.loads(V19.read_text(encoding="utf-8"))
    closure = json.loads(M4L.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION":
        raise ValueError("Gate V19 predecessor drift")
    if previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V19 was not fail closed")
    if closure.get("result_id") != "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1":
        raise ValueError("M4L identity drift")
    if closure["claim_flags"]["M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE"] is not True:
        raise ValueError("M4L is not complete")
    if closure["claim_flags"]["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False:
        raise ValueError("M4R firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v20-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V20_RECONCILIATION",
        "result_state": "M4L_LOCAL_CYCLIC_PAIRING_COMPLETE_M1_M3R_M4R_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "e8d8b3e8c9870074ffe8122ac49e926880919c91",
        "question": "Does the common strict 386-row carrier now satisfy the local part of the cyclic-pairing gate, and what exactly remains residual?",
        "answer": "Yes for the complete local graph carrier. Its exact odd pairing has rank 386 and 410 ordered rational entries covering all endpoint, generalized-auxiliary and mapping-cone/cotangent rows. On the same M3L manifest, q1, endpoint-SDR, D, q2 and q3 cyclicity obligations replay with zero defects. The old M4 item is therefore split: M4L is complete, while M4R is a REDUCED-MODE induced-pairing obligation that cannot be defined until M3R constructs the endpoint-to-W+/W- comparison. Gate A accepts no new top-level hash and remains fail closed with M1, M3R and M4R open.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V20.md",
    })
    value["minimal_missing_bundle"] = [
        ({
            "id": "M4R_TYPED_RESIDUAL_CYCLICITY",
            "object": "After M3R constructs the endpoint-to-W+/W- comparison, derive the induced residual pairing and replay q_res, inclusion/projection, homotopy and residual-transfer cyclic side conditions in the REDUCED-MODE category.",
            "unlocks": ["cyclic_compatibility", "final full cyclic contraction", "residual transfer premise"],
        } if item["id"] == "M4_FULL_CYCLIC_PAIRING" else item)
        for item in previous["minimal_missing_bundle"]
    ]
    cyclic_export = one(value["export_reconciliation"], "export_id", "cyclic_pairing")
    cyclic_export.update({
        "status": "RECEIVER_VERIFIED_SCOPED",
        "evidence": list(dict.fromkeys([
            *cyclic_export["evidence"],
            "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
            "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1",
            "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1",
            "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1",
            closure["result_id"],
        ])),
        "established": "The complete 386-row local graph carrier has an exact rank-386 odd pairing with 410 ordered rational entries, and q1/endpoint-SDR/D/q2/q3 cyclicity replays with zero local defects on the M3L common manifest.",
        "remaining_for_gate_a": "Construct M3R, derive its induced REDUCED-MODE residual pairing, replay M4R residual cyclicity, then bind the accepted pairing hash in the M1 freeze.",
        "boundary": "Complete local graph cyclicity does not define or certify cyclicity of a global harmonic residual comparison that has not been constructed.",
    })
    cyclic_check = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic_check.update({
        "status": "BLOCKED_MISSING_TYPED_RESIDUAL_COMPARISON",
        "evidence": list(dict.fromkeys([*cyclic_check["evidence"], closure["result_id"]])),
        "established": "All local pairing and cyclicity obligations close on the common 386-row manifest; the separate two-class Gram control remains compatible.",
        "remaining_for_gate_a": "Construct M3R and replay the induced M4R pairing, adjointness and cyclic side conditions on the actual W+/W- residual carrier.",
        "boundary": "The remaining check is REDUCED-MODE and cannot be discharged by treating global harmonic coefficients as local graph rows.",
    })
    value["required_hash_disposition"]["pairing_hash"].update({
        "candidate": closure["pairing_replay"]["pairing_sha256"],
        "candidate_scope": "STRICT_386_FULL_LOCAL_PAIRING_M4L_COMPLETE_M4R_AND_M1_OPEN",
    })
    value["m4_typed_local_cyclicity_resolution"] = {
        "status": "M4L_RECEIVER_VERIFIED_SCOPED_COMPLETE_M4R_OPEN",
        "evidence": closure["result_id"],
        "certificate_sha256": sha(M4L),
        "carrier_rows": closure["pairing_replay"]["carrier_rows"],
        "pairing_entries": closure["pairing_replay"]["nonzero_ordered_pairing_entries"],
        "exact_pairing_rank": closure["pairing_replay"]["exact_rational_rank"],
        "local_cyclicity_defects": sum(
            count for key, count in closure["local_cyclicity_replay"].items() if key.endswith("defects")
        ),
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": "COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN_BLOCKED_BY_M3R",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M3L_M4L_COMPLETE_M1_M3R_M4R_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(V19.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(V19),
            "role": "immutable Gate-A V19 predecessor",
        },
        {
            "path": str(M4L.relative_to(ROOT)),
            "result_or_artifact_id": closure["result_id"],
            "sha256": sha(M4L),
            "role": "receiver-verified local cyclic-pairing closure and M4 type split",
        },
    ]
    value["claim_flags"].update({
        "STRICT_386_FULL_LOCAL_ODD_PAIRING_NONDEGENERATE": True,
        "STRICT_386_LOCAL_Q1_SDR_D_Q2_Q3_CYCLICITY_COMPLETE": True,
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE": True,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": False,
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
        "the M3R endpoint-to-W+/W- harmonic comparison or its induced residual pairing",
        "M4R residual cyclicity, a second accepted Gate-A hash, or the common all-object freeze",
        "nonlinear Green compatibility, a full-complex Hadamard state, renormalized Lorentzian products, QME restoration, residual transfer or physical positivity",
    ]))
    value["next_gate"] = "Construct M3R as a typed endpoint-to-W+/W- comparison, then derive and replay M4R residual cyclicity. When both close, bind M1 and replay the final all-object freeze before any Hadamard or QME promotion."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v20_reconciliation.py",
        "checks": [
            "V19 predecessor and M4L certificate pins",
            "independent M4L checker replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M4 replacement by typed M4R while M1 and M3R remain",
            "full local pairing candidate hash and zero-defect projection",
            "local/residual type firewall",
            "Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    resolution = value["m4_typed_local_cyclicity_resolution"]
    return f"""# Classical import Gate-A reconciliation v20

**Result:** `{value['result_id']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Gate A:** `FAIL_CLOSED`

M4's local half is complete.  The common strict graph carrier has
{resolution['carrier_rows']} rows, an exact rank-{resolution['exact_pairing_rank']}
odd pairing with {resolution['pairing_entries']} ordered rational entries, and
zero combined local cyclicity defects for q1, the endpoint SDR, D, q2 and q3.

The former `M4_FULL_CYCLIC_PAIRING` requirement mixed two carrier types.  It is
replaced by completed `M4L_LOCAL_GRAPH_CYCLIC_PAIRING` and open
`M4R_TYPED_RESIDUAL_CYCLICITY`.  M4R depends on the still-missing M3R harmonic
comparison.  Gate A accepts no new top-level hash and remains fail closed with
M1, M3R and M4R open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v20_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v20_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v20_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V20_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V20_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
