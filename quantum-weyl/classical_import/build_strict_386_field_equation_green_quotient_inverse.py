#!/usr/bin/env python3
"""Build the typed field-equation restriction of the strict Green homotopy."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.md"

BASIS = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
UNARY = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
RESPONSE = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
FORMAL = HERE / "certificates/STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1.json"
INPUTS = (
    (BASIS, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed graded carrier and pairing"),
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "exact graph q1 component jets and homotopy identity"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1", "represented retarded/advanced Green homotopies"),
    (UNARY, "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1", "accepted unary-causal common hash"),
    (RESPONSE, "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1", "candidate q2 response identity"),
    (FORMAL, "STRICT_386_POLARIZED_FORMAL_MOLLER_COEFFICIENTS_V1", "formal recursion and lambda-squared diagnostic"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("certificate_id") or value.get("schema")


def q1_degree_census(basis: Mapping[str, Any], graph: Mapping[str, Any]) -> tuple[dict[str, int], dict[str, Any]]:
    rows = basis["component_basis"]["rows"]
    degree_of = {row["index"]: row["degree"] for row in rows}
    degree_counts = {str(key): value for key, value in sorted(Counter(degree_of.values()).items())}
    edge_counts: Counter[tuple[int, int]] = Counter()
    table_ids: dict[tuple[int, int], set[str]] = defaultdict(set)
    defects = 0
    for table in graph["graph_q1_serialization"]["tables"]:
        for coefficient in table["coefficients"]:
            for entry in coefficient["entries"]:
                target, source = entry[:2]
                source_degree = degree_of[source]
                target_degree = degree_of[target]
                if target_degree != source_degree + 1:
                    defects += 1
                edge_counts[(source_degree, target_degree)] += 1
                table_ids[(source_degree, target_degree)].add(table["table_id"])
    edges = {
        f"{source}_to_{target}": {
            "source_degree": source,
            "target_degree": target,
            "nonzero_rational_jet_coefficients": edge_counts[(source, target)],
            "operator_tables": sorted(table_ids[(source, target)]),
        }
        for source, target in sorted(edge_counts)
    }
    return degree_counts, {"edges": edges, "degree_step_defects": defects}


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    basis, graph, green, unary, response, formal = (values[path] for path, _, _ in INPUTS)
    if not graph["formal_transport_replay"].get("graph_q1_squared_zero"):
        raise ValueError("exact q1 nilpotency unavailable")
    if not green["analytic_and_exact_replay"].get("full_graph_homotopy_identity_exact"):
        raise ValueError("full Green-homotopy identity unavailable")
    if not unary["claim_flags"].get("STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_ACCEPTED"):
        raise ValueError("unary-causal common snapshot unavailable")

    degree_counts, edge_census = q1_degree_census(basis, graph)
    expected_degrees = {"-2": 14, "-1": 63, "0": 116, "1": 116, "2": 63, "3": 14}
    if degree_counts != expected_degrees or edge_census["degree_step_defects"]:
        raise ValueError("graded carrier drift")
    edges = edge_census["edges"]
    if [edges[key]["nonzero_rational_jet_coefficients"] for key in ("-1_to_0", "0_to_1", "1_to_2")] != [425, 3264, 425]:
        raise ValueError("field-equation neighborhood drift")

    literature = {
        "id": "benini-musante-schenkel-2023",
        "citation": "Marco Benini, Giorgio Musante and Alexander Schenkel, Green hyperbolic complexes on Lorentzian manifolds, Communications in Mathematical Physics 405 (2024), Article 28.",
        "stable_url": "https://arxiv.org/abs/2207.04069",
        "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/2207.04069",
            "sha256": "8f43ffd1d381743001914e56facbc11afa38d24a0476cd05ab38e90435d2cecc",
        },
        "imported_statement": "Definitions 3.5 and the introductory specialization distinguish a retarded/advanced Green homotopy of a gauge complex, delta Lambda=id, from a two-sided Green operator for a nondegenerate two-term field equation. Gauge degeneracy prevents the ungauge-fixed equation operator from being Green hyperbolic.",
        "application_boundary": "The source supplies the homological type distinction. The Weyl-specific ranks, component counts, quotient identities and nonlinear gate are derived from repository certificates, not imported from the paper.",
    }
    literature["sha256"] = digest(literature)

    typed_complex = {
        "complex": "... -> C^-1 --R--> C^0 --K--> C^1 --N--> C^2 -> ...",
        "degree_counts": degree_counts,
        "field_space": {"symbol": "C^0", "rows": 116, "endpoint_metric_rows": 10},
        "equation_space": {"symbol": "C^1", "rows": 116, "endpoint_metric_antifield_rows": 10},
        "gauge_map": {
            "symbol": "R=q1|-1",
            "type": "C^-1 -> C^0",
            "nonzero_rational_jet_coefficients": edges["-1_to_0"]["nonzero_rational_jet_coefficients"],
            "nonzero": True,
        },
        "field_equation_operator": {
            "symbol": "K=q1|0",
            "type": "C^0 -> C^1",
            "nonzero_rational_jet_coefficients": edges["0_to_1"]["nonzero_rational_jet_coefficients"],
            "nonzero": True,
        },
        "noether_map": {
            "symbol": "N=q1|1",
            "type": "C^1 -> C^2",
            "nonzero_rational_jet_coefficients": edges["1_to_2"]["nonzero_rational_jet_coefficients"],
            "nonzero": True,
        },
        "exact_complex_identities": ["K R=0", "N K=0"],
        "q1_degree_step_defects": edge_census["degree_step_defects"],
        "basis_sha256": unary["accepted_objects"]["component_basis_sha256"],
        "graph_q1_sha256": unary["accepted_objects"]["graph_q1_sha256"],
    }
    typed_complex["sha256"] = digest(typed_complex)

    component = {
        "definition": "G_sigma=pr_C0 Lambda_graph,sigma inc_C1",
        "type": "Gamma_c^infinity(M,C^1) -> Gamma^infinity_Jsigma(M,C^0)",
        "neighbor_components": {
            "C_sigma": "pr_C-1 Lambda_graph,sigma inc_C0 : C^0 -> C^-1",
            "A_sigma": "pr_C1 Lambda_graph,sigma inc_C2 : C^2 -> C^1",
        },
        "orientations": {
            "plus": {
                "name": "retarded/future-supported",
                "full_green_name_sha256": unary["accepted_objects"]["plus_green_name_sha256"],
            },
            "minus": {
                "name": "advanced/past-supported",
                "full_green_name_sha256": unary["accepted_objects"]["minus_green_name_sha256"],
            },
        },
        "support": "Each component inherits supp G_sigma(s) subset J_sigma(supp s).",
        "component_bytes_flattened": False,
        "definition_mode": "CONTENT_ADDRESSED_DEGREE_RESTRICTION_OF_REPRESENTED_OPERATOR_NAME",
    }
    component["sha256"] = digest(component)

    identities = {
        "source_identity": "K G_sigma + A_sigma N = identity_C1",
        "field_identity": "G_sigma K + R C_sigma = identity_C0",
        "constrained_right_inverse": "For s in ker N, K G_sigma(s)=s.",
        "quotient_left_inverse": "For [phi] in C^0/im R, [G_sigma K(phi)]=[phi].",
        "induced_isomorphism": "K_bar:C^0/im R -> ker N has inverse [G_sigma] on each certified causal support class.",
        "proof": [
            "project q1 Lambda_sigma+Lambda_sigma q1=identity to total degree 1",
            "project the same identity to total degree 0",
            "use K R=0 and N K=0 from q1 squared zero",
            "restrict the degree-1 identity to ker N and the degree-0 identity modulo im R",
        ],
        "orientations_checked": 2,
        "structural_defects": 0,
    }
    identities["sha256"] = digest(identities)

    no_go = {
        "full_left_inverse_of_K_on_C0": False,
        "left_inverse_contradiction": "If L K=identity_C0, then R=L K R=0, contradicting the certified nonzero gauge map R.",
        "full_right_inverse_of_K_on_C1": False,
        "right_inverse_contradiction": "If K J=identity_C1, then N=N K J=0, contradicting the certified nonzero Noether map N.",
        "scope": "No two-sided Green operator exists for the ungauge-fixed K on the full declared field/equation spaces. This does not obstruct a gauge-fixed operator, the certified complex Green homotopy, or the quotient/constrained inverse above.",
        "nonzero_gauge_coefficients": typed_complex["gauge_map"]["nonzero_rational_jet_coefficients"],
        "nonzero_noether_coefficients": typed_complex["noether_map"]["nonzero_rational_jet_coefficients"],
        "status": "EXACT_GAUGE_COMPLEX_OBSTRUCTION",
    }
    no_go["sha256"] = digest(no_go)

    nonlinear = {
        "candidate_q2_type": "q2:C^0 x C^0 -> C^1 on ghost-number-zero inputs",
        "first_order_source": "s_1=(1/2)q2(x,x)",
        "first_order_cocycle": "q1(x)=0 and the arity-two identity imply N s_1=0",
        "first_order_solution": "K G_sigma(s_1)=s_1",
        "first_order_status": "TYPED_AND_CERTIFIED_FOR_THE_CANDIDATE",
        "all_order_criterion": "At every coupling order m, the assembled nonlinear source S_m must satisfy N S_m=0; then phi_m=-G_sigma(S_m) solves K phi_m=-S_m modulo gauge.",
        "lambda_squared_diagnostic": formal["bv_equation_diagnostic"]["order_lambda_squared_residual"],
        "lambda_squared_source_cocycle_certified": False,
        "corrected_promotion_gate": "SOURCE_CERTIFIED_Q2_Q3_HIGHER_L_INFINITY_IDENTITIES_AND_COEFFICIENTWISE_NONLINEAR_SOURCE_COCYCLE_CLOSURE",
        "full_ungauge_fixed_two_sided_inverse_required": False,
        "meaning": "The previous request for a full field-equation inverse was overstrong. The complex homotopy supplies exactly the constrained/quotient inverse needed once nonlinear source closure is proved; the remaining obstruction is theory identity, not unary causal inversion.",
    }
    nonlinear["sha256"] = digest(nonlinear)

    foundations = {
        "classification": "FINITE_EXACT_TYPED_RESTRICTION_OVER_IMPORTED_CLASSICAL_GREEN_HOMOTOPY",
        "finite_layer": "Degree partition, coefficient census, block identities, quotient proof and no-go contradiction are primitive-recursive finite checks over pinned exact tables.",
        "analytic_layer": "Existence, continuity and causal support of Lambda_sigma retain the classical smooth LF/Frechet and spectral assumptions of the accepted unary-causal snapshot.",
        "choice_operation_added": False,
        "quotient_requires_representative_selection": False,
        "reason": "The induced quotient map is defined by equivalence classes; no global gauge representative or complement is selected.",
        "weakest_complete_foundational_base": "NOT_ESTABLISHED",
    }
    foundations["sha256"] = digest(foundations)

    authority = {
        "typed_field_equation_green_component": True,
        "constrained_and_quotient_inverse": True,
        "full_ungauge_fixed_two_sided_inverse": False,
        "candidate_q2_only": True,
        "authoritative_full_q2_imported": False,
        "q3_or_higher_operations_imported": False,
        "all_order_nonlinear_source_closure": False,
        "formal_moller_map_for_weyl_bv_certified": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }
    authority["sha256"] = digest(authority)

    flags = {
        "STRICT_386_FIELD_EQUATION_GREEN_COMPONENT_TYPED": True,
        "STRICT_386_FIELD_EQUATION_CONSTRAINED_RIGHT_INVERSE_CERTIFIED": True,
        "STRICT_386_FIELD_EQUATION_QUOTIENT_LEFT_INVERSE_CERTIFIED": True,
        "STRICT_386_UNGAUGE_FIXED_TWO_SIDED_GREEN_INVERSE_OBSTRUCTED": True,
        "STRICT_386_UNGAUGE_FIXED_TWO_SIDED_GREEN_INVERSE_CONSTRUCTED": False,
        "STRICT_386_CANDIDATE_FIRST_ORDER_YANG_FELDMAN_SOURCE_TYPED": True,
        "STRICT_386_ALL_ORDER_NONLINEAR_SOURCE_CLOSURE_CERTIFIED": False,
        "STRICT_386_AUTHORITATIVE_FORMAL_MOLLER_MAP_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    snapshot = {
        "kind": "STRICT_386_TYPED_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_SNAPSHOT",
        "unary_causal_snapshot_sha256": unary["common_snapshot"]["sha256"],
        "typed_complex_sha256": typed_complex["sha256"],
        "green_component_sha256": component["sha256"],
        "restricted_identities_sha256": identities["sha256"],
        "full_inverse_obstruction_sha256": no_go["sha256"],
        "nonlinear_gate_sha256": nonlinear["sha256"],
        "foundations_sha256": foundations["sha256"],
        "authority_sha256": authority["sha256"],
        "receiver_status": "QUOTIENT_INVERSE_ACCEPTED_FULL_INVERSE_REJECTED_NONLINEAR_SOURCE_CLOSURE_OPEN",
    }
    snapshot["sha256"] = digest(snapshot)

    value = {
        "$schema": "../schema/strict-386-field-equation-green-quotient-inverse-v1.schema.json",
        "schema": "strict-386-field-equation-green-quotient-inverse-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-field-equation-green-quotient-inverse-v1.schema.json",
        "result_id": "STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1",
        "result_kind": "TYPED_BV_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_AND_FULL_INVERSE_NO_GO",
        "result_state": "CONSTRAINED_RIGHT_AND_QUOTIENT_LEFT_INVERSE_CERTIFIED_FULL_UNGAUGE_FIXED_INVERSE_OBSTRUCTED",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "f828b7b249d8ce762e4cabec6f2bae2ee0f381c6",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Does the accepted 386-row Green homotopy restrict to the field-equation inverse required by Yang-Feldman, and if not, what is the exact replacement?",
        "answer": "The degree-one-to-zero component G_sigma of each accepted Green homotopy is now typed exactly. It is a right inverse of the 386-row field-equation operator K on Noether-compatible sources and a left inverse modulo gauge. A two-sided inverse on the full ungauge-fixed field and equation spaces is impossible: the exact complex has nonzero gauge and Noether maps with K R=0 and N K=0. Consequently the correct nonlinear gate is not a stronger unary inverse. It is coefficientwise proof that every q2/q3/higher nonlinear source is N-closed. The candidate first-order source passes; the lambda-squared source remains undecided. Gate A, Hadamard and QME remain fail closed.",
        "scope": {
            "theory": "strict pure-Weyl unary BV complex with candidate q2 diagnostic",
            "background": "unit ultrastatic conformal cylinder R x S3",
            "carrier": "accepted 386-row unary-causal graph snapshot",
            "support": "compact source to retarded/advanced causal support",
        },
        "literature_context": literature,
        "typed_complex": typed_complex,
        "green_field_equation_component": component,
        "restricted_homotopy_identities": identities,
        "full_inverse_obstruction": no_go,
        "nonlinear_consequence": nonlinear,
        "foundational_strength": foundations,
        "authority_boundary": authority,
        "typed_inverse_snapshot": snapshot,
        "claim_flags": flags,
        "does_not_establish": [
            "a two-sided inverse of the ungauge-fixed field-equation operator on all fields and all equation sources",
            "a selected gauge fixing, global gauge slice or representative-selection operation",
            "flattened component bytes for the nonlocal Green kernel or an effective numerical solver",
            "that the stabilized q2 candidate is the authoritative nonlinear Weyl BV operation",
            "coefficientwise nonlinear source closure beyond first order",
            "vanishing or nonvanishing of the lambda-squared B(q2) residual",
            "q3 or higher source brackets or a Weyl-BV Maurer-Cartan/Moller theorem",
            "the authoritative twenty-export classical import Gate A",
            "a Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Retire the impossible full ungauge-fixed inverse target. Source-certify the authoritative q2 and any q3/higher brackets, then replay N S_m=0 coefficientwise, beginning with the displayed lambda-squared source. Only after nonlinear source closure and Gate-A identity may the formal response series be promoted toward a Weyl-BV Moller map.",
        "canonical_hashes": {
            "literature_context_sha256": literature["sha256"],
            "typed_complex_sha256": typed_complex["sha256"],
            "green_component_sha256": component["sha256"],
            "restricted_identities_sha256": identities["sha256"],
            "full_inverse_obstruction_sha256": no_go["sha256"],
            "nonlinear_consequence_sha256": nonlinear["sha256"],
            "foundational_strength_sha256": foundations["sha256"],
            "authority_boundary_sha256": authority["sha256"],
            "typed_inverse_snapshot_sha256": snapshot["sha256"],
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_field_equation_green_quotient_inverse.py",
            "checks": [
                "six dependency identities and content hashes",
                "independent degree partition and q1 coefficient census",
                "degreewise restriction of q Lambda+Lambda q=identity",
                "gauge and Noether no-go contradictions",
                "first-order source cocycle and all-order closure boundary",
                "foundational and Gate-A/Hadamard/QME firewalls",
                "nine canonical section digests",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    typed = value["typed_complex"]
    nonlinear = value["nonlinear_consequence"]
    return "\n".join([
        "# Strict 386-row field-equation Green quotient inverse", "", "## Outcome", "",
        value["answer"], "", "## The typed complex", "", "```text",
        typed["complex"],
        f"rows: C^0={typed['field_space']['rows']}, C^1={typed['equation_space']['rows']}",
        f"nonzero jet coefficients: R={typed['gauge_map']['nonzero_rational_jet_coefficients']}, K={typed['field_equation_operator']['nonzero_rational_jet_coefficients']}, N={typed['noether_map']['nonzero_rational_jet_coefficients']}",
        "```", "", "## What the Green homotopy actually gives", "", "```text",
        value["green_field_equation_component"]["definition"],
        value["restricted_homotopy_identities"]["source_identity"],
        value["restricted_homotopy_identities"]["field_identity"],
        "```", "",
        "Thus `G_sigma` is an exact right inverse on `ker N` and an exact left inverse on `C^0/im R`. No gauge representative is selected.", "",
        "## Why the stronger inverse is impossible", "",
        f"- {value['full_inverse_obstruction']['left_inverse_contradiction']}",
        f"- {value['full_inverse_obstruction']['right_inverse_contradiction']}", "",
        "This is the expected distinction between a Green operator for a nondegenerate two-term equation and a Green homotopy for a gauge complex, as formalized by Benini--Musante--Schenkel.", "",
        "## Consequence for the formal response", "", "```text",
        nonlinear["first_order_cocycle"], nonlinear["first_order_solution"],
        f"next: {nonlinear['all_order_criterion']}", "```", "",
        f"The lambda-squared diagnostic remains `{nonlinear['lambda_squared_diagnostic']}`. Its source-cocycle closure is not certified.", "",
        "## Reproduction", "", "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_field_equation_green_quotient_inverse.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_field_equation_green_quotient_inverse.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_field_equation_green_quotient_inverse.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_field_equation_green_quotient_inverse.py -v",
        "```", "", "## Boundaries", "",
        *[f"- This does not establish {item}." for item in value["does_not_establish"]], "",
    ])


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    if args.check:
        stale = []
        if not RESULT.is_file() or RESULT.read_bytes() != result_bytes:
            stale.append(str(RESULT.relative_to(ROOT)))
        if not REPORT.is_file() or REPORT.read_bytes() != report_bytes:
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print("STRICT_386_FIELD_EQUATION_GREEN_QUOTIENT_INVERSE_V1: CURRENT")
        return 0
    RESULT.write_bytes(result_bytes)
    REPORT.write_bytes(report_bytes)
    print(RESULT.relative_to(ROOT))
    print(REPORT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
