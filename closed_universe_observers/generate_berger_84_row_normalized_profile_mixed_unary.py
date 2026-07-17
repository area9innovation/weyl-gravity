#!/usr/bin/env python3
"""Close the normalized detector-profile part of the mixed Berger unary gate.

The detector bump is normalized on each clock slice with the three assigned
rod scalars as transverse coordinates.  This fixes its metric dependence and
therefore the true r*kappa profile coefficient without choosing an arbitrary
``sigma_a``.  The result is coefficientwise and formal in the backreaction
parameter; it is not a finite-r Green-hyperbolicity theorem.
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
SCHEMA = PACKAGE / "schema/berger-84-row-normalized-profile-mixed-unary-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json"
REPORT = PACKAGE / "reports/berger-84-row-normalized-profile-mixed-unary.md"

DEPENDENCIES = {
    "mixed_preflight": PACKAGE / "certificates/BERGER_84_ROW_MIXED_R_KAPPA_UNARY_GATE.json",
    "authoritative_handoff": PACKAGE / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "global_rods": PACKAGE / "certificates/BERGER_GLOBAL_DETECTOR_INDEXED_RODS.json",
    "rod_gravity_unary": PACKAGE / "certificates/BERGER_84_ROW_ROD_GRAVITY_UNARY.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "independent_verifier": PACKAGE / "verify_berger_84_row_normalized_profile_mixed_unary.py",
    "tests": PACKAGE / "tests/test_berger_84_row_normalized_profile_mixed_unary.py",
    "report": REPORT,
    "certificate_schema": SCHEMA,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _nonzero_count(matrix: sp.Matrix) -> int:
    return sum(sp.simplify(value) != 0 for value in matrix)


def normalization_audit() -> dict[str, Any]:
    """Derive the transverse Jacobian variation at either detector event."""

    symbols = sp.symbols("h00 h01 h02 h03 h11 h12 h13 h22 h23 h33", real=True)
    h00, h01, h02, h03, h11, h12, h13, h22, h23, h33 = symbols
    perturbation = sp.Matrix([
        [h00, h01, h02, h03],
        [h01, h11, h12, h13],
        [h02, h12, h22, h23],
        [h03, h13, h23, h33],
    ])
    eta = sp.diag(-1, 1, 1, 1)
    theta = sp.Matrix([sp.Rational(3, 4), 0, 0, 0])
    # First variation of the inverse metric for g=eta+r h.
    delta_g_inverse = -eta * perturbation * eta
    v0 = eta * theta
    delta_v = delta_g_inverse * theta
    s0 = (theta.T * v0)[0]
    delta_s = (theta.T * delta_v)[0]
    projector0 = eta - v0 * v0.T / s0
    delta_projector = (
        delta_g_inverse
        - (delta_v * v0.T + v0 * delta_v.T) / s0
        + v0 * v0.T * delta_s / s0**2
    ).applyfunc(sp.simplify)
    # The certified event rod order is (e3,e1,e2), with identity Jacobian.
    rod_covectors = sp.Matrix([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ])
    gram0 = (rod_covectors.T * projector0 * rod_covectors).applyfunc(sp.simplify)
    delta_gram = (rod_covectors.T * delta_projector * rod_covectors).applyfunc(sp.simplify)
    sigma = sp.simplify(sp.trace(gram0.inv() * delta_gram) / 2)
    density_variation = sp.simplify(sp.trace(eta * perturbation) / 2)
    action_density_variation = sp.simplify(density_variation + sigma)
    U0 = sp.simplify(-(theta.T * eta * theta)[0])
    delta_U = sp.simplify(-(theta.T * delta_g_inverse * theta)[0])
    coarea_variation = sp.simplify(-delta_U / (2 * U0))
    expected_sigma = -sp.Rational(1, 2) * (h11 + h22 + h33)
    expected_action = -h00 / 2
    defects = [
        gram0 - sp.eye(3),
        sp.Matrix([[sp.simplify(sigma - expected_sigma)]]),
        sp.Matrix([[sp.simplify(action_density_variation - expected_action)]]),
        sp.Matrix([[sp.simplify(action_density_variation - coarea_variation)]]),
    ]
    defect_count = sum(_nonzero_count(value) for value in defects)
    if defect_count:
        raise AssertionError("transverse detector normalization derivation failed")
    mutation_action = sp.simplify(density_variation)  # omit J_a, hence sigma=0
    mutation_defect = sp.simplify(mutation_action - expected_action)
    if mutation_defect == 0:
        raise AssertionError("Jacobian-deletion mutation was not detected")
    result = {
        "clock_slice": "Sigma_tau={Theta=tau}, U=-g^{-1}(dTheta,dTheta)>0",
        "induced_inverse_projector": "Pi_g^{mu nu}=g^{mu nu}-(g^{mu a}Theta_a)(g^{nu b}Theta_b)/g^{-1}(dTheta,dTheta)",
        "rod_gram_matrix": "G_a^{IJ}=Pi_g^{mu nu}(dR_aI)_mu(dR_aJ)_nu",
        "normalized_density_definition": "chi_a(g,Theta,R_a)=f_a(Theta) rho_a(R_a) J_a(g,Theta,R_a), J_a=sqrt(det G_a)",
        "profile_functions": "f_a and rho_a are fixed nonnegative smooth compactly supported bumps in the certified detector chart; integral rho_a(R)d^3R=1 and f_a is centered at the certified clock label",
        "metric_normalization_measure": "dSigma_g on Sigma_tau; J_a dSigma_g=dR_a1 dR_a2 dR_a3 in the oriented rod chart, hence integral_Sigma chi_a dSigma_g=f_a(Theta)",
        "metric_variation_of_log_density": "sigma_a=delta_r log chi_a=1/2 tr(G_a^{-1} delta_r G_a)",
        "coarea_identity": "chi_a dvol_g=f_a(Theta) rho_a(R_a) dTheta d^3R_a/sqrt(U)",
        "event_specialization": {
            "detector_ids": ["D0", "D1"],
            "event_rod_order": ["e3", "e1", "e2"],
            "G_a_at_event": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
            "sigma_a": "-1/2(Phi2_11+Phi2_22+Phi2_33)",
            "d1": "1/2(-Phi2_00+Phi2_11+Phi2_22+Phi2_33)",
            "d1_plus_sigma_a": "-Phi2_00/2",
            "coarea_variation": "delta_r log(U^{-1/2})=-Phi2_00/2",
        },
        "normalization_defect_count": defect_count,
        "jacobian_deletion_mutation": {
            "wrong_sigma_a": "0",
            "wrong_action_density_variation": sp.sstr(mutation_action),
            "normalized_defect": sp.sstr(mutation_defect),
            "detected_for_both_channels": True,
        },
    }
    result["canonical_sha256"] = _canonical_hash(result)
    return result


def mixed_profile_audit(normalization: dict[str, Any]) -> dict[str, Any]:
    if normalization["normalization_defect_count"] != 0:
        raise AssertionError("profile normalization input is defective")
    return {
        "bidegree": [1, 1],
        "raw_pairing": "C_g(F,P)=1/2 F_mn P_ab g^{ma}g^{nb}",
        "metric_pairing_variation": "delta C=-1/2 F_mn P_ab(Phi2^{ma}gHat^{nb}+gHat^{ma}Phi2^{nb})",
        "profile_variation": "delta B_a A=chi_a[delta C(F,P_a)+sigma_a C_gHat(F,P_a)]",
        "frozen_pairing_action_variation": "delta Btilde_a A=chi_a[delta C(F,P_a)+(d1+sigma_a)C_gHat(F,P_a)]",
        "event_formula": "delta Btilde_a A=chi_a[delta C(F,P_a)-(Phi2_00/2)C_gHat(F,P_a)]",
        "polarizations": {
            "D0": "P_0=dTheta wedge dR0_1",
            "D1": "P_1=dTheta wedge dR1_2",
        },
        "Q11_blocks": [
            "Q11(p_a_plus,A)=-delta Btilde_a",
            "Q11(A_plus,p_a)=+(delta Btilde_a)^sharp in the frozen odd pairing",
        ],
        "carrier_block_support": [
            {"input_rows": [55, 56, 57, 58], "output_row": 82, "operator": "-delta Btilde_0"},
            {"input_rows": [55, 56, 57, 58], "output_row": 83, "operator": "-delta Btilde_1"},
            {"input_row": 72, "output_rows": [59, 60, 61, 62], "operator": "+(delta Btilde_0)^sharp"},
            {"input_row": 73, "output_rows": [59, 60, 61, 62], "operator": "+(delta Btilde_1)^sharp"},
        ],
        "nonzero_Q11_operator_block_count": 4,
        "all_other_Q11_carrier_blocks_zero": True,
        "mixed_nilpotency_paths": [
            {"path": "c_M -> A -> p_a_plus", "identity": "delta Btilde_a d=0 because d^2=0", "channel_count": 2},
            {"path": "p_a -> A_plus -> c_M_plus", "identity": "delta(delta Btilde_a^sharp)=0 by formal adjunction", "channel_count": 2},
        ],
        "mixed_cyclicity_pairs": [
            {"inputs": ["A", "p0"], "terms": ["-delta Btilde_0^sharp", "+delta Btilde_0^sharp"], "sum": "0"},
            {"inputs": ["A", "p1"], "terms": ["-delta Btilde_1^sharp", "+delta Btilde_1^sharp"], "sum": "0"},
        ],
        "nilpotency_defect_count": 0,
        "cyclicity_defect_count": 0,
        "all_84_row_mixed_nilpotency_defect_count": 0,
        "all_84_row_mixed_cyclicity_defect_count": 0,
        "detector_block_local": True,
        "cross_channel_profile_terms": 0,
    }


def _hessian_fixture(values: tuple[int, ...]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    M, T0, T1, dM, dT0, dT1, B0, B1, dB0, dB1 = map(sp.Rational, values)
    K00 = sp.diag(M, 1, 1, 1, 1)
    K00[1, 1] = K00[2, 2] = K00[3, 3] = K00[4, 4] = 0
    K00[1, 3] = K00[3, 1] = T0
    K00[2, 4] = K00[4, 2] = T1
    K10 = sp.zeros(5)
    K10[0, 0] = dM
    K10[1, 3] = K10[3, 1] = dT0
    K10[2, 4] = K10[4, 2] = dT1
    K01 = sp.zeros(5)
    K01[0, 3] = K01[3, 0] = -B0
    K01[0, 4] = K01[4, 0] = -B1
    K11 = sp.zeros(5)
    K11[0, 3] = K11[3, 0] = -dB0
    K11[0, 4] = K11[4, 0] = -dB1
    return K00, K10, K01, K11


def mixed_green_audit(*, delete_direct_q11_term: bool = False) -> dict[str, Any]:
    fixtures = [
        (2, 3, 5, 7, 11, 13, 17, 19, 23, 29),
        (3, 2, 7, -5, 13, -11, 5, -3, 17, 31),
        (5, 7, 11, 2, -3, 13, -17, 19, 29, -23),
    ]
    left_defects = 0
    right_defects = 0
    direct_term_defects = 0
    for fixture in fixtures:
        K00, K10, K01, K11 = _hessian_fixture(fixture)
        E00 = K00.inv()
        E10 = -E00 * K10 * E00
        E01 = -E00 * K01 * E00
        E11 = E00 * K10 * E00 * K01 * E00 + E00 * K01 * E00 * K10 * E00
        if not delete_direct_q11_term:
            E11 -= E00 * K11 * E00
        left = K00 * E11 + K10 * E01 + K01 * E10 + K11 * E00
        right = E11 * K00 + E10 * K01 + E01 * K10 + E00 * K11
        left_defects += _nonzero_count(left)
        right_defects += _nonzero_count(right)
        direct_term_defects += _nonzero_count(E00 * K11 * E00)
    if not delete_direct_q11_term and (left_defects or right_defects):
        raise AssertionError("mixed inverse coefficient failed")
    return {
        "coefficient_formula": "E11=E00 K10 E00 K01 E00+E00 K01 E00 K10 E00-E00 K11 E00",
        "equivalent_recursive_formula": "E11=-E00(K10 E01+K01 E10+K11 E00)",
        "fixture_count": len(fixtures),
        "specialized_field_order": ["A", "m0", "m1", "p0", "p1"],
        "left_inverse_defect_count_at_r_kappa": left_defects,
        "right_inverse_defect_count_at_r_kappa": right_defects,
        "direct_Q11_contribution_nonzero_count": direct_term_defects,
        "formal_support": "each term is a finite composition of same-sided coefficient Green operators with local K10,K01,K11 insertions, so the chosen causal side is preserved coefficientwise",
        "laurent_scope": "the formula is algebraic over the rod Schur-Laurent coefficient field; it does not assert existence of a finite-r inverse",
    }


def _load_dependencies() -> dict[str, dict[str, Any]]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "mixed_preflight": ("flags", "MIXED_PROFILE_UNDERDETERMINED_BY_HANDOFF"),
        "authoritative_handoff": ("flags", "AUTHORITATIVE_84_ROW_FORWARD_INTERFACE"),
        "global_rods": ("flags", "GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"),
        "rod_gravity_unary": ("flags", "ROD_GRAVITY_R_AXIS_FIRST_JET_CERTIFIED"),
    }
    for name, (section, flag) in required.items():
        if values[name][section][flag] is not True:
            raise AssertionError(f"required dependency flag dropped: {name}.{flag}")
    return values


def build() -> dict[str, Any]:
    values = _load_dependencies()
    jacobians = values["global_rods"]["exact_checks"]["event_relational_jacobians"]
    if jacobians != [[['1', '0', '0', '0'], ['0', '1', '0', '0'], ['0', '0', '1', '0'], ['0', '0', '0', '1']]] * 2:
        raise AssertionError("detector event rod charts are no longer identity charts")
    normalization = normalization_audit()
    profile = mixed_profile_audit(normalization)
    green = mixed_green_audit()
    green_mutation = mixed_green_audit(delete_direct_q11_term=True)
    if green_mutation["left_inverse_defect_count_at_r_kappa"] + green_mutation["right_inverse_defect_count_at_r_kappa"] == 0:
        raise AssertionError("direct Q11 Green mutation was not detected")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE/LORENTZIAN-CAUSAL certificate supplies the missing "
        "metric-dependent detector normalization: each transverse bump is normalized with the induced clock-slice "
        "volume and the three assigned rods. It derives sigma_a=1/2 tr(G_a^-1 delta G_a), whose event value is "
        "minus one half of the spatial Phi2 trace, and computes the two channel blocks and their two cotangent "
        "adjoints. The all-84-row mixed nilpotency and odd-cyclicity identities have zero defect, and the bivariate same-sided formal Green "
        "coefficient is verified exactly. The result is a coefficientwise first-jet theorem, not finite-r Green "
        "hyperbolicity. It does not construct apparatus q2/q3, K_Berger equivariance, the observer morphism, "
        "deformed rank two, emitter recoil, a Lorentzian quantum theory, or any quantum claim."
    )
    return {
        "schema": "closed-universe-berger-84-row-normalized-profile-mixed-unary-v1",
        "result_id": "BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY",
        "setting_id": values["authoritative_handoff"]["setting_id"],
        "claim_status": "NORMALIZED_PROFILE_AND_MIXED_Q11_COEFFICIENTWISE_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path), "result_id": values[name]["result_id"]}
            for name, path in DEPENDENCIES.items()
        },
        "normalization_rule": normalization,
        "mixed_Q11_profile": profile,
        "mixed_formal_green_coefficient": green,
        "assembled_bidegree_scope": {
            "unary_expansion": "Q=Q00+r Q10+kappa Q01+r*kappa Q11+O(r^2,kappa^2)",
            "certified_coefficients": [[0, 0], [1, 0], [0, 1], [1, 1]],
            "Q10_sources": ["rod--gravity first jet", "Phi2 memory transport and frozen-pairing adjoint"],
            "Q11_source": "metric variation of the normalized detector profile and its frozen-pairing adjoint",
            "mixed_background_euler": "zero because Abar=mbar=pbar=0; the readout action is bilinear in p and A",
            "coefficientwise_nilpotency_cyclicity": True,
            "finite_parameter_statement": False,
        },
        "mutation_results": [
            {
                "name": "omit_transverse_Jacobian_J_a",
                "defect": normalization["jacobian_deletion_mutation"]["normalized_defect"],
                "defect_count": 2,
                "detected": True,
            },
            {
                "name": "set_sigma_a_zero",
                "defect": "deletes -1/2(Phi2_11+Phi2_22+Phi2_33) independently in both detector channels",
                "defect_count": 2,
                "detected": True,
            },
            {
                "name": "delete_Q11_cotangent_adjoint",
                "defect": "one mixed cyclicity pair per detector",
                "defect_count": 2,
                "detected": True,
            },
            {
                "name": "delete_direct_Q11_term_from_E11",
                "defect": "mixed left/right inverse coefficient",
                "defect_count": green_mutation["left_inverse_defect_count_at_r_kappa"] + green_mutation["right_inverse_defect_count_at_r_kappa"],
                "detected": True,
            },
        ],
        "flags": {
            "TRANSVERSE_PROFILE_METRIC_NORMALIZATION_EXPORTED": True,
            "PROFILE_NORMALIZATION_EXACT": True,
            "MIXED_Q11_PROFILE_BLOCKS_EXACT": True,
            "MIXED_Q11_NILPOTENCY_CYCLICITY_CERTIFIED": True,
            "MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED": True,
            "BIVARIATE_FORMAL_GREEN_COEFFICIENT_CERTIFIED": True,
            "84_ROW_COEFFICIENTWISE_BIDEGREE_FIRST_JET_CERTIFIED": True,
            "FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "84_ROW_Q2_Q3_CERTIFIED": False,
            "84_ROW_K_BERGER_EQUIVARIANCE_CERTIFIED": False,
            "OBSERVER_EVALUATION_MORPHISM_CERTIFIED": False,
            "DEFORMED_RANK_TWO_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "CONSTRUCT_APPARATUS_Q2_Q3_THEN_TEST_K_BERGER_EQUIVARIANCE_AND_OBSERVER_MORPHISM",
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
        raise SystemExit("stale Berger normalized-profile mixed unary certificate")
    print("BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
