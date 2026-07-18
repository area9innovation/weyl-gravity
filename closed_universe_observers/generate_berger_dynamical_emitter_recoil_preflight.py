#!/usr/bin/env python3
"""Fix detector recoil order and certify its remaining evaluation input gate."""

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
CERTIFICATE = PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE.json"
SCHEMA = PACKAGE / "schema/berger-dynamical-emitter-recoil-order-and-input-gate-v1.schema.json"
REPORT = PACKAGE / "reports/berger-dynamical-emitter-recoil-order-and-input-gate.md"
DEPENDENCIES = {
    "rank_two": PACKAGE / "certificates/BERGER_DYNAMICAL_EMITTER_CAUCHY_RANK_TWO.json",
    "causal_chain": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY.json",
    "unary_recoil": PACKAGE / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
}
SOURCE_FILES = {
    "producer": Path(__file__),
    "verifier": PACKAGE / "verify_berger_dynamical_emitter_recoil_preflight.py",
    "tests": PACKAGE / "tests/test_berger_dynamical_emitter_recoil_preflight.py",
    "schema": SCHEMA,
    "report": REPORT,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recoil_order_audit(*, delete_cubic: bool = False, insert_quadratic: bool = False) -> dict[str, Any]:
    """Expand emitter-data to Maxwell response through absolute order g^3."""
    p, e0, e1, v0, v1, g = sp.symbols("p e0 e1 v0 v1 g", nonzero=True)
    operator0 = sp.diag(p, e0, e1)
    coupling = sp.Matrix([[0, -v0, -v1], [-v0, 0, 0], [-v1, 0, 0]])
    green0 = operator0.inv()
    coefficients = [
        green0,
        -green0 * coupling * green0,
        green0 * coupling * green0 * coupling * green0,
        -green0 * coupling * green0 * coupling * green0 * coupling * green0,
    ]
    if delete_cubic:
        coefficients[3] = sp.zeros(3)
    if insert_quadratic:
        coefficients[2] = coefficients[2].copy()
        coefficients[2][0, 1] += 1
    candidate = sum((g**power * value for power, value in enumerate(coefficients)), sp.zeros(3))
    left = sp.expand((operator0 + g * coupling) * candidate - sp.eye(3))
    right = sp.expand(candidate * (operator0 + g * coupling) - sp.eye(3))
    defects = sum(
        int(sp.simplify(value.coeff(g, power)) != 0)
        for matrix in (left, right)
        for value in matrix
        for power in range(4)
    )
    leading = [sp.factor(coefficients[1][0, column]) for column in (1, 2)]
    quadratic = [sp.factor(coefficients[2][0, column]) for column in (1, 2)]
    cubic = [sp.factor(coefficients[3][0, column]) for column in (1, 2)]
    expected_cubic = [
        sp.factor(leading[column] * (v0**2 / (p * e0) + v1**2 / (p * e1)))
        for column in range(2)
    ]
    return {
        "left_right_inverse_defect_count_through_g3": defects,
        "emitter_to_Maxwell_leading_g1": [sp.sstr(value) for value in leading],
        "emitter_to_Maxwell_absolute_g2": [sp.sstr(value) for value in quadratic],
        "emitter_to_Maxwell_first_recoil_g3": [sp.sstr(value) for value in cubic],
        "expected_first_recoil_g3": [sp.sstr(value) for value in expected_cubic],
        "absolute_g2_term_zero": all(value == 0 for value in quadratic),
        "cubic_matches_leading_times_relative_g2_self_energy": all(sp.simplify(left_value - right_value) == 0 for left_value, right_value in zip(cubic, expected_cubic, strict=True)),
    }


def preparation_underdetermination_audit() -> dict[str, Any]:
    """Show leading normalization does not determine the recoil functional."""
    c = sp.symbols("c", nonzero=True)
    u0, u1 = sp.Matrix([1, 0]), sp.Matrix([1, 1])
    leading = sp.Matrix([[1, 0]])
    recoil = sp.Matrix([[1, c]])
    leading_values = [sp.simplify((leading * value)[0]) for value in (u0, u1)]
    recoil_values = [sp.simplify((recoil * value)[0]) for value in (u0, u1)]
    return {
        "preparations": [[str(item) for item in value] for value in (u0, u1)],
        "leading_values": [sp.sstr(value) for value in leading_values],
        "recoil_values": [sp.sstr(value) for value in recoil_values],
        "same_nonzero_leading_response": leading_values == [1, 1],
        "different_recoil_response": sp.simplify(recoil_values[1] - recoil_values[0]) != 0,
    }


def formal_rank_stability_audit(*, erase_second_leading_diagonal: bool = False) -> dict[str, Any]:
    """Retain the exact leading determinant as the recoil-ring constant term."""
    kappa0, kappa1, mu, epsilon = sp.symbols("kappa_0 kappa_1 mu epsilon", nonzero=True)
    r00, r01, r10, r11 = sp.symbols("r_00 r_01 r_10 r_11")
    leading = sp.Matrix([[kappa0, 0], [mu, 0 if erase_second_leading_diagonal else kappa1]])
    recoil = sp.Matrix([[r00, r01], [r10, r11]])
    determinant = sp.expand((leading + epsilon * recoil).det())
    constant = sp.factor(determinant.coeff(epsilon, 0))
    return {
        "formal_determinant": sp.sstr(determinant),
        "constant_term": sp.sstr(constant),
        "constant_term_nonzero": constant != 0,
        "rank_two_over_formal_recoil_ring": constant != 0,
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["rank_two"]["flags"]["DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_CERTIFIED"] is not True:
        raise AssertionError("dynamical-emitter rank input drifted")
    if values["causal_chain"]["flags"]["108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2_CERTIFIED"] is not True:
        raise AssertionError("causal-chain input drifted")
    if values["unary_recoil"]["flags"]["FIRST_FORMAL_EMITTER_RECOIL_GREEN_OPERATOR_COMPUTED"] is not True:
        raise AssertionError("formal recoil input drifted")
    order = recoil_order_audit()
    missing_cubic = recoil_order_audit(delete_cubic=True)
    spurious_quadratic = recoil_order_audit(insert_quadratic=True)
    underdetermination = preparation_underdetermination_audit()
    rank_stability = formal_rank_stability_audit()
    rank_mutation = formal_rank_stability_audit(erase_second_leading_diagonal=True)
    if order["left_right_inverse_defect_count_through_g3"] or not order["absolute_g2_term_zero"] or not order["cubic_matches_leading_times_relative_g2_self_energy"]:
        raise AssertionError("detector recoil order audit failed")
    if not missing_cubic["left_right_inverse_defect_count_through_g3"] or not spurious_quadratic["left_right_inverse_defect_count_through_g3"]:
        raise AssertionError("detector recoil order mutation rail failed")
    if not underdetermination["same_nonzero_leading_response"] or not underdetermination["different_recoil_response"]:
        raise AssertionError("preparation underdetermination audit failed")
    if not rank_stability["rank_two_over_formal_recoil_ring"] or rank_mutation["rank_two_over_formal_recoil_ring"]:
        raise AssertionError("formal recoil rank-stability audit failed")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL preflight corrects the recoil order for records generated by free emitter Cauchy data. The leading emitter-to-Maxwell record is absolute order g. Bipartite A-K coupling parity forces the absolute g^2 coefficient to vanish; the first feedback of Maxwell onto the emitters and back to Maxwell is absolute order g^3, equivalently a relative g^2 correction. For fixed preparation u_b its exact operator is sum_c Q_a[d G_A,ret g_c delta h_c G_Ec,ret g_c h_c d G_A,ret g_b delta(h_b K_b^(0))]. A two-emitter fixture verifies both inverse orders through g^3, the zero quadratic term, and the cubic coefficient equal to the leading transfer times the relative self-energy. The coefficient is not numerically evaluated: the rank theorem exports only an existence/first-nonzero-basis rule and nonzero kappa_b, not explicit compact preparation profiles, exact switch functions, or their Berger massive-Green images. Two preparations can have the same leading response and different recoil response, so the missing data are material. This does not demote leading rank two, include emitter stress/clock backreaction, promote finite-parameter or all-orders Green hyperbolicity, construct the full apparatus Dirac bracket, or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-dynamical-emitter-recoil-order-and-input-gate-v1",
        "result_id": "BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE",
        "setting_id": values["rank_two"]["setting_id"],
        "claim_status": "FIRST_RECOIL_IS_ABSOLUTE_G3_OPERATOR_COMPUTED_NUMERICAL_COEFFICIENT_INPUT_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "order_audit": order,
        "detector_recoil_operator": {
            "leading_column_b": "M_ab^(1)=Q_a[d G_A,ret g_b delta(h_b K_b^(0))]",
            "absolute_g2": "zero by A-K bipartite block parity",
            "absolute_g3": "Delta M_ab^(3)=sum_c Q_a[d G_A,ret g_c delta h_c G_Ec,ret g_c h_c d G_A,ret g_b delta(h_b K_b^(0))]",
            "relative_order": "Delta M^(3) is relative order g_c^2 with respect to the leading g_b column",
            "same_sided_support": "all displayed Green factors are retarded and switches are local",
        },
        "evaluation_input_gate": {
            "underdetermination_fixture": underdetermination,
            "available": ["existence-level compact localized u_0,u_1", "nonzero leading kappa_0,kappa_1", "qualitative switch support order", "formal same-sided Green operators"],
            "missing": ["serialized compact Cauchy profiles u_0,u_1", "exact normalized functions h_0,h_1", "evaluated Berger massive-two-form Green images on those profiles", "the resulting detector smearing integrals"],
            "consequence": "the operator is certified but no numerical or closed-form detector coefficient follows from the present artifacts",
        },
        "formal_rank_stability": rank_stability,
        "mutation_results": [
            {"name": "delete_absolute_g3_term", "detected": missing_cubic["left_right_inverse_defect_count_through_g3"] > 0, "audit": missing_cubic},
            {"name": "insert_spurious_absolute_g2_emitter_to_Maxwell_term", "detected": spurious_quadratic["left_right_inverse_defect_count_through_g3"] > 0, "audit": spurious_quadratic},
            {"name": "erase_second_leading_diagonal_before_recoil", "detected": not rank_mutation["rank_two_over_formal_recoil_ring"], "audit": rank_mutation},
        ],
        "flags": {
            "EMITTER_TO_DETECTOR_ABSOLUTE_G2_TERM_ZERO_CERTIFIED": True,
            "FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED": True,
            "FIRST_DETECTOR_RECOIL_RELATIVE_G2_OPERATOR_COMPUTED": True,
            "DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED": False,
            "DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_RETAINED": True,
            "EMITTER_STRESS_BACKREACTION_INCLUDED": False,
            "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED": False,
            "FULL_APPARATUS_DIRAC_BRACKET_CERTIFIED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXPORT_EXPLICIT_COMPACT_U0_U1_AND_H0_H1_THEN_EVALUATE_DELTA_M_AB_ABSOLUTE_G3",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES.values()]},
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
        raise SystemExit("stale dynamical-emitter recoil preflight")
    print("BERGER_DYNAMICAL_EMITTER_RECOIL_ORDER_AND_INPUT_GATE generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
