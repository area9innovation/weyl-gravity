#!/usr/bin/env python3
"""Build atlas V16 from V15 plus full D and Gate-A v6 reconciliation."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15.json"
FULL_D = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_FULL_D_ACTION_V1.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V6_RECONCILIATION.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v16.md"


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
        "strict_full_d_action", "strict_gate_v6_reconciliation", "berger_h26_c26_decision_chain",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, full_d, gate = (json.loads(path.read_text()) for path in (PREDECESSOR, FULL_D, GATE))
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V15":
        raise ValueError("V15 predecessor drift")
    if full_d.get("result_id") != "STRICT_386_FULL_D_ACTION_V1" or not all(
        full_d["claim_flags"].get(key) is True
        for key in ("STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED", "STRICT_386_D_Q1_COMMUTATOR_REPLAYED", "STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED")
    ):
        raise ValueError("full D dependency drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V6_RECONCILIATION" or gate["gate_disposition"].get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate V6 dependency drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v16",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16",
        "created": "2026-08-15",
        "repository_base_commit": "3fa9c8cc37040960afbc5f6de7a0260389c2bd66",
        "question": "Can the V15 unary-causal graph snapshot be extended by a correctly typed full cylinder-flow action on all 386 rows, can its q1 equivariance be replayed independently, and how does that narrow the classical Gate-A frontier without promoting q2 or quantum completion?",
        "answer": "Atlas V16 closes the first-ranked V15 route. The real compact-cylinder flow is T=Lie_{partial_t}; the Hermitian mode convention is D=iT after complexification. In a global frame Lie-dragged by partial_t on the stationary unit cylinder, T is one temporal derivative on every natural-bundle component, not a finite energy matrix, Minkowski dilation or Berger helical generator. The exact action table contains 386 rational first-order diagonal entries across all twenty-two graph blocks. An independent receiver constructs Tq1 and q1T separately for all twenty-seven graph-q1 tables, seventy derivative multiindices and 4,374 rational coefficients; their commutator has zero defects. Formal skew-adjointness replays against all 410 ordered pairing entries. The accepted scoped unary-causal snapshot therefore grows from thirteen to fourteen object hashes. Gate-A reconciliation V6 promotes the strict local-D export and D/q1 check to RECEIVER_VERIFIED_SCOPED, but accepts no top-level Gate hash. Five transitive V5 provenance files have drifted and are recorded without silent rebinding. M2 is narrowed to extending q2 over every required nonminimal, generalized-auxiliary and graph row, followed by D/q2 and full-carrier q2 cyclicity. The complete manifest, residual SDR, full residual pairing, SO(4,2) payload and centered representatives remain separate blockers. Hadamard, products, QME and residual quantum transfer remain false.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v16.md",
    })
    replay = full_d["exact_replay"]
    d_projection = {
        "result_id": full_d["result_id"],
        "status": full_d["result_state"],
        "selected_real_generator": full_d["generator_selection"]["selected_real_generator"],
        "hermitian_mode_convention": full_d["D_action"]["hermitian_mode_convention"],
        "carrier_rows": full_d["scope"]["carrier_rows"],
        "component_blocks": full_d["scope"]["component_blocks"],
        "D_coefficients": full_d["D_action"]["nonzero_coefficients"],
        "temporal_multiindex": full_d["D_action"]["temporal_multiindex"],
        "q1_tables_checked": replay["q1_operator_tables_checked"],
        "q1_multiindices_checked": replay["q1_derivative_multiindices_checked"],
        "q1_coefficients_checked": replay["q1_rational_coefficients_checked"],
        "D_q1_commutator_defects": replay["D_q1_commutator_defects"],
        "pairing_entries_checked": replay["formal_skew_adjoint_pairing_entries_checked"],
        "formal_skew_adjoint_defects": replay["formal_skew_adjoint_defects"],
        "scoped_snapshot_hashes": full_d["extended_common_snapshot"]["accepted_object_hashes"],
        "D_action_sha256": full_d["canonical_hashes"]["D_action_sha256"],
        "full_q2_common_snapshot": full_d["claim_flags"]["STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT"],
        "D_q2_derivation": full_d["claim_flags"]["STRICT_386_D_Q2_DERIVATION_REPLAYED"],
        "D_gauge_or_charge_decided": full_d["claim_flags"]["D_PROPER_GAUGE_OR_CHARGED_DECIDED"],
        "next_gate": full_d["next_gate"],
    }
    gate_projection = {
        "result_id": gate["result_id"],
        "status": gate["result_state"],
        "exports_total": gate["gate_disposition"]["exports_total"],
        "exports_receiver_verified_scoped": gate["gate_disposition"]["same_theory_receiver_verified_scoped"],
        "freeze_checks_total": gate["gate_disposition"]["freeze_checks_total"],
        "freeze_checks_receiver_verified_scoped": gate["gate_disposition"]["freeze_checks_receiver_verified_scoped"],
        "accepted_top_level_hashes": gate["gate_disposition"]["accepted_common_snapshot_hashes"],
        "gate_a_status": gate["gate_disposition"]["gate_a_status"],
        "D_candidate_hash_accepted": gate["required_hash_disposition"]["D_action_hash"]["accepted"] is not None,
        "transitive_provenance_files_checked": gate["transitive_provenance_drift"]["files_checked"],
        "transitive_provenance_drifted_files": gate["transitive_provenance_drift"]["drifted_files"],
        "missing_bundle_ids": [item["id"] for item in gate["minimal_missing_bundle"]],
        "next_gate": gate["next_gate"],
    }
    value["strict_full_d_action"] = d_projection
    value["strict_gate_v6_reconciliation"] = gate_projection
    s0 = stage(value, "S0_CLASSICAL_AUTHORITY")
    s0.update({
        "status": "FAIL_CLOSED",
        "statement": "The accepted strict unary-causal graph now includes the full 386-row cylinder flow and a zero-defect D/q1 replay in a fourteen-hash scoped snapshot. Gate V6 promotes those two obligations only; full-carrier q2/D-q2 and five other Gate bundles remain open.",
        "evidence": [*s0["evidence"], full_d["result_id"], gate["result_id"]],
        "boundary": "The local D action is not a q2 extension, D/q2 theorem, D-Cartan homotopy, physical quotient decision, complete Gate-A manifest or quantum result. Zero top-level Gate hashes are accepted.",
    })
    strict_branch(value)["next_decisive_object"] = "Extend strict q2 to every required row of the accepted 386-row unary-causal-D snapshot and independently replay q1q2, D/q2, Koszul symmetry, row completeness and q2 cyclicity."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "Graph q1, local SDR, represented Green actions and the full cylinder flow now inhabit one fourteen-hash scoped snapshot; [D,q1] and formal D skew-adjointness are exact. The first missing same-carrier datum is full 386-row q2.",
        "best_next_object": "A complete 386-row strict q2 payload in the canonical pairing convention, followed by independent q1q2, D/q2, Koszul, completeness and cyclicity replay.",
    }
    value["strict_gate_a_progress"].update({
        "status": "UNARY_CAUSAL_D_COMMON_SNAPSHOT_ACCEPTED_FULL_Q2_AND_GATE_BUNDLES_REQUIRED",
        "full_d_action_control": d_projection,
        "gate_v6_reconciliation_control": gate_projection,
        "remaining_common_carrier": full_d["next_gate"],
        "boundary": "The scoped snapshot now includes D and D/q1, but Gate V6 accepts zero top-level hashes. Full-carrier q2/D-q2, residual SDR, full cyclic pairing, residual representation data and centered representatives remain independent required bundles.",
    })
    routes = [
        ("STRICT_386_Q2_D_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Extend canonical strict q2 to every required 386-row sector and replay q1q2, D/q2, Koszul symmetry, row completeness and q2 cyclicity on the accepted unary-causal-D snapshot."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to all nonminimal, auxiliary and residual rows so the full-carrier q2 cyclic replay and residual-SDR side conditions share bytes."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control on the same support-local carrier and replay every contraction and chain-map identity."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual fifteen-mode bases, exact SO(4,2) structure constants, representation matrices and q_res on one residual carrier."),
        ("STRICT_CENTERED_REPRESENTATIVES", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Export exact normalized W-plus-squared and W-minus-squared representative vectors together with centered H3, H4 and H5 bases."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent Hadamard route as a control while refusing to use its q2 or D as strict-theory Gate-A evidence."),
        ("STRICT_GREEN_NAME_EFFECTIVE_REFINEMENT", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "MEDIUM", "Optionally add effective projector/tail algorithms or kernel bytes without making them prerequisites for the certified classical convergent name."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "After q2 is common, distinguish local D equivariance from a nonlinear Cartan homotopy and independently decide the proper-gauge, charged or sector-dependent status of the cylinder generator."),
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
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V15 atlas predecessor"},
        {"path": str(FULL_D.relative_to(ROOT)), "sha256": sha(FULL_D), "role": "strict full cylinder D action and D/q1 replay"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "Gate-A V6 scoped D reconciliation and provenance drift ledger"},
    ]
    value["claim_flags"].update({
        "v15_preserved": True,
        "strict_386_full_local_d_action_certified": True,
        "strict_386_d_q1_commutator_replayed": True,
        "strict_386_d_formal_skew_adjoint_replayed": True,
        "strict_386_unary_causal_d_scoped_snapshot_accepted": True,
        "strict_386_full_carrier_q2_certified": False,
        "strict_386_d_q2_derivation_replayed": False,
        "strict_386_d_cartan_homotopy_constructed": False,
        "strict_d_gauge_or_charge_decided": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "a full-carrier strict q2 or D/q2 theorem from the unary D/q1 replay",
        "a nonlinear D-Cartan homotopy or a proper-gauge/charge decision for the cylinder generator",
        "a silently rebound replay of the five drifted Gate-V5 transitive provenance files",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v16.py",
        "checks": [
            "V15 predecessor and 77-cell preservation", "full-D exact inventory projection",
            "Gate-V6 count/hash/provenance-drift projection", "strict S0-only evidence augmentation",
            "fourteen-hash scoped snapshot", "q2/D-q2 fail-closed frontier",
            "eight-route deterministic ranking", "quantum lifecycle firewall", "append-only provenance",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    d = value["strict_full_d_action"]
    gate = value["strict_gate_v6_reconciliation"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v16", "", "## Outcome", "", value["answer"], "",
        "## Full cylinder-flow certificate", "",
        f"- Real generator: `{d['selected_real_generator']}`; {d['hermitian_mode_convention']}.",
        f"- Carrier: **{d['carrier_rows']}** rows in **{d['component_blocks']}** blocks; **{d['D_coefficients']}** exact first-order entries.",
        f"- q1 replay: **{d['q1_tables_checked']}** tables, **{d['q1_multiindices_checked']}** multiindices and **{d['q1_coefficients_checked']}** coefficients; defects **{d['D_q1_commutator_defects']}**.",
        f"- Pairing replay: **{d['pairing_entries_checked']}** entries; skew-adjoint defects **{d['formal_skew_adjoint_defects']}**.",
        f"- Scoped snapshot objects: **{d['scoped_snapshot_hashes']}**.", "",
        "## Gate-A disposition", "",
        f"Gate V6 has **{gate['exports_receiver_verified_scoped']} / {gate['exports_total']}** scoped export rows and **{gate['freeze_checks_receiver_verified_scoped']} / {gate['freeze_checks_total']}** scoped checks. It accepts **{gate['accepted_top_level_hashes']}** top-level hashes and remains `{gate['gate_a_status']}`.",
        f"It records **{gate['transitive_provenance_drifted_files']}** drifted files among **{gate['transitive_provenance_files_checked']}** inherited provenance records without rebinding them.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v16.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v16.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v16.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v16.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V16: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
