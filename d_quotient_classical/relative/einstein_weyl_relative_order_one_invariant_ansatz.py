#!/usr/bin/env python3
"""Classify the complete SO(2)-invariant order-one lift ansatz."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-one-invariant-ansatz.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-one-invariant-ansatz-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_one_invariant_ansatz.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_one_invariant_ansatz.py"
DEPENDENCIES = {
    "shifted_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json",
    "order_zero_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
    "endpoint_normalization": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1.json",
    "current_export": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
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


def _sym_weights(order: int) -> Counter[int]:
    weights = [0, 0, 1, -1]
    return Counter(sum(weights[index] for index in monomial) for monomial in combinations_with_replacement(range(4), order))


def _hom_dimension(source: dict[int, int], target: dict[int, int], order: int) -> int:
    domain: Counter[int] = Counter()
    for left, multiplicity in source.items():
        for right, symmetric_multiplicity in _sym_weights(order).items():
            domain[left + right] += multiplicity * symmetric_multiplicity
    return sum(domain[weight] * multiplicity for weight, multiplicity in target.items())


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    current = values["current_export"]
    target_q1 = values["target_q1"]["content"]
    if current["payload"]["maximum_coefficient_jet_order"] != 1:
        raise AssertionError("current coefficient-jet boundary drifted")
    if target_q1["coefficient_jet_order"] < 2:
        raise AssertionError("target q1 lacks coefficient jets for order-one composition")

    p3 = {0: 8, 1: 5, -1: 5, 2: 1, -2: 1}
    p4 = {0: 3, 1: 1, -1: 1}
    w1 = {0: 6, 1: 3, -1: 3, 2: 1, -2: 1}
    w2 = {0: 4, 1: 1, -1: 1}
    a1 = [_hom_dimension(p3, w1, order) for order in range(3)]
    a2 = [_hom_dimension(p4, w2, order) for order in range(3)]
    if a1 != [80, 284, 626] or a2 != [14, 42, 86]:
        raise AssertionError(f"invariant Hom census drifted: {a1}, {a2}")

    return {
        "schema": "pure-weyl-relative-order-one-invariant-ansatz-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_ORDER_ONE_INVARIANT_ANSATZ_CLASSIFIED_COEFFICIENT_SOLVE_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "support-local homogeneous differential-operator ansatz before harmonic or causal reduction",
            "charge_sector": "five connected spacetime stabilizer currents",
            "carrier": "A1:P3(20)->W1(14), A2:P4(5)->W2(6)",
            "degree": "one and two", "parity": "even chain-map components",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "arbitrary local covector", "omega": "arbitrary local covector",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "isotropy": {
            "group": "SO(2)",
            "tangent_covector": "2*1 + V1",
            "stabilizer_dual": "3*1 + V1",
            "derivation": "SO(2) fixes the t and x directions and rotates the theta-phi plane; so(3) restricts as 1+V1",
        },
        "bundle_decomposition": {
            "P3": {"real": "8*1 + 5*V1 + V2", "rank": 20, "complex_weights": {"-2": 1, "-1": 5, "0": 8, "1": 5, "2": 1}},
            "P4": {"real": "3*1 + V1", "rank": 5, "complex_weights": {"-1": 1, "0": 3, "1": 1}},
            "W1": {"real": "6*1 + 3*V1 + V2", "rank": 14, "complex_weights": {"-2": 1, "-1": 3, "0": 6, "1": 3, "2": 1}},
            "W2": {"real": "4*1 + V1", "rank": 6, "complex_weights": {"-1": 1, "0": 4, "1": 1}},
        },
        "homogeneous_symbol_dimensions": {
            "symmetric_covector_weights": [{"order": order, "weights": {str(k): v for k, v in sorted(_sym_weights(order).items())}} for order in range(3)],
            "A1_exact_order_0_1_2": a1,
            "A2_exact_order_0_1_2": a2,
            "A1_cumulative_through_0_1_2": [sum(a1[: order + 1]) for order in range(3)],
            "A2_cumulative_through_0_1_2": [sum(a2[: order + 1]) for order in range(3)],
        },
        "order_one_solver_contract": {
            "A1_order_zero_unknowns": 80,
            "A1_order_one_symbol_unknowns": 284,
            "A2_order_zero_part": "fixed exactly by EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1",
            "A2_order_one_symbol_unknowns": 42,
            "total_free_symbol_and_lower_coefficients": 406,
            "top_descent": "q1_W^(1->2) A1=A2 d_H^(3->4)",
            "coefficient_incidence_after_chain_solve": "Delta2-A1 C=delta(f2)",
        },
        "input_adequacy": {
            "target_q1_coefficient_jet_order": target_q1["coefficient_jet_order"],
            "current_export_coefficient_jet_order": current["payload"]["maximum_coefficient_jet_order"],
            "required_current_coefficient_jet_order_for_order_one_A1_C": 2,
            "current_payload_sufficient_for_full_order_one_incidence": False,
            "top_descent_symbol_solve_can_start_without_current_regeneration": True,
        },
        "classification": {
            "complete_invariant_Hom_ansatz_through_order_one": True,
            "endpoint_normalization_inserted": True,
            "order_one_top_descent_solved": False,
            "positive_order_lift_exists": False,
            "positive_order_lift_obstructed": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "EXPORT_CURRENT_COEFFICIENT_JETS_THROUGH_ORDER_TWO_AND_SOLVE_THE_406_PARAMETER_ORDER_ONE_CHAIN_SYSTEM",
        "provenance": {
            "source_manifest": {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)},
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_one_invariant_ansatz --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_one_invariant_ansatz",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_one_invariant_ansatz",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-order-one-invariant-ansatz-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1.json"
            ]
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC preflight classifies the complete homogeneous SO(2)-invariant symbol spaces for A1 and A2 through differential order two and freezes the 406 free coefficients of the endpoint-normalized order-one search. It does not solve the chain equation, assert existence or obstruction at positive order, export the required second current coefficient jets, repair relative q2 or establish causal, observable, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return """# Complete order-one invariant lift ansatz\n\nAt the compact-product base point the isotropy is `SO(2)`.  The relevant bundles decompose as `P3=8*1+5*V1+V2`, `P4=3*1+V1`, `W1=6*1+3*V1+V2`, and `W2=4*1+V1`.  Exact character multiplication gives homogeneous invariant Hom dimensions `(80,284,626)` for `A1` and `(14,42,86)` for `A2` at differential orders zero, one and two.\n\nWith the order-zero endpoint part of `A2` fixed, the complete order-one solve has 406 free coefficients: 364 in `A1` through order one and 42 in the derivative symbol of `A2`.  The target q1 export is adequate, but composing order-one `A1` with the current requires current coefficient jets through order two; the current payload presently stops at order one.  No positive-order verdict is claimed.\n"""


def _guards(value: dict[str, Any]) -> None:
    for key in ("order_one_top_descent_solved", "positive_order_lift_exists", "positive_order_lift_obstructed", "relative_q2_repaired", "causal_observable_particle_or_quantum_claim"):
        mutant = deepcopy(value); mutant["classification"][key] = True
        try: validate(mutant)
        except Exception: continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true"); parser.add_argument("--guards", action="store_true"); args = parser.parse_args()
    value = build(); validate(value)
    if args.write: OUTPUT.write_text(_render(value)); REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()): raise AssertionError("order-one invariant ansatz outputs drifted")
    if args.guards: _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__": main()
