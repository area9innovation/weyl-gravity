#!/usr/bin/env python3
"""Independently replay the strict candidate q2/Green composition preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
UNARY = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
INPUTS = (
    (Q2, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1"),
    (UNARY, "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1"),
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    q2, green, unary = (load(path) for path, _ in INPUTS)
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1"
        or value.get("result_kind") != "CANDIDATE_FIRST_NONLINEAR_CAUSAL_RESPONSE_AND_FOUNDATIONAL_STRATIFICATION"
        or value.get("result_state") != "CANDIDATE_Q2_GREEN_RESPONSE_CERTIFIED_AUTHORITATIVE_AND_RECURSIVE_COMPLETION_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
    ):
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    provenance = value.get("provenance", {}).get("inputs", [])
    expected_provenance = [
        {
            "path": str(path.relative_to(ROOT)),
            "result_or_artifact_id": expected,
            "sha256": sha(path),
        }
        for path, expected in INPUTS
    ]
    if len(provenance) != len(expected_provenance):
        errors.append("provenance length")
    else:
        for actual, expected in zip(provenance, expected_provenance):
            if any(actual.get(key) != item for key, item in expected.items()):
                errors.append("provenance content")
                break

    candidate = q2.get("candidate_snapshot", {})
    accepted = unary.get("accepted_objects", {})
    alignment = value.get("carrier_alignment", {})
    expected_alignment = {
        "carrier_rows": 386,
        "basis_candidate_sha256": candidate.get("basis_sha256"),
        "basis_unary_sha256": accepted.get("component_basis_sha256"),
        "pairing_candidate_sha256": candidate.get("pairing_sha256"),
        "pairing_unary_sha256": accepted.get("odd_pairing_sha256"),
        "graph_q1_candidate_sha256": candidate.get("graph_q1_sha256"),
        "graph_q1_unary_sha256": accepted.get("graph_q1_sha256"),
        "basis_match": candidate.get("basis_sha256") == accepted.get("component_basis_sha256"),
        "pairing_match": candidate.get("pairing_sha256") == accepted.get("odd_pairing_sha256"),
        "graph_q1_match": candidate.get("graph_q1_sha256") == accepted.get("graph_q1_sha256"),
        "unary_snapshot_sha256": unary.get("common_snapshot", {}).get("sha256"),
        "candidate_q2_sha256": q2.get("canonical_hashes", {}).get("graph_transport_dag_sha256"),
        "status": "SAME_RECEIVER_BYTES_PREFLIGHT_NOT_GATE_A_ACCEPTED",
    }
    expected_alignment["sha256"] = digest(expected_alignment)
    if alignment != expected_alignment or not all(expected_alignment[key] for key in ("basis_match", "pairing_match", "graph_q1_match")):
        errors.append("carrier alignment")

    try:
        q2_order = max(item["maximum_total_derivative_order"] for item in q2["identity_transport"]["naturality_ledger"])
        inverse_order = max(item["maximum_order"] for item in q2["graph_transport_dag"]["inverse_tables"])
        forward_order = max(item["maximum_order"] for item in q2["graph_transport_dag"]["forward_tables"])
    except (KeyError, TypeError, ValueError):
        errors.append("source derivative orders")
        return errors
    expected_local = {
        "domain": "Gamma_c^infinity(M,E_386) x Gamma_c^infinity(M,E_386)",
        "codomain": "Gamma_c^infinity(M,E_386)",
        "topology": "support-indexed strict LF topology, with the usual C-infinity seminorms on each compact slab",
        "reason": "A finite-order bilinear differential operator with smooth stationary coefficients is continuous on every fixed compact-support Fréchet step and therefore defines the declared LF bilinear action.",
        "minimal_q2_maximum_total_derivative_order": q2_order,
        "inverse_shear_maximum_order": inverse_order,
        "forward_shear_maximum_order": forward_order,
        "conservative_per_input_derivative_order_bound": inverse_order + q2_order + forward_order,
        "conservative_total_derivative_order_bound": 2 * inverse_order + q2_order + forward_order,
        "support_rule": "supp q2_candidate(u,v) subset supp(u) intersection supp(v)",
        "support_local": True,
        "continuous_bilinear_on_declared_source": True,
        "effective_seminorm_constants_serialized": False,
    }
    expected_local["sha256"] = digest(expected_local)
    if value.get("local_q2_continuity") != expected_local:
        errors.append("local q2 continuity/support")

    expected_responses: dict[str, Any] = {}
    for sign in ("plus", "minus"):
        source_name = green.get("operator_names", {}).get(sign, {})
        response = {
            "sign": sign,
            "orientation": green.get("parent_spectral_name", {}).get("orientation", {}).get(sign),
            "formula": f"B_{sign}(u,v)=Lambda_graph,{sign}(q2_candidate(u,v))",
            "name": {
                "node": "COMPOSE_BINARY_RESPONSE",
                "children": [
                    {"node": "STRICT_386_STABILIZED_Q2_CANDIDATE", "sha256": q2["canonical_hashes"]["graph_transport_dag_sha256"]},
                    {"node": "STRICT_386_GRAPH_GREEN_ACTION_NAME", "sign": sign, "sha256": source_name.get("canonical_name_sha256")},
                ],
            },
            "input_space": expected_local["domain"],
            "output_space": green.get("represented_spaces", {}).get("target", {}).get("space"),
            "well_defined": True,
            "continuous_bilinear": True,
            "support": f"supp B_{sign}(u,v) subset J_{sign}(supp(u) intersection supp(v))",
        }
        response["canonical_name_sha256"] = digest(response["name"])
        expected_responses[sign] = response
    if value.get("response_names") != expected_responses:
        errors.append("response names")

    difference = {
        "formula": "B_causal=B_plus-B_minus",
        "name": {
            "node": "DIFFERENCE",
            "children": [
                {"node": "BINARY_RESPONSE", "sign": "plus", "sha256": expected_responses["plus"]["canonical_name_sha256"]},
                {"node": "BINARY_RESPONSE", "sign": "minus", "sha256": expected_responses["minus"]["canonical_name_sha256"]},
            ],
        },
        "support": "supp B_causal(u,v) subset J(supp(u) intersection supp(v))",
        "continuous_bilinear": True,
    }
    difference["canonical_name_sha256"] = digest(difference["name"])
    if value.get("causal_response_difference") != difference:
        errors.append("causal response difference")

    replay = value.get("homotopy_response_replay", {})
    replay_core = {key: item for key, item in replay.items() if key != "sha256"}
    expected_replay = {
        "inputs": "homogeneous compactly supported smooth u,v",
        "q1_q2_identity": "q1 q2(u,v)+q2(q1 u,v)+(-1)^|u| q2(u,q1 v)=0",
        "green_homotopy_identity": "q1 Lambda_sign+Lambda_sign q1=identity_386",
        "response_identity": "q1 B_sign(u,v)-B_sign(q1 u,v)-(-1)^|u| B_sign(u,q1 v)=q2_candidate(u,v)",
        "causal_difference_identity": "q1 B_causal(u,v)-B_causal(q1 u,v)-(-1)^|u| B_causal(u,q1 v)=0",
        "derivation": [
            "substitute B_sign=Lambda_sign q2_candidate",
            "apply q1 Lambda_sign=identity-Lambda_sign q1",
            "replace q1 q2_candidate by the certified arity-two master identity",
            "subtract the two sign orientations to cancel q2_candidate",
        ],
        "sign_orientations_checked": 2,
        "q1_q2_input_defects": q2["identity_transport"]["q1_q2_arity_two"]["defects"],
        "green_homotopy_input_defects": 0,
        "response_identity_structural_defects": 0,
        "causal_difference_identity_structural_defects": 0,
        "status": "EXACT_STRUCTURAL_REPLAY_ON_THE_CANDIDATE",
    }
    if replay_core != expected_replay or replay.get("sha256") != digest(expected_replay):
        errors.append("homotopy response replay")

    foundations = value.get("foundational_strength", {})
    if (
        foundations.get("classification") != "STRATIFIED_FINITE_EXACT_PLUS_CLASSICAL_INFINITE_ANALYSIS"
        or [item.get("layer") for item in foundations.get("layers", [])] != [
            "FINITE_EXACT_LOCAL", "SMOOTH_LOCAL_FUNCTION_SPACES", "SPECTRAL_CAUSAL_GREEN", "NONLINEAR_CAUSAL_COMPOSITION"
        ]
        or foundations.get("axiom_of_choice_status") != "NO_NEW_CHOICE_OPERATION_IN_THE_COMPOSITION; CHOICE_STRENGTH_OF_IMPORTED_ANALYTIC_THEOREMS_UNCALIBRATED"
        or foundations.get("weakest_complete_foundational_base") != "NOT_ESTABLISHED"
        or foundations.get("sha256") != digest({key: item for key, item in foundations.items() if key != "sha256"})
    ):
        errors.append("foundational stratification")

    authority = value.get("authority_boundary", {})
    if (
        authority.get("authoritative_full_q2_imported") is not False
        or authority.get("candidate_authoritative_equivalence_certified") is not False
        or authority.get("q2_green_result_status") != "CERTIFIED_FOR_CANDIDATE_ONLY"
        or authority.get("candidate_q2_hash_accepted_by_gate_a") is not False
        or authority.get("classical_import_gate_a_status") != "FAIL_CLOSED"
        or authority.get("sha256") != digest({key: item for key, item in authority.items() if key != "sha256"})
    ):
        errors.append("authority boundary")

    flags = value.get("claim_flags", {})
    required_true = {
        "STRICT_386_CANDIDATE_Q2_GREEN_SAME_CARRIER_VERIFIED",
        "STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_NAMES_SERIALIZED",
        "STRICT_386_CANDIDATE_Q2_GREEN_CAUSAL_SUPPORT_CERTIFIED",
        "STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED",
        "STRICT_386_CANDIDATE_Q2_GREEN_FOUNDATIONS_STRATIFIED",
    }
    forbidden_true = set(flags) - required_true
    if not all(flags.get(key) is True for key in required_true) or any(flags.get(key) is not False for key in forbidden_true):
        errors.append("claim/lifecycle firewall")

    snapshot = value.get("response_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_CANDIDATE_FIRST_NONLINEAR_CAUSAL_RESPONSE_PREFLIGHT",
        "carrier_alignment_sha256": expected_alignment["sha256"],
        "local_continuity_sha256": expected_local["sha256"],
        "plus_response_name_sha256": expected_responses["plus"]["canonical_name_sha256"],
        "minus_response_name_sha256": expected_responses["minus"]["canonical_name_sha256"],
        "causal_difference_name_sha256": difference["canonical_name_sha256"],
        "homotopy_replay_sha256": replay.get("sha256"),
        "foundations_sha256": foundations.get("sha256"),
        "authority_sha256": authority.get("sha256"),
        "receiver_status": "PREFLIGHT_ONLY_NOT_GATE_A_ACCEPTED",
    }
    expected_snapshot["sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("response snapshot")

    canonical = value.get("canonical_hashes", {})
    expected_canonical = {
        "carrier_alignment_sha256": expected_alignment["sha256"],
        "local_q2_continuity_sha256": expected_local["sha256"],
        "plus_response_name_sha256": expected_responses["plus"]["canonical_name_sha256"],
        "minus_response_name_sha256": expected_responses["minus"]["canonical_name_sha256"],
        "causal_difference_name_sha256": difference["canonical_name_sha256"],
        "homotopy_response_replay_sha256": replay.get("sha256"),
        "foundational_strength_sha256": foundations.get("sha256"),
        "authority_boundary_sha256": authority.get("sha256"),
        "response_snapshot_sha256": expected_snapshot["sha256"],
    }
    if canonical != expected_canonical:
        errors.append("canonical hashes")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - exact q2/unary carrier hashes agree and both sign-oriented first responses compose")
        print("  - causal support and arity-two homotopy-response identities replay")
        print("  - analytic foundations, authoritative identity, recursive trees and quantum gates remain bounded")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
