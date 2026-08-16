#!/usr/bin/env python3
"""Build Gate-A v19 after the common local endpoint-SDR binding."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V18 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
BINDING = HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V19.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m5_residual_exact_payload_resolution", "m6_centered_representatives_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(V18.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION":
        raise ValueError("Gate V18 predecessor drift")
    if previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V18 was not fail closed")
    if binding.get("result_id") != "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1":
        raise ValueError("M3L binding identity drift")
    if binding["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not True:
        raise ValueError("M3L binding is not complete")
    if binding["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not False:
        raise ValueError("M3L result crossed the residual type boundary")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v19-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION",
        "result_state": "M3L_COMMON_ENDPOINT_SDR_BOUND_THREE_TYPED_PACKAGES_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "669895e3a9f75681f36de94f73a9b3b6039af8d7",
        "question": "Does the exact local graph endpoint SDR now inhabit the same content-addressed strict 386-row carrier as q1, q2, q3, D, pairing, suspension and the represented Green names?",
        "answer": "Yes, within M3L's local endpoint scope. Ten artifact pins and seventeen canonical object hashes bind the exact 386-to-30 graph SDR to the common q1/q2/q3/D carrier, and fifteen cross-certificate compatibility checks plus all projected exact identities have zero defects. This removes M3L from the missing bundle. It does not construct the nonlocal endpoint-to-residual comparison, close its cyclic pairing, accept another top-level freeze hash, or pass Gate A. M3R, M4 and M1 remain open; Gate A still accepts one of seven hashes and remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V19.md",
    })
    value["minimal_missing_bundle"] = [
        item for item in previous["minimal_missing_bundle"]
        if item["id"] != "M3L_COMMON_ENDPOINT_SDR_BINDING"
    ]
    value["m3_scoped_resolution"].update({
        "status": "LOCAL_ENDPOINT_COMMON_BINDING_COMPLETE_TYPED_RESIDUAL_COMPARISON_OPEN",
        "local_common_binding_evidence": binding["result_id"],
        "local_common_manifest_sha256": binding["common_manifest"]["sha256"],
        "remaining": ["M3R_TYPED_RESIDUAL_COMPARISON"],
    })
    value["m3_type_and_locality_resolution"].update({
        "M3L_common_endpoint_sdr_bound": True,
        "M3R_typed_residual_comparison_constructed": False,
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    })
    value["m3l_common_endpoint_sdr_binding_resolution"] = {
        "status": "RECEIVER_VERIFIED_SCOPED_COMPLETE",
        "evidence": binding["result_id"],
        "certificate_sha256": sha(BINDING),
        "common_manifest_id": binding["common_manifest"]["manifest_id"],
        "common_manifest_sha256": binding["common_manifest"]["sha256"],
        "carrier_rows": binding["common_manifest"]["carrier_rows"],
        "endpoint_rows": binding["common_manifest"]["endpoint_rows"],
        "contracted_rows": binding["common_manifest"]["contracted_rows"],
        "artifact_pins": len(binding["common_manifest"]["artifact_pins"]),
        "canonical_object_hashes": len(binding["common_manifest"]["object_hashes"]),
        "compatibility_links_checked": binding["exact_replay"]["compatibility_links_checked"],
        "total_projected_identity_defects": sum(
            count for key, count in binding["exact_replay"].items() if key.endswith("defects")
        ),
        "support_local": binding["claim_flags"]["STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL"],
        "residual_comparison_included": False,
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M3L_COMPLETE_THREE_TYPED_PACKAGES_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(V18.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(V18),
            "role": "immutable Gate-A V18 predecessor",
        },
        {
            "path": str(BINDING.relative_to(ROOT)),
            "result_or_artifact_id": binding["result_id"],
            "sha256": sha(BINDING),
            "role": "receiver-verified common local endpoint-SDR binding",
        },
    ]
    value["claim_flags"].update({
        "STRICT_386_COMMON_ENDPOINT_SDR_MANIFEST_BOUND": True,
        "STRICT_386_COMMON_ENDPOINT_SDR_IDENTITIES_REPLAYED": True,
        "STRICT_386_Q1_D_Q2_Q3_SAME_LOCAL_CARRIER": True,
        "M3L_COMMON_ENDPOINT_SDR_BOUND": True,
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": False,
        "COMMON_GATE_A_FREEZE_BOUND": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "the typed endpoint-to-W+/W- residual harmonic comparison or support-locality of its global projectors",
        "residual cyclicity, a second accepted Gate-A hash, or the common all-object freeze",
        "nonlinear Green compatibility, a full-complex Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Close M4's local graph pairing obligations against the now-common endpoint SDR and construct M3R as a separately typed REDUCED-MODE comparison. After both close, bind M1 and replay the final all-object freeze."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v19_reconciliation.py",
        "checks": [
            "V18 predecessor and M3L certificate pins",
            "independent M3L checker replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M3L removal leaving M1/M3R/M4",
            "common manifest and zero-defect projection",
            "local/residual type firewall",
            "Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    resolution = value["m3l_common_endpoint_sdr_binding_resolution"]
    gate = value["gate_disposition"]
    return f"""# Classical import Gate-A reconciliation v19

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `{gate['gate_a_status']}`

M3L is complete.  The common local endpoint manifest binds
{resolution['carrier_rows']} graph rows to {resolution['endpoint_rows']} local
endpoint species, contracts {resolution['contracted_rows']} rows, pins
{resolution['artifact_pins']} source artifacts and records
{resolution['canonical_object_hashes']} canonical object hashes.  All
{resolution['compatibility_links_checked']} cross-certificate compatibility
links agree and the projected exact defect total is
{resolution['total_projected_identity_defects']}.

This is a scoped integration result, not a new residual map.  The global
W+/W- harmonic comparison remains M3R and must stay typed `REDUCED-MODE`.
Residual cyclicity remains M4.  No new top-level Gate-A hash is accepted, so
the gate remains fail closed with one of seven hashes and three missing
packages: M1, M3R and M4.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v19_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v19_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v19_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V19_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V19_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
