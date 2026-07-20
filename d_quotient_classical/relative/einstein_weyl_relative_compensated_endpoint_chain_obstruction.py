#!/usr/bin/env python3
"""Certify the flat-symbol obstruction to the compensated relative chain lift."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-compensated-endpoint-chain-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-compensated-endpoint-chain-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_compensated_endpoint_chain_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_compensated_endpoint_chain_obstruction.py"
DEPENDENCIES = {
    "compensated_endpoint": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1.json",
    "order_one_obstruction": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1.json",
    "order_one_payload": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_order_one_chain_obstruction_v1/system.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
    "target_layout": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/row_layout.json",
    "current_layout": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json",
}


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


def _fraction(value: sp.Rational | Fraction | int) -> str:
    rational = sp.Rational(value)
    return str(int(rational.p)) if rational.q == 1 else f"{int(rational.p)}/{int(rational.q)}"


def _target_flat_terms(q1: dict[str, Any], layout: dict[str, Any]) -> dict[str, str]:
    rows = {row["index"]: row["row_id"] for row in layout["content"]["rows"]}
    profiles = {
        item["index"]: {
            tuple(jet["word"]): sp.Rational(jet["coefficient"])
            for jet in item["coefficient_jets"]
        }
        for item in q1["content"]["coefficient_profiles"]
    }
    selected: dict[str, sp.Rational] = {}
    for term in q1["content"]["terms"]:
        incoming = term["inputs"][0]
        word = incoming["word"]
        if (
            term["output_row"] not in (34, 35)
            or incoming["row"] not in (20, 21, 24, 30, 31)
            or len(word) != 1
            or word[0] not in (0, 1)
        ):
            continue
        coefficient = profiles[term["coefficient_profile"]].get((), sp.S.Zero)
        if coefficient != sp.Rational(term["coefficient"]):
            raise AssertionError("target q1 display coefficient/profile mismatch")
        key = f"{rows[term['output_row']]}<-d{word[0]}({rows[incoming['row']]})"
        selected[key] = selected.get(key, sp.S.Zero) + coefficient
    expected = {
        "c_0_star<-d0(g_00_star)": sp.Rational(-2),
        "c_1_star<-d0(g_01_star)": sp.Rational(1),
        "c_0_star<-d1(g_01_star)": sp.Rational(-1),
        "c_1_star<-d1(g_11_star)": sp.Rational(2),
    }
    metric_selected = {key: value for key, value in selected.items() if "g_" in key}
    if metric_selected != expected:
        raise AssertionError(f"flat diffeomorphism symbol drifted: {metric_selected}")
    forbidden_maxwell = {
        key: value
        for key, value in selected.items()
        if key.startswith(("c_0_star", "c_1_star")) and "A_" in key
    }
    if forbidden_maxwell:
        raise AssertionError(f"flat diffeomorphism rows acquired Maxwell terms: {forbidden_maxwell}")
    return {key: _fraction(value) for key, value in sorted(expected.items())}


def _current_flat_term(layout: dict[str, Any]) -> dict[str, Any]:
    p3 = {
        row["index"]: row
        for row in layout["rows"]
        if row["chain"] == "primal" and row["form_degree"] == 3
    }
    p4 = {
        row["index"]: row
        for row in layout["rows"]
        if row["chain"] == "primal" and row["form_degree"] == 4
    }
    source = next(
        index
        for index, row in p3.items()
        if row["row_id"] == "P_H_3_t_theta_phi"
    )
    target = next(
        index
        for index, row in p4.items()
        if row["row_id"] == "P_H_4_t_x_theta_phi"
    )
    matching = [
        term
        for term in layout["unary_terms"]
        if term["source_row"] == source and term["target_row"] == target
    ]
    projected = [
        {
            "source_row": term["source_row"],
            "target_row": term["target_row"],
            "derivative": term["derivative"],
            "coefficient": term["coefficient"],
        }
        for term in matching
    ]
    if projected != [{"source_row": source, "target_row": target, "derivative": "x", "coefficient": -1}]:
        raise AssertionError(f"H-current flat differential drifted: {matching}")
    return {
        "source_row": p3[source]["row_id"],
        "target_row": p4[target]["row_id"],
        "derivative": "x",
        "coefficient": "-1",
    }


def _flat_obstruction() -> dict[str, Any]:
    # Lowest flat differential degree.  u,v,w are the constant coefficients
    # into g_00_star, g_01_star and g_11_star, respectively.
    matrix = sp.Matrix(
        [
            [-2, 0, 0],
            [0, -1, 0],
            [0, 1, 0],
            [0, 0, 2],
        ]
    )
    rhs = sp.Matrix([0, -1, 0, 0])
    rank = matrix.rank()
    augmented_rank = matrix.row_join(rhs).rank()
    if (rank, augmented_rank) != (3, 4):
        raise AssertionError("flat compensated endpoint obstruction drifted")
    left_null = sp.Matrix([[0, 1, 1, 0]])
    if left_null * matrix != sp.zeros(1, 3) or left_null * rhs != sp.Matrix([[-1]]):
        raise AssertionError("flat left-null witness drifted")

    tau, xi = sp.symbols("tau xi")
    ideal = sp.groebner([tau, xi**2], tau, xi, order="lex", domain=sp.QQ)
    _, remainder = ideal.reduce(xi)
    if remainder != xi:
        raise AssertionError("polynomial obstruction remainder drifted")
    return {
        "ring": "Q[tau,xi]",
        "unknowns": ["u=g_00_star coefficient", "v=g_01_star coefficient", "w=g_11_star coefficient"],
        "equations": [
            "-2*tau*u-xi*v=-xi",
            "tau*v+2*xi*w=0",
        ],
        "lowest_degree_matrix": [[int(value) for value in matrix.row(row)] for row in range(matrix.rows)],
        "lowest_degree_rhs": [int(value) for value in rhs],
        "rank_over_Q": rank,
        "augmented_rank_over_Q": augmented_rank,
        "left_null_witness": {
            "row_coefficients": [0, 1, 1, 0],
            "matrix_evaluation": [0, 0, 0],
            "rhs_evaluation": "-1",
        },
        "polynomial_elimination": {
            "from_second_equation": "v=2*xi*s and w=-tau*s",
            "remaining_membership_test": "xi in ideal(tau,xi^2)",
            "groebner_basis": ["tau", "xi^2"],
            "normal_form_of_xi": "xi",
            "membership": False,
        },
    }


def _minimal_symbol_repair() -> dict[str, Any]:
    # b is the (0,1) component of an antisymmetric equation two-form.
    matrix = sp.Matrix(
        [
            [-2, 0, 0, 0],
            [0, -1, 0, -1],
            [0, 1, 0, -1],
            [0, 0, 2, 0],
        ]
    )
    rhs = sp.Matrix([0, -1, 0, 0])
    solution = sp.Matrix([0, sp.Rational(1, 2), 0, sp.Rational(1, 2)])
    if matrix * solution != rhs or matrix.det() == 0:
        raise AssertionError("antisymmetric symbol repair drifted")
    return {
        "added_module": "Lambda^2(T^*M)",
        "rank_in_four_dimensions": 6,
        "representation_identity": "(T^*M tensor T^*M)/Sym^2(T^*M)=Lambda^2(T^*M)",
        "flat_added_component": "b=B_01",
        "extended_equations": [
            "-2*tau*u-xi*v-xi*b=-xi",
            "tau*v-tau*b+2*xi*w=0",
        ],
        "unique_lowest_degree_solution": {
            "u": "0",
            "v": "1/2",
            "w": "0",
            "b": "1/2",
        },
        "extended_matrix_determinant": _fraction(matrix.det()),
        "minimality_scope": "minimal GL(4)-covariant tensor-symbol completion of the symmetric metric-equation carrier",
        "cyclic_dual_completion_constructed": False,
        "full_chain_map_on_enlarged_carrier_constructed": False,
    }


def _order_one_regression(
    old: dict[str, Any], payload: dict[str, Any], endpoint: dict[str, Any]
) -> dict[str, Any]:
    witness = old["exact_linear_system"]["left_null_witness"]
    if witness["terms"] != [[70, "-1"], [339, "-1"]]:
        raise AssertionError("order-one left-null witness drifted")
    rows = {70: {}, 339: {}}
    for row, column, value in payload["matrix_coo"]:
        if row in rows:
            rows[row][column] = sp.Rational(value)
    if rows != {70: {7: sp.Rational(1)}, 339: {7: sp.Rational(-1)}}:
        raise AssertionError(f"order-one witness rows drifted: {rows}")
    combination = {
        column: -rows[70].get(column, 0) - rows[339].get(column, 0)
        for column in set(rows[70]) | set(rows[339])
    }
    if any(combination.values()):
        raise AssertionError("order-one witness no longer annihilates the matrix")
    lambdas = endpoint["correlated_maxwell_compensator"]["lambda_X"]
    if lambdas["H"] != "0":
        raise AssertionError("H acquired a forbidden U(1) compensator")
    rhs = dict((int(row), sp.Rational(value)) for row, value in payload["rhs_sparse"])
    if rhs.get(70, 0) != 0 or rhs.get(339, 0) != -1:
        raise AssertionError("old H witness RHS drifted")
    # Compensation changes only lambda_cov_star rows for rotational currents;
    # these two H/c rows therefore retain the exact same evaluation.
    evaluation = -rhs.get(70, 0) - rhs.get(339, 0)
    if evaluation != 1:
        raise AssertionError("compensated order-one witness vanished")
    return {
        "matrix_shape": payload["shape"],
        "matrix_rank_over_Q": old["exact_linear_system"]["rank_over_Q"],
        "compensated_augmented_rank_over_Q": old["exact_linear_system"]["rank_over_Q"] + 1,
        "witness_rows": [70, 339],
        "witness_matrix_rows": [
            [[column, _fraction(value)] for column, value in sorted(rows[row].items())]
            for row in (70, 339)
        ],
        "compensated_rhs_on_witness_rows": ["0", "-1"],
        "left_null_coefficients": ["-1", "-1"],
        "left_null_evaluation": "1",
        "reason_compensation_does_not_change_witness": "lambda_H=0 and the repair changes only the lambda_cov_star endpoint row, whereas both witness rows are c_0_star/c_1_star rows for the H-current input",
    }


def build() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    endpoint = values["compensated_endpoint"]
    if not endpoint["classification"]["correlated_maxwell_endpoint_removes_pairing_obstruction"]:
        raise AssertionError("compensated endpoint prerequisite is not certified")
    if endpoint["correlated_maxwell_compensator"]["independent_constant_u1_current_added"]:
        raise AssertionError("independent constant U(1) current entered the endpoint")
    flat_terms = _target_flat_terms(values["target_q1"], values["target_layout"])
    current_term = _current_flat_term(values["current_layout"])
    obstruction = _flat_obstruction()
    repair = _minimal_symbol_repair()
    regression = _order_one_regression(
        values["order_one_obstruction"], values["order_one_payload"], endpoint
    )
    return {
        "schema": "pure-weyl-relative-compensated-endpoint-chain-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPENSATED_ENDPOINT_PAIRING_REPAIRED_BUT_EXISTING_CARRIER_CHAIN_LIFT_ALL_ORDER_OBSTRUCTED",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            **endpoint["scope"],
            "carrier": "product-equivariant finite-order support-local relative chain maps on the existing shifted five-current and Weyl-Maxwell carriers",
            "degree": "unary top descent; flat (t,x) lowest differential filtration",
            "parity": "unrestricted in the flat symbol block; covariant tensor repair classified",
        },
        "dependencies": {
            name: _artifact(path, values[name])
            for name, path in DEPENDENCIES.items()
        },
        "compensated_endpoint": {
            "formula": endpoint["correlated_maxwell_compensator"]["corrected_endpoint"],
            "corrected_gram": endpoint["correlated_maxwell_compensator"]["corrected_gram"],
            "lambda_H": endpoint["correlated_maxwell_compensator"]["lambda_X"]["H"],
            "lambda_P_x": endpoint["correlated_maxwell_compensator"]["lambda_X"]["P_x"],
            "independent_constant_u1_current_added": False,
            "pairing_obstruction_removed": True,
        },
        "raw_operator_projection": {
            "flat_factor": "(t,x)",
            "current_term": current_term,
            "target_q1_terms": flat_terms,
            "Maxwell_contribution_to_c0_c1_flat_rows": "zero because F has only theta-phi components",
            "higher_order_decoupling": "product-equivariant coefficients are parallel in t,x; after restriction to the sphere-covariantly-constant zero mode, positive flat differential degree cannot change the lowest degree-one endpoint equation",
        },
        "flat_polynomial_obstruction": obstruction,
        "order_one_original_system_regression": regression,
        "minimal_covariant_symbol_repair": repair,
        "classification": {
            "compensated_endpoint_pairing_obstruction_removed": True,
            "complete_existing_carrier_unary_chain_lift_exists": False,
            "existing_carrier_all_finite_differential_orders_obstructed": True,
            "obstruction_uses_order_extrapolation": False,
            "first_new_invariant_obstruction_certified": True,
            "minimal_covariant_symbol_carrier_repair_classified": True,
            "full_chain_map_on_enlarged_carrier_constructed": False,
            "relative_q2_or_f2_activated": False,
            "causal_observable_nonlinear_particle_or_quantum_claim": False,
        },
        "next_gate": "DECLARE_A_CYCLIC_LAMBDA2_EQUATION_PAIR_EXTENSION_OR_CHANGE_THE_CURRENT_RESOLUTION_BEFORE_RESTARTING_THE_UNARY_CHAIN_LIFT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_compensated_endpoint_chain_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_compensated_endpoint_chain_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_compensated_endpoint_chain_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-compensated-endpoint-chain-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem proves that adding the certified correlated Maxwell compensators removes the endpoint-pairing obstruction but does not produce a unary chain map on the existing carriers. On the translation-invariant flat (t,x) zero-mode quotient, the H endpoint requires the polynomial symmetric-divergence system -2 tau u-xi v=-xi, tau v+2 xi w=0. Its lowest differential component has rank 3 and augmented rank 4, and equivalently xi has nonzero normal form modulo (tau,xi^2). Higher finite differential order cannot alter this lowest flat filtration component, so every product-equivariant finite-order support-local lift on the existing carrier is obstructed. The minimal GL(4)-covariant tensor-symbol repair is a Lambda^2(T^*M) equation component, which supplies the missing antisymmetric half with u=w=0 and v=b=1/2. This classifies only the symbol-level carrier repair; it does not construct its cyclic dual completion or full chain map, activate q2/f2, add an independent U(1) current, change the magnetic bundle, or establish causal, observable, nonlinear, particle or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(value: dict[str, Any]) -> str:
    obstruction = value["flat_polynomial_obstruction"]
    repair = value["minimal_covariant_symbol_repair"]
    return f"""# Compensated endpoint chain obstruction

The correlated fixed-bundle Maxwell endpoint makes the five-stabilizer Gram
matrix constant, but it does not complete the unary chain map.  Restrict the
chain equation to the translation-invariant `(t,x)` zero mode and the
`P_H_3_t_theta_phi` current component.  Since `lambda_H=0` and the magnetic
field has only `theta-phi` components, the exact target block is

```text
-2 tau u - xi v = -xi
   tau v + 2 xi w = 0.
```

The lowest differential coefficient system has rank
`{obstruction['rank_over_Q']}` and augmented rank
`{obstruction['augmented_rank_over_Q']}`.  Its two-row left-null witness
evaluates to `{obstruction['left_null_witness']['rhs_evaluation']}`.  The
equivalent polynomial elimination leaves the nonzero normal form `xi` modulo
`(tau,xi^2)`.  This is a filtration obstruction, not an extrapolation from
orders one through three, so no finite-order product-equivariant support-local
lift exists on the current carrier.

The missing tensor component is exactly antisymmetric.  Adjoining the
covariant module `{repair['added_module']}` makes the flat block square and
invertible, with the unique normalized solution

```text
u = 0,  v = 1/2,  w = 0,  b = 1/2.
```

This classifies the minimal covariant symbol repair only.  A cyclic dual
completion and the resulting full chain map remain unconstructed, and
`q2/f2` stays inactive.

CLOSE-OUT: OBSTRUCTED — the compensated endpoint removes the pairing defect but the existing symmetric equation carrier has an exact all-finite-order flat-symbol obstruction
EVIDENCE: EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "complete_existing_carrier_unary_chain_lift_exists",
        "obstruction_uses_order_extrapolation",
        "full_chain_map_on_enlarged_carrier_constructed",
        "relative_q2_or_f2_activated",
        "causal_observable_nonlinear_particle_or_quantum_claim",
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
        REPORT.write_text(_report(value))
    if args.check and (
        OUTPUT.read_text() != _render(value)
        or REPORT.read_text() != _report(value)
    ):
        raise AssertionError("compensated endpoint chain obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
