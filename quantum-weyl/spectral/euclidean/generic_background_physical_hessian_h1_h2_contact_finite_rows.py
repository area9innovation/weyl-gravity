#!/usr/bin/env python3
"""Compute the minimally-subtracted finite physical H1-H2 contact rows."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from .generic_background_ghost_n3_five_carrier_projection import (
    CHANNELS,
    DERIVATIVE_ORDERS,
    _carrier_value,
    _carrier_system,
    _fixture_momenta,
    _homogeneous_monomials,
    _transverse_tracefree_basis,
)
from .generic_background_physical_hessian_h1_h2_contact_residue_projection import (
    FIXTURE_OUTPUT as RESIDUE_FIXTURE,
    OUTPUT as RESIDUE_CERTIFICATE,
    _evaluate_q_matrix,
)
from .generic_background_physical_hessian_mixed_h1_h2_corner_fixture import (
    MOMENTA as EQUAL_BOX_MOMENTA,
    TT_BASIS_INDICES,
    _polarized_h2_representation,
)
from .generic_background_physical_hessian_n3_five_carrier_projection import (
    PHYSICAL_MOMENTUM_FIXTURES,
    UNISOLVENCE_PRIME,
    UNSEEN_MOMENTUM_FIXTURES,
    _fraction,
    _modular_pivot_rows,
    _modular_rank,
    _vertex_q_matrix,
)
from .generic_background_physical_hessian_n3_triangle_fixture import (
    _linearized_riemann,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE_OUTPUT = HERE / "fixtures/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_COORDINATES.json"
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json"
FIXTURE_SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-finite-fixture-ledger-v1.schema.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-finite-rows-v1.schema.json"
ENGINE_VERSION = "physical-hessian-h1-h2-contact-finite-v1"


def _q(value: Any) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _trace_polynomial(
    left: sp.Matrix,
    right: list[list[dict[tuple[int, ...], Fraction]]],
) -> dict[tuple[int, ...], Fraction]:
    result: dict[tuple[int, ...], Fraction] = {}
    for row in range(left.rows):
        for column in range(left.cols):
            coefficient = _fraction(left[row, column])
            if not coefficient:
                continue
            for exponent, value in right[column][row].items():
                result[exponent] = result.get(exponent, Fraction()) + coefficient * value
    return {exponent: value for exponent, value in result.items() if value}


def _pair_wick(polynomial: dict[tuple[int, ...], Fraction]) -> sp.Rational:
    """Return the normalized four-dimensional Gaussian pair contraction."""
    value = Fraction()
    for axis in range(4):
        exponent = [0, 0, 0, 0]
        exponent[axis] = 2
        value += polynomial.get(tuple(exponent), Fraction())
    return sp.Rational(value.numerator, value.denominator)


def _finite_contact_value(
    h2: sp.Matrix,
    vertex: list[list[dict[tuple[int, ...], Fraction]]],
    momentum: sp.Matrix,
) -> tuple[sp.Rational, dict[str, Any]]:
    box = sp.Rational(momentum.dot(momentum))
    at_zero = sp.trace(h2 * _evaluate_q_matrix(vertex, sp.zeros(4, 1)))
    at_minus = sp.trace(h2 * _evaluate_q_matrix(vertex, -momentum))
    at_mid = sp.trace(h2 * _evaluate_q_matrix(vertex, -momentum / 2))
    pair = _pair_wick(_trace_polynomial(h2, vertex))
    c2 = sp.factor(4 * at_mid - 2 * at_zero - 2 * at_minus)
    finite = sp.factor(-c2 / (2 * box**2) - pair / (4 * box))

    t = sp.symbols("t")
    reconstructed = sp.expand(
        at_minus * (1 - t) + at_zero * t + c2 * t * (1 - t)
    )
    if any(
        sp.expand(reconstructed.subs(t, point) - expected) != 0
        for point, expected in (
            (sp.S.Zero, at_minus),
            (sp.S.One, at_zero),
            (sp.Rational(1, 2), at_mid),
        )
    ):
        raise ValueError("contact quadratic reconstruction failed")
    return finite, {
        "constant_at_zero": _q(at_zero),
        "constant_at_minus_momentum": _q(at_minus),
        "constant_at_midpoint": _q(at_mid),
        "regular_quadratic_coefficient_c2": _q(c2),
        "pair_wick_coefficient": _q(pair),
        "minimal_subtraction_finite_value": _q(finite),
    }


def _fixture_coordinates(
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
) -> dict[str, Any]:
    momenta = _fixture_momenta(fixture)
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices, carrier_matrix, pivot_rows, inverse = _carrier_system(momenta)
    pivot_choices = [choices[index] for index in pivot_rows]

    needed_h1 = [sorted({choice[leg] for choice in pivot_choices}) for leg in range(3)]
    vertices = [
        {
            basis_index: _vertex_q_matrix(momenta[leg], bases[leg][basis_index])
            for basis_index in needed_h1[leg]
        }
        for leg in range(3)
    ]

    needed_h2: set[tuple[int, int, int, int]] = set()
    for choice in pivot_choices:
        for singled_leg in range(3):
            paired = [index for index in range(3) if index != singled_leg]
            needed_h2.add(
                (paired[0], choice[paired[0]], paired[1], choice[paired[1]])
            )
    needed_riemann = [set() for _ in range(3)]
    for first, first_basis, second, second_basis in needed_h2:
        needed_riemann[first].add(first_basis)
        needed_riemann[second].add(second_basis)
    riemann = [
        {
            basis_index: _linearized_riemann(momenta[leg], bases[leg][basis_index])
            for basis_index in sorted(needed_riemann[leg])
        }
        for leg in range(3)
    ]
    h2_bank = {
        (first, first_basis, second, second_basis): _polarized_h2_representation(
            bases[first][first_basis],
            riemann[first][first_basis],
            bases[second][second_basis],
            riemann[second][second_basis],
        )[0]
        for first, first_basis, second, second_basis in sorted(needed_h2)
    }

    values = [[] for _ in range(3)]
    tensor_ledger = [[] for _ in range(3)]
    for choice in pivot_choices:
        for singled_leg in range(3):
            paired = [index for index in range(3) if index != singled_leg]
            h2 = h2_bank[
                paired[0], choice[paired[0]], paired[1], choice[paired[1]]
            ]
            finite, ledger = _finite_contact_value(
                h2,
                vertices[singled_leg][choice[singled_leg]],
                momenta[singled_leg],
            )
            values[singled_leg].append(finite)
            tensor_ledger[singled_leg].append(ledger)

    contacts = []
    for singled_leg in range(3):
        coordinates = inverse * sp.Matrix(values[singled_leg] + [0])
        if sum(coordinates[7:10], sp.S.Zero) != 0:
            raise ValueError("finite contact projection left the I28 quotient section")
        contacts.append(
            {
                "singled_leg": singled_leg + 1,
                "minimal_subtraction_finite_coordinates": [_q(value) for value in coordinates],
                "tensor_rows": tensor_ledger[singled_leg],
            }
        )
    return {
        "fixture": [list(vector) for vector in fixture],
        "boxes": [int(momentum.dot(momentum)) for momentum in momenta],
        "carrier_matrix_rank": int(carrier_matrix.rank()),
        "pivot_tensor_rows": list(pivot_rows),
        "pivot_tensor_choices": [list(choice) for choice in pivot_choices],
        "contacts": contacts,
    }


def rebuild_fixture_ledger(workers: int) -> dict[str, Any]:
    fixtures = PHYSICAL_MOMENTUM_FIXTURES + UNSEEN_MOMENTUM_FIXTURES
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            entries = list(pool.map(_fixture_coordinates, fixtures))
    else:
        entries = [_fixture_coordinates(fixture) for fixture in fixtures]
    value = {
        "schema": "quantum-weyl-generic-background-physical-hessian-h1-h2-contact-finite-fixture-ledger-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_FIXTURE_LEDGER",
        "result_state": "EXACT_MINIMAL_SUBTRACTION_FINITE_CONTACT_FIXTURES_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "engine_version": ENGINE_VERSION,
        "generator_sha256": _sha256(Path(__file__)),
        "dependencies": {
            "residue_fixture": _reference(RESIDUE_FIXTURE),
            "residue_certificate": _reference(RESIDUE_CERTIFICATE),
        },
        "training_fixture_count": len(PHYSICAL_MOMENTUM_FIXTURES),
        "unseen_fixture_count": len(UNSEEN_MOMENTUM_FIXTURES),
        "entries": entries,
        "entry_digest": _digest(entries),
    }
    validate_fixture(value)
    return value


def _load_fixture_ledger() -> dict[str, Any]:
    value = json.loads(FIXTURE_OUTPUT.read_text())
    validate_fixture(value)
    if (
        value["engine_version"] != ENGINE_VERSION
        or value["generator_sha256"] != _sha256(Path(__file__))
        or value["entry_digest"] != _digest(value["entries"])
    ):
        raise ValueError("finite contact fixture provenance drifted")
    return value


def _interpolation_solver(
    entries: list[dict[str, Any]], degree: int
) -> tuple[tuple[tuple[int, ...], ...], sp.Matrix, tuple[int, ...], sp.Matrix]:
    monomials = _homogeneous_monomials(degree, 3)
    integer_rows = [
        [
            int(sp.prod(entry["boxes"][index] ** exponent[index] for index in range(3)))
            for exponent in monomials
        ]
        for entry in entries
    ]
    if _modular_rank(integer_rows, UNISOLVENCE_PRIME) != len(monomials):
        raise ValueError("finite-contact interpolation basis is not unisolvent")
    pivots = _modular_pivot_rows(integer_rows, UNISOLVENCE_PRIME)
    matrix = sp.Matrix(integer_rows)
    square = sp.Matrix([list(matrix.row(index)) for index in pivots])
    return monomials, matrix, pivots, square.inv()


def _interpolate_rows(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    solvers = {}
    rows = []
    for contact_index in range(3):
        for channel_index, (carrier, labels) in enumerate(CHANNELS):
            derivative_order = DERIVATIVE_ORDERS[carrier]
            degree = 5 - derivative_order // 2
            if degree not in solvers:
                solvers[degree] = _interpolation_solver(entries, degree)
            monomials, matrix, pivots, inverse = solvers[degree]
            values = sp.Matrix(
                [
                    sp.prod(sp.Integer(box) ** 2 for box in entry["boxes"])
                    * _from_q(
                        entry["contacts"][contact_index][
                            "minimal_subtraction_finite_coordinates"
                        ][channel_index]
                    )
                    for entry in entries
                ]
            )
            coefficients = inverse * sp.Matrix([values[index] for index in pivots])
            if matrix * coefficients != values:
                raise ValueError("finite contact interpolation residual")
            terms = [
                {"box_exponents": list(exponent), "coefficient": _q(coefficient)}
                for exponent, coefficient in zip(monomials, coefficients)
                if coefficient
            ]
            rows.append(
                {
                    "contact_id": f"H1_{contact_index + 1}_H2_{''.join(str(i + 1) for i in range(3) if i != contact_index)}",
                    "singled_H1_leg": contact_index + 1,
                    "carrier_id": carrier,
                    "label_order": [index + 1 for index in labels],
                    "explicit_derivative_order": derivative_order,
                    "box_denominator_exponents": [2, 2, 2],
                    "numerator_box_degree": degree,
                    "finite_term_count": len(terms),
                    "minimal_subtraction_finite_terms": terms,
                }
            )
    return rows


def _evaluate(row: dict[str, Any], boxes: list[int]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(boxes[index] ** exponent for index, exponent in enumerate(term["box_exponents"]))
        for term in row["minimal_subtraction_finite_terms"]
    )
    denominator = sp.prod(
        boxes[index] ** exponent
        for index, exponent in enumerate(row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def _validate_rows(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 33:
        raise ValueError("finite contact row count drifted")
    for contact_index in range(3):
        block = rows[11 * contact_index : 11 * (contact_index + 1)]
        for row in block:
            if any(
                sum(term["box_exponents"]) != row["numerator_box_degree"]
                for term in row["minimal_subtraction_finite_terms"]
            ):
                raise ValueError("finite contact homogeneity drifted")
        exponents = {
            tuple(term["box_exponents"])
            for row in block[7:10]
            for term in row["minimal_subtraction_finite_terms"]
        }
        for exponent in exponents:
            if sum(
                _from_q(term["coefficient"])
                for row in block[7:10]
                for term in row["minimal_subtraction_finite_terms"]
                if tuple(term["box_exponents"]) == exponent
            ) != 0:
                raise ValueError("finite contact I28 relation failed")


def build() -> dict[str, Any]:
    fixture = _load_fixture_ledger()
    residue = json.loads(RESIDUE_CERTIFICATE.read_text())
    if not residue["claim_flags"]["GENERIC_CONTACT_SCALE_LOG_KERNELS_COMPUTED"]:
        raise ValueError("contact residues are not certified")
    training = fixture["entries"][: len(PHYSICAL_MOMENTUM_FIXTURES)]
    unseen = fixture["entries"][len(PHYSICAL_MOMENTUM_FIXTURES) :]
    rows = _interpolate_rows(training)
    _validate_rows(rows)
    mellin_parameter = sp.symbols("s", positive=True)
    endpoint_beta = (
        sp.gamma(mellin_parameter)
        * sp.gamma(mellin_parameter + 1)
        / sp.gamma(2 * mellin_parameter + 1)
    )
    endpoint_finite_part = sp.limit(
        endpoint_beta - 1 / mellin_parameter,
        mellin_parameter,
        0,
        dir="+",
    )
    if endpoint_finite_part != 0:
        raise ValueError("Mellin endpoint finite constant drifted")
    unseen_ledger = []
    for entry in unseen:
        defects = []
        for row_index, row in enumerate(rows):
            contact_index, channel_index = divmod(row_index, 11)
            expected = _from_q(
                entry["contacts"][contact_index][
                    "minimal_subtraction_finite_coordinates"
                ][channel_index]
            )
            if _evaluate(row, entry["boxes"]) != expected:
                defects.append(row_index)
        if defects:
            raise ValueError(f"unseen finite-contact defects: {defects}")
        unseen_ledger.append({"boxes": entry["boxes"], "channel_defect_count": 0})

    equal_box_entry = _fixture_coordinates(
        (
            tuple(EQUAL_BOX_MOMENTA[0]),
            tuple(EQUAL_BOX_MOMENTA[1]),
        )
    )
    # The helper reconstructs the third momentum from conservation.
    equal_momenta = [sp.Matrix(row) for row in EQUAL_BOX_MOMENTA]
    fixture_bases = [_transverse_tracefree_basis(momentum) for momentum in equal_momenta]
    fixture_tensors = [
        fixture_bases[leg][basis]
        for leg, basis in enumerate(TT_BASIS_INDICES)
    ]
    fixture_carriers = [
        sp.Rational(_carrier_value(carrier, equal_momenta, fixture_tensors, labels))
        for carrier, labels in CHANNELS
    ]
    equal_box_contact_values = [
        sp.factor(
            sum(
                fixture_carriers[index] * _from_q(value)
                for index, value in enumerate(
                    contact["minimal_subtraction_finite_coordinates"]
                )
            )
        )
        for contact in equal_box_entry["contacts"]
    ]

    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-h1-h2-contact-finite-rows-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS",
        "result_state": "GENERIC_H1_H2_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": residue["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "carrier": "scalar-flat ten-dimensional five-carrier quotient",
            "subtraction": "common resolved-boundary Mellin minimal subtraction at unit dimensionless scale",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
        },
        "finite_contact_theorem": {
            "quadratic_decomposition": "C(t)=C(-p)*(1-t)+C(0)*t+c2*t*(1-t)",
            "coefficient_reconstruction": "c2=4*C(-p/2)-2*C(-p)-2*C(0)",
            "density": "-C(t)/(2*t*(1-t)*p^4)-P/(4*p^2)",
            "minimal_subtraction_finite_row": "-c2/(2*p^4)-P/(4*p^2)",
            "endpoint_finite_constant": "FP[B(s,s+1)] at s=0 is zero",
            "mellin_endpoint_check": _q(endpoint_finite_part),
            "contact_count": 3,
            "raw_channel_count_per_contact": 11,
            "quotient_dimension": 10,
        },
        "interpolation": {
            "training_fixture_count": len(training),
            "unseen_fixture_count": len(unseen),
            "common_box_denominator_exponents": [2, 2, 2],
            "numerator_degree_rule": "5-explicit_derivative_order/2",
            "unisolvence_prime": UNISOLVENCE_PRIME,
            "row_count": len(rows),
            "formula_digest": _digest(rows),
            "unseen_ledger": unseen_ledger,
        },
        "projection_rows": rows,
        "equal_box_regression": {
            "box_invariants": equal_box_entry["boxes"],
            "contact_finite_values": [_q(value) for value in equal_box_contact_values],
            "combined_contact_finite_value": _q(sum(equal_box_contact_values)),
            "TT_basis_indices": list(TT_BASIS_INDICES),
            "carrier_coordinate_count": len(fixture_carriers),
        },
        "fixture_ledger": _reference(FIXTURE_OUTPUT),
        "dependencies": {
            "contact_residue_projection": _reference(RESIDUE_CERTIFICATE),
            "contact_residue_fixture": _reference(RESIDUE_FIXTURE),
        },
        "claim_flags": {
            "GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED": True,
            "ALL_THREE_CONTACT_FINITE_ROWS_PROJECTED": True,
            "QUADRATIC_CONTACT_RECONSTRUCTION_VERIFIED": True,
            "GENERIC_I28_QUOTIENT_RELATION_PRESERVED": True,
            "FINITE_COUNTERTERM_NORMALIZATION_FIXED": False,
            "RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "REDUCE_RENORMALIZED_PHYSICAL_TRIANGLE_BULK_AND_ASSEMBLE_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate computes the generic finite H1-H2 contact contribution selected by the already-declared common Mellin minimal-subtraction extension. It does not fix an arbitrary mu-independent finite local counterterm, reduce the renormalized H1-cubed triangle bulk, complete the physical form factors, change the anomaly/QME disposition, or certify a Lorentzian theory.",
    }
    validate(result)
    return result


def validate_fixture(value: dict[str, Any]) -> None:
    schema = json.loads(FIXTURE_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild-fixtures", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.rebuild_fixtures:
        value = rebuild_fixture_ledger(max(1, args.workers))
        FIXTURE_OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != rendered:
            raise SystemExit("stored finite contact rows are stale")
        print("physical H1-H2 finite contact rows: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
