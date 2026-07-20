#!/usr/bin/env python3
"""Certify the complete order-zero shifted-current lift obstruction.

The order-zero ansatz is deliberately unrestricted: ``A1`` is an arbitrary
14 by 20 pointwise matrix and ``A2`` an arbitrary 6 by 5 pointwise matrix.
The principal top-descent equation is solved exactly over the rationals.  Its
five-dimensional kernel consists only of Maxwell de Rham tails, so ``A1`` has
no metric-equation output.  A normalized fourth-order metric term in the
relative arity-two defect therefore cannot equal ``A1 C`` when ``f2=0``.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-order-zero-lift-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-order-zero-lift-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_order_zero_lift_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_order_zero_lift_obstruction.py"

DEPENDENCIES = {
    "shifted_cone": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1.json",
    "current_export": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json",
    "current_payload": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_full_five_current_pbw_export_v1/current_q2.json",
    "current_layout": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json",
    "target_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
    "relative_delta2": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_arity_two_defect_v1/delta2.json",
}

AXES = {"t": 0, "x": 1, "theta": 2, "phi": 3}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _fraction(value: Fraction | sp.Rational) -> str:
    value = Fraction(int(value.p), int(value.q)) if isinstance(value, sp.Rational) else value
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _target_symbol(q1: dict[str, Any]) -> list[list[list[Fraction]]]:
    content = q1["content"]
    profiles = {
        item["index"]: {
            tuple(jet["word"]): Fraction(jet["coefficient"])
            for jet in item["coefficient_jets"]
        }
        for item in content["coefficient_profiles"]
    }
    matrices = [[[Fraction() for _ in range(14)] for _ in range(6)] for _ in range(4)]
    for term in content["terms"]:
        output = term["output_row"]
        incoming = term["inputs"][0]
        if not (34 <= output < 40 and 20 <= incoming["row"] < 34):
            continue
        if len(incoming["word"]) != 1:
            continue
        coefficient = profiles[term["coefficient_profile"]].get((), Fraction())
        if coefficient != Fraction(term["coefficient"]):
            raise AssertionError("q1 display coefficient disagrees with its authoritative profile")
        matrices[incoming["word"][0]][output - 34][incoming["row"] - 20] += coefficient
    return matrices


def _current_symbol(layout: dict[str, Any]) -> tuple[list[list[list[Fraction]]], list[dict], list[dict]]:
    p3 = sorted(
        (row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 3),
        key=lambda row: row["index"],
    )
    p4 = sorted(
        (row for row in layout["rows"] if row["chain"] == "primal" and row["form_degree"] == 4),
        key=lambda row: row["index"],
    )
    if len(p3) != 20 or len(p4) != 5:
        raise AssertionError("current row census drifted")
    p3_index = {row["index"]: local for local, row in enumerate(p3)}
    p4_index = {row["index"]: local for local, row in enumerate(p4)}
    matrices = [[[Fraction() for _ in range(20)] for _ in range(5)] for _ in range(4)]
    for term in layout["unary_terms"]:
        if term["source_row"] not in p3_index or term["target_row"] not in p4_index:
            continue
        matrices[AXES[term["derivative"]]][p4_index[term["target_row"]]][p3_index[term["source_row"]]] += Fraction(term["coefficient"])
    return matrices, p3, p4


def _system(target: list, current: list) -> tuple[sp.MutableSparseMatrix, list[list[Any]]]:
    entries: dict[tuple[int, int], sp.Rational] = {}
    records: list[list[Any]] = []
    for axis in range(4):
        for output in range(6):
            for incoming in range(20):
                equation = (axis * 6 + output) * 20 + incoming
                for middle in range(14):
                    value = target[axis][output][middle]
                    if value:
                        unknown = middle * 20 + incoming
                        coefficient = sp.Rational(value.numerator, value.denominator)
                        entries[(equation, unknown)] = entries.get((equation, unknown), 0) + coefficient
                for middle in range(5):
                    value = current[axis][middle][incoming]
                    if value:
                        unknown = 280 + output * 5 + middle
                        coefficient = -sp.Rational(value.numerator, value.denominator)
                        entries[(equation, unknown)] = entries.get((equation, unknown), 0) + coefficient
    for (equation, unknown), coefficient in sorted(entries.items()):
        if coefficient:
            records.append([equation, unknown, _fraction(coefficient)])
    return sp.MutableSparseMatrix(480, 310, entries), records


def _normalized_kernel(matrix: sp.MutableSparseMatrix) -> list[list[list[Any]]]:
    output: list[list[list[Any]]] = []
    for vector in matrix.nullspace():
        values = [Fraction(int(value.p), int(value.q)) for value in vector]
        common = 1
        for value in values:
            common = sp.ilcm(common, value.denominator)
        integers = [int(value * common) for value in values]
        divisor = 0
        for value in integers:
            divisor = gcd(divisor, abs(value))
        if divisor:
            integers = [value // divisor for value in integers]
        first = next(value for value in integers if value)
        if first < 0:
            integers = [-value for value in integers]
        output.append([[index, value] for index, value in enumerate(integers) if value])
    return output


def _matrix_digest(records: list[list[Any]]) -> str:
    return hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()


def _delta_witness(delta: dict[str, Any]) -> dict[str, Any]:
    terms = delta["content"]["terms"]
    candidates = [
        term
        for term in terms
        if 20 <= term["output_row"] < 30
        and all(5 <= item["row"] < 19 for item in term["inputs"])
        and sum(len(item["word"]) for item in term["inputs"]) == 4
    ]
    if not candidates:
        raise AssertionError("fourth-order metric Delta2 witness disappeared")
    candidates.sort(key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    preferred = {
        "coefficient": "1/4",
        "inputs": [{"row": 5, "word": []}, {"row": 5, "word": [1, 1, 1, 1]}],
        "output_row": 20,
    }
    if preferred not in candidates:
        raise AssertionError("normalized Delta2 witness drifted")
    return {"term": preferred, "metric_order_four_term_count": len(candidates)}


def exact_data() -> dict[str, Any]:
    values = {name: _load(path) for name, path in DEPENDENCIES.items()}
    current_certificate = values["current_export"]
    current_payload = values["current_payload"]
    if current_certificate["payload"]["sha256"] != _sha(DEPENDENCIES["current_payload"]):
        raise AssertionError("current payload is not pinned by its export certificate")
    if current_payload["maximum_input_derivative_order"] != 4:
        raise AssertionError("current derivative order drifted")

    target = _target_symbol(values["target_q1"])
    current, p3, p4 = _current_symbol(values["current_layout"])
    matrix, records = _system(target, current)
    rank = matrix.rank()
    kernel = _normalized_kernel(matrix)
    if rank != 305 or len(kernel) != 5:
        raise AssertionError(f"order-zero rank drifted: {rank}, {len(kernel)}")

    target_rows = values["relative_delta2"]["target_rows"]
    w1 = [row for row in target_rows if 20 <= row["index"] < 34]
    w2 = [row for row in target_rows if 34 <= row["index"] < 40]
    if len(w1) != 14 or len(w2) != 6:
        raise AssertionError("target row census drifted")
    metric_unknowns = set(range(0, 10 * 20))
    if any(index in metric_unknowns for vector in kernel for index, _ in vector):
        raise AssertionError("an order-zero top-descent solution has metric output")

    decoded_kernel = []
    for generator, vector in zip(("H", "P_x", "J_1", "J_2", "J_3"), kernel, strict=True):
        terms = []
        for index, coefficient in vector:
            if index < 280:
                output, incoming = divmod(index, 20)
                terms.append({
                    "map": "A1",
                    "output": w1[output]["row_id"],
                    "input": p3[incoming]["row_id"],
                    "coefficient": coefficient,
                })
            else:
                output, incoming = divmod(index - 280, 5)
                terms.append({
                    "map": "A2",
                    "output": w2[output]["row_id"],
                    "input": p4[incoming]["row_id"],
                    "coefficient": coefficient,
                })
        decoded_kernel.append({"generator": generator, "terms": terms})

    return {
        "values": values,
        "records": records,
        "rank": rank,
        "kernel": kernel,
        "decoded_kernel": decoded_kernel,
        "w1": w1,
        "w2": w2,
        "p3": p3,
        "p4": p4,
        "witness": _delta_witness(values["relative_delta2"]),
    }


def build() -> dict[str, Any]:
    data = exact_data()
    values = data["values"]
    return {
        "schema": "pure-weyl-relative-order-zero-lift-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_UNRESTRICTED_ORDER_ZERO_LIFT_OBSTRUCTED_POSITIVE_ORDER_OPEN",
        "lifecycle_status": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "pointwise principal-symbol problem at the homogeneous base point; no harmonic or causal reduction",
            "charge_sector": "five connected stabilizer currents H,P_x,J_1,J_2,J_3",
            "carrier": "degree-zero chain map A:K_P->C_W with A1:P3(20)->W1(14), A2:P4(5)->W2(6)",
            "degree": "top descent in cochain degrees one and two; strict field-pair incidence with f2=0",
            "parity": "complete unrestricted pointwise maps, hence stronger than an invariant order-zero ansatz",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced",
            "k": "not harmonic-reduced", "omega": "not harmonic-reduced",
        },
        "dependencies": {name: _artifact(path, values[name]) for name, path in DEPENDENCIES.items()},
        "ansatz": {
            "A1_shape": [14, 20],
            "A2_shape": [6, 5],
            "A1_unknowns": 280,
            "A2_unknowns": 30,
            "total_unknowns": 310,
            "differential_order": 0,
            "invariance_restrictions_imposed": False,
            "top_descent": "sigma_1(q1_W) A1 = A2 sigma_1(d_H)",
        },
        "exact_linear_system": {
            "covector_axes": ["t", "x", "theta", "phi"],
            "equations": 480,
            "unknowns": 310,
            "nonzero_entries": len(data["records"]),
            "rank_over_Q": data["rank"],
            "nullity": len(data["kernel"]),
            "matrix_coo_sha256": _matrix_digest(data["records"]),
            "normalized_kernel_sparse": data["kernel"],
        },
        "kernel_classification": {
            "dimension": 5,
            "basis": data["decoded_kernel"],
            "description": "one Maxwell de Rham tail for each stabilizer generator",
            "all_A1_metric_equation_coefficients_zero": True,
            "A1_metric_rows": [row["row_id"] for row in data["w1"][:10]],
            "A1_Maxwell_rows": [row["row_id"] for row in data["w1"][10:]],
        },
        "strict_incidence_obstruction": {
            "attempt": "f2=0 and A1,A2 of differential order zero",
            "required_identity": "Delta2=A1 C on source field pairs",
            "current_maximum_input_derivative_order": 4,
            "normalized_metric_witness": data["witness"]["term"],
            "metric_order_four_delta2_terms": data["witness"]["metric_order_four_term_count"],
            "A1_C_metric_output": "zero for every solution of the order-zero top descent",
            "conclusion": "the normalized g_00_star fourth-order term of Delta2 cannot be produced by A1 C",
        },
        "classification": {
            "complete_unrestricted_order_zero_top_descent_solved": True,
            "order_zero_top_descent_has_only_Maxwell_de_rham_tails": True,
            "strict_order_zero_f2_zero_lift_exists": False,
            "positive_order_lift_ruled_out": False,
            "nonzero_f2_ruled_out": False,
            "alternate_current_improvement_ruled_out": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "FREEZE_ENDPOINT_NORMALIZATION_AND_SOLVE_THE_COMPLETE_ORDER_ONE_INVARIANT_TOP_DESCENT_WITH_SUFFICIENT_CURRENT_COEFFICIENT_JETS",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_order_zero_lift_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_order_zero_lift_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_order_zero_lift_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-order-zero-lift-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": "This exact LOCAL-ALGEBRAIC obstruction exhausts every unrestricted pointwise order-zero pair A1:P3->W1 and A2:P4->W2. The top-descent kernel is five-dimensional and contains only the Maxwell de Rham tails, forcing every metric output of A1 to vanish; hence the displayed fourth-order metric term of Delta2 cannot equal A1 C when f2=0. The result does not rule out order-one or higher differential lifts, nonzero f2, another current improvement, a larger carrier, causal data, observables, particles or quantum claims.",
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Complete order-zero relative-lift obstruction

The declared order-zero search is unrestricted: `A1:P3(20)->W1(14)` has 280
coefficients and `A2:P4(5)->W2(6)` has 30.  Equating the four covector
coefficients in

\[
\sigma_1(q_{1,W})A^1=A^2\sigma_1(d_H)
\]

gives a 480 by 310 rational system with 520 nonzero entries, rank 305 and
nullity five.  The normalized kernel contains exactly one Maxwell de Rham
tail for each of `H,P_x,J_1,J_2,J_3`.  Every coefficient of `A1` landing in
a metric Euler row is zero.

Consequently `A1 C` has zero metric output for every order-zero top-descent
solution.  The exact relative defect `Delta2` instead contains 29,628
fourth-order metric terms; a normalized witness is the coefficient `1/4` of
`g_00 * partial_x^4 g_00` in the `g_00_star` row.  Thus the strict incidence
`Delta2=A1 C` with `f2=0` has no order-zero solution.

This is not a global lifting no-go.  An order-one symbol solve is not
obstructed by this calculation, and nonzero `f2`, higher differential order,
other current improvements and larger carriers remain open.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "strict_order_zero_f2_zero_lift_exists",
        "positive_order_lift_ruled_out",
        "nonzero_f2_ruled_out",
        "alternate_current_improvement_ruled_out",
        "relative_q2_repaired",
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
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("order-zero lift obstruction outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
