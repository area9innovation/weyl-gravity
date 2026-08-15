#!/usr/bin/env python3
"""Build atlas V17 from V16 plus the stabilized-q2 preflight and Gate V7."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16.json"
PREFLIGHT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V7_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v17.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge",
        "strict_suspended_adjoint_bridge", "strict_component_pairing_serialization",
        "strict_operator_portability", "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "strict_canonical_shear_component_jets", "strict_graph_q1_sdr_component_jets",
        "strict_graph_green_action_name", "strict_unary_causal_common_snapshot",
        "strict_full_d_action", "strict_gate_v6_reconciliation", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def strict_stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, preflight, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, PREFLIGHT, GATE))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16":
        raise ValueError("V16 predecessor drift")
    if preflight.get("result_id") != "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1" or not preflight["claim_flags"].get("STRICT_386_STABILIZED_D_Q2_DERIVATION_VERIFIED"):
        raise ValueError("stabilized q2 preflight drift")
    if preflight["claim_flags"].get("STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED") is not False:
        raise ValueError("q2 preflight authority over-promotion")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V7_RECONCILIATION" or gate["gate_disposition"].get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V7 dependency drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v17",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17",
        "created": "2026-08-15",
        "repository_base_commit": "2040f0c7964077686b7171b528be69cde62d4772",
        "question": "Does the strict 386-row theory admit an exact q2 completion compatible with q1, cyclicity and D, and what remains once a receiver-constructed stabilization is distinguished from an authoritative classical import?",
        "answer": "Atlas V17 resolves the algebraic part of the first-ranked V16 route while exposing a sharper import boundary. Extend the certified minimal q2 by zero on the 356 split contractible rows and transport it by the exact BV-canonical shear. The resulting compositional graph action has 140 ordered-component channels, 68 potentially nonzero block triples and 110-row input/output envelopes; 196 rows remain interaction-inert in both roles. The candidate satisfies q1/q2, Koszul symmetry, q2 cyclicity and D/q2 exactly by direct-sum reasoning, canonical conjugation and stationary tensor naturality. This is a valid cyclic L-infinity stabilization, but it is a quantum-receiver construction rather than an authoritative nonlinear classical export. Gate V7 therefore records its q2 hash as an unaccepted candidate and narrows M2 to source-certified theory identity: either export the intended full q2 or certify a cyclic L-infinity equivalence to the stabilization. All 77 typed atlas cells are preserved, Gate A still accepts zero hashes, and Hadamard, products, QME and residual transfer remain false.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v17.md",
    })
    dag = preflight["graph_transport_dag"]
    identities = preflight["identity_transport"]
    q2_projection = {
        "result_id": preflight["result_id"],
        "status": preflight["result_state"],
        "construction_kind": preflight["split_candidate"]["construction_kind"],
        "carrier_rows": preflight["scope"]["carrier_rows"],
        "endpoint_rows": preflight["scope"]["endpoint_rows"],
        "split_contractible_rows": preflight["scope"]["split_contractible_rows"],
        "minimal_primary_components": preflight["split_candidate"]["minimal_primary_components"],
        "minimal_ordered_components": preflight["split_candidate"]["minimal_ordered_components"],
        "expanded_component_channels": dag["expanded_ordered_component_channels"],
        "unique_block_triples": dag["unique_block_triples"],
        "input_row_envelope": dag["active_input_row_envelope"],
        "output_row_envelope": dag["active_output_row_envelope"],
        "interaction_inert_rows": dag["interaction_inert_rows"],
        "q1_q2_defects": identities["q1_q2_arity_two"]["defects"],
        "koszul_defects": identities["q2_koszul_symmetry"]["defects"],
        "cyclicity_defects": identities["q2_cyclicity"]["defects"],
        "D_q2_defects": identities["D_q2_derivation"]["derivation_defects"],
        "candidate_q2_sha256": preflight["canonical_hashes"]["graph_transport_dag_sha256"],
        "authoritative_full_q2_imported": preflight["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED"],
        "candidate_theory_identity_certified": preflight["claim_flags"]["STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED"],
        "next_gate": preflight["next_gate"],
    }
    gate_projection = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": gate["gate_disposition"]["exports_total"],
        "exports_receiver_verified_scoped": gate["gate_disposition"]["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": gate["gate_disposition"]["freeze_checks_total"],
        "freeze_checks_receiver_verified_scoped": gate["gate_disposition"]["freeze_checks_receiver_verified_scoped"],
        "freeze_checks_supporting_evidence_only": gate["gate_disposition"]["freeze_checks_supporting_evidence_only"],
        "freeze_checks_blocked": gate["gate_disposition"]["freeze_checks_blocked"],
        "accepted_top_level_hashes": gate["gate_disposition"]["accepted_common_snapshot_hashes"],
        "gate_a_status": gate["gate_disposition"]["gate_a_status"],
        "candidate_q2_hash_accepted": gate["required_hash_disposition"]["q2_hash"]["accepted"] is not None,
        "transitive_provenance_files_checked": gate["transitive_provenance_drift"]["files_checked"],
        "transitive_provenance_drifted_files": gate["transitive_provenance_drift"]["drifted_files"],
        "missing_bundle_ids": [item["id"] for item in gate["minimal_missing_bundle"]],
        "next_gate": gate["next_gate"],
    }
    value["strict_stabilized_q2_lift_preflight"] = q2_projection
    value["strict_gate_v7_reconciliation"] = gate_projection
    s0 = strict_stage(value, "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "status": "FAIL_CLOSED",
        "statement": "A cyclic 386-row q2 stabilization now exists and satisfies q1q2, Koszul, cyclicity and D/q2 exactly as a receiver construction. Gate V7 narrows M2 to authoritative classical theory identity; zero top-level hashes are accepted and five other Gate bundles remain open.",
        "evidence": [*s0["evidence"], preflight["result_id"], gate["result_id"]],
        "boundary": "A receiver-constructed cyclic stabilization is not an authoritative classical import. No common q2 hash, Gate-A pass, Hadamard state or QME state follows.",
    })
    strict_branch(value)["next_decisive_object"] = "Source-certify the strict nonlinear q2 theory identity by exporting the full 386-row interaction ledger or a cyclic L-infinity equivalence to the stabilized candidate."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The algebraic 386-row q2 stabilization is exact and compatible with q1, cyclicity and D. What is missing is evidence that it is the authoritative nonlinear extension chosen by the classical programme.",
        "best_next_object": "A source-certified full q2 export or cyclic L-infinity equivalence to STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1, followed by receiver comparison and common-hash binding.",
    }
    value["strict_gate_a_progress"].update({
        "status": "STABILIZED_Q2_CANDIDATE_CERTIFIED_AUTHORITATIVE_IDENTITY_REQUIRED",
        "stabilized_q2_candidate_control": q2_projection,
        "gate_v7_reconciliation_control": gate_projection,
        "remaining_common_carrier": gate["next_gate"],
        "boundary": "Candidate q2/q1q2/cyclicity/Dq2 are exact, but Gate V7 accepts zero hashes because the authoritative classical theory-identity bridge is absent. Residual SDR, full cyclic pairing, residual representation data and centered representatives remain independent required bundles.",
    })
    routes = [
        ("STRICT_386_AUTHORITATIVE_Q2_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Export the authoritative full nonlinear q2 or a source-certified cyclic L-infinity equivalence to the exact stabilized candidate; independently compare it and bind the q2 hash."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control on the same support-local carrier and replay every contraction and chain-map identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows so residual-SDR side conditions share exact bytes."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual fifteen-mode bases, exact SO(4,2) structure constants, representation matrices and q_res on one residual carrier."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized W-plus-squared and W-minus-squared representative vectors together with centered H3, H4 and H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent Hadamard route as a control while refusing to use its q2 or D as strict-theory Gate-A evidence."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "With a candidate nonlinear q2 now available, classify whether D admits a Cartan homotopy and is proper gauge, charged or sector-dependent without confusing that question with D/q2 equivariance."),
        ("STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "MEDIUM", "Optionally add effective projector/tail algorithms or kernel bytes without making them prerequisites for the certified classical convergent name."),
    ]
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V16 atlas predecessor"},
        {"path": str(PREFLIGHT.relative_to(ROOT)), "sha256": sha(PREFLIGHT), "role": "strict stabilized-q2 construction and theory-identity preflight"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "Gate-A V7 candidate/import reconciliation"},
    ]
    value["claim_flags"].update({
        "v16_preserved": True,
        "strict_386_stabilized_q2_candidate_certified": True,
        "strict_386_stabilized_q1_q2_identity_verified": True,
        "strict_386_stabilized_q2_cyclicity_verified": True,
        "strict_386_stabilized_d_q2_derivation_verified": True,
        "strict_386_authoritative_full_q2_imported": False,
        "strict_386_candidate_theory_identity_certified": False,
        "strict_386_full_carrier_q2_certified": False,
        "strict_386_d_q2_derivation_replayed": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "that the receiver-constructed q2 stabilization is the authoritative nonlinear classical extension",
        "a source-certified cyclic L-infinity equivalence or an accepted q2 Gate-A hash",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v17.py",
        "checks": [
            "V16 predecessor and 77-cell preservation", "q2 support-envelope projection",
            "candidate q1q2/Koszul/cyclicity/Dq2 zero-defect projection", "Gate-V7 count/hash firewall",
            "authoritative theory-identity frontier", "eight-route deterministic ranking",
            "quantum lifecycle firewall", "append-only provenance",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    q2 = value["strict_stabilized_q2_lift_preflight"]
    gate = value["strict_gate_v7_reconciliation"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v17", "", "## Outcome", "", value["answer"], "",
        "## Stabilized q2 candidate", "",
        f"- Carrier: **{q2['carrier_rows']}** rows = **{q2['endpoint_rows']}** endpoint + **{q2['split_contractible_rows']}** contractible rows.",
        f"- Graph support envelope: **{q2['expanded_component_channels']}** component channels, **{q2['unique_block_triples']}** block triples, **{q2['input_row_envelope']} / {q2['output_row_envelope']}** input/output rows.",
        f"- Candidate defects: q1/q2 **{q2['q1_q2_defects']}**, Koszul **{q2['koszul_defects']}**, cyclicity **{q2['cyclicity_defects']}**, D/q2 **{q2['D_q2_defects']}**.",
        f"- Authoritative full q2 imported: **{q2['authoritative_full_q2_imported']}**; theory identity certified: **{q2['candidate_theory_identity_certified']}**.", "",
        "## Gate-A disposition", "",
        f"Gate V7 has **{gate['exports_receiver_verified_scoped']} / {gate['exports_total']}** scoped exports and **{gate['freeze_checks_receiver_verified_scoped']} / {gate['freeze_checks_total']}** scoped checks. One further check is supporting evidence and one is blocked. It accepts **{gate['accepted_top_level_hashes']}** hashes and remains `{gate['gate_a_status']}`.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v17.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v17.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v17.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v17.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {boundary}." for boundary in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V17: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
