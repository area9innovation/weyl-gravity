#!/usr/bin/env python3
"""Exact fixed-action counterflow component and round-limit disposition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json"

IMPORTS = {
    "positive_clock_action": (
        "d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json",
        "35e1bb8a56b0591b3dd00aa8f22c328ad826ecd341c290564cfd1a68fcc3e687",
        "POSITIVE_BERGER_CLOCK_BACKGROUND",
        "bb5738d6e3e30a68adcc9a70c35dac089079e3db",
    ),
    "trace_charge_preflight_and_round_boundary": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1.json",
        "2b578967ece7a2e6a8079c8fd84665ac40cf2b7e0aeef41d96882553c35115ea",
        "TWO_PHASE_COUNTERFLOW_TRACE_CHARGE_PREFLIGHT_V1",
        "d6d54a6efaa30ffe48dd7b9718c1954fa4ea514b",
    ),
    "causal_parent": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1.json",
        "7d969e7e630f793dfe12fe07b0e98a67b2543f9aa85fa03277e491fb00296db7",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
    "causal_parent_payload": (
        "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1.json",
        "7c73705cc07062baf652c9cc0cb0977beda2a96d5b642fa186d6bfaeae01db57",
        "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_PAYLOAD_V1",
        "951e88307abbea0996513773a33e66b37555272b",
    ),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _q(value: sp.Expr) -> str:
    return str(sp.factor(sp.cancel(value)))


def _load_imports() -> tuple[dict[str, Any], dict[str, Any]]:
    records: dict[str, Any] = {}
    values: dict[str, Any] = {}
    for role, (relative, expected, result_id, source_commit) in IMPORTS.items():
        path = ROOT / relative
        actual = _sha(path)
        value = json.loads(path.read_text())
        if actual != expected or value.get("result_id") != result_id:
            raise AssertionError(f"{role} import drifted")
        records[role] = {
            "path": relative,
            "sha256": actual,
            "result_id": result_id,
            "source_commit": source_commit,
            "oracle_fields_consumed": [],
        }
        values[role] = value

    preflight = values["trace_charge_preflight_and_round_boundary"]
    parent = values["causal_parent"]
    if preflight["terminal_verdict"]["selected_Berger"] != "PASSED_FIXED_RELATIVE_CHARGE_BERGER_STRATUM":
        raise AssertionError("selected Berger input is not certified")
    if preflight["terminal_verdict"]["cylinder"] != "OBSTRUCTED_NEGATIVE_REAL_TRACE_MODE":
        raise AssertionError("round-cylinder boundary was not imported")
    if parent["terminal_verdict"]["result_state"] != "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT":
        raise AssertionError("causal parent is not certified")
    return records, values


def _stationary_system() -> dict[str, Any]:
    q, x, energy = sp.symbols("q x C", real=True)
    alpha_b = sp.Integer(5)
    m2 = -sp.Rational(1, 6)
    v0 = sp.Rational(119, 1920)

    bach = [
        (1 - q) ** 2 * x**2 / 6,
        (1 - q) * (1 - 3 * q) * x**2 / 6,
        (1 - q) * (5 * q - 1) * x**2 / 6,
    ]
    scalar = (4 - q) * x / 2
    equations = [
        sp.factor(alpha_b * bach[0] + m2 * scalar / 2 - energy / 2 - v0),
        sp.factor(alpha_b * bach[1] - m2 * q * x / 4 - energy / 2 + v0),
        sp.factor(alpha_b * bach[2] + m2 * (3 * q - 4) * x / 4 - energy / 2 + v0),
    ]
    primitive = [sp.expand(1920 * row) for row in equations]
    groebner = sp.groebner(primitive, energy, x, q, order="lex")
    expected_groebner = [
        sp.expand(1920 * energy - 12160 * q**2 + 16136 * q - 4095),
        sp.expand(160 * x - 3200 * q**2 + 4280 * q - 961),
        sp.expand((q - 1) * (16 * q - 5) * (40 * q - 9)),
    ]
    for expected in expected_groebner:
        if groebner.reduce(expected)[1] != 0:
            raise AssertionError("stationary elimination basis drifted")
    expected_ideal = sp.groebner(expected_groebner, energy, x, q, order="lex")
    if any(expected_ideal.reduce(row)[1] != 0 for row in primitive):
        raise AssertionError("declared elimination basis does not generate every stationary row")

    roots = [sp.Rational(9, 40), sp.Rational(5, 16), sp.Integer(1)]
    solutions: list[dict[str, Any]] = []
    jacobian = sp.Matrix(equations).jacobian([energy, x, q])
    jacobian_det = sp.factor(jacobian.det())
    for q0 in roots:
        x0 = sp.factor(20 * q0**2 - sp.Rational(107, 4) * q0 + sp.Rational(961, 160))
        energy0 = sp.factor((12160 * q0**2 - 16136 * q0 + 4095) / 1920)
        substitution = {q: q0, x: x0, energy: energy0}
        if any(sp.factor(row.subs(substitution)) != 0 for row in equations):
            raise AssertionError("stationary solution failed substitution")
        det0 = sp.factor(jacobian_det.subs(substitution))
        if det0 == 0:
            raise AssertionError("stationary point is not simple")
        beta = sp.factor(alpha_b * bach[0].subs(substitution))
        curvature = sp.factor(scalar.subs(substitution))
        kinetic = sp.factor(3 * (beta - sp.Rational(3, 4) * energy0) / curvature)
        mass = sp.factor(beta - sp.Rational(3, 2) * energy0)
        lam2 = sp.factor(mass / kinetic)
        solutions.append(
            {
                "q": _q(q0),
                "x": _q(x0),
                "C": _q(energy0),
                "stationary_rank": 3,
                "jacobian_determinant": _q(det0),
                "physical_positive_domain": bool(q0 > 0 and x0 > 0 and energy0 > 0),
                "reduced_velocity_hessian": _q(2 * kinetic),
                "reduced_u_squared_coefficient": _q(mass),
                "lambda_squared": _q(lam2),
                "characteristic_multiplicity": "two_simple_roots",
                "Jordan_type": "1+1",
            }
        )

    selected = solutions[0]
    if selected != {
        "q": "9/40",
        "x": "1",
        "C": "9/16",
        "stationary_rank": 3,
        "jacobian_determinant": "217/192",
        "physical_positive_domain": True,
        "reduced_velocity_hessian": "1/4",
        "reduced_u_squared_coefficient": "-659/1920",
        "lambda_squared": "-659/240",
        "characteristic_multiplicity": "two_simple_roots",
        "Jordan_type": "1+1",
    }:
        raise AssertionError("selected component data drifted")

    return {
        "coordinates": {
            "q": "c_squared/a_squared",
            "x": "a^(-2)",
            "C": "mu_squared*Omega^2",
            "physical_domain": "q>0 and x>0 and C>0",
        },
        "fixed_action": {
            "alpha_B": "5",
            "alpha_R": "0",
            "M_P_squared": "-1/6",
            "V0": "119/1920",
            "phase_weights": ["f1_squared=2", "f2_squared=2"],
            "F": "4",
            "mu_squared": "1",
        },
        "orthonormal_stationary_rows_times_1920": [_q(row) for row in primitive],
        "elimination_basis": [_q(row) for row in expected_groebner],
        "squashing_separator": "(q-1)*(16*q-5)*(40*q-9)=0",
        "solutions": solutions,
        "physical_solution_count": 1,
        "selected_open_box": {
            "conditions": ["1/5<q<1/4", "3/4<x<5/4", "1/2<C<5/8"],
            "stationary_intersection": ["q=9/40", "x=1", "C=9/16"],
            "interpretation": "open ambient semialgebraic neighbourhood; its fixed-action stationary intersection is a singleton",
        },
        "component_theorem": {
            "real_physical_stationary_locus": "{(q,x,C)=(9/40,1,9/16)}",
            "selected_component_dimension": 0,
            "open_geometry_phase": False,
            "first_separator": "stationarity is lost in every punctured q-neighbourhood; the exact elimination invariant is the squashing separator",
        },
    }


def _charge_and_stabilizer() -> dict[str, Any]:
    r1, r2 = sp.symbols("r1 r2", positive=True, real=True)
    sum_eq = r1 + r2 - 4
    product_eq = r1 * r2 - 4
    resultant = sp.factor(sp.resultant(sum_eq, product_eq, r2))
    if resultant != -(r1 - 2) ** 2:
        raise AssertionError("fixed phase-weight uniqueness drifted")
    return {
        "fixed_action_weight_equations": ["f1_squared+f2_squared=4", "f1_squared*f2_squared=4"],
        "positive_solution": ["f1_squared=2", "f2_squared=2"],
        "weight_resultant": "-(f1_squared-2)^2 (resultant convention; zero locus is f1_squared=2)",
        "compact_charge_matrix": [[1], [1]],
        "compact_gauge_rank": 1,
        "relative_charge_rank": 1,
        "relative_phase_dimension": 1,
        "Q_diag": "0 by Gauss",
        "Q_rel": "nonzero on the selected unrestricted stationary background",
        "D": "charged global generator with H_D=Omega*Q_rel",
        "K": "D-Omega*R_rel; null Hamiltonian and background stabilizer",
        "D_K_degeneracy": "rank one span{D,R_rel} moment map with one-dimensional kernel span{K}",
        "fixed_Q_rel_leaf": "R_rel and D become presymplectic-null only after explicit fixed-charge restriction",
        "continuous_spatial_stabilizer": "SU(2)_L x U(1)_R",
        "stabilizer_dimension_proof": "the left SU(2) action contributes three generators; the biaxial equality a1=a2 adds one right U(1); q=9/40!=1 forbids the two extra right generators present only at the round point",
        "stabilizer_basis": ["L1", "L2", "L3", "R3", "K=D-Omega*R_rel"],
        "spatial_stabilizer_dimension": 4,
        "helical_stabilizer_dimension": 1,
        "residual_global_stabilizer_dimension": 5,
        "old_SO_4_2_receiver": "NO_CERTIFIED_MAP",
    }


def _round_disposition() -> dict[str, Any]:
    return {
        "same_action_round_stationarity": {
            "round_q": "1",
            "algebraic_solution": ["x=-119/160", "C=119/1920"],
            "physical_status": "OBSTRUCTED_NEGATIVE_SPATIAL_SCALE",
            "direct_cylinder_locus_conditions": ["C=2*M_P_squared=-1/3", "C=V0=119/1920"],
            "contradiction": "-1/3 != 119/1920",
        },
        "connected_component": {
            "selected_component": "singleton q=9/40",
            "path_to_round_q_1": False,
            "nearest_other_stationary_q_toward_round": "5/16",
            "open_stationary_gap": "9/40<q<5/16",
            "next_branch_x": "-2/5",
            "first_invariant_change": "positive spatial inverse scale x>0 is absent on the next stationary branch",
        },
        "imported_retuned_round_boundary": {
            "scope": "a separately retuned alpha_R=0 round stationary locus with C>0, not the fixed action above",
            "reduced_L2": "-3*C*dot_u^2/8-3*C*u^2/2",
            "velocity_hessian": "-3*C/4",
            "characteristic_roots": ["-2", "2"],
            "status": "OBSTRUCTED_NEGATIVE_REAL_TRACE_MODE",
            "not_recomputed": True,
        },
        "round_stabilizer_note": "round spatial isometry would jump from dimension 4 to 6, but no same-action positive stationary carrier reaches that stratum",
    }


def _payload(imports: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": "pure-weyl-two-phase-counterflow-background-component-round-disposition-payload-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "oracle_fields_consumed": [],
        "stationary_component_stratification": _stationary_system(),
        "charge_and_stabilizer_stratification": _charge_and_stabilizer(),
        "round_cylinder_disposition": _round_disposition(),
        "causal_transport": {
            "selected_point": "CERTIFIED_70_COMPONENT_SUPPORT_LOCAL_CAUSAL_BV_PARENT",
            "away_from_selected_stationary_point": "NO_CERTIFIED_MAP",
            "reason": "the fixed-action physical stationary geometry has no neighbouring point",
        },
        "content_sha256": "PENDING",
    }
    value["content_sha256"] = _digest({k: v for k, v in value.items() if k != "content_sha256"})
    return value


def _certificate(imports: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    terminal = {
        "result_state": "CERTIFIED_ISOLATED_PHYSICAL_BERGER_COMPONENT_AND_ROUND_NONINHERITANCE",
        "physical_stationary_component_dimension": 0,
        "open_fixed_action_geometry_family": False,
        "selected_causal_parent_retained": True,
        "same_action_round_stationary_background": False,
        "round_boundary_inherited": False,
    }
    boundary = {
        "establishes": [
            "complete exact fixed-action stationary locus in the declared Berger algebraic family",
            "unique positive stationary point and its constrained reduced inertia and simple characteristic roots",
            "relative-charge rank, D/K moment-map kernel and five-dimensional continuous global stabilizer",
            "absence of a same-action stationary path to the round cylinder",
            "strict separation between same-action nonstationarity and the imported retuned round trace obstruction",
        ],
        "does_not_establish": [
            "a causal parent away from the selected Berger point",
            "survival of the fifteen-generator SO(4,2) residual receiver",
            "nonlinear q2 stability, an Einstein-source map or a relational observable",
            "Hadamard data, a QME, particles, scattering, positivity or unitarity",
            "a no-go outside the fixed certified action and declared homogeneous Berger family",
        ],
    }
    return {
        "schema": "pure-weyl-two-phase-counterflow-background-component-round-disposition-v1",
        "result_id": "TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1",
        "result_state": terminal["result_state"],
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "imports": imports,
        "payload_ref": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": "PENDING_WRITE",
            "content_sha256": payload["content_sha256"],
        },
        "terminal_verdict": terminal,
        "claim_boundary": boundary,
        "claim_flags": {
            "EXACT_FIXED_ACTION_COMPONENT_CLASSIFICATION": True,
            "OPEN_FIXED_ACTION_GEOMETRY_PHASE": False,
            "SELECTED_70_COMPONENT_CAUSAL_PARENT": True,
            "CAUSAL_TRANSPORT_AWAY_FROM_SELECTED": False,
            "ROUND_SAME_ACTION_BACKGROUND": False,
            "SO_4_2_RECEIVER": False,
            "HADAMARD_OR_QUANTUM": False,
        },
        "content_hashes": {
            "stationary_sha256": _digest(payload["stationary_component_stratification"]),
            "charge_stabilizer_sha256": _digest(payload["charge_and_stabilizer_stratification"]),
            "round_sha256": _digest(payload["round_cylinder_disposition"]),
            "terminal_sha256": _digest(terminal),
            "boundary_sha256": _digest(boundary),
        },
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_payload = _digest({k: v for k, v in payload.items() if k != "content_sha256"})
    if payload["content_sha256"] != expected_payload or payload["oracle_fields_consumed"] != []:
        raise AssertionError("payload provenance failed")
    stationary = payload["stationary_component_stratification"]
    if stationary["physical_solution_count"] != 1 or stationary["component_theorem"]["selected_component_dimension"] != 0:
        raise AssertionError("component disposition drifted")
    if payload["round_cylinder_disposition"]["connected_component"]["path_to_round_q_1"]:
        raise AssertionError("round path was silently promoted")
    flags = certificate["claim_flags"]
    forbidden = ["OPEN_FIXED_ACTION_GEOMETRY_PHASE", "CAUSAL_TRANSPORT_AWAY_FROM_SELECTED", "ROUND_SAME_ACTION_BACKGROUND", "SO_4_2_RECEIVER", "HADAMARD_OR_QUANTUM"]
    if any(flags[key] for key in forbidden):
        raise AssertionError("claim boundary promoted")
    expected_hashes = {
        "stationary_sha256": _digest(payload["stationary_component_stratification"]),
        "charge_stabilizer_sha256": _digest(payload["charge_and_stabilizer_stratification"]),
        "round_sha256": _digest(payload["round_cylinder_disposition"]),
        "terminal_sha256": _digest(certificate["terminal_verdict"]),
        "boundary_sha256": _digest(certificate["claim_boundary"]),
    }
    if certificate["content_hashes"] != expected_hashes:
        raise AssertionError("certificate hash ledger drifted")


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    imports, _ = _load_imports()
    payload = _payload(imports)
    certificate = _certificate(imports, payload)
    validate(certificate, payload)
    return certificate, payload


def write() -> None:
    certificate, payload = build()
    PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    validate(certificate, payload)
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")


def check() -> None:
    certificate, payload = build()
    certificate["payload_ref"]["sha256"] = _sha(PAYLOAD)
    if json.loads(PAYLOAD.read_text()) != payload or json.loads(OUTPUT.read_text()) != certificate:
        raise AssertionError("stored component artifacts drifted")
    print("TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()


if __name__ == "__main__":
    main()
