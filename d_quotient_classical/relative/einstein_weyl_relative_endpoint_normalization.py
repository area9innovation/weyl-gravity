#!/usr/bin/env python3
"""Freeze the endpoint normalization of the shifted five-current lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-endpoint-normalization.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-endpoint-normalization-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_endpoint_normalization.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_endpoint_normalization.py"

DEPENDENCIES = {
    "linear_triangle": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "shifted_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json",
    "current_layout": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json",
    "order_zero_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value.get("result_id", value.get("schema"))), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    endpoints = values["linear_triangle"]["global_endpoints"]
    if endpoints["map_matrix"] != [[int(i == j) for j in range(6)] for i in range(6)]:
        raise AssertionError("global endpoint map is no longer the identity")
    if endpoints["source_basis"][:5] != ["partial_t", "partial_x", "J_1", "J_2", "J_3"]:
        raise AssertionError("spacetime endpoint ordering drifted")
    layout = values["current_layout"]
    p4 = sorted(
        [row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 4],
        key=lambda row: row["index"],
    )
    if [row["generator"] for row in p4] != ["H", "P_x", "J_1", "J_2", "J_3"]:
        raise AssertionError("P4 generator ordering drifted")
    if any(row["pairing_coefficient"] != 1 for row in p4):
        raise AssertionError("P4 orientation/pairing sign drifted")
    order_zero = values["order_zero_obstruction"]
    if not order_zero["kernel_classification"]["all_A1_metric_equation_coefficients_zero"]:
        raise AssertionError("order-zero boundary changed")

    formulas = [
        {"generator": "H", "source_row": p4[0]["row_id"], "target_terms": [{"row": "c_0_star", "coefficient": "1"}]},
        {"generator": "P_x", "source_row": p4[1]["row_id"], "target_terms": [{"row": "c_1_star", "coefficient": "1"}]},
        {"generator": "J_1", "source_row": p4[2]["row_id"], "target_terms": [{"row": "c_3_star", "coefficient": "1"}]},
        {"generator": "J_2", "source_row": p4[3]["row_id"], "target_terms": [{"row": "c_2_star", "coefficient": "cos(phi)"}, {"row": "c_3_star", "coefficient": "-sin(phi)*cot(theta)"}]},
        {"generator": "J_3", "source_row": p4[4]["row_id"], "target_terms": [{"row": "c_2_star", "coefficient": "sin(phi)"}, {"row": "c_3_star", "coefficient": "cos(phi)*cot(theta)"}]},
    ]
    return {
        "schema": "pure-weyl-relative-endpoint-normalization-v1",
        "result_id": RESULT_ID,
        "result_state": "FIVE_STABILIZER_ENDPOINT_NORMALIZATION_FROZEN_ORDER_ONE_LIFT_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "closed oriented Cauchy slice with fixed N=2 magnetic bundle",
            "charge_sector": "connected spacetime stabilizers H,P_x,J_1,J_2,J_3; constant U(1) is not in K_P",
            "carrier": "top endpoint A2:P4(5)->W2(6) of the shifted current chain map",
            "degree": 2, "parity": "even identity-density endpoint",
            "ell": "global reducibility endpoint", "m": "global reducibility endpoint",
            "k": "global reducibility endpoint", "omega": "zero reducibility frequency",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "derivation": {
            "global_endpoint_map": "identity on (partial_t,partial_x,J_1,J_2,J_3,u1_constant)",
            "current_endpoint_basis": ["H", "P_x", "J_1", "J_2", "J_3"],
            "target_identity_basis": ["c_0_star", "c_1_star", "c_2_star", "c_3_star", "lambda_cov_star", "sigma_W_star"],
            "pairing_identity": "<c,A2(P_X^4)>=X^mu c_mu for every target diffeomorphism ghost c",
            "orientation_sign": 1,
            "forced_formula": "A2(P_X^4)=X^mu c_mu_star",
            "u1_component": "zero because the five-current carrier resolves spacetime stabilizers only",
            "Weyl_component": "zero because connected conformal reducibilities are product Killing fields on this background",
        },
        "A2": formulas,
        "equatorial_basepoint_values": {
            "point": {"theta": "pi/2", "phi": "0"},
            "H": {"c_0_star": "1"},
            "P_x": {"c_1_star": "1"},
            "J_1": {"c_3_star": "1"},
            "J_2": {"c_2_star": "1"},
            "J_3": {},
            "pointwise_rank": 4,
            "global_map_rank": 5,
            "rank_note": "J_3 vanishes at the selected equatorial base point but is a nonzero global Killing field; pointwise rank is not global endpoint rank",
        },
        "consequence_for_lift_search": {
            "order_zero_kernel_A2_target": "lambda_cov_star only",
            "endpoint_A2_target": "diffeomorphism identity rows only",
            "endpoint_normalized_order_zero_chain_map_exists": False,
            "positive_order_chain_map_ruled_out": False,
            "required_next_ansatz": "finite-order differential A1,A2 with the displayed order-zero endpoint part fixed",
        },
        "classification": {
            "endpoint_normalization_exact": True,
            "endpoint_sign_fixed_by_pairing": True,
            "endpoint_normalized_order_zero_chain_map_exists": False,
            "positive_order_chain_map_ruled_out": False,
            "support_local_chain_map_A_constructed": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "SOLVE_THE_COMPLETE_ORDER_ONE_INVARIANT_TOP_DESCENT_WITH_THIS_A2_ENDPOINT_NORMALIZATION_FIXED",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_endpoint_normalization --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_endpoint_normalization",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_endpoint_normalization",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-endpoint-normalization-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json"
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate freezes the top endpoint required of the shifted five-current chain map: A2 sends the oriented P4 generator for each spacetime stabilizer X to X^mu c_mu_star, with sign fixed by the current and BV endpoint pairings. It excludes the constant U(1) and Weyl identity rows for the stated reasons. Combined with the complete order-zero kernel theorem it rules out an endpoint-normalized order-zero chain map, but it does not rule out positive differential order, construct A1, solve the coefficient descent, repair relative q2 or establish causal, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Relative endpoint normalization

The endpoint is fixed by the identity map on the five connected spacetime
reducibilities and by the declared current/BV pairings.  For every product
Killing field `X`,

\[
A^2(P_X^{(4)})=X^\mu c_\mu^*,
\qquad
\langle c,A^2(P_X^{(4)})\rangle=X^\mu c_\mu.
\]

Thus `H` maps to `c_0_star`, `P_x` to `c_1_star`, and the three rotations to
their exact coordinate-vector combinations.  There is no `lambda_cov_star`
component because the current carrier resolves only the five spacetime
stabilizers, and no `sigma_W_star` component because all connected conformal
reducibilities are product Killing fields on this background.

The complete order-zero top-descent kernel instead lands only in
`lambda_cov_star`.  Hence an endpoint-normalized order-zero chain map is
impossible.  Positive differential order remains open and must keep this
endpoint part fixed.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("endpoint_normalized_order_zero_chain_map_exists", "positive_order_chain_map_ruled_out", "support_local_chain_map_A_constructed", "relative_q2_repaired", "causal_observable_particle_or_quantum_claim"):
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
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("relative endpoint normalization outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
