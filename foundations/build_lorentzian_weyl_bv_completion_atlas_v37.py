#!/usr/bin/env python3
"""Build Atlas V37 after the common endpoint-SDR binding."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json"
BINDING = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v37.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_v19_reconciliation", "strict_common_endpoint_sdr_binding",
        "strict_residual_sdr_type_audit", "strict_source_q2_common_assembly",
        "strict_source_q3_common_assembly", "strict_residual_zero_mode_payload",
        "strict_centered_cohomology_payload", "route_selection", "research_queue",
    )
    return hashlib.sha256(
        json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    branch = next(item for item in value["branches"] if item["id"] == branch_id)
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V36":
        raise ValueError("Atlas V36 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION":
        raise ValueError("Gate V19 unavailable")
    if binding.get("result_id") != "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1":
        raise ValueError("M3L binding unavailable")
    if gate["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"] is not True:
        raise ValueError("Gate V19 does not accept scoped M3L completion")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v37",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37",
        "created": "2026-08-16",
        "question": "After binding the local endpoint SDR to the common strict nonlinear carrier, what is the strongest surviving route toward Lorentzian Weyl BV completion?",
        "answer": "Atlas V37 closes the low-depth M3L integration route. The exact 386-to-30 support-local endpoint SDR now shares a content-addressed manifest with q1, q2, q3, D, pairing, suspension and represented Green names. The strongest next route is to finish the full cyclic pairing on this common carrier, while the separately typed endpoint-to-residual spectral comparison is constructed as REDUCED-MODE data. Only after both can the common freeze be attempted. Gate A remains fail closed at one of seven hashes, so no Hadamard or QME stage is promoted.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v37.md",
    })
    value.pop("strict_gate_v18_reconciliation", None)
    disposition = gate["gate_disposition"]
    value["strict_gate_v19_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": len(gate["export_reconciliation"]),
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "remaining_top_level_hashes": 7 - disposition["accepted_common_snapshot_hashes"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
        "M3L_common_endpoint_sdr_bound": gate["claim_flags"]["M3L_COMMON_ENDPOINT_SDR_BOUND"],
        "M3R_typed_residual_comparison_constructed": gate["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"],
        "gate_a_status": disposition["gate_a_status"],
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_receiver_verified_scoped": disposition["same_theory_receiver_verified_scoped"],
        "exports_total": len(gate["export_reconciliation"]),
        "freeze_checks_receiver_verified_scoped": disposition["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_total": len(gate["freeze_check_reconciliation"]),
        "accepted_top_level_hashes": disposition["accepted_common_snapshot_hashes"],
        "gate_a_status": disposition["gate_a_status"],
        "minimal_missing_bundle": [item["id"] for item in gate["minimal_missing_bundle"]],
    }
    value["strict_common_endpoint_sdr_binding"] = {
        "result_id": binding["result_id"],
        "manifest_id": binding["common_manifest"]["manifest_id"],
        "manifest_sha256": binding["common_manifest"]["sha256"],
        "carrier_rows": binding["common_manifest"]["carrier_rows"],
        "endpoint_rows": binding["common_manifest"]["endpoint_rows"],
        "contracted_rows": binding["common_manifest"]["contracted_rows"],
        "artifact_pins": len(binding["common_manifest"]["artifact_pins"]),
        "canonical_object_hashes": len(binding["common_manifest"]["object_hashes"]),
        "compatibility_links_checked": binding["exact_replay"]["compatibility_links_checked"],
        "projected_identity_defects": sum(
            count for key, count in binding["exact_replay"].items() if key.endswith("defects")
        ),
        "support_local": True,
        "residual_comparison_included": False,
    }
    s0 = stage(value, "STRICT_PURE_WEYL_386", "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "statement": "The q1/q2/q3/D/pairing and exact local graph endpoint SDR now share one scoped content-addressed 386-row manifest. Residual zero modes and centered H4 payload remain exact in their separate reduced-mode scopes; their typed spectral comparison, residual cyclicity and the common all-object freeze remain open.",
        "evidence": list(dict.fromkeys([*s0["evidence"], binding["result_id"], gate["result_id"]])),
        "boundary": "M3L supplies only the support-local endpoint contraction. It does not make global harmonic projectors local, construct M3R, accept another Gate-A hash, or promote Hadamard/QME claims.",
    })

    routes = [deepcopy(row) for row in previous["route_selection"] if row["route"] != "STRICT_COMMON_ENDPOINT_SDR_BINDING"]
    by_route = {row["route"]: row for row in routes}
    ordered_names = [
        "STRICT_FULL_CYCLIC_PAIRING",
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION",
        "STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE",
        "STRICT_CANDIDATE_Q2_Q3_GREEN_LAMBDA2_RESPONSE",
        "DIRECT_SPACETIME_Q26_HADAMARD",
        "STRICT_D_CARTAN_AND_CHARGE_DECISION",
        "STRICT_ANALYTIC_MOLLER_CONVERGENCE",
        "STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN",
    ]
    by_route["STRICT_FULL_CYCLIC_PAIRING"]["recommendation"] = "Audit the already serialized 386-row graph pairing against q1/q2/q3 and every local endpoint-SDR cyclic side condition, then isolate the genuinely residual cyclicity obligations that depend on M3R."
    by_route["STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON"]["recommendation"] = "Construct a typed harmonic restriction/comparison from endpoint sections to W+/W- coefficients, with explicit test/distribution domains, zero-mode policy and REDUCED-MODE labels for every support-expanding map."
    by_route["STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION"]["recommendation"] = "After M4 and M3R, bind the local and reduced-mode objects under one typed manifest and accept each top-level hash only after its category-correct identities replay."
    ordered = [by_route[name] for name in ordered_names]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    value["route_selection"] = ordered
    why = {
        "STRICT_FULL_CYCLIC_PAIRING": "Most graph pairing bytes and local cyclic identities already exist; the audit can separate an attainable local closure from residual cyclicity that genuinely waits for M3R.",
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON": "The remaining M3 task is a typed analytic bridge, not another finite endpoint contraction.",
        "STRICT_COMMON_FREEZE_SNAPSHOT_AND_FINAL_CYCLIC_CONTRACTION": "The all-object freeze becomes meaningful only after M4 and M3R close in their distinct categories.",
    }
    value["research_queue"] = [
        {"priority": row["rank"], "branch": row["branch"], "object": row["route"], "why": why.get(row["route"], row["recommendation"])}
        for row in ordered
    ]
    value["frontier_summary"] = {
        "highest_value_next_route": "STRICT_FULL_CYCLIC_PAIRING",
        "route_count": len(ordered),
        "completed_since_v36": ["STRICT_COMMON_ENDPOINT_SDR_BINDING", "GATE_V19_M3L_INTEGRATION"],
        "new_positive_result": "The exact local graph endpoint SDR and the q1/q2/q3/D nonlinear layers now inhabit one scoped content-addressed 386-row manifest.",
        "new_no_go": "None. The V36 prohibition on treating global harmonic projection as support-local remains in force.",
        "surprise": "M3L required no new homotopy: the decisive work was proving that ten existing artifacts share seventeen canonical object hashes and fifteen exact compatibility links.",
        "hard_boundary": "M4 pairing, M3R typed spectral comparison, M1 freeze, six hashes, nonlinear Green compatibility, Hadamard and QME remain open.",
    }
    value["claim_flags"].update({
        "v36_preserved": True,
        "strict_386_common_endpoint_sdr_manifest_bound": True,
        "strict_386_common_endpoint_sdr_identities_replayed": True,
        "strict_386_q1_d_q2_q3_same_local_carrier": True,
        "strict_M3L_common_endpoint_sdr_bound": True,
        "strict_M3R_typed_residual_comparison_constructed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_q2_q3_green_compatibility_certified": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": sha(PREDECESSOR), "role": "immutable V36 predecessor"},
        {"path": str(BINDING.relative_to(ROOT)), "result_or_artifact_id": binding["result_id"], "sha256": sha(BINDING), "role": "common local endpoint-SDR binding"},
        {"path": str(GATE.relative_to(ROOT)), "result_or_artifact_id": gate["result_id"], "sha256": sha(GATE), "role": "Gate-A V19 M3L reconciliation"},
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v37.py",
        "checks": [
            "V36 predecessor and 77-cell preservation",
            "Gate V19 and M3L content pins",
            "386/30/356 manifest and zero-defect projection",
            "M3L completion with M3R type firewall",
            "three-package Gate remainder and one accepted hash",
            "nine-route reranking",
            "Gate-A/Green/Hadamard/QME firewalls",
            "canonical atlas digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def report(value: dict[str, Any]) -> str:
    binding = value["strict_common_endpoint_sdr_binding"]
    gate = value["strict_gate_v19_reconciliation"]
    routes = "\n".join(f"{row['rank']}. `{row['route']}` — {row['recommendation']}" for row in value["route_selection"])
    return f"""# Lorentzian Weyl BV completion atlas v37

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Decision

M3L is complete.  A scoped common manifest binds {binding['carrier_rows']}
graph rows, {binding['endpoint_rows']} local endpoint species and
{binding['contracted_rows']} contracted rows across
{binding['artifact_pins']} artifacts and
{binding['canonical_object_hashes']} canonical object hashes.  All
{binding['compatibility_links_checked']} compatibility links agree and the
projected defect count is {binding['projected_identity_defects']}.

Gate V19 still accepts {gate['accepted_top_level_hashes']} of seven hashes.
M1, M3R and M4 remain open.  The local endpoint contraction is not identified
with any global harmonic or zero-mode projector.

## Ranked routes

{routes}

## Boundary

No nonlinear Green compatibility, full-complex Hadamard state, renormalized
Lorentzian product, QME restoration or residual quantum transfer is claimed.
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V37: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
