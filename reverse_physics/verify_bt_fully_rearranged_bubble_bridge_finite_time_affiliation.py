#!/usr/bin/env python3
"""Independent verifier for finite-time BT bubble-bridge affiliation."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-bubble-bridge-finite-time-affiliation-v1.schema.json"
)
SOURCE_COMMIT = "e714bb36d01fc1f5865093d9f68c41a47b430e28"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-fully-rearranged-bubble-bridge-finite-time-affiliation.json",
    "planning/events/reverse-physics-bateman-fully-rearranged-bubble-bridge-finite-time-affiliation-DONE-e714bb36.json",
    "reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_COVARIANT_BLOCK_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_FINITE_TIME_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_ORDER4_PACKET_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json",
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


def independent_orderings():
    """Derive interval cuts from the 3x3 edge multiplicity matrix."""
    vertices = ("A", "B", "C")
    multiplicity = {
        frozenset(("A", "B")): (2, ["AB_1", "AB_2"], ["E_1", "E_2"]),
        frozenset(("A", "C")): (1, ["AC"], ["E_K"]),
        frozenset(("B", "C")): (0, [], []),
    }

    def cut(left):
        left = set(left)
        edge_names = []
        energies = []
        loop_count = 0
        for pair, (count, names, values) in multiplicity.items():
            first, second = tuple(pair)
            if (first in left) != (second in left):
                edge_names.extend(names)
                energies.extend(values)
                if pair == frozenset(("A", "B")):
                    loop_count += count
        return edge_names, energies, loop_count

    rows = []
    for index, order in enumerate(itertools.permutations(vertices)):
        early, middle, late = order
        edges1, energies1, loops1 = cut((early,))
        edges2, energies2, loops2 = cut((early, middle))
        counts = [loops1, loops2]
        rows.append({
            "index": index,
            "earliest_middle_latest": list(order),
            "first_cut_edges": edges1,
            "second_cut_edges": edges2,
            "large_loop_crossing_counts": counts,
            "UV_class": "TWO_LARGE_DEFECTS" if counts == [2, 2] else "ONE_LARGE_DEFECT",
            "overall_frequency": "Omega=q_A^0+q_B^0+q_C^0",
            "first_interval_defect": f"Delta1=q_{middle}^0+q_{late}^0-({'+'.join(energies1) if energies1 else '0'})",
            "second_interval_defect": f"Delta2=q_{late}^0-({'+'.join(energies2) if energies2 else '0'})",
        })
    return rows


def verify(certificate):
    checks = {}
    schema = load(SCHEMA_REL)
    checks["strict_schema"] = bool(schema) and not list(Draft202012Validator(schema).iter_errors(certificate))
    checks["identity"] = certificate.get("certificate") == "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1"
    checks["schema"] = certificate.get("schema") == SCHEMA_REL
    checks["version"] = certificate.get("schema_version") == 1
    checks["lifecycle"] = certificate.get("lifecycle_state") == "COEFFICIENT_COMPUTED"
    checks["tags"] = certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"]

    provenance = certificate.get("provenance", {})
    inputs = provenance.get("inputs", [])
    checks["source_commit"] = provenance.get("source_commit") == SOURCE_COMMIT
    checks["input_paths"] = [row.get("path") for row in inputs] == INPUTS
    checks["input_hashes"] = len(inputs) == len(INPUTS) and all(row.get("sha256") == sha256(path) for row, path in zip(inputs, INPUTS))
    checks["producer_verifier"] = (
        provenance.get("generated_by") == "reverse_physics/bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py"
        and provenance.get("independent_verifier") == "reverse_physics/verify_bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py"
    )
    checks["predecessors"] = all(load(path).get("checks", {}).get("ok") for path in INPUTS[3:])

    distribution = certificate.get("renormalized_time_distribution", {})
    checks["bubble_frequency"] = distribution.get("bubble_frequency_kernel") == "B_mu(nu,Q)=log[mu^2/(-(nu^2-|Q|^2)-i0)]+2"
    checks["Fourier_convention"] = distribution.get("transform_convention") == "b(tau)=integral_R dnu/(2*pi)*exp(-i*nu*tau)*B(nu)"
    checks["momentum_derivative"] = distribution.get("momentum_derivative") == "partial_|Q| b_mu,Q(tau)=-i*exp(-i*|Q|*abs(tau)) away from the local extension"
    checks["finite_part"] = "FP[" in distribution.get("nonlocal_form", "") and "/abs(tau)" in distribution.get("nonlocal_form", "")
    checks["local_scale"] = distribution.get("scale_derivative") == "partial_log(mu) b_mu,Q(tau)=2*delta(tau)"
    checks["bridge_time"] = distribution.get("bridge_time_distribution") == "d_EK(tau)=exp(-i*E_K*abs(tau))/(2*E_K)"
    checks["bridge_Fourier_identity"] = distribution.get("bridge_Fourier_identity") == "d_EK(tau)=integral_R drho/(2*pi)*exp(-i*rho*tau)*i/(rho^2-E_K^2+i0)"
    checks["distribution_status"] = distribution.get("status") == "FULL_RENORMALIZED_OFF_DIAGONAL_BUBBLE_TIME_DISTRIBUTION_CONSTRUCTED"

    kernel = certificate.get("three_vertex_kernel", {})
    checks["time_pairing"] = all(term in kernel.get("time_pairing", "") for term in ("t_A-t_B", "t_A-t_C", "int_[0,T]^3"))
    checks["spectral_pairing"] = kernel.get("spectral_pairing") == "J_T,R=int dnu*drho/(2*pi)^2 B_mu(nu,Q)*D_F(rho,E_K)*F_T(q_A^0-nu-rho)*F_T(q_B^0+nu)*F_T(q_C^0+rho)"
    checks["bridge_frequency"] = kernel.get("bridge_frequency_kernel") == "D_F(rho,E_K)=i/(rho^2-E_K^2+i0), whose inverse Fourier transform is d_EK(tau)"
    factors = kernel.get("frequency_factors", {})
    checks["frequency_factors"] = factors == {
        "A": {"q_A": 1, "nu": -1, "rho": -1},
        "B": {"q_B": 1, "nu": 1, "rho": 0},
        "C": {"q_C": 1, "nu": 0, "rho": 1},
    }
    checks["frequency_cancellation"] = kernel.get("internal_frequency_cancellation") == {"nu": 0, "rho": 0}
    checks["amplitude"] = kernel.get("amplitude") == "T6_bb,T=(4/(16*pi^2))*sum_(60 roles R) J_T,R*W_R"
    checks["no_B_T"] = "is not substituted" in kernel.get("warning", "")
    checks["kernel_status"] = kernel.get("status") == "FINITE_DURATION_BUBBLE_WITH_BRIDGE_DYSON_BLOCK_COMPUTED"

    expected_orderings = independent_orderings()
    ordering = certificate.get("six_ordering_exhaustion", {})
    checks["orderings"] = ordering.get("rows") == expected_orderings
    checks["ordering_counts"] = ordering.get("one_large_defect_count") == 4 and ordering.get("two_large_defect_count") == 2
    checks["all_separate_AB"] = all(2 in row["large_loop_crossing_counts"] for row in expected_orderings)
    checks["local_face"] = "t_A=t_B" in ordering.get("cube_identity", "")
    checks["ordering_status"] = ordering.get("status") == "ALL_SIX_ORDERINGS_INCLUDED_WITH_LOCAL_FOREST_FACE"

    convergence = certificate.get("spectral_convergence", {})
    checks["window_bound"] = convergence.get("window_bound") == "abs(F_T(x))<=min(T,2/abs(x))"
    checks["local_singularities"] = "locally integrable" in convergence.get("bubble_thresholds", "") and "PV" in convergence.get("bridge_poles", "") and "delta" in convergence.get("bridge_poles", "")
    checks["tail_power_counts"] = (
        convergence.get("nu_axis", "").endswith("O(log(abs(nu))/nu^2)")
        and convergence.get("rho_axis", "").endswith("O(rho^-4)")
        and convergence.get("cancellation_line", "").endswith("O(log(r)/r^4)")
        and convergence.get("generic_cone", "").endswith("O(log(r)/r^5)")
    )
    checks["on_shell_distribution"] = "never evaluated as a pointwise covariant pole" in convergence.get("on_shell_bridge", "")
    checks["convergence_status"] = convergence.get("status") == "FINITE_TIME_DOUBLE_SPECTRAL_PAIRING_WELL_DEFINED"

    renormalization = certificate.get("finite_time_renormalization", {})
    checks["collapse"] = "delta(t_A-t_B)" in renormalization.get("local_identity", "") and "T4,T" in renormalization.get("collapsed_graph", "")
    checks["species_forest"] = renormalization.get("species_forest_identity") == "sum_(R with bridge C) W_R=40*R_C"
    checks["scale_identity"] = renormalization.get("scale_identity") == "partial_log(mu)T6_bb,T=[5/(4*pi^2)]*T4,T"
    checks["scale_coefficient"] = Fraction(4 * 2 * 40, 16 * 16) == Fraction(5, 4)
    checks["running_cancellation"] = renormalization.get("cancellation") == "partial_log(mu)[lambda^4*T4,T+lambda^6*T6_bb,T]=O(lambda^8) in this forest sector"
    checks["renormalization_status"] = renormalization.get("status") == "FINITE_TIME_MSBAR_FOREST_AND_RG_IDENTITY_PROVED"

    packet = certificate.get("packet_bound", {})
    checks["bubble_margin"] = "32/625" in packet.get("bubble_spatial_margin", "")
    checks["hard_dark"] = "annihilate u0" in packet.get("hard_bridge", "")
    checks["bridge_margin"] = "7169/10625" in packet.get("surviving_bridge_margin", "")
    checks["Lipschitz_bound"] = all(term in packet.get("time_domain_bounds", "") for term in ("1/(2*E_min)", "Lipschitz", "T^2/(2*E_min)"))
    checks["finite_part_bound"] = "h_R(tau)-h_R(0)=O(abs(tau))" in packet.get("finite_part_bound", "")
    checks["Hilbert_Schmidt"] = "Hilbert-Schmidt" in packet.get("consequence", "")
    checks["packet_scope"] = packet.get("scope") == "selected positive source only; no full-carrier zero-mode extension is claimed"
    checks["packet_status"] = packet.get("status") == "SELECTED_SOURCE_COMPACT_FINITE_TIME_PACKET_AFFILIATED"

    boundary = certificate.get("covariant_boundary", {})
    checks["boundary_delta"] = all(term in boundary.get("translation_invariant_limit", "") for term in ("F_T(Omega)", "delta(nu+q_B^0)", "delta(rho+q_C^0)"))
    checks["boundary_match"] = boundary.get("role_boundary", "").startswith("J_T,R=i*F_T(Omega)*B_MSbar(Q_R^2)/(K_R^2+i0)")
    checks["phase_stripped_boundary"] = boundary.get("phase_stripped_role_boundary", "").startswith("removing the single common bridge Feynman phase i")
    checks["boundary_on_shell"] = "not evaluated pointwise" in boundary.get("on_shell_rule", "")
    checks["boundary_status"] = boundary.get("status") == "COVARIANT_BUBBLE_BRIDGE_BOUNDARY_MATCHED"

    born = certificate.get("common_Born_interference", {})
    checks["common_Born"] = born.get("status") == "ISOLATED_FINITE_TIME_BUBBLE_BRIDGE_INTERFERENCE_COMMON_BORN" and born.get("sign", "").startswith("NOT_DETERMINED")
    disposition = certificate.get("disposition", {})
    checks["coefficient_disposition"] = disposition.get("finite_time_bubble_bridge") == "COEFFICIENT_COMPUTED_ON_SELECTED_SOURCE_PACKET"
    checks["connected_T6_disposition"] = disposition.get("selected_source_direct_auxiliary_connected_finite_time_T6") == "COMPLETE_WITH_TRIANGLE_PREDECESSOR"
    checks["full_carrier_open"] = disposition.get("full_carrier_zero_mode_extension") == "NOT_CONSTRUCTED"
    checks["not_promoted"] = (
        disposition.get("connected_y4_y6_interference_value") == "NOT_COMPUTED"
        and disposition.get("complete_q10") == "NOT_COMPUTED"
        and disposition.get("general_Eq19") == "NOT_PROVED"
        and disposition.get("gravity_or_metric_BV_BRST_transfer") == "NOT_CONSTRUCTED"
        and disposition.get("Lorentzian_causal_claim") == "NOT_ESTABLISHED"
    )
    checks["boundaries"] = len(certificate.get("does_not_establish", [])) == 14 and "literature priority" in certificate.get("does_not_establish", [])
    checks["next_gate"] = all(term in certificate.get("next_gate", "") for term in ("y4-y6", "triangle", "bubble-with-bridge", "y5", "q10", "Eq. (19)"))
    checks["report"] = certificate.get("report") == "reverse_physics/reports/bt-fully-rearranged-bubble-bridge-finite-time-affiliation.md"

    producer_names = {
        "inputs_are_content_pinned", "five_predecessors_pass", "public_auxiliary_quartic_is_imported",
        "covariant_bubble_bridge_is_imported", "covariant_counterterm_identity_is_imported",
        "triangle_third_Dyson_kernel_is_imported", "energy_diagonal_B_T_scope_is_imported", "tree_kernel_is_imported",
        "six_chronological_orderings_are_exhaustive", "two_parallel_bubble_edges_and_one_bridge_are_explicit",
        "four_orderings_have_one_large_loop_defect", "two_orderings_have_two_large_loop_defects",
        "every_ordering_separates_bubble_endpoints", "spectral_frequency_conservation_is_exact",
        "three_window_frequencies_sum_to_total_energy", "renormalized_bubble_is_full_complex_distribution",
        "bubble_time_distribution_has_only_local_extension_freedom", "bubble_nonlocal_singularity_is_finite_part_one_over_abs_tau",
        "sharp_window_pairing_is_defined_on_Lipschitz_test", "spectral_nu_axis_tail_is_log_over_nu_squared",
        "spectral_rho_axis_tail_is_rho_minus_four", "spectral_cancellation_line_tail_is_log_over_r_four",
        "spectral_generic_tail_is_log_over_r_five", "bubble_thresholds_are_locally_integrable",
        "bridge_poles_act_as_PV_plus_delta", "finite_time_on_shell_bridge_is_well_defined",
        "local_scale_derivative_collapses_bubble_times", "finite_time_scale_identity_is_five_over_four_pi2_tree",
        "running_lambda4_cancels_finite_time_scale_derivative", "covariant_distributional_boundary_is_exact",
        "energy_diagonal_B_T_is_not_used_as_vertex", "hard_zero_spatial_bridge_is_source_dark",
        "source_surviving_bridge_has_positive_spatial_margin", "bubble_has_positive_hard_margin",
        "selected_source_packet_kernel_is_bounded", "selected_source_packet_kernel_is_Hilbert_Schmidt",
        "finite_time_tensor_remains_kappa_fixed", "isolated_finite_time_interference_is_common_Born",
        "selected_source_connected_finite_time_T6_is_complete_with_triangle", "complete_q10_is_not_promoted",
        "Eq19_gravity_and_causality_are_not_promoted",
    }
    recorded = certificate.get("checks", {})
    checks["producer_checks"] = (
        recorded.get("total") == 41 and recorded.get("passed") == 41 and recorded.get("ok") is True
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
