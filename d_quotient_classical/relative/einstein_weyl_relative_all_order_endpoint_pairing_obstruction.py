#!/usr/bin/env python3
"""Certify the all-order pairing obstruction and its minimal compensated endpoint."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from bridge.einstein_sector.product_taylor_engine import COORDINATES
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-all-order-endpoint-pairing-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-all-order-endpoint-pairing-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_all_order_endpoint_pairing_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_all_order_endpoint_pairing_obstruction.py"
DEPENDENCIES = {
    "endpoint": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json",
    "linear_triangle": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "current_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
    "order_three": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1.json",
    "target_layout": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json",
}
NAMES = ("H", "P_x", "J_1", "J_2", "J_3")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _sstr(value: sp.Expr) -> str:
    return sp.sstr(sp.trigsimp(sp.simplify(value)))


def _geometry() -> dict[str, Any]:
    _, _, theta, phi = COORDINATES
    metric = sp.diag(-1, 1, 1, sp.sin(theta) ** 2)
    field = sp.zeros(4)
    field[2, 3] = sp.sin(theta)
    field[3, 2] = -field[2, 3]
    vectors = stabilizer_vectors()
    compensators = {
        "H": sp.S.Zero,
        "P_x": sp.S.Zero,
        "J_1": -sp.cos(theta),
        "J_2": -sp.sin(theta) * sp.sin(phi),
        "J_3": sp.sin(theta) * sp.cos(phi),
    }

    raw = sp.Matrix(
        len(NAMES),
        len(NAMES),
        lambda row, column: sp.trigsimp(
            (vectors[NAMES[row]].T * metric * vectors[NAMES[column]])[0]
        ),
    )
    correction = sp.Matrix(
        len(NAMES),
        len(NAMES),
        lambda row, column: compensators[NAMES[row]] * compensators[NAMES[column]],
    )
    corrected = raw + correction
    expected = sp.diag(-1, 1, 1, 1, 1)
    if corrected.applyfunc(sp.trigsimp) != expected:
        raise AssertionError(f"compensated Gram matrix drifted: {corrected}")

    reducibility: dict[str, list[str]] = {}
    for name in NAMES:
        residual = []
        for mu, coordinate in enumerate(COORDINATES):
            value = sp.diff(compensators[name], coordinate)
            value += sum(vectors[name][nu] * field[nu, mu] for nu in range(4))
            residual.append(_sstr(value))
        if residual != ["0", "0", "0", "0"]:
            raise AssertionError(f"Maxwell compensator for {name} is not exact")
        reducibility[name] = residual

    raw_j1 = sp.trigsimp(raw[NAMES.index("J_1"), NAMES.index("J_1")])
    raw_j1_derivative = sp.trigsimp(sp.diff(raw_j1, theta))
    if raw_j1 != sp.sin(theta) ** 2 or raw_j1_derivative == 0:
        raise AssertionError("J_1 Gram witness drifted")
    return {
        "metric": [_sstr(metric[row, column]) for row in range(4) for column in range(4)],
        "magnetic_field_F_theta_phi": _sstr(field[2, 3]),
        "vectors": {
            name: [_sstr(component) for component in vectors[name]] for name in NAMES
        },
        "compensators": {name: _sstr(compensators[name]) for name in NAMES},
        "maxwell_reducibility_residuals": reducibility,
        "raw_gram": [[_sstr(raw[row, column]) for column in range(5)] for row in range(5)],
        "corrected_gram": [
            [_sstr(corrected[row, column]) for column in range(5)]
            for row in range(5)
        ],
        "witness": {
            "X": "J_1",
            "Y": "J_1",
            "B0_XY": _sstr(raw_j1),
            "d_B0_XY": "2*sin(theta)*cos(theta)*dtheta",
            "nonzero_open_set": "0<theta<pi/2",
            "compact_test_form": "alpha=chi(t,x,theta,phi)*dt^dx^dphi with chi>=0 supported in 0<theta<pi/2",
        },
    }


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    endpoint = dependencies["endpoint"]
    if any(
        term["row"] == "lambda_cov_star"
        for record in endpoint["A2"]
        for term in record["target_terms"]
    ):
        raise AssertionError("declared diffeomorphism-only endpoint changed")
    triangle = dependencies["linear_triangle"]["global_endpoints"]
    if triangle["source_basis"] != [
        "partial_t",
        "partial_x",
        "J_1",
        "J_2",
        "J_3",
        "u1_constant",
    ]:
        raise AssertionError("global reducibility basis drifted")
    target_rows = {
        row["row_id"]: row
        for row in dependencies["target_layout"]["content"]["rows"]
    }
    if target_rows["lambda_cov"]["dual_row"] != target_rows["lambda_cov_star"]["index"]:
        raise AssertionError("Maxwell ghost/identity pairing drifted")

    geometry = _geometry()
    return {
        "schema": "pure-weyl-relative-all-order-endpoint-pairing-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "DIFFEO_ONLY_ENDPOINT_ALL_ORDER_OBSTRUCTED_COMPENSATED_ENDPOINT_IDENTIFIED",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": endpoint["scope"],
        "dependencies": {
            name: _artifact(path, dependencies[name])
            for name, path in DEPENDENCIES.items()
        },
        "formal_pairing_theorem": {
            "chain_equation": "q_W A1 = A2 d_H",
            "reducibility_condition": "q_W^sharp zeta_Y=0",
            "compact_support_identity": "0=<zeta_Y,q_W A1 alpha>=<zeta_Y,A2 d_H alpha>=integral B0(X,Y)d_H alpha=-integral d_H B0(X,Y)^alpha",
            "necessary_condition": "d_H B0(X,Y)=0 for every current label X and target reducibility Y",
            "differential_order_bound": "none",
            "locality_assumption_used": "none beyond mapping compact test sections into the formal-adjoint pairing domain",
            "boundary_assumption": "compact support, so the horizontal Stokes term vanishes",
        },
        "diffeomorphism_only_endpoint": {
            "formula": "A2(P_X^4)=X^mu c_mu_star",
            "pairing_kernel": "B0(X,Y)=g(X,Y)",
            "raw_gram_basis": list(NAMES),
            "raw_gram": geometry["raw_gram"],
            "normalized_nonconstant_witness": geometry["witness"],
            "all_finite_differential_orders_obstructed": True,
        },
        "correlated_maxwell_compensator": {
            "background_metric_flattened": geometry["metric"],
            "magnetic_field_F_theta_phi": geometry["magnetic_field_F_theta_phi"],
            "vectors": geometry["vectors"],
            "lambda_X": geometry["compensators"],
            "reducibility_equation": "d lambda_X+i_X F=0",
            "reducibility_residuals": geometry["maxwell_reducibility_residuals"],
            "corrected_endpoint": "A2_comp(P_X^4)=X^mu c_mu_star+lambda_X lambda_cov_star",
            "corrected_pairing_kernel": "Bcomp(X,Y)=g(X,Y)+lambda_X lambda_Y",
            "corrected_gram_basis": list(NAMES),
            "corrected_gram": geometry["corrected_gram"],
            "corrected_gram_constant": True,
            "independent_constant_u1_current_added": False,
            "normalization": "lambda_X is the unique zero-mean solution modulo the independent constant U1 reducibility",
        },
        "minimal_repair": {
            "kind": "CHANGED_ENDPOINT_INCIDENCE_ON_EXISTING_TARGET_ROW",
            "new_target_rows": 0,
            "existing_row_used": "lambda_cov_star",
            "carrier_rank_enlargement_required_at_pairing_gate": 0,
            "reason_minimal": "the diffeomorphism-only Gram defect has rank-one scalar correction type, and the existing correlated Maxwell compensator supplies it exactly; zero added rows is minimal",
            "complete_corrected_chain_map_constructed": False,
        },
        "classification": {
            "fixed_diffeomorphism_only_endpoint_obstructed_at_all_finite_orders": True,
            "all_order_statement_uses_order_extrapolation": False,
            "correlated_maxwell_endpoint_removes_pairing_obstruction": True,
            "corrected_endpoint_chain_map_constructed": False,
            "current_carrier_enlargement_required_at_pairing_gate": False,
            "relative_q2_or_f2_activated": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "RESTART_THE_RELATIVE_CHAIN_LIFT_WITH_THE_CORRELATED_MAXWELL_COMPENSATOR_ENDPOINT_BEGINNING_AT_ORDER_ZERO",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_all_order_endpoint_pairing_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_all_order_endpoint_pairing_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_all_order_endpoint_pairing_obstruction",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem proves that the fixed diffeomorphism-only endpoint on the untwisted five-copy de Rham current carrier cannot extend to a chain map at any finite differential order: formal adjunction forces every pointwise stabilizer Gram entry g(X,Y) to be constant, contradicted by g(J_1,J_1)=sin(theta)^2. It also identifies the smallest endpoint-incidence repair: use the existing Maxwell identity row with the correlated zero-mean compensators satisfying d lambda_X+i_X F=0, for which g(X,Y)+lambda_X lambda_Y=diag(-1,1,1,1,1). This removes the pairing obstruction but does not construct the corrected chain map, activate relative q2 or f2, require a carrier enlargement, or establish causal, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# All-order endpoint-pairing obstruction and compensated repair

For the fixed endpoint \(A^2(P_X^{(4)})=X^\mu c_\mu^*\), pair the chain
equation \(q_WA^1=A^2d_H\) with any target reducibility \(\zeta_Y\).
Formal adjunction and compact support give

\[
0=\langle\zeta_Y,q_WA^1\alpha\rangle
 =-\int d\,g(X,Y)\wedge\alpha .
\]

Hence every pointwise Gram entry \(g(X,Y)\) would have to be constant,
independently of the differential order of \(A^1\).  This fails already for
\(X=Y=J_1\), since \(g(J_1,J_1)=\sin^2\theta\).  The fixed
diffeomorphism-only endpoint is therefore obstructed at every finite order.

The obstruction also identifies its minimal repair.  The rotations are
fixed-bundle Maxwell reducibilities only together with their correlated
zero-mean compensators:

\[
d\lambda_X+\iota_XF=0.
\]

Adding \(\lambda_X\lambda_{\rm cov}^*\) to the endpoint uses an existing
target row and yields

\[
g(X,Y)+\lambda_X\lambda_Y
=\operatorname{diag}(-1,1,1,1,1).
\]

This removes the endpoint-pairing obstruction without adding an independent
constant \(U(1)\) current or enlarging the carrier.  The complete corrected
chain map remains to be constructed.

CLOSE-OUT: OBSTRUCTED — the fixed endpoint family has an all-order pairing obstruction; its minimal compensated endpoint repair is classified
EVIDENCE: EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "all_order_statement_uses_order_extrapolation",
        "corrected_endpoint_chain_map_constructed",
        "current_carrier_enlargement_required_at_pairing_gate",
        "relative_q2_or_f2_activated",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (
        OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()
    ):
        raise AssertionError("all-order endpoint-pairing outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
