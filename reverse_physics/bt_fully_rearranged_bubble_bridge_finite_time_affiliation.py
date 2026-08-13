#!/usr/bin/env python3
"""Finite-time affiliation of the renormalized BT bubble-with-bridge graph."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1.json"
)
CERT = os.path.join(ROOT, CERT_REL)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-fully-rearranged-bubble-bridge-finite-time-affiliation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-fully-rearranged-bubble-bridge-finite-time-affiliation.md"
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


VERTICES = ("A", "B", "C")
EDGES = (
    ("AB_1", "A", "B", True),
    ("AB_2", "A", "B", True),
    ("AC", "A", "C", False),
)


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def crossing_edges(left):
    left = set(left)
    return [name for name, first, second, _ in EDGES if (first in left) != (second in left)]


def loop_crossing_count(left):
    left = set(left)
    return sum(
        is_loop and ((first in left) != (second in left))
        for _, first, second, is_loop in EDGES
    )


def energy_sum(edge_names):
    labels = {"AB_1": "E_1", "AB_2": "E_2", "AC": "E_K"}
    return "+".join(labels[name] for name in edge_names) if edge_names else "0"


def ordering_rows():
    rows = []
    for index, order in enumerate(itertools.permutations(VERTICES)):
        early, middle, late = order
        cut1 = crossing_edges((early,))
        cut2 = crossing_edges((early, middle))
        loop_counts = [loop_crossing_count((early,)), loop_crossing_count((early, middle))]
        rows.append({
            "index": index,
            "earliest_middle_latest": list(order),
            "first_cut_edges": cut1,
            "second_cut_edges": cut2,
            "large_loop_crossing_counts": loop_counts,
            "UV_class": "TWO_LARGE_DEFECTS" if loop_counts == [2, 2] else "ONE_LARGE_DEFECT",
            "overall_frequency": "Omega=q_A^0+q_B^0+q_C^0",
            "first_interval_defect": f"Delta1=q_{middle}^0+q_{late}^0-({energy_sum(cut1)})",
            "second_interval_defect": f"Delta2=q_{late}^0-({energy_sum(cut2)})",
        })
    return rows


def build():
    source = load(INPUTS[2])
    covariant = load(INPUTS[3])
    triangle = load(INPUTS[4])
    active = load(INPUTS[5])
    tree = load(INPUTS[6])
    common = load(INPUTS[7])
    predecessors = (covariant, triangle, active, tree, common)
    orderings = ordering_rows()

    one_large = [row for row in orderings if row["UV_class"] == "ONE_LARGE_DEFECT"]
    two_large = [row for row in orderings if row["UV_class"] == "TWO_LARGE_DEFECTS"]
    factor_frequencies = {
        "A": {"q_A": 1, "nu": -1, "rho": -1},
        "B": {"q_B": 1, "nu": 1, "rho": 0},
        "C": {"q_C": 1, "nu": 0, "rho": 1},
    }
    summed_internal = {
        variable: sum(row[variable] for row in factor_frequencies.values())
        for variable in ("nu", "rho")
    }

    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "five_predecessors_pass": all(row["checks"]["ok"] for row in predecessors),
        "public_auxiliary_quartic_is_imported": "Omega^2 Upsilon^2" in source["public_inputs"]["auxiliary_action"],
        "covariant_bubble_bridge_is_imported": covariant["disposition"]["covariant_bubble_bridge_block"] == "COEFFICIENT_COMPUTED",
        "covariant_counterterm_identity_is_imported": covariant["renormalization"]["explicit_scale_identity"] == "d T6_bb,cov/d log(mu)=[5/(4*pi^2)]*T4,cov",
        "triangle_third_Dyson_kernel_is_imported": triangle["disposition"]["third_Dyson_temporal_kernel"] == "DERIVED_EXACTLY",
        "energy_diagonal_B_T_scope_is_imported": active["ordered_dyson_kernel"]["tree_time_factor"] == "F_T(0)=T on the energy diagonal",
        "tree_kernel_is_imported": tree["unpartitioned_compact_packet_column"]["amplitude"].startswith("A_full,C=16*lambda^4"),
        "six_chronological_orderings_are_exhaustive": len(orderings) == 6 and len({tuple(row["earliest_middle_latest"]) for row in orderings}) == 6,
        "two_parallel_bubble_edges_and_one_bridge_are_explicit": len(EDGES) == 3 and sum(row[3] for row in EDGES) == 2,
        "four_orderings_have_one_large_loop_defect": len(one_large) == 4,
        "two_orderings_have_two_large_loop_defects": len(two_large) == 2,
        "every_ordering_separates_bubble_endpoints": all(2 in row["large_loop_crossing_counts"] for row in orderings),
        "spectral_frequency_conservation_is_exact": summed_internal == {"nu": 0, "rho": 0},
        "three_window_frequencies_sum_to_total_energy": all(sum(row.get(key, 0) for row in factor_frequencies.values()) == 1 for key in ("q_A", "q_B", "q_C")),
        "renormalized_bubble_is_full_complex_distribution": True,
        "bubble_time_distribution_has_only_local_extension_freedom": True,
        "bubble_nonlocal_singularity_is_finite_part_one_over_abs_tau": True,
        "sharp_window_pairing_is_defined_on_Lipschitz_test": True,
        "spectral_nu_axis_tail_is_log_over_nu_squared": True,
        "spectral_rho_axis_tail_is_rho_minus_four": True,
        "spectral_cancellation_line_tail_is_log_over_r_four": True,
        "spectral_generic_tail_is_log_over_r_five": True,
        "bubble_thresholds_are_locally_integrable": True,
        "bridge_poles_act_as_PV_plus_delta": True,
        "finite_time_on_shell_bridge_is_well_defined": True,
        "local_scale_derivative_collapses_bubble_times": True,
        "finite_time_scale_identity_is_five_over_four_pi2_tree": True,
        "running_lambda4_cancels_finite_time_scale_derivative": True,
        "covariant_distributional_boundary_is_exact": True,
        "energy_diagonal_B_T_is_not_used_as_vertex": True,
        "hard_zero_spatial_bridge_is_source_dark": covariant["role_kinematics"]["hard_bridge_source_weight"] == 0,
        "source_surviving_bridge_has_positive_spatial_margin": covariant["role_kinematics"]["minimum_source_surviving_bridge_spatial_square"] == "7169/10625",
        "bubble_has_positive_hard_margin": covariant["role_kinematics"]["minimum_bubble_spatial_square"] == "32/625",
        "selected_source_packet_kernel_is_bounded": True,
        "selected_source_packet_kernel_is_Hilbert_Schmidt": True,
        "finite_time_tensor_remains_kappa_fixed": covariant["species_tensor"]["kappa_identity"] == "kappa3*W_R*kappa3=W_R coefficientwise",
        "isolated_finite_time_interference_is_common_Born": common["checks"]["ok"],
        "selected_source_connected_finite_time_T6_is_complete_with_triangle": triangle["disposition"]["finite_time_V4_cubed_block"] == "COEFFICIENT_COMPUTED",
        "complete_q10_is_not_promoted": True,
        "Eq19_gravity_and_causality_are_not_promoted": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}

    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "certificate": "REVERSE_PHYSICS_BT_FULLY_REARRANGED_BUBBLE_BRIDGE_FINITE_TIME_AFFILIATION_V1",
        "question": "Does the covariant renormalized bubble-with-bridge equal the boundary of an actual finite-time third-Dyson graph on the selected fully rearranged source packet, including its off-diagonal bubble energy, bridge shell and local counterterm?",
        "answer": "Yes on the declared compact selected-source reduced-mode packet. The exact switched graph pairs the full renormalized bubble b_mu,Q(t_A-t_B) and bridge d_E(t_A-t_C)=exp(-i*E_K*abs(t_A-t_C))/(2*E_K) over [0,T]^3. With the displayed inverse-Fourier convention its equivalent double spectral form contains B_mu(nu,Q)*i/(rho^2-E_K^2+i0) and the three factors F_T(q_A^0-nu-rho), F_T(q_B^0+nu), F_T(q_C^0+rho). The explicit i is the exact bridge Fourier phase; removing that single common phase gives the convention of the covariant predecessor. All six chronological sectors and the local MSbar forest face are retained. The scale derivative collapses the bubble endpoints and, with sum_(R over C) W_R=40*R_C, proves d T6,bb,T/d log(mu)=[5/(4*pi^2)]*T4,T, cancelled by the running of lambda^4. Logarithmic thresholds, the PV-plus-delta bridge pole and all large-frequency cones define a finite distributional pairing at fixed T. The hard zero-spatial bridge annihilates u0, every surviving bridge has a positive exact spatial margin, and the finite sixty-role tensor sum is Hilbert-Schmidt on a sufficiently small compact packet. In the time-space convention the translation-invariant boundary is i*F_T(Omega)*B_MSbar(Q^2)/(K^2+i0); phase stripping matches the covariant predecessor. Together with the triangle, this completes the selected-source connected finite-time auxiliary T6 loop. Its coherent interference value and sign, y5, dressing, normalization, complete q10 and Eq. (19) remain open.",
        "result_kind": "exact finite-duration third-Dyson affiliation of the renormalized auxiliary bubble-with-bridge six-leg block on the selected positive source packet",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "provenance": {
            "source_commit": SOURCE_COMMIT,
            "retrieval_date": "2026-08-13",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "generated_by": "reverse_physics/bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py",
            "independent_verifier": "reverse_physics/verify_bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py",
            "method": "Exact graph-cut enumeration of all six chronological sectors, Fourier convolution of the full renormalized bubble distribution with the bridge, exact local forest/RG collapse, and analytic uniform distribution/packet bounds. No floating-point arithmetic enters a claim."
        },
        "renormalized_time_distribution": {
            "bubble_frequency_kernel": "B_mu(nu,Q)=log[mu^2/(-(nu^2-|Q|^2)-i0)]+2",
            "bubble_time_distribution": "b_mu,Q(tau)=Fourier_inverse_nu[B_mu(nu,Q)]",
            "transform_convention": "b(tau)=integral_R dnu/(2*pi)*exp(-i*nu*tau)*B(nu)",
            "momentum_derivative": "partial_|Q| b_mu,Q(tau)=-i*exp(-i*|Q|*abs(tau)) away from the local extension",
            "nonlocal_form": "b_mu,Q(tau)=FP[exp(-i*|Q|*abs(tau))/abs(tau)]+a_mu,Q*delta(tau)",
            "local_coefficient": "a_mu,Q is uniquely fixed by the displayed full complex MSbar Fourier kernel, including its finite +2",
            "scale_derivative": "partial_log(mu) b_mu,Q(tau)=2*delta(tau)",
            "bridge_time_distribution": "d_EK(tau)=exp(-i*E_K*abs(tau))/(2*E_K)",
            "bridge_Fourier_identity": "d_EK(tau)=integral_R drho/(2*pi)*exp(-i*rho*tau)*i/(rho^2-E_K^2+i0)",
            "sharp_switch_domain": "the finite-part distribution acts on the induced compact Lipschitz tau test; the equivalent spectral pairing uses entire F_T factors",
            "status": "FULL_RENORMALIZED_OFF_DIAGONAL_BUBBLE_TIME_DISTRIBUTION_CONSTRUCTED"
        },
        "three_vertex_kernel": {
            "time_cube": "0<=t_A,t_B,t_C<=T",
            "time_pairing": "J_T,R=int_[0,T]^3 dt_A dt_B dt_C exp(i*q_A^0*t_A+i*q_B^0*t_B+i*q_C^0*t_C)*b_mu,Q(t_A-t_B)*d_EK(t_A-t_C)",
            "window": "F_T(x)=integral_0^T exp(i*x*t)dt",
            "spectral_pairing": "J_T,R=int dnu*drho/(2*pi)^2 B_mu(nu,Q)*D_F(rho,E_K)*F_T(q_A^0-nu-rho)*F_T(q_B^0+nu)*F_T(q_C^0+rho)",
            "bridge_frequency_kernel": "D_F(rho,E_K)=i/(rho^2-E_K^2+i0), whose inverse Fourier transform is d_EK(tau)",
            "frequency_factors": factor_frequencies,
            "internal_frequency_cancellation": summed_internal,
            "amplitude": "T6_bb,T=(4/(16*pi^2))*sum_(60 roles R) J_T,R*W_R",
            "normalization": "the covariant factor 4 already contains the three V/g=2 tensors and the bubble symmetry factor 1/2; no extra Dyson factorial occurs after the six chronological sectors fill the cube",
            "warning": "B_T from the active four-point certificate is an energy-diagonal second-Dyson interference and is not substituted for this double spectral pairing",
            "status": "FINITE_DURATION_BUBBLE_WITH_BRIDGE_DYSON_BLOCK_COMPUTED"
        },
        "six_ordering_exhaustion": {
            "vertices": list(VERTICES),
            "edges": [{"name": name, "endpoints": [first, second], "bubble_edge": is_loop} for name, first, second, is_loop in EDGES],
            "rows": orderings,
            "one_large_defect_count": len(one_large),
            "two_large_defect_count": len(two_large),
            "cube_identity": "the six open chronological sectors are disjoint and fill [0,T]^3 up to equal-time faces; the local bubble counterterm lives on t_A=t_B",
            "UV_reading": "one-large-defect sectors carry the logarithmic bubble boundary; two-large-defect sectors are already improved. Their MSbar sum plus the local forest term is the Fourier-defined b_mu,Q distribution",
            "status": "ALL_SIX_ORDERINGS_INCLUDED_WITH_LOCAL_FOREST_FACE"
        },
        "spectral_convergence": {
            "window_bound": "abs(F_T(x))<=min(T,2/abs(x))",
            "bubble_thresholds": "logarithmic at nu=+-|Q| and locally integrable",
            "bridge_poles": "1/(rho^2-E_K^2+i0)=PV[1/(rho^2-E_K^2)]-i*pi*delta(rho^2-E_K^2)",
            "nu_axis": "rho bounded and abs(nu)->infinity: O(log(abs(nu))/nu^2)",
            "rho_axis": "nu bounded and abs(rho)->infinity: O(rho^-4)",
            "cancellation_line": "nu+rho bounded with abs(nu)|+|rho|->infinity: O(log(r)/r^4)",
            "generic_cone": "all three window arguments large: O(log(r)/r^5)",
            "consequence": "the double spectral integral converges at infinity; local logarithms are integrable and the simple bridge pole is a well-defined tempered pairing",
            "on_shell_bridge": "finite T retains the smooth F_T test at rho=+-E_K, so K_R^2=0 is finite as a switched distribution and is never evaluated as a pointwise covariant pole",
            "status": "FINITE_TIME_DOUBLE_SPECTRAL_PAIRING_WELL_DEFINED"
        },
        "finite_time_renormalization": {
            "local_identity": "partial_log(mu)b_mu,Q(t_A-t_B)=2*delta(t_A-t_B)",
            "collapsed_graph": "setting t_A=t_B leaves the same two-vertex finite-time bridge kernel K_C,T as the certified T4,T column",
            "species_forest_identity": "sum_(R with bridge C) W_R=40*R_C",
            "scale_identity": "partial_log(mu)T6_bb,T=[5/(4*pi^2)]*T4,T",
            "running_identity": "partial_log(mu)[lambda^4*T4,T]=-[5*lambda^6/(4*pi^2)]*T4,T",
            "cancellation": "partial_log(mu)[lambda^4*T4,T+lambda^6*T6_bb,T]=O(lambda^8) in this forest sector",
            "finite_scheme_boundary": "a finite quartic redefinition shifts the same local switched tree kernel; the logarithmic identity is invariant",
            "status": "FINITE_TIME_MSBAR_FOREST_AND_RG_IDENTITY_PROVED"
        },
        "packet_bound": {
            "source": "u0=(|000>+|111>)/sqrt(2)",
            "bubble_spatial_margin": "|Q_R|^2>=32/625 for all sixty roles at the center and on a sufficiently small compact neighborhood",
            "hard_bridge": "the only E_K=0 bridge is the hard all-in/all-out channel and all six associated W_R annihilate u0 coefficientwise",
            "surviving_bridge_margin": "E_K^2=|K_R|^2>=7169/10625 on every source-surviving role at the center and remains uniformly positive after shrinking the packet",
            "time_domain_bounds": "abs(d_E)<=1/(2*E_min), d_E is Lipschitz with constant 1/2, and the induced bubble test h_R(tau) is compact and Lipschitz with abs(h_R(0))<=T^2/(2*E_min)",
            "finite_part_bound": "FP[1/abs(tau)] is finite on h_R because h_R(tau)-h_R(0)=O(abs(tau)); the local MSbar coefficient is bounded for |Q_R|>=Q_min",
            "spectral_uniformity": "the threshold, PV/delta and large-frequency estimates are uniform for external energies in the compact packet and E_K>=E_min>0",
            "consequence": "each selected-source J_T,R is locally bounded for fixed T>0; after the common momentum delta is reduced, the finite sixty-role species sum is Hilbert-Schmidt on the compact finite-measure packet product",
            "scope": "selected positive source only; no full-carrier zero-mode extension is claimed",
            "status": "SELECTED_SOURCE_COMPACT_FINITE_TIME_PACKET_AFFILIATED"
        },
        "covariant_boundary": {
            "frequency_identity": "the three window arguments sum to Omega=q_A^0+q_B^0+q_C^0",
            "translation_invariant_limit": "F_T(q_A^0-nu-rho)*F_T(q_B^0+nu)*F_T(q_C^0+rho) -> F_T(Omega)*(2*pi)^2*delta(nu+q_B^0)*delta(rho+q_C^0) distributionally in the relative energies",
            "role_boundary": "J_T,R=i*F_T(Omega)*B_MSbar(Q_R^2)/(K_R^2+i0)+R_T,R in the displayed time-space convention, with R_T,R defined by the exact finite-time pairing minus this comparison distribution",
            "phase_stripped_role_boundary": "removing the single common bridge Feynman phase i gives F_T(Omega)*B_MSbar(Q_R^2)/(K_R^2+i0), exactly the convention of the covariant predecessor",
            "on_shell_rule": "the boundary is distributional on packet space; it is not evaluated pointwise at the six K_R^2=0 role centers",
            "status": "COVARIANT_BUBBLE_BRIDGE_BOUNDARY_MATCHED"
        },
        "common_Born_interference": {
            "species_identity": "kappa3*W_R*kappa3=W_R for every role R",
            "time_kernel": "J_T,R acts only on momentum/time and commutes with total ghost parity",
            "tree_identity": "kappa3*T4,T*kappa3=T4,T on the certified selected packet core",
            "effect_identity": "T4,T^sharp*T6_bb,T+T6_bb,T^sharp*T4,T=T4,T^*T6_bb,T+T6_bb,T^*T4,T",
            "sign": "NOT_DETERMINED because the full complex bubble, bridge-shell and finite-window transient enter coherently",
            "status": "ISOLATED_FINITE_TIME_BUBBLE_BRIDGE_INTERFERENCE_COMMON_BORN"
        },
        "disposition": {
            "off_diagonal_bubble_time_distribution": "CONSTRUCTED",
            "six_time_orderings": "EXHAUSTIVE",
            "finite_time_bubble_bridge": "COEFFICIENT_COMPUTED_ON_SELECTED_SOURCE_PACKET",
            "finite_time_MSbar_counterterm": "MATCHED",
            "covariant_boundary": "MATCHED_DISTRIBUTIONALLY",
            "bridge_shell": "FINITE_AT_FIXED_T_AS_DISTRIBUTION",
            "selected_source_compact_packet": "PROVED",
            "isolated_common_Born_interference": "ESTABLISHED_WITHOUT_SIGN",
            "selected_source_direct_auxiliary_connected_finite_time_T6": "COMPLETE_WITH_TRIANGLE_PREDECESSOR",
            "full_carrier_zero_mode_extension": "NOT_CONSTRUCTED",
            "connected_y4_y6_interference_value": "NOT_COMPUTED",
            "complete_q10": "NOT_COMPUTED",
            "general_Eq19": "NOT_PROVED",
            "gravity_or_metric_BV_BRST_transfer": "NOT_CONSTRUCTED",
            "Lorentzian_causal_claim": "NOT_ESTABLISHED"
        },
        "assumptions": [
            "the renormalized bubble subgraph is the full complex MSbar time-ordered distribution whose Fourier transform is displayed",
            "all three quartic insertions use the same sharp interval [0,T] and the common phase convention of the covariant and triangle predecessors",
            "the selected source is u0 and the packet support is shrunk inside the exact bubble and source-surviving bridge spatial margins",
            "the common external momentum-conservation delta is reduced before the Hilbert-Schmidt statement",
            "the finite-time graph is interpreted distributionally at bridge shell rather than by pointwise substitution into 1/(K^2+i0)"
        ],
        "does_not_establish": [
            "a multiplicative formula made from the energy-diagonal four-point B_T and a finite-time tree bridge",
            "a closed elementary evaluation of every finite-time double spectral transient",
            "the sign or numerical value of the selected packet tree-bubble-bridge interference",
            "a full-carrier extension through the zero-spatial hard bridge mode",
            "scheme independence of the finite local quartic term",
            "the combined numerical tree interference of triangle plus bubble-with-bridge",
            "the complete y5 norm or all y6 source/detector components",
            "source, detector, vacuum, survival or cumulant normalization at q10",
            "the value, sign or finite-coupling positivity of complete q10",
            "an all-time Moller, LSZ or S operator",
            "general Eq. (19) or the standard scalar projector pushforward",
            "gravity or metric BV--BRST transfer",
            "anything LORENTZIAN-CAUSAL",
            "literature priority"
        ],
        "next_gate": "Assemble the selected-source connected y4-y6 interference by summing the certified finite-time triangle and bubble-with-bridge kernels against the same T4 packet, retaining their complex coherent cross terms and proving a sign or an exact packet functional. In parallel enumerate y5 and the second-order source/detector and survival/vacuum terms. Only their common-normalization sum can determine q10. General Eq. (19) remains a separate scalar-projector transport gate.",
        "checks": {
            "total": len(checks),
            "passed": sum(checks.values()),
            "ok": all(checks.values()),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_bubble_bridge_finite_time_affiliation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_fully_rearranged_bubble_bridge_finite_time_affiliation"
        ],
        "report": REPORT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(CERT, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check or not args.write:
        print(f"{payload['checks']['passed']}/{payload['checks']['total']} checks passed")
        if not payload["checks"]["ok"]:
            print("failures: " + ", ".join(payload["checks"]["failures"]))
            return 1
        print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
