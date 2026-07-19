#!/usr/bin/env python3
"""Reconstruct the six-master coordinates of all physical triangle rows."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .generic_background_ghost_n3_pole3_relative_ibp import (
    X1,
    X2,
    X3,
    _domain_matrix,
)
from .generic_background_physical_hessian_triangle_master_completeness import (
    NEW_MASTER_IDS,
    PIVOT_FIXTURE,
    PROJECTION,
    _system,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-six-master-coordinates-v1.schema.json"
COMPLETENESS = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json"
MASTER_VALUES = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json"

XS = (X1, X2, X3)
LAMBDA = sp.expand(
    X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3
)
CHART_FACTOR = sp.expand(2 * X1 * X2 + X2**2 - 2 * X2 * X3 + X3**2)
MASTER_IDS = ("J_triangle", "M_x1", "M_x2", *NEW_MASTER_IDS)
MASTER_DEGREES = (3, 2, 2, 0, 0, 0)
DENOMINATOR_POWER = 5
HOLDOUTS = ((2, 3, 5), (3, 5, 7), (5, 7, 11), (7, 11, 13), (11, 13, 17))

_SOLVE_SQUARE: DomainMatrix | None = None
_SOLVE_TARGETS: DomainMatrix | None = None


def _q(value: sp.Expr | int) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _poly_terms(expression: sp.Expr) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *XS, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def polynomial_from_terms(terms: list[dict[str, Any]]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * X1 ** term["exponents"][0]
            * X2 ** term["exponents"][1]
            * X3 ** term["exponents"][2]
            for term in terms
        )
    )


def _rational_function(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator = sp.Poly(numerator, *XS, domain=sp.QQ)
    denominator = sp.Poly(denominator, *XS, domain=sp.QQ)
    if denominator.LC() < 0:
        numerator = -numerator
        denominator = -denominator
    return {
        "numerator_terms": _poly_terms(numerator.as_expr()),
        "denominator_terms": _poly_terms(denominator.as_expr()),
    }


def _compile_element(value: Any) -> tuple[tuple[tuple[tuple[int, ...], int], ...], tuple[tuple[tuple[int, ...], int], ...]]:
    return (
        tuple((tuple(exponents), int(coefficient)) for exponents, coefficient in value.numer.items()),
        tuple((tuple(exponents), int(coefficient)) for exponents, coefficient in value.denom.items()),
    )


def _evaluate_element(
    value: tuple[tuple[tuple[tuple[int, ...], int], ...], tuple[tuple[tuple[int, ...], int], ...]],
    point: tuple[int, int, int],
) -> Any:
    def evaluate(terms: tuple[tuple[tuple[int, ...], int], ...]) -> int:
        return sum(
            coefficient
            * point[0] ** exponents[0]
            * point[1] ** exponents[1]
            * point[2] ** exponents[2]
            for exponents, coefficient in terms
        )

    return sp.QQ(evaluate(value[0]), evaluate(value[1]))


def _compiled_numeric_system(system: dict[str, Any]) -> dict[str, Any]:
    selected = system["selected_matrix"]
    targets = _domain_matrix(system["targets"], system["basis"], selected.domain)
    numeric = selected.to_Matrix().subs(PIVOT_FIXTURE)
    pivot_rows = tuple(numeric.transpose().rref()[1])
    if len(pivot_rows) != 52:
        raise ValueError("six-master coordinate pivot-row count drifted")
    selected_rows = selected.extract(pivot_rows, range(52)).rep.to_list()
    target_rows = targets.extract(pivot_rows, range(11)).rep.to_list()
    return {
        "pivot_rows": pivot_rows,
        "selected": [[_compile_element(value) for value in row] for row in selected_rows],
        "targets": [[_compile_element(value) for value in row] for row in target_rows],
    }


def _numeric_coordinates(compiled: dict[str, Any], point: tuple[int, int, int]) -> sp.Matrix:
    selected = DomainMatrix.from_list(
        [[_evaluate_element(value, point) for value in row] for row in compiled["selected"]],
        sp.QQ,
    )
    targets = DomainMatrix.from_list(
        [[_evaluate_element(value, point) for value in row] for row in compiled["targets"]],
        sp.QQ,
    )
    numerator, denominator = selected.solve_den(targets)
    return (numerator.to_field() / denominator).to_Matrix()[-6:, :]


def _selected_minor_factorization(system: dict[str, Any], pivot_rows: tuple[int, ...]) -> dict[str, Any]:
    ring = sp.ZZ.poly_ring(*XS)
    square = system["selected_matrix"].extract(pivot_rows, range(52)).convert_to(ring)
    determinant = square.det()
    expected = ring.from_sympy(
        132239526912
        * X1**14
        * X2**13
        * X3**10
        * CHART_FACTOR**3
        * LAMBDA**DENOMINATOR_POWER
    )
    if determinant != expected:
        raise ValueError("selected six-master minor factorization drifted")
    return {
        "constant": 132239526912,
        "factors": [
            {"factor": "x1", "power": 14, "status": "CHART_SPURIOUS"},
            {"factor": "x2", "power": 13, "status": "CHART_SPURIOUS"},
            {"factor": "x3", "power": 10, "status": "CHART_SPURIOUS"},
            {"factor": sp.sstr(CHART_FACTOR), "power": 3, "status": "CHART_SPURIOUS"},
            {"factor": sp.sstr(LAMBDA), "power": 5, "status": "PHYSICAL_QUOTIENT_DENOMINATOR"},
        ],
        "total_degree": 53,
        "term_count": len(determinant),
        "status": "EXACT_POLYNOMIAL_RING_FACTORIZATION",
    }


def _solve_channel(channel_index: int) -> list[dict[str, Any]]:
    if _SOLVE_SQUARE is None or _SOLVE_TARGETS is None:
        raise RuntimeError("polynomial coordinate worker was not initialized")
    right_hand_side = _SOLVE_TARGETS.extract(range(52), [channel_index])
    numerator, denominator = _SOLVE_SQUARE.solve_den(right_hand_side)
    if _SOLVE_SQUARE.matmul(numerator) != right_hand_side.scalarmul(denominator):
        raise ValueError(f"polynomial relative-IBP solve failed: channel {channel_index}")
    field = _SOLVE_SQUARE.domain.frac_field()
    solution = (
        numerator.extract(range(46, 52), [0]).convert_to(field)
        / field.convert(denominator)
    ).to_Matrix()
    return [_rational_function(sp.cancel(solution[index, 0])) for index in range(6)]


def _coordinate_payload(
    system: dict[str, Any], compiled: dict[str, Any], *, jobs: int
) -> dict[str, Any]:
    global _SOLVE_SQUARE, _SOLVE_TARGETS
    projection = json.loads(PROJECTION.read_text())
    channel_ids = [row["channel_id"] for row in projection["projection_rows"]]
    channel_degrees = [row["numerator_box_degree"] for row in projection["projection_rows"]]
    ring = sp.QQ.poly_ring(*XS)

    def convert(matrix: Any) -> DomainMatrix:
        return DomainMatrix.from_list(
            [
                [ring.from_sympy(value.as_expr()) for value in row]
                for row in matrix.rep.to_list()
            ],
            ring,
        )

    selected = system["selected_matrix"].extract(compiled["pivot_rows"], range(52))
    targets = _domain_matrix(
        system["targets"], system["basis"], system["selected_matrix"].domain
    ).extract(compiled["pivot_rows"], range(11))
    square = convert(selected)
    _SOLVE_SQUARE = square
    _SOLVE_TARGETS = convert(targets)
    if jobs <= 1:
        coordinate_data = [_solve_channel(index) for index in range(11)]
    else:
        context = multiprocessing.get_context("fork")
        with ProcessPoolExecutor(max_workers=jobs, mp_context=context) as executor:
            coordinate_data = list(executor.map(_solve_channel, range(11)))

    rows = []
    for channel_index, (channel_id, target_degree) in enumerate(
        zip(channel_ids, channel_degrees)
    ):
        master_rows = []
        for master_index, (master_id, master_degree) in enumerate(
            zip(MASTER_IDS, MASTER_DEGREES)
        ):
            rational = coordinate_data[channel_index][master_index]
            numerator_expression = polynomial_from_terms(rational["numerator_terms"])
            denominator_expression = polynomial_from_terms(rational["denominator_terms"])
            expected_weight = target_degree - master_degree
            actual_weight = (
                sp.Poly(numerator_expression, *XS).total_degree()
                - sp.Poly(denominator_expression, *XS).total_degree()
            )
            if actual_weight != expected_weight:
                raise ValueError(f"coordinate homogeneity drifted: {channel_id} {master_id}")
            master_rows.append(
                {
                    "master_id": master_id,
                    "homogeneity_weight": expected_weight,
                    "coordinate": rational,
                }
            )
        rows.append(
            {
                "channel_id": channel_id,
                "target_box_degree": target_degree,
                "master_coordinates": master_rows,
            }
        )

    for point in HOLDOUTS:
        actual = _numeric_coordinates(compiled, point)
        for channel_index, row in enumerate(rows):
            for master_index, master_row in enumerate(row["master_coordinates"]):
                rational = master_row["coordinate"]
                expected = sp.cancel(
                    polynomial_from_terms(rational["numerator_terms"]).subs(dict(zip(XS, point)))
                    / polynomial_from_terms(rational["denominator_terms"]).subs(dict(zip(XS, point)))
                )
                if actual[master_index, channel_index] != expected:
                    raise ValueError(
                        f"six-master coordinate holdout failed: {point} "
                        f"{MASTER_IDS[master_index]} {channel_ids[channel_index]}"
                    )
    return {
        "channel_rows": rows,
        "solve_ledger": {
            "method": "FRACTION_FREE_POLYNOMIAL_RING_SOLVE_ON_EXACT_52_BY_52_PIVOT_MINOR",
            "common_minor_denominator_bound": sp.sstr(
                X1**14 * X2**13 * X3**10 * CHART_FACTOR**3 * LAMBDA**5
            ),
            "coordinate_reduction": "ENTRYWISE_EXACT_GCD_CANCELLATION",
            "full_solution_identity": "ELEVEN_EXACT_IDENTITIES_SQUARE_TIMES_NUMERATOR_EQUALS_TARGET_TIMES_DENOMINATOR",
            "holdout_points": [list(point) for point in HOLDOUTS],
            "holdout_identity_count": len(HOLDOUTS) * 6 * 11,
            "holdout_status": "ALL_EXACT",
        },
    }


def build(*, jobs: int = 1) -> dict[str, Any]:
    completeness = json.loads(COMPLETENESS.read_text())
    master_values = json.loads(MASTER_VALUES.read_text())
    projection = json.loads(PROJECTION.read_text())
    if (
        completeness["claim_flags"]["ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN"]
        is not True
        or master_values["claim_flags"]["RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"]
        is not True
        or len(projection["projection_rows"]) != 11
    ):
        raise ValueError("six-master coordinate dependency gate is not closed")
    system = _system(projection)
    compiled = _compiled_numeric_system(system)
    payload = {
        "selected_minor": _selected_minor_factorization(system, compiled["pivot_rows"]),
        "pivot_rows": list(compiled["pivot_rows"]),
        **_coordinate_payload(system, compiled, jobs=max(1, jobs)),
    }
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-triangle-six-master-coordinates-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES",
        "result_state": "ALL_ELEVEN_PHYSICAL_TRIANGLE_SIX_MASTER_COORDINATE_FUNCTIONS_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": completeness["classical_commit"],
        "dependencies": {
            "physical_five_carrier_projection": _reference(PROJECTION),
            "six_master_completeness": _reference(COMPLETENESS),
            "renormalized_master_values": _reference(MASTER_VALUES),
        },
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "generic nonexceptional x1,x2,x3 with lambda nonzero",
            "input": "eleven exact physical three-H1 numerator rows over Delta^4",
            "output": "six exact rational master-coordinate functions per physical channel",
        },
        **payload,
        "formula_digest": _canonical_digest(payload),
        "claim_flags": {
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED": True,
            "ALL_ELEVEN_CHANNELS_COORDINATED": True,
            "SELECTED_MINOR_LAMBDA5_FACTOR_CERTIFIED": True,
            "PHYSICAL_N3_TRIANGLE_BOUNDARY_FLUX_COMPUTED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "COMPUTE_PHYSICAL_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX_AND_ASSEMBLE_FIVE_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate computes the six reduced rational master-coordinate functions of all eleven physical three-H1 triangle channels by a fraction-free polynomial-ring solve. The exact selected-minor factorization isolates the lambda^5 factor and all chart factors; individual coordinate denominators are reduced independently and are not asserted to equal lambda^5. It does not compute the relative-IBP boundary flux, integrate the complete physical triangle, assemble the five repository third-curvature form factors, supply Gamma1 or Q1, restore a QME, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in ("selected_minor", "pivot_rows", "channel_rows", "solve_ledger")
    }
    if _canonical_digest(payload) != value["formula_digest"]:
        raise ValueError("six-master coordinate formula digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    if args.fast:
        if args.emit:
            raise SystemExit("--fast cannot emit an exhaustive coordinate certificate")
        if not OUTPUT.exists():
            raise SystemExit(f"missing six-master coordinate certificate: {OUTPUT}")
        value = json.loads(OUTPUT.read_text())
        validate(value)
    else:
        value = build(jobs=max(1, args.jobs))
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale six-master coordinate certificate: {OUTPUT}")
    print("GENERIC PHYSICAL TRIANGLE SIX-MASTER COORDINATES: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
