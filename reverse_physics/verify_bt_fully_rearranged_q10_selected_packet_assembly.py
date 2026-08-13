#!/usr/bin/env python3
"""Independent verifier for the selected finite-time BT q10 assembly."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-q10-selected-packet-assembly-v1.schema.json"
)
SOURCE_COMMIT = "5b286625d63840c31f3051f8ceda54453acc8ffe"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-q10-selected-packet-assembly.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-q10-selected-packet-assembly-DONE-5b286625.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_FRAME_TYPED_LOOP_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json",
]


def load(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def sha256(path):
    digest = hashlib.sha256()
    try:
        with open(os.path.join(ROOT, path), "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError:
        return ""
    return digest.hexdigest()


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def independent_dressing_fixture():
    """Use exponential coefficients, not the producer's Cayley matrix."""
    r1 = [[Fraction(0), Fraction(2)], [Fraction(-2), Fraction(0)]]
    r2 = [[Fraction(-2), Fraction(0)], [Fraction(0), Fraction(-2)]]
    v4 = [Fraction(2), Fraction(-1)]

    def transpose_mv(matrix, vector):
        return [sum(matrix[j][i] * vector[j] for j in range(2)) for i in range(2)]

    y5 = transpose_mv(r1, v4)
    dressing_y6 = transpose_mv(r2, v4)
    cancellation = dot(y5, y5) + 2 * dot(v4, dressing_y6)
    second_order_unitarity = [
        [r2[i][j] + r2[j][i] + sum(r1[k][i] * r1[k][j] for k in range(2)) for j in range(2)]
        for i in range(2)
    ]
    return cancellation, second_order_unitarity, y5


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["strict_schema"] = bool(schema) and not list(Draft202012Validator(schema).iter_errors(certificate))
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1"
    checks["schema"] = certificate.get("schema") == SCHEMA_REL
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == SOURCE_COMMIT
    checks["input_paths"] = [row.get("path") for row in inputs] == INPUTS
    checks["input_hashes"] = len(inputs) == len(INPUTS) and all(
        row.get("sha256") == sha256(path) for row, path in zip(inputs, INPUTS)
    )
    checks["producer_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_q10_selected_packet_assembly.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_q10_selected_packet_assembly.py"
    )
    checks["predecessors"] = all(load(path).get("checks", {}).get("ok") for path in INPUTS[3:])

    expansion = certificate.get("fixed_auxiliary_expansion", {})
    checks["coupling"] = expansion.get("coupling") == "g=lambda^2"
    checks["even_amplitude"] = expansion.get("restricted_amplitude") == "A_YX=P_Y*(U_T-I)*P_X=g^2*T4,T+g^3*T6,T+O(g^4)=lambda^4*T4,T+lambda^6*T6,T+O(lambda^8)"
    checks["fixed_y5"] = expansion.get("fixed_y5") == "0"
    checks["q10_formula"] = expansion.get("q10") == "q10[F]=2*Re<T4,T F,T6,T F>"
    checks["expansion_status"] = expansion.get("status") == "FIXED_AUXILIARY_Q10_REDUCES_TO_TREE_LOOP_INTERFERENCE"

    exhaustion = certificate.get("order_g3_exhaustion", {})
    checks["external_support"] = "202" in exhaustion.get("external_disconnected", "")
    checks["forward_support"] = exhaustion.get("forward_survival", "").startswith("P_Y*P_X=0")
    checks["vacuum_order"] = all(term in exhaustion.get("vacuum", "") for term in ("g^1", "g^2", "normal-ordered"))
    checks["topologies"] = exhaustion.get("normal_ordered_topologies") == ["triangle", "bubble_with_bridge"]
    checks["complete_T6"] = exhaustion.get("complete_kernel") == "T6,T=T6,triangle,T+T6,bb,T"
    checks["exhaustion_status"] = exhaustion.get("status") == "NO_MISSING_SOURCE_DETECTOR_VACUUM_SURVIVAL_OR_GRAPH_TERM_AT_SELECTED_Q10"

    dressing = certificate.get("similarity_dressing_cancellation", {})
    fixture = dressing.get("exact_fixture", {})
    checks["selected_similarity"] = dressing.get("selected_scalar_identity", "").startswith("tr(P_phi*E_phi)=tr(P_u*E_BT)")
    checks["general_dressing_relation"] = all(term in dressing.get("general_relation", "") for term in ("R^dagger R=1", "||r1^dagger*y4||^2", "r2^dagger*y4"))
    checks["producer_fixture"] = (
        fixture.get("pulled_y5") == ["-2", "1"]
        and fixture.get("y5_norm") == "5"
        and fixture.get("second_order_dressing_cross") == "-5"
        and fixture.get("dressing_sum") == "0"
        and fixture.get("fixed_q10") == fixture.get("pulled_q10") == "2"
    )
    cancellation, unitary_second_order, independent_y5 = independent_dressing_fixture()
    checks["independent_nonzero_y5"] = independent_y5 != [Fraction(0), Fraction(0)]
    checks["independent_second_order_unitarity"] = unitary_second_order == [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    checks["independent_dressing_cancellation"] = cancellation == 0
    checks["dressing_scope"] = "not the standard shift-invariant Eq. (19) projector" in dressing.get("scope", "")
    checks["dressing_status"] = dressing.get("status") == "ALL_SELECTED_RT_DRESSING_CANCELS_FROM_Q10"

    functional = certificate.get("assembled_packet_functional", {})
    checks["kernel_sum"] = functional.get("complete_T6") == "T6,T=T6,triangle,T+T6,bb,T"
    checks["functional_formula"] = all(term in functional.get("q10", "") for term in ("16*sum_C", "8*sum_P", "4/(16*pi^2)", "2*Re"))
    checks["common_packet"] = "same rational fully rearranged center" in functional.get("packet_domain", "")
    checks["bounded"] = "Hilbert-Schmidt" in functional.get("boundedness", "") and "finite" in functional.get("boundedness", "")
    checks["value_boundary"] = functional.get("value") == "EXACT_PACKET_FUNCTIONAL_NOT_REDUCED_TO_A_PACKET_INDEPENDENT_NUMBER"
    checks["sign_boundary"] = functional.get("sign") == "NOT_DETERMINED"
    checks["functional_status"] = functional.get("status") == "COMPLETE_SELECTED_PACKET_Q10_FUNCTIONAL_COMPUTED"

    born = certificate.get("common_Born_identity", {})
    checks["Born_effect"] = born.get("effect") == "T4,T^sharp*T6,T+T6,T^sharp*T4,T=T4,T^*T6,T+T6,T^*T4,T"
    checks["Born_conclusion"] = born.get("conclusion") == "q10_public[F]=q10_Hilbert[F] on the selected positive packet carrier"
    checks["Born_status"] = born.get("status") == "COMPLETE_Q10_IS_COMMON_BORN"

    rg = certificate.get("renormalization_group", {})
    checks["bubble_scale"] = rg.get("bubble_scale_derivative") == "partial_log(mu)T6,bb,T=[5/(4*pi^2)]*T4,T"
    checks["q10_scale"] = rg.get("q10_scale_derivative") == "partial_log(mu)q10=[5/(2*pi^2)]*q8"
    checks["beta"] = rg.get("beta") == "partial_log(mu)lambda=-5*lambda^3/(16*pi^2)"
    checks["RG_arithmetic"] = 2 * Fraction(5, 4) == Fraction(5, 2) and 8 * Fraction(-5, 16) == Fraction(-5, 2)
    checks["RG_cancellation"] = rg.get("cancellation") == "partial_log(mu)[lambda^8*q8+lambda^10*q10]=O(lambda^12)"
    checks["scheme_boundary"] = "MSbar coordinate" in rg.get("finite_scheme_rule", "")
    checks["RG_status"] = rg.get("status") == "ORDER_LAMBDA10_PACKET_PROBABILITY_IS_RG_INVARIANT"

    disposition = certificate.get("disposition", {})
    checks["coefficient_disposition"] = disposition.get("selected_finite_time_q10") == "COEFFICIENT_COMPUTED_AS_EXACT_PACKET_FUNCTIONAL"
    checks["common_Born_disposition"] = disposition.get("selected_q10_common_Born") == "PROVED"
    checks["not_promoted"] = (
        disposition.get("selected_q10_sign") == "NOT_DETERMINED"
        and disposition.get("standard_shift_invariant_projector") == "NOT_CONSTRUCTED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("all_time_scattering") == "NOT_CONSTRUCTED"
        and disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 11 and "literature priority" in certificate.get("does_not_establish", [])
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("shift-invariant", "order-lambda^2", "q10", "Eq. (19)", "Lorentzian"))
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-q10-selected-packet-assembly.md"

    producer_names = {
        "inputs_are_content_pinned", "work_item_is_active", "done_event_matches", "seven_predecessors_pass",
        "public_auxiliary_interaction_has_lambda_squared_only", "direct_auxiliary_has_no_cubic_vertex",
        "fixed_amplitude_is_even_in_lambda", "q8_is_a4_squared", "fixed_y5_and_q9_are_zero",
        "q10_is_two_a4_a6", "all_external_disconnected_partitions_are_off_support",
        "fully_rearranged_identity_and_forward_are_zero", "normal_ordered_survivors_are_triangle_and_bubble_bridge",
        "one_vertex_vacuum_factor_is_zero_by_normal_ordering", "vacuum_factors_cannot_enter_amplitude_order_g3",
        "triangle_is_finite_time_computed", "bubble_bridge_is_finite_time_computed", "connected_T6_is_complete",
        "common_packet_intersection_is_nonempty", "T4_and_T6_packet_maps_are_Hilbert_Schmidt",
        "Rt_is_formally_two_sided", "selected_scalar_trace_is_similarity_invariant",
        "similarity_fixture_is_exactly_orthogonal", "similarity_fixture_has_nonzero_apparent_y5",
        "y5_norm_cancels_second_order_dressing", "pulled_and_fixed_q10_agree",
        "triangle_interference_is_common_Born", "bubble_interference_is_common_Born",
        "assembled_q10_is_common_Born", "explicit_scale_derivative_is_five_over_two_pi2_q8",
        "leading_running_is_minus_five_over_two_pi2_q8", "order_lambda10_scale_terms_cancel",
        "sign_and_Eq19_are_not_promoted",
    }
    recorded = certificate.get("checks", {})
    checks["producer_checks"] = (
        recorded.get("total") == 33 and recorded.get("passed") == 33 and recorded.get("ok") is True
        and recorded.get("failures") == [] and set(recorded.get("details", {})) == producer_names
        and all(recorded.get("details", {}).values())
    )
    return checks


def main():
    checks = verify(load(CERT_REL))
    failures = [name for name, passed in checks.items() if not passed]
    print(f"{len(checks) - len(failures)}/{len(checks)} checks passed")
    if failures:
        print("failures: " + ", ".join(failures))
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
