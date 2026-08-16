#!/usr/bin/env python3
"""Build Gate-A v18 after the residual-SDR type/locality audit."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V17 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V17_RECONCILIATION.json"
AUDIT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V18_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V18.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m5_residual_exact_payload_resolution",
        "m6_centered_representatives_resolution", "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(V17.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    dfinite = json.loads(DFINITE.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V17_RECONCILIATION" or previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V17 predecessor drift")
    if audit.get("result_id") != "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1" or audit["claim_flags"]["M3_TYPED_SPLIT_REQUIRED"] is not True:
        raise ValueError("M3 type audit unavailable")
    if audit["claim_flags"]["DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL"] is not False or audit["claim_flags"]["STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL"] is not True:
        raise ValueError("M3 locality disposition drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v18-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V18_RECONCILIATION",
        "result_state": "M3_TYPE_REPAIRED_LOCAL_ENDPOINT_BINDING_AND_TYPED_RESIDUAL_COMPARISON_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "0e0e5670576da72bcaaf2b6d6189cc1d25287ce5",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can Gate A close M3 by treating the local 386-to-30 graph SDR, the 4,490-to-470 D-finite residual SDR and the thirty-dimensional conformal-Killing cotangent payload as one support-local contraction?",
        "answer": "No. Gate V18 repairs M3 rather than accepting a type error. The graph 30 counts local endpoint field species, the D-finite 470 counts W+/W- harmonic coefficients, and the M5 30 counts global symmetry-cotangent coefficients. A global harmonic projector expands support and cannot be used in the support-local Green-transfer premise. M3 is therefore split into M3L, common binding of the already exact local graph endpoint SDR, and M3R, a separately typed harmonic restriction/residual comparison whose nonlocal maps remain REDUCED-MODE. Gate A still accepts one of seven hashes and remains fail closed.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V18.md",
    })
    missing = []
    for item in value["minimal_missing_bundle"]:
        if item["id"] != "M3_RESIDUAL_SDR":
            missing.append(item)
            continue
        missing.extend([
            {
                "id": "M3L_COMMON_ENDPOINT_SDR_BINDING",
                "object": "Bind the exact support-local graph-coordinate i_end_graph, p_end_graph and H_alg_graph on the 386-row strict carrier to the same manifest and hashes as q1/q2/q3/D and the transported suspension.",
                "unlocks": ["common-snapshot local endpoint intertwiners", "386-row contraction identity on accepted bytes", "local premise for causal Green-homotopy transfer"],
            },
            {
                "id": "M3R_TYPED_RESIDUAL_COMPARISON",
                "object": "Construct the harmonic restriction/comparison diagram from the 30-species endpoint section complex to the W+/W- residual coefficient complex, with function spaces and every nonlocal harmonic or zero-mode projection explicitly typed REDUCED-MODE.",
                "unlocks": ["type-correct comparison with the D-finite residual control", "residual intertwiners on declared harmonic domains", "later residual transfer without a false support-local premise"],
            },
        ])
    value["minimal_missing_bundle"] = missing
    value["m3_scoped_resolution"] = {
        "status": "TWO_CERTIFIED_SCOPES_SEPARATED_TYPED_COMPARISON_OPEN",
        "local_endpoint_evidence": graph["result_id"],
        "local_carrier_component_species": graph["scope"]["carrier_dimension"],
        "local_endpoint_component_species": graph["scope"]["retained_endpoint_dimension"],
        "local_graph_sdr_sha256": graph["canonical_hashes"]["graph_sdr_component_maps_sha256"],
        "dfinite_evidence": dfinite["result_id"],
        "dfinite_full_coordinates": dfinite["global_direct_sum"]["full_dimension"],
        "dfinite_residual_coordinates": dfinite["global_direct_sum"]["residual_dimension"],
        "dfinite_residual_sdr_hash": dfinite["global_direct_sum"]["residual_sdr_hash"],
        "direct_support_local_identification": "OBSTRUCTED_FOR_THE_SPECIFIED_GLOBAL_MODE_PROJECTORS",
        "remaining": ["M3L_COMMON_ENDPOINT_SDR_BINDING", "M3R_TYPED_RESIDUAL_COMPARISON"],
        "boundary": "The local endpoint SDR and finite harmonic residual SDR remain valid in their own categories; neither is promoted to the other category.",
    }
    value["m3_type_and_locality_resolution"] = {
        "status": "ORIGINAL_M3_REPLACED_BY_TYPED_TWO_STAGE_CONTRACT",
        "evidence": audit["result_id"],
        "type_census_sha256": audit["type_census"]["sha256"],
        "architecture_decision_sha256": audit["architecture_decision"]["sha256"],
        "graph_endpoint_30_is_finite_residual_30": False,
        "dfinite_residual_projector_support_local": False,
        "zero_mode_projector_support_local": False,
        "M3L_common_endpoint_sdr_bound": False,
        "M3R_typed_residual_comparison_constructed": False,
        "accepted_common_snapshot_hashes_added": 0,
        "gate_a_status": "FAIL_CLOSED",
    }
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M3_TYPE_REPAIRED_FOUR_TYPED_PACKAGES_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V17.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(V17), "role": "immutable Gate-A V17 predecessor"},
        {"path": str(AUDIT.relative_to(ROOT)), "result_or_artifact_id": audit["result_id"], "sha256": sha(AUDIT), "role": "M3 carrier-type and support-locality audit"},
        {"path": str(GRAPH.relative_to(ROOT)), "result_or_artifact_id": graph["result_id"], "sha256": sha(GRAPH), "role": "exact local graph endpoint SDR"},
        {"path": str(DFINITE.relative_to(ROOT)), "result_or_artifact_id": dfinite["result_id"], "sha256": sha(DFINITE), "role": "finite harmonic residual SDR control"},
    ]
    value["claim_flags"].update({
        "STRICT_386_GRAPH_ENDPOINT_SDR_SUPPORT_LOCAL": True,
        "GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30": False,
        "DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL": False,
        "ZERO_MODE_PROJECTOR_SUPPORT_LOCAL": False,
        "ORIGINAL_M3_SINGLE_OBJECT_TYPE_CORRECT": False,
        "M3_TYPED_SPLIT_REQUIRED": True,
        "M3L_COMMON_ENDPOINT_SDR_BOUND": False,
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
        "an identification between thirty local endpoint field species and thirty global conformal-Killing cotangent coefficients",
        "support-locality of the D-finite W+/W- harmonic projector",
        "common-snapshot binding of the already exact graph endpoint SDR",
        "the typed endpoint-to-residual harmonic comparison",
        "a full-complex Hadamard state, renormalized Lorentzian products, QME restoration, or residual transfer",
    ]))
    value["next_gate"] = "Complete M3L by binding the exact graph endpoint SDR to the common strict manifest; in parallel build M3R as a separately typed harmonic restriction/residual comparison. Then close M4 and freeze only after every map is checked in its declared category."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v18_reconciliation.py",
        "checks": [
            "V17 predecessor and type-audit pins", "independent type/locality replay",
            "unchanged twenty exports, ten checks and one accepted hash", "M3 replaced by M3L/M3R",
            "local graph and finite harmonic dimensions/hashes", "support-locality promotion firewall",
            "Gate-A/Hadamard/QME/residual-transfer firewalls", "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    m3 = value["m3_scoped_resolution"]
    gate = value["gate_disposition"]
    return f"""# Classical import Gate-A reconciliation v18

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `{gate['gate_a_status']}`

Gate V18 repairs a type error in the former `M3_RESIDUAL_SDR` requirement.
The exact graph SDR maps {m3['local_carrier_component_species']} local component
species onto {m3['local_endpoint_component_species']} endpoint field species.
The D-finite SDR instead maps {m3['dfinite_full_coordinates']:,} harmonic
coefficients onto {m3['dfinite_residual_coordinates']} W+/W- coefficients.
M5's separate number thirty counts conformal-Killing cotangent coefficients.
These are not interchangeable carriers.

A global constant or harmonic projector expands support, so the existing
reduced-mode receiver cannot be inserted as a support-local map in the causal
Green-transfer premise.  The old M3 item is replaced by:

- `M3L_COMMON_ENDPOINT_SDR_BINDING`, using the already exact local graph SDR;
- `M3R_TYPED_RESIDUAL_COMPARISON`, explicitly nonlocal and `REDUCED-MODE`.

Gate A still accepts one of seven hashes.  No export or freeze count is
promoted, and four typed packages remain: M1, M3L, M3R and M4.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v18_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v18_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v18_reconciliation.py
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
        print("CLASSICAL_IMPORT_GATE_V18_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V18_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
