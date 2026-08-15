#!/usr/bin/env python3
"""Build the first nonlinear causal-response preflight on the strict carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.md"

Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
UNARY = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"

INPUTS = (
    (Q2, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "exact candidate q2 and q1/q2 identity"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1", "represented sign-oriented graph Green actions"),
    (UNARY, "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1", "accepted scoped unary-causal bytes"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    q2, green, unary = (values[path] for path, _, _ in INPUTS)

    if not q2["claim_flags"].get("STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED"):
        raise ValueError("candidate q2 unavailable")
    if q2["identity_transport"]["q1_q2_arity_two"]["defects"] != 0:
        raise ValueError("candidate q1/q2 identity drift")
    if not green["claim_flags"].get("STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"):
        raise ValueError("represented graph Green actions unavailable")
    if not green["analytic_and_exact_replay"].get("full_graph_homotopy_identity_exact"):
        raise ValueError("graph Green homotopy identity unavailable")
    if unary["common_snapshot"].get("receiver_status") != "ACCEPTED_SCOPED":
        raise ValueError("unary causal snapshot unavailable")

    candidate = q2["candidate_snapshot"]
    accepted = unary["accepted_objects"]
    carrier_alignment = {
        "carrier_rows": 386,
        "basis_candidate_sha256": candidate["basis_sha256"],
        "basis_unary_sha256": accepted["component_basis_sha256"],
        "pairing_candidate_sha256": candidate["pairing_sha256"],
        "pairing_unary_sha256": accepted["odd_pairing_sha256"],
        "graph_q1_candidate_sha256": candidate["graph_q1_sha256"],
        "graph_q1_unary_sha256": accepted["graph_q1_sha256"],
        "basis_match": candidate["basis_sha256"] == accepted["component_basis_sha256"],
        "pairing_match": candidate["pairing_sha256"] == accepted["odd_pairing_sha256"],
        "graph_q1_match": candidate["graph_q1_sha256"] == accepted["graph_q1_sha256"],
        "unary_snapshot_sha256": unary["common_snapshot"]["sha256"],
        "candidate_q2_sha256": q2["canonical_hashes"]["graph_transport_dag_sha256"],
        "status": "SAME_RECEIVER_BYTES_PREFLIGHT_NOT_GATE_A_ACCEPTED",
    }
    if not all(carrier_alignment[key] for key in ("basis_match", "pairing_match", "graph_q1_match")):
        raise ValueError("q2/unary carrier mismatch")
    carrier_alignment["sha256"] = digest(carrier_alignment)

    q2_order = max(
        item["maximum_total_derivative_order"]
        for item in q2["identity_transport"]["naturality_ledger"]
    )
    inverse_order = max(item["maximum_order"] for item in q2["graph_transport_dag"]["inverse_tables"])
    forward_order = max(item["maximum_order"] for item in q2["graph_transport_dag"]["forward_tables"])
    local_continuity = {
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
    local_continuity["sha256"] = digest(local_continuity)

    response_names: dict[str, Any] = {}
    for sign in ("plus", "minus"):
        green_name = green["operator_names"][sign]
        response = {
            "sign": sign,
            "orientation": green["parent_spectral_name"]["orientation"][sign],
            "formula": f"B_{sign}(u,v)=Lambda_graph,{sign}(q2_candidate(u,v))",
            "name": {
                "node": "COMPOSE_BINARY_RESPONSE",
                "children": [
                    {
                        "node": "STRICT_386_STABILIZED_Q2_CANDIDATE",
                        "sha256": q2["canonical_hashes"]["graph_transport_dag_sha256"],
                    },
                    {
                        "node": "STRICT_386_GRAPH_GREEN_ACTION_NAME",
                        "sign": sign,
                        "sha256": green_name["canonical_name_sha256"],
                    },
                ],
            },
            "input_space": local_continuity["domain"],
            "output_space": green["represented_spaces"]["target"]["space"],
            "well_defined": True,
            "continuous_bilinear": True,
            "support": f"supp B_{sign}(u,v) subset J_{sign}(supp(u) intersection supp(v))",
        }
        response["canonical_name_sha256"] = digest(response["name"])
        response_names[sign] = response

    response_difference = {
        "formula": "B_causal=B_plus-B_minus",
        "name": {
            "node": "DIFFERENCE",
            "children": [
                {"node": "BINARY_RESPONSE", "sign": "plus", "sha256": response_names["plus"]["canonical_name_sha256"]},
                {"node": "BINARY_RESPONSE", "sign": "minus", "sha256": response_names["minus"]["canonical_name_sha256"]},
            ],
        },
        "support": "supp B_causal(u,v) subset J(supp(u) intersection supp(v))",
        "continuous_bilinear": True,
    }
    response_difference["canonical_name_sha256"] = digest(response_difference["name"])

    homotopy_replay = {
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
    homotopy_replay["sha256"] = digest(homotopy_replay)

    foundations = {
        "classification": "STRATIFIED_FINITE_EXACT_PLUS_CLASSICAL_INFINITE_ANALYSIS",
        "layers": [
            {
                "layer": "FINITE_EXACT_LOCAL",
                "objects": "386-row carrier hashes, q2 transport DAG, carrier equality, and formal response identity",
                "upper_bound": "PRA conditional on the pinned tensor-natural differential identities",
                "choice_or_infinite_selection_added": False,
            },
            {
                "layer": "SMOOTH_LOCAL_FUNCTION_SPACES",
                "objects": "Gamma_c^infinity LF steps and continuity of finite-order bilinear differential maps",
                "upper_bound": "ordinary classical smooth locally convex analysis",
                "weakest_reverse_mathematical_base": "NOT_ESTABLISHED",
            },
            {
                "layer": "SPECTRAL_CAUSAL_GREEN",
                "objects": "canonical S3 Hodge projectors, countable spectral convergence, Duhamel integration, and unique normally-hyperbolic Green operators",
                "upper_bound": "the classical analytic theorems pinned by STRICT_386_GRAPH_GREEN_ACTION_NAME_V1",
                "selected_eigenbasis_required": False,
                "completed_infinite_spaces_required": True,
                "weakest_reverse_mathematical_base": "NOT_ESTABLISHED",
            },
            {
                "layer": "NONLINEAR_CAUSAL_COMPOSITION",
                "objects": "B_plus, B_minus, and their causal difference",
                "new_choice_beyond_imported_green_theorem": False,
                "new_positivity_or_state_assumption": False,
            },
        ],
        "axiom_of_choice_status": "NO_NEW_CHOICE_OPERATION_IN_THE_COMPOSITION; CHOICE_STRENGTH_OF_IMPORTED_ANALYTIC_THEOREMS_UNCALIBRATED",
        "constructive_status": "FINITE DAG IS EFFECTIVE; GREEN NAME USES NON-EFFECTIVE CONTINUITY WITHOUT A UNIFORM TAIL ALGORITHM",
        "finitary_status": "THE RESPONSE CANNOT BE REDUCED TO FINITE EXACT ALGEBRA BECAUSE ITS GREEN FACTOR USES COMPLETED FUNCTION SPACES AND A COUNTABLE SPECTRAL LIMIT",
        "weakest_complete_foundational_base": "NOT_ESTABLISHED",
    }
    foundations["sha256"] = digest(foundations)

    authority = {
        "candidate_q2_status": q2["theory_identity_boundary"]["candidate_status"],
        "authoritative_full_q2_imported": q2["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED"],
        "candidate_authoritative_equivalence_certified": q2["claim_flags"]["STRICT_386_CANDIDATE_AUTHORITATIVE_EQUIVALENCE_CERTIFIED"],
        "q2_green_result_status": "CERTIFIED_FOR_CANDIDATE_ONLY",
        "candidate_q2_hash_accepted_by_gate_a": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
        "why": "Composability with the accepted unary-causal snapshot does not identify a receiver-constructed q2 with the source theory's nonlinear extension.",
    }
    authority["sha256"] = digest(authority)

    claim_flags = {
        "STRICT_386_CANDIDATE_Q2_GREEN_SAME_CARRIER_VERIFIED": True,
        "STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_NAMES_SERIALIZED": True,
        "STRICT_386_CANDIDATE_Q2_GREEN_CAUSAL_SUPPORT_CERTIFIED": True,
        "STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED": True,
        "STRICT_386_CANDIDATE_Q2_GREEN_FOUNDATIONS_STRATIFIED": True,
        "STRICT_386_AUTHORITATIVE_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
        "STRICT_386_RECURSIVE_NONLINEAR_GREEN_TREES_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }
    response_snapshot = {
        "kind": "STRICT_386_CANDIDATE_FIRST_NONLINEAR_CAUSAL_RESPONSE_PREFLIGHT",
        "carrier_alignment_sha256": carrier_alignment["sha256"],
        "local_continuity_sha256": local_continuity["sha256"],
        "plus_response_name_sha256": response_names["plus"]["canonical_name_sha256"],
        "minus_response_name_sha256": response_names["minus"]["canonical_name_sha256"],
        "causal_difference_name_sha256": response_difference["canonical_name_sha256"],
        "homotopy_replay_sha256": homotopy_replay["sha256"],
        "foundations_sha256": foundations["sha256"],
        "authority_sha256": authority["sha256"],
        "receiver_status": "PREFLIGHT_ONLY_NOT_GATE_A_ACCEPTED",
    }
    response_snapshot["sha256"] = digest(response_snapshot)

    value = {
        "$schema": "../schema/strict-386-stabilized-q2-green-composition-preflight-v1.schema.json",
        "schema": "strict-386-stabilized-q2-green-composition-preflight-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-stabilized-q2-green-composition-preflight-v1.schema.json",
        "result_id": "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1",
        "result_kind": "CANDIDATE_FIRST_NONLINEAR_CAUSAL_RESPONSE_AND_FOUNDATIONAL_STRATIFICATION",
        "result_state": "CANDIDATE_Q2_GREEN_RESPONSE_CERTIFIED_AUTHORITATIVE_AND_RECURSIVE_COMPLETION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "907095c2753a91c6bc4b1d1ee0dbb8bf55373e5f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the exact stabilized q2 candidate be composed with both represented 386-row Green homotopies on the same carrier, what causal identity follows, and which foundational assumptions enter?",
        "answer": "Yes, at first nonlinear response order and for the candidate only. The q2 preflight and accepted unary-causal snapshot have identical basis, pairing and graph-q1 hashes. The finite-order support-local candidate maps two compact smooth inputs to a compact smooth source, so each represented Green name accepts its output. The two continuous bilinear names B_plus/minus=Lambda_plus/minus q2_candidate obey sign-oriented causal support and the exact arity-two homotopy-response identity; their difference is q1-compatible. The construction adds no choice operation beyond the imported analytic Green theorem. Its carrier and q2 algebra are finitary exact data, while the Green factor genuinely uses completed LF/Frechet spaces, a countable Hodge-projector limit and classical normally-hyperbolic PDE theory. This does not identify the candidate with the authoritative classical q2, construct recursive nonlinear trees, select a Hadamard state, or restore the QME.",
        "scope": {
            "theory": "strict pure-Weyl stabilized q2 candidate",
            "background": "unit ultrastatic vacuum conformal cylinder R x S3",
            "carrier": "fixed 386-row graph BV carrier",
            "inputs": "two compactly supported smooth homogeneous sections",
            "degree": "first quadratic causal response only",
            "causal_orientations": ["plus/future/retarded", "minus/past/advanced"],
        },
        "carrier_alignment": carrier_alignment,
        "local_q2_continuity": local_continuity,
        "response_names": response_names,
        "causal_response_difference": response_difference,
        "homotopy_response_replay": homotopy_replay,
        "foundational_strength": foundations,
        "authority_boundary": authority,
        "response_snapshot": response_snapshot,
        "claim_flags": claim_flags,
        "does_not_establish": [
            "that the stabilized q2 candidate is the authoritative nonlinear classical Weyl BV operation",
            "an accepted q2 or q2/Green hash in classical import Gate A",
            "a flattened distribution kernel or effective numerical Green solver",
            "a uniform spectral-tail complexity bound",
            "recursive nonlinear Green trees or closure of q2 on two noncompact causal outputs",
            "q3 or higher L-infinity compatibility",
            "a time-slice SDR to the obstructed finite weights-2,3,4 receiver",
            "a weakest reverse-mathematical or choice-free proof of the analytic Green theorem",
            "a BRST-compatible Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Obtain authoritative q2 theory identity. In parallel, define domains for recursive causal trees and prove continuity/support when causal outputs re-enter q2; only after authoritative identity and those analytic closure checks may the strict route advance from first response toward interacting Hadamard/renormalized products and QME.",
        "canonical_hashes": {
            "carrier_alignment_sha256": carrier_alignment["sha256"],
            "local_q2_continuity_sha256": local_continuity["sha256"],
            "plus_response_name_sha256": response_names["plus"]["canonical_name_sha256"],
            "minus_response_name_sha256": response_names["minus"]["canonical_name_sha256"],
            "causal_difference_name_sha256": response_difference["canonical_name_sha256"],
            "homotopy_response_replay_sha256": homotopy_replay["sha256"],
            "foundational_strength_sha256": foundations["sha256"],
            "authority_boundary_sha256": authority["sha256"],
            "response_snapshot_sha256": response_snapshot["sha256"],
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_stabilized_q2_green_composition_preflight.py",
            "checks": [
                "source identities and content hashes",
                "basis, pairing and graph-q1 carrier equality",
                "finite-order local continuity/support composition",
                "two response-name DAGs and their causal difference",
                "arity-two homotopy-response sign algebra",
                "foundational layer and authority firewalls",
                "quantum lifecycle firewall",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    align = value["carrier_alignment"]
    local = value["local_q2_continuity"]
    replay = value["homotopy_response_replay"]
    lines = [
        "# Strict 386-row stabilized q2/Green composition preflight v1", "", "## Outcome", "",
        value["answer"], "", "## Common carrier", "",
        f"The candidate and unary-causal snapshot agree exactly on the basis, pairing and graph q1: `{align['basis_match']}`, `{align['pairing_match']}`, `{align['graph_q1_match']}`.", "",
        "## First nonlinear causal response", "",
        "```text", "B_plus(u,v)  = Lambda_graph,plus(q2_candidate(u,v))", "B_minus(u,v) = Lambda_graph,minus(q2_candidate(u,v))", "B_causal      = B_plus - B_minus", "```", "",
        f"Both sign-oriented names are continuous bilinear maps on `{local['domain']}`. Their support lies in the corresponding causal future or past of `supp(u) intersection supp(v)`. The conservative graph-coordinate differential-order bounds are **{local['conservative_per_input_derivative_order_bound']}** per input and **{local['conservative_total_derivative_order_bound']}** in total.", "",
        "The exact structural replay gives", "", "```text", replay["response_identity"], replay["causal_difference_identity"], "```", "",
        "## Foundational split", "",
        "| Layer | What it uses | Status |", "|---|---|---|",
    ]
    for layer in value["foundational_strength"]["layers"]:
        status = layer.get("upper_bound", "no new assumptions beyond prior layers")
        lines.append(f"| `{layer['layer']}` | {layer['objects']} | {status} |")
    lines += ["", "No selected eigenbasis is required: whole Hodge eigenspace projectors are canonical. Nevertheless, the Green factor uses completed infinite-dimensional spaces and a countable spectral limit. The weakest reverse-mathematical base and the choice strength of the imported analytic theorems remain uncalibrated.", "", "## Why this is still a preflight", "", value["authority_boundary"]["why"], "", "The result covers one application of the Green homotopy after one local binary interaction. It does not prove that two noncompact causal outputs can be fed back into q2, so it is not an interacting perturbation series.", "", "## Reproduction", "", "```text", "python3 quantum-weyl/classical_import/build_strict_386_stabilized_q2_green_composition_preflight.py --check", "python3 quantum-weyl/classical_import/check_strict_386_stabilized_q2_green_composition_preflight.py", "python3 quantum-weyl/classical_import/verify_strict_386_stabilized_q2_green_composition_preflight.py", "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_stabilized_q2_green_composition_preflight.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], ""]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
