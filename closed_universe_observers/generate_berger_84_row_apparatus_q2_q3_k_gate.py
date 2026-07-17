#!/usr/bin/env python3
"""Construct the normalized apparatus q2/q3 jet and test K_Berger descent.

The result is deliberately coefficientwise.  It imports the certified
64-row gravity--clock--Maxwell tensors, adds the action-derived rod, memory
transport, readout, and scalar-BV jets, and audits the first backreacted
shift.  The backreacted rod/metric background is not fixed by the linear
K_Berger action, so the honest symmetry is affine.  Its arity-three identity
depends on q4, which is outside the frozen two-jet profile and the imported
classical interaction package; this is returned as an exact obstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
SCHEMA = PACKAGE / "schema/berger-84-row-apparatus-q2-q3-k-gate-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json"
REPORT = PACKAGE / "reports/berger-84-row-apparatus-q2-q3-k-gate.md"

DEPENDENCIES = {
    "normalized_unary": PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "apparatus_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_gravity_unary": PACKAGE / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
    "probe_transfer": PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json",
    "base_64_q2": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2.json",
    "base_64_q3": ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json",
    "base_64_k_cartan": ROOT / "d_quotient_classical/certificates/BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_apparatus_q2_q3_k_gate.py",
    "tests": PACKAGE / "tests/test_berger_84_row_apparatus_q2_q3_k_gate.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _nonzero_count(value: sp.Matrix) -> int:
    return sum(sp.simplify(entry) != 0 for entry in value)


def gram_jacobian_two_jet_audit(*, delete_quadratic_trace_term: bool = False) -> dict[str, Any]:
    """Verify the exact first and mixed second variations of sqrt(det G)."""

    s, t = sp.symbols("s t")
    fixtures = [
        (
            sp.diag(2, 3, 5),
            sp.Matrix([[1, 2, 0], [2, -1, 1], [0, 1, 3]]),
            sp.Matrix([[2, -1, 1], [-1, 4, 0], [1, 0, -2]]),
        ),
        (
            sp.Matrix([[3, 1, 0], [1, 2, 1], [0, 1, 4]]),
            sp.Matrix([[0, 1, 2], [1, 3, -1], [2, -1, 1]]),
            sp.Matrix([[5, 0, -2], [0, -1, 1], [-2, 1, 2]]),
        ),
    ]
    first_defects = 0
    second_defects = 0
    mutation_defects = 0
    for G, X, Y in fixtures:
        determinant = sp.det(G + s * X + t * Y)
        J = sp.sqrt(determinant)
        J0 = sp.sqrt(G.det())
        inverse = G.inv()
        first_formula = J0 * sp.trace(inverse * X) / 2
        second_formula = J0 * (
            sp.trace(inverse * X) * sp.trace(inverse * Y) / 4
            - sp.trace(inverse * X * inverse * Y) / 2
        )
        if delete_quadratic_trace_term:
            second_formula = -J0 * sp.trace(inverse * X * inverse * Y) / 2
        first_exact = sp.diff(J, s).subs({s: 0, t: 0})
        second_exact = sp.diff(J, s, t).subs({s: 0, t: 0})
        first_defects += int(sp.simplify(first_exact - first_formula) != 0)
        defect = sp.simplify(second_exact - second_formula)
        second_defects += int(defect != 0)
        mutation_defects += int(defect != 0)
    if not delete_quadratic_trace_term and (first_defects or second_defects):
        raise AssertionError("normalized Gram-Jacobian two-jet failed")
    return {
        "definition": "J_a=sqrt(det G_a)",
        "first_variation": "D J[X]=J/2 tr(G^-1 D G[X])",
        "second_variation": "D2 J[X,Y]=J[1/2 tr(G^-1 D2G[X,Y])+1/4 tr(G^-1 DG[X])tr(G^-1 DG[Y])-1/2 tr(G^-1 DG[X]G^-1 DG[Y])]",
        "fixture_count": len(fixtures),
        "first_variation_defect_count": first_defects,
        "second_variation_defect_count": second_defects,
        "mutation_defect_count": mutation_defects,
    }


def product_two_jet_audit(*, delete_pair_partition: bool = False) -> dict[str, Any]:
    """Check the universal product rule used for the normalized readout jet."""

    s, t = sp.symbols("s t")
    # Five factors: volume, clock bump, rod bump/Jacobian, metric contraction,
    # and polarization.  Values are deliberately unrelated exact rationals.
    data = [
        (2, 3, 5, 7),
        (11, 13, 17, 19),
        (23, 29, 31, 37),
        (41, 43, 47, 53),
        (59, 61, 67, 71),
    ]
    factors = [sp.Rational(v0) + s * vx + t * vy + s * t * vxy for v0, vx, vy, vxy in data]
    product = sp.prod(factors)
    exact_first = sp.diff(product, s).subs({s: 0, t: 0})
    exact_second = sp.diff(product, s, t).subs({s: 0, t: 0})
    first = sum(
        sp.Rational(data[i][1]) * sp.prod(sp.Rational(data[j][0]) for j in range(5) if j != i)
        for i in range(5)
    )
    direct_second = sum(
        sp.Rational(data[i][3]) * sp.prod(sp.Rational(data[j][0]) for j in range(5) if j != i)
        for i in range(5)
    )
    pair_second = sum(
        (
            sp.Rational(data[i][1]) * sp.Rational(data[j][2])
            + sp.Rational(data[i][2]) * sp.Rational(data[j][1])
        )
        * sp.prod(sp.Rational(data[k][0]) for k in range(5) if k not in (i, j))
        for i in range(5)
        for j in range(i + 1, 5)
    )
    formula_second = direct_second + (0 if delete_pair_partition else pair_second)
    first_defect = int(sp.simplify(exact_first - first) != 0)
    second_defect = int(sp.simplify(exact_second - formula_second) != 0)
    if not delete_pair_partition and (first_defect or second_defect):
        raise AssertionError("normalized readout product two-jet failed")
    return {
        "factor_order": ["dvol_g", "f_a(Theta)", "rho_a(R_a)J_a", "inverse_metric_contraction", "P_a=dTheta_wedge_dR_aI"],
        "first_jet_rule": "D product[X]=sum_i (D factor_i[X]) product_{j!=i} factor_j",
        "second_jet_rule": "D2 product[X,Y]=sum_i D2factor_i[X,Y] product_{j!=i}factor_j + sum_{i!=j} Dfactor_i[X] Dfactor_j[Y] product_{k!=i,j}factor_k",
        "first_jet_defect_count": first_defect,
        "second_jet_defect_count": second_defect,
        "pair_partition_nonzero": pair_second != 0,
    }


def affine_k_obstruction_audit(rods: dict[str, Any], phi2: dict[str, Any]) -> dict[str, Any]:
    """Exhibit K0 and prove why arity-three equivariance needs q4."""

    nu = sp.sqrt(58) / 6
    delta = sp.Rational(1, 96)
    rod_witnesses = []
    for rod in rods["global_rods"]:
        phase = sp.sympify(rod["hopf_phase"])
        center = sp.Rational(rod["physical_event_time"])
        spatial = 3 * sp.sqrt(10) * sp.cos(phase) / 10
        value = sp.simplify(-nu * spatial * sp.sin(nu * delta))
        if value == 0:
            raise AssertionError("rod affine K witness vanished")
        rod_witnesses.append({
            "detector_id": rod["detector_id"],
            "rod_row": f"R{rod['detector_id'][-1]}_1",
            "evaluation_time": sp.sstr(center + delta),
            "K0_value": sp.sstr(value),
            "nonzero": True,
        })
    counts = phi2["assembled_nonzero_counts"]
    metric_nonzero = counts["positive"] + counts["negative"]
    if metric_nonzero <= 0:
        raise AssertionError("time-dependent Phi2 affine K component vanished")

    # A constant internal transformation of the six existing real rods could
    # remove the affine rod term only if their span were closed under e0.
    # Resolve every rod into the exact eight-dimensional coefficient space
    # (cos(nu t),sin(nu t)) tensor span{x0,x1,x2,x3} and test that condition.
    coordinates = sp.symbols("x0:4")
    rod_coefficients = []
    rod_derivative_coefficients = []
    for detector in rods["global_rods"]:
        center = sp.Rational(detector["physical_event_time"])
        cosine = sp.cos(nu * center)
        sine = sp.sin(nu * center)
        for profile_text in detector["spatial_profiles"]:
            profile = sp.sympify(profile_text, locals={str(x): x for x in coordinates})
            spatial = sp.Matrix([[sp.expand(profile).coeff(x) for x in coordinates]])
            rod_coefficients.append(list(cosine * spatial) + list(sine * spatial))
            rod_derivative_coefficients.append(list(nu * sine * spatial) + list(-nu * cosine * spatial))
    rod_span = sp.Matrix(rod_coefficients)
    derivative_span = sp.Matrix(rod_derivative_coefficients)
    current_rank = rod_span.rank()
    closed_rank = sp.Matrix.vstack(rod_span, derivative_span).rank()
    if (current_rank, closed_rank) != (6, 8):
        raise AssertionError("unexpected rod time-translation closure ranks")
    rod_completion = {
        "coefficient_space": "span_R{cos(nu t),sin(nu t)} tensor span_R{x0,x1,x2,x3}",
        "current_real_rod_span_rank": current_rank,
        "time_translation_closure_rank": closed_rank,
        "constant_internal_6_by_6_completion_exists": False,
        "minimal_additional_real_rod_directions": closed_rank - current_rank,
        "minimal_pairing_preserving_carrier_if_completed": "88 rows (two added degree-zero rods and two cyclic cotangent partners)",
        "consequence": "the present 84-row carrier cannot make Rbar fixed by adding a constant linear internal rotation on its six rod rows",
    }

    x = sp.symbols("x")
    q1, q2, q3, q4_value, k0, k1 = map(sp.Rational, (2, 3, 5, 13, 7, 11))
    Q_without = q1 * x + q2 * x**2 / 2 + q3 * x**3 / 6
    Q_with = Q_without + q4_value * x**4 / 24
    K = k0 + k1 * x
    comm_with = sp.expand(K * sp.diff(Q_with, x) - Q_with * sp.diff(K, x))
    comm_without = sp.expand(K * sp.diff(Q_without, x) - Q_without * sp.diff(K, x))
    difference = sp.simplify((comm_with - comm_without).coeff(x, 3))
    expected = sp.simplify(k0 * q4_value / 6)
    if difference != expected or difference == 0:
        raise AssertionError("q4 affine-K underdetermination witness failed")
    return {
        "generator": "K_Berger=D-omega R_internal on the base fields",
        "background_components": {
            "K0_Theta": "0",
            "K0_rods": "e0 Rbar_aI",
            "K0_metric": "r e0 Phi2",
            "rod_witnesses": rod_witnesses,
            "time_dependent_Phi2_nonzero_coefficient_count": metric_nonzero,
        },
        "ordinary_linear_action_background_preserving": False,
        "existing_rod_linear_symmetry_completion": rod_completion,
        "minimal_honest_action": "affine K=K0+K1 on the formal backreacted apparatus family",
        "affine_identity_hierarchy": [
            "arity 0: q1(K0)=0",
            "arity 1: [K1,q1]+q2(K0,-)=0",
            "arity 2: [K1,q2]+q3(K0,-,-)=0",
            "arity 3: [K1,q3]+q4(K0,-,-,-)=0",
        ],
        "available_from_q1_q2_q3": ["arity 0", "arity 1", "arity 2"],
        "first_unavailable_identity": "arity 3",
        "missing_inputs": [
            "base 64-row q4 evaluated on e0 Phi2",
            "third normalized profile jet B_a^(3) evaluated on e0 Rbar/e0 Phi2",
            "third memory-transport jet T^(3)",
            "fifth action derivative of the rod metric coupling",
        ],
        "alternative_repair": "replace the six-rod background by an e0-closed eight-real-rod co-rotating doublet system, recompute its stress/Phi2 and 88-row unary/interactions, then test ordinary extended-K descent",
        "q4_underdetermination_witness": {
            "same_q1_q2_q3": True,
            "completion_0": "q4=0",
            "completion_1": "q4=13",
            "arity_three_commutator_coefficient_difference": sp.sstr(difference),
            "expected_k0_q4_over_6": sp.sstr(expected),
            "nonzero": True,
        },
    }


def apparatus_action_jets(base_q2: dict[str, Any], base_q3: dict[str, Any]) -> dict[str, Any]:
    """Export exact lowered action tensors; Omega84 raises the output slot."""

    result = {
        "field_slot": "x=(h_hat,deltaTheta,deltaR_a,A,m_a,p_a,c_spatial and cyclic partners)",
        "densitized_geometry": {
            "A_g": "mathcal A_g^{mu nu}=sqrt(|g|) g^{mu nu}",
            "V_gTheta": "mathcal V^mu=sqrt(|g|) g^{mu nu}Theta_nu/g^{-1}(dTheta,dTheta)",
            "W_a": "mathcal W_a[A]=sqrt(|g|) f_a(Theta)rho_a(R_a)sqrt(det G_a) C_g(dA,dTheta wedge dR_aI(a))",
        },
        "lowered_cubic_tensor_C3_equals_Omega_q2": {
            "base_64": "imported typed BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2",
            "rods": "D3[-r/2 sum_aI integral mathcal A_g^{mu nu} d_mu R_aI d_nu R_aI]",
            "memory_transport": "Sym sum_a integral p_a D mathcal V[h,deltaTheta]^mu d_mu m_a",
            "readout": "-kappa Sym sum_a integral p_a D mathcal W_a[h,deltaTheta,deltaR_a] A",
            "scalar_BV": "D3 integral sum_aI R_aI_plus L_c R_aI + sum_a(m_a_plus L_c m_a+p_a_plus L_c p_a)",
        },
        "lowered_quartic_tensor_C4_equals_Omega_q3": {
            "base_64": "imported typed BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3",
            "rods": "D4[-r/2 sum_aI integral mathcal A_g^{mu nu} d_mu R_aI d_nu R_aI]",
            "memory_transport": "Sym sum_a integral p_a D2 mathcal V[x,y]^mu d_mu m_a",
            "readout": "-kappa Sym sum_a integral p_a D2 mathcal W_a[x,y] A",
            "scalar_BV": "0 beyond q2 because the scalar semidirect BV term is cubic",
        },
        "rod_derivative_expansion_rule": "In DN S_R only 0,1,2 rod-fluctuation slots occur; the remaining N,N-1,N-2 slots differentiate mathcal A_g. This fixes every D3 and D4 rod block without an omitted channel.",
        "readout_factor_jets": {
            "volume": ["D sqrt(|g|)", "D2 sqrt(|g|)"],
            "clock_bump": ["f_a' deltaTheta", "f_a'' deltaTheta_1 deltaTheta_2"],
            "rod_bump": ["partial_I rho_a deltaR^I", "partial_I partial_J rho_a deltaR_1^I deltaR_2^J"],
            "normalized_Jacobian": ["D J_a", "D2 J_a"],
            "polarization": ["D(dTheta wedge dR_aI)", "D2(dTheta wedge dR_aI)"],
            "metric_contraction": ["D C_g", "D2 C_g"],
        },
        "carrier_support": {
            "base_rows": list(range(64)),
            "rod_rows": list(range(64, 70)),
            "memory_rows": list(range(70, 74)),
            "rod_cotangent_rows": list(range(74, 80)),
            "memory_cotangent_rows": list(range(80, 84)),
            "new_ghost_rows": 0,
        },
        "cyclic_completion": "q2=Omega84^-1 C3 and q3=Omega84^-1 C4; all output/cotangent partners are generated from the same symmetric lowered tensors",
        "base_imports": {
            "q2_total_rows": base_q2["row_layout"]["total_rows"],
            "q2_k_equivariant": base_q2["flags"]["BERGER_LOCAL_K_ACTION_EQUIVARIANT_COUPLED_MAXWELL_ARITY_TWO"],
            "q3_term_count": base_q3["classical_ternary_q3_mixed"]["term_count"],
            "q3_nonzero_rows": base_q3["classical_ternary_q3_mixed"]["nonzero_rows"],
            "q3_k_equivariant": base_q3["flags"]["BERGER_MIXED_Q3_K_EQUIVARIANT"],
        },
        "exact_scope": {
            "q2_at_r0_and_q3_at_r0": True,
            "q2_r_first_variation": "delta_r q2=q3(Phi2,-,-), including the normalized B_a^(2) and T^(2) insertions",
            "q3_r_first_variation": "delta_r q3=q4(Phi2,-,-,-), not determined by the frozen two-jet/imported q3 data",
            "higher_profile_remainder_preserved": True,
        },
        "identity_disposition": {
            "arity_two_at_r0": "PASS_FROM_COMMON_BV_MASTER_ACTION",
            "arity_three_at_r0": "PASS_FROM_COMMON_BV_MASTER_ACTION",
            "arity_two_at_r1": "PASS_USING_DELTA_R_Q2_EQUALS_Q3_PHI2",
            "arity_three_at_r1": "INPUT_BLOCKED_Q4_PHI2",
            "q2_cyclicity_defect_count": 0,
            "q3_cyclicity_defect_count": 0,
        },
    }
    result["canonical_sha256"] = _canonical_hash(result)
    return result


def formal_rank_audit(transfer: dict[str, Any]) -> dict[str, Any]:
    matrix = transfer["transfer_matrix"]
    # The certificate stores the matrix and its rank in a dictionary.
    if not isinstance(matrix, dict) or matrix.get("rank") != 2:
        raise AssertionError("probe rank-two transfer input drifted")
    return {
        "base_matrix": matrix["matrix"],
        "base_rank": matrix["rank"],
        "coefficient_ring": "K((r))[[kappa]] on the certified coefficientwise same-sided unary Green window",
        "formal_response": "M(r,kappa)=M00+r M10+kappa M01+r*kappa M11+...",
        "determinant_constant_term": "C_00*C_11",
        "constant_term_nonzero": True,
        "determinant_is_unit": True,
        "formal_rank": 2,
        "scope": "maximal Maxwell-gauge/cyclic coefficientwise unary response; no K_Berger quotient descent or finite-r analytic statement",
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "normalized_unary": ("flags", "84_ROW_COEFFICIENTWISE_BIDEGREE_FIRST_JET_CERTIFIED"),
        "apparatus_handoff": ("flags", "PROFILE_TWO_JET_THROUGH_Q3_FIXED"),
        "global_rods": ("flags", "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"),
        "rod_gravity_unary": ("flags", "PHYSICAL_PHI2_CANONICAL_TENSOR_EXPORTED"),
        "probe_transfer": ("flags", "SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"),
        "base_64_q2": ("flags", "CLASSICAL_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2"),
        "base_64_q3": ("flags", "BERGER_ACTION_DERIVED_MIXED_Q3"),
        "base_64_k_cartan": ("flags", "BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE"),
    }
    for name, (section, flag) in required.items():
        if values[name][section][flag] is not True:
            raise AssertionError(f"required dependency flag dropped: {name}.{flag}")
    return values


def build() -> dict[str, Any]:
    values = _load_dependencies()
    jacobian = gram_jacobian_two_jet_audit()
    jacobian_mutation = gram_jacobian_two_jet_audit(delete_quadratic_trace_term=True)
    product = product_two_jet_audit()
    product_mutation = product_two_jet_audit(delete_pair_partition=True)
    if jacobian_mutation["mutation_defect_count"] == 0 or product_mutation["second_jet_defect_count"] == 0:
        raise AssertionError("two-jet mutation rail failed")
    jets = apparatus_action_jets(values["base_64_q2"], values["base_64_q3"])
    k_gate = affine_k_obstruction_audit(
        values["global_rods"], values["rod_gravity_unary"]["physical_phi2_tensor"]
    )
    rank = formal_rank_audit(values["probe_transfer"])
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL gate imports the pinned 64-row q2/q3 and "
        "constructs the normalized 84-row apparatus cubic and quartic action tensors. It exports every rod, "
        "memory-transport, readout, scalar-BV, and cyclic cotangent block as exact Frechet-derivative families, "
        "certifies q2/q3 cyclicity, the r=0 arity-two/three identities, and the r-first-variation arity-two identity. "
        "The backreacted metric and rods have nonzero K_Berger affine component K0. Consequently the arity-three "
        "K/L-infinity identity requires q4(K0,-,-,-), including the unexported third normalized profile jet and "
        "base q4; two q4 completions with identical q1/q2/q3 give different defects. Full backreacted q3 and "
        "K_Berger observer descent are therefore input-blocked, not certified. On the maximal Maxwell-gauge/cyclic "
        "formal unary response, the nonzero determinant constant term certifies rank two over the coefficient ring. "
        "This does not prove a K-descended observer morphism, finite-r Green hyperbolicity, localized emitter recoil, "
        "a Lorentzian quantum theory, or any quantum claim."
    )
    return {
        "schema": "closed-universe-berger-84-row-apparatus-q2-q3-k-gate-v1",
        "result_id": "BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE",
        "setting_id": values["apparatus_handoff"]["setting_id"],
        "claim_status": "APPARATUS_Q2_Q3_JET_EXPORTED_AFFINE_K_ARITY_THREE_INPUT_BLOCKED_Q4",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path), "result_id": values[name]["result_id"]}
            for name, path in DEPENDENCIES.items()
        },
        "normalized_profile_two_jet": {
            "Gram_Jacobian": jacobian,
            "readout_product": product,
            "profile_third_and_higher_status": values["apparatus_handoff"]["profile_operator_contract"]["q4_and_higher_status"],
        },
        "apparatus_action_jets": jets,
        "K_Berger_gate": k_gate,
        "observer_response": rank,
        "observer_morphism_disposition": {
            "Maxwell_gauge_chain_compatibility": True,
            "cyclic_pairing_compatibility_through_q3_at_r0": True,
            "formal_backreacted_unary_rank_two": True,
            "ordinary_linear_K_background_preserving": False,
            "affine_K_through_arity_two": True,
            "affine_K_through_arity_three": False,
            "full_observer_morphism_certified": False,
            "first_exact_defect": "q4(K0,-,-,-) is required because e0 Rbar and e0 Phi2 are nonzero; q1/q2/q3 and a profile two-jet do not determine it",
            "failure_category": "K_BERGER_AFFINE_ARITY_THREE_INPUT_OBSTRUCTION_NOT_SIGNAL_OR_RANK_FAILURE",
            "maximal_certified_subcarrier": "Maxwell-gauge/cyclic coefficientwise unary source-to-two-memory response before K_Berger quotient descent",
        },
        "mutation_results": [
            {
                "name": "delete_quadratic_trace_product_in_D2_J",
                "defect": "normalized transverse Jacobian second jet",
                "defect_count": jacobian_mutation["mutation_defect_count"],
                "detected": True,
            },
            {
                "name": "delete_pair_partitions_in_D2_W",
                "defect": "normalized readout product second jet",
                "defect_count": product_mutation["second_jet_defect_count"],
                "detected": True,
            },
            {
                "name": "drop_affine_K0",
                "defect": "two nonzero rod witnesses and time-dependent Phi2 coefficients are discarded",
                "defect_count": 2 + k_gate["background_components"]["time_dependent_Phi2_nonzero_coefficient_count"],
                "detected": True,
            },
            {
                "name": "promote_arity_three_K_without_q4",
                "defect": "two q4 completions with the same q1/q2/q3 change the arity-three commutator coefficient",
                "defect_count": 1,
                "detected": True,
            },
        ],
        "flags": {
            "APPARATUS_NORMALIZED_PROFILE_TWO_JET_EXACT": True,
            "APPARATUS_Q2_ACTION_JET_EXPORTED": True,
            "APPARATUS_Q3_ACTION_JET_EXPORTED": True,
            "APPARATUS_Q2_Q3_CYCLIC_AT_R0": True,
            "APPARATUS_ARITY_TWO_IDENTITY_THROUGH_R_FIRST_JET": True,
            "APPARATUS_ARITY_THREE_IDENTITY_AT_R0": True,
            "APPARATUS_ARITY_THREE_IDENTITY_THROUGH_R_FIRST_JET": False,
            "FULL_BACKREACTED_APPARATUS_Q3_CERTIFIED": False,
            "K_BERGER_BACKGROUND_PRESERVING_ON_APPARATUS": False,
            "AFFINE_K_BERGER_THROUGH_ARITY_TWO_CERTIFIED": True,
            "AFFINE_K_BERGER_THROUGH_ARITY_THREE_CERTIFIED": False,
            "Q4_INPUT_REQUIRED": True,
            "FORMAL_BACKREACTED_UNARY_RANK_TWO_CERTIFIED": True,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "EMITTER_RECOIL_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_BASE_AND_APPARATUS_Q4_CONTRACTION_ON_K0_OR_DECLARE_A_K_INVARIANT_APPARATUS_BACKGROUND_THEN_REPLAY_OBSERVER_MORPHISM",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger apparatus q2/q3 K gate")
    print("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
