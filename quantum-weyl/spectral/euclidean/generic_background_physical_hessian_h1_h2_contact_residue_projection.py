#!/usr/bin/env python3
"""Project the generic physical H1-H2 endpoint residue to CPT carriers.

The mixed cubic trace-log term is a two-propagator contact cell.  Its
logarithmic endpoint residue depends only on the loop-independent part of the
H1 vertex.  For the contact with singled leg ``i`` it is

    -Tr[H2_jk (H1_i(k_i,0)+H1_i(k_i,-k_i))]/(2 (k_i^2)^2).

The left and right endpoint contributions are equal separately.  Expensive
tensor evaluation is frozen in a content-addressed fixture ledger; the normal
certificate path performs only exact rational interpolation and unseen-row
checks.
"""

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
    _carrier_system,
    _fixture_momenta,
    _homogeneous_monomials,
    _transverse_tracefree_basis,
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
    _modular_pivot_rows,
    _modular_rank,
    _vertex_q_matrix,
)
from .generic_background_physical_hessian_n3_triangle_fixture import (
    _linearized_riemann,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE_OUTPUT = HERE / "fixtures/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_COORDINATES.json"
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION.json"
FIXTURE_SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-residue-fixture-ledger-v1.schema.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-h1-h2-contact-residue-projection-v1.schema.json"
ENGINE_VERSION = "physical-hessian-h1-h2-contact-residue-v1"
DEPENDENCIES = {
    "physical_H1": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
    "physical_H2": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_CURVATURE_SQUARED.json",
    "physical_five_carrier_projection": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
    "mixed_equal_box_fixture": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_MIXED_H1_H2_CORNER_FIXTURE.json",
    "covariant_Volterra_carrier": HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json",
}


def _q(value: Any) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


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


def _evaluate_q_polynomial(
    polynomial: dict[tuple[int, ...], Fraction], point: sp.Matrix
) -> sp.Rational:
    return sp.Rational(
        sum(
            coefficient
            * sp.prod(point[index] ** exponent[index] for index in range(4))
            for exponent, coefficient in polynomial.items()
        )
    )


def _evaluate_q_matrix(
    matrix: list[list[dict[tuple[int, ...], Fraction]]], point: sp.Matrix
) -> sp.Matrix:
    return sp.Matrix(
        [
            [_evaluate_q_polynomial(entry, point) for entry in row]
            for row in matrix
        ]
    )


def _fixture_coordinates(
    fixture: tuple[tuple[int, ...], tuple[int, ...]],
) -> dict[str, Any]:
    momenta = _fixture_momenta(fixture)
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices, carrier_matrix, pivot_rows, inverse = _carrier_system(momenta)
    pivot_choices = [choices[index] for index in pivot_rows]

    needed_h1 = [
        sorted({choice[leg] for choice in pivot_choices}) for leg in range(3)
    ]
    endpoint_vertices: list[dict[int, tuple[sp.Matrix, sp.Matrix]]] = []
    for leg in range(3):
        bank = {}
        for basis_index in needed_h1[leg]:
            polynomial = _vertex_q_matrix(
                momenta[leg], bases[leg][basis_index]
            )
            bank[basis_index] = (
                _evaluate_q_matrix(polynomial, sp.zeros(4, 1)),
                _evaluate_q_matrix(polynomial, -momenta[leg]),
            )
        endpoint_vertices.append(bank)

    needed_h2: set[tuple[int, int, int, int]] = set()
    for choice in pivot_choices:
        for singled_leg in range(3):
            paired = [index for index in range(3) if index != singled_leg]
            needed_h2.add(
                (
                    paired[0],
                    choice[paired[0]],
                    paired[1],
                    choice[paired[1]],
                )
            )
    needed_riemann = [set() for _ in range(3)]
    for first, first_basis, second, second_basis in needed_h2:
        needed_riemann[first].add(first_basis)
        needed_riemann[second].add(second_basis)
    riemann = [
        {
            basis_index: _linearized_riemann(
                momenta[leg], bases[leg][basis_index]
            )
            for basis_index in sorted(needed_riemann[leg])
        }
        for leg in range(3)
    ]
    h2_bank = {}
    for first, first_basis, second, second_basis in sorted(needed_h2):
        h2_bank[first, first_basis, second, second_basis] = (
            _polarized_h2_representation(
                bases[first][first_basis],
                riemann[first][first_basis],
                bases[second][second_basis],
                riemann[second][second_basis],
            )[0]
        )

    left_values = [[] for _ in range(3)]
    right_values = [[] for _ in range(3)]
    endpoint_defects = 0
    for choice in pivot_choices:
        for singled_leg in range(3):
            paired = [index for index in range(3) if index != singled_leg]
            h2 = h2_bank[
                paired[0],
                choice[paired[0]],
                paired[1],
                choice[paired[1]],
            ]
            at_zero, at_minus_k = endpoint_vertices[singled_leg][
                choice[singled_leg]
            ]
            box = momenta[singled_leg].dot(momenta[singled_leg])
            left = sp.factor(-sp.Rational(1, 2) * sp.trace(h2 * at_zero) / box**2)
            right = sp.factor(
                -sp.Rational(1, 2) * sp.trace(h2 * at_minus_k) / box**2
            )
            endpoint_defects += int(left != right)
            left_values[singled_leg].append(left)
            right_values[singled_leg].append(right)
    if endpoint_defects:
        raise ValueError("generic H1-H2 left/right endpoint equality failed")

    contacts = []
    for singled_leg in range(3):
        left_coordinates = inverse * sp.Matrix(left_values[singled_leg] + [0])
        right_coordinates = inverse * sp.Matrix(right_values[singled_leg] + [0])
        if left_coordinates != right_coordinates:
            raise ValueError("projected contact endpoint equality failed")
        if sum(left_coordinates[7:10], sp.S.Zero) != 0:
            raise ValueError("contact projection left the symmetric I28 section")
        contacts.append(
            {
                "singled_leg": singled_leg + 1,
                "single_endpoint_coordinates": [_q(value) for value in left_coordinates],
                "combined_endpoint_coordinates": [
                    _q(2 * value) for value in left_coordinates
                ],
            }
        )
    boxes = [int(momentum.dot(momentum)) for momentum in momenta]
    return {
        "fixture": [list(vector) for vector in fixture],
        "boxes": boxes,
        "carrier_matrix_rank": int(carrier_matrix.rank()),
        "pivot_tensor_rows": list(pivot_rows),
        "pivot_tensor_choices": [list(choice) for choice in pivot_choices],
        "unique_H2_pair_count": len(needed_h2),
        "endpoint_equality_defect_count": endpoint_defects,
        "contacts": contacts,
    }


def _equal_box_regression() -> dict[str, Any]:
    momenta = [sp.Matrix(row) for row in EQUAL_BOX_MOMENTA]
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    tensors = [
        bases[leg][basis_index]
        for leg, basis_index in enumerate(TT_BASIS_INDICES)
    ]
    riemann = [
        _linearized_riemann(momentum, tensor)
        for momentum, tensor in zip(momenta, tensors)
    ]
    values = []
    for singled_leg in range(3):
        paired = [index for index in range(3) if index != singled_leg]
        h2 = _polarized_h2_representation(
            tensors[paired[0]],
            riemann[paired[0]],
            tensors[paired[1]],
            riemann[paired[1]],
        )[0]
        vertex = _vertex_q_matrix(momenta[singled_leg], tensors[singled_leg])
        at_zero = _evaluate_q_matrix(vertex, sp.zeros(4, 1))
        at_minus_k = _evaluate_q_matrix(vertex, -momenta[singled_leg])
        box = momenta[singled_leg].dot(momenta[singled_leg])
        left = sp.factor(-sp.Rational(1, 2) * sp.trace(h2 * at_zero) / box**2)
        right = sp.factor(
            -sp.Rational(1, 2) * sp.trace(h2 * at_minus_k) / box**2
        )
        if left != right:
            raise ValueError("equal-box contact endpoint equality failed")
        values.append(left)
    return {
        "box_invariants": [int(momentum.dot(momentum)) for momentum in momenta],
        "TT_basis_indices": list(TT_BASIS_INDICES),
        "single_endpoint_coefficients": [_q(value) for value in values],
        "combined_all_contacts": _q(2 * sum(values)),
    }


def rebuild_fixture_ledger(workers: int) -> dict[str, Any]:
    fixtures = PHYSICAL_MOMENTUM_FIXTURES + UNSEEN_MOMENTUM_FIXTURES
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            entries = list(pool.map(_fixture_coordinates, fixtures))
    else:
        entries = [_fixture_coordinates(fixture) for fixture in fixtures]
    value = {
        "schema": "quantum-weyl-generic-background-physical-hessian-h1-h2-contact-residue-fixture-ledger-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_FIXTURE_LEDGER",
        "result_state": "EXACT_CONTACT_RESIDUE_COORDINATE_FIXTURES_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "engine_version": ENGINE_VERSION,
        "generator_sha256": _sha256(Path(__file__)),
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "training_fixture_count": len(PHYSICAL_MOMENTUM_FIXTURES),
        "unseen_fixture_count": len(UNSEEN_MOMENTUM_FIXTURES),
        "entries": entries,
        "equal_box_regression": _equal_box_regression(),
        "entry_digest": _canonical_digest(entries),
    }
    validate_fixture(value)
    return value


def _load_fixture_ledger() -> dict[str, Any]:
    if not FIXTURE_OUTPUT.is_file():
        raise ValueError("contact fixture ledger is absent; run --rebuild-fixtures")
    value = json.loads(FIXTURE_OUTPUT.read_text())
    validate_fixture(value)
    if (
        value["engine_version"] != ENGINE_VERSION
        or value["generator_sha256"] != _sha256(Path(__file__))
        or value["training_fixture_count"] != len(PHYSICAL_MOMENTUM_FIXTURES)
        or value["unseen_fixture_count"] != len(UNSEEN_MOMENTUM_FIXTURES)
        or value["entry_digest"] != _canonical_digest(value["entries"])
    ):
        raise ValueError("contact fixture ledger provenance drifted")
    for name, path in DEPENDENCIES.items():
        reference = value["dependencies"][name]
        if reference != _reference(path):
            raise ValueError(f"contact fixture dependency drifted: {name}")
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
        raise ValueError(f"contact box basis is not unisolvent at degree {degree}")
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
            numerator_degree = 5 - derivative_order // 2
            if numerator_degree not in solvers:
                solvers[numerator_degree] = _interpolation_solver(
                    entries, numerator_degree
                )
            monomials, matrix, pivots, inverse = solvers[numerator_degree]
            values = sp.Matrix(
                [
                    sp.prod(sp.Integer(box) ** 2 for box in entry["boxes"])
                    * _from_q(
                        entry["contacts"][contact_index][
                            "single_endpoint_coordinates"
                        ][channel_index]
                    )
                    for entry in entries
                ]
            )
            coefficients = inverse * sp.Matrix([values[index] for index in pivots])
            if matrix * coefficients != values:
                raise ValueError(
                    f"contact Laurent interpolation residual for leg {contact_index + 1} {carrier} {labels}"
                )
            terms = [
                {"box_exponents": list(exponent), "coefficient": _q(coefficient)}
                for exponent, coefficient in zip(monomials, coefficients)
                if coefficient
            ]
            rows.append(
                {
                    "contact_id": f"H1_{contact_index + 1}_H2_{''.join(str(index + 1) for index in range(3) if index != contact_index)}",
                    "singled_H1_leg": contact_index + 1,
                    "carrier_id": carrier,
                    "label_order": [index + 1 for index in labels],
                    "explicit_derivative_order": derivative_order,
                    "box_denominator_exponents": [2, 2, 2],
                    "numerator_box_degree": numerator_degree,
                    "single_endpoint_term_count": len(terms),
                    "single_endpoint_terms": terms,
                    "left_right_endpoint_equality": "EXACT",
                    "combined_endpoint_multiplier": 2,
                    "renormalized_scale_kernel": f"2*endpoint_residue*log(mu^2/x{contact_index + 1})",
                }
            )
    return rows


def _evaluate_row(row: dict[str, Any], boxes: list[int]) -> sp.Rational:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(
            boxes[index] ** exponent
            for index, exponent in enumerate(term["box_exponents"])
        )
        for term in row["single_endpoint_terms"]
    )
    denominator = sp.prod(
        boxes[index] ** exponent
        for index, exponent in enumerate(row["box_denominator_exponents"])
    )
    return sp.Rational(numerator / denominator)


def _validate_projection_rows(rows: list[dict[str, Any]]) -> None:
    """Check exact structure not expressible compactly in JSON Schema.

    The raw eleven-channel carrier list contains three I28 labelings with one
    symmetric linear relation.  The interpolation must preserve the quotient
    section used by every tensor fixture; checking it coefficient by
    coefficient prevents a rational fit from drifting outside the declared
    ten-dimensional carrier quotient.
    """

    if len(rows) != 3 * len(CHANNELS):
        raise ValueError("contact projection row count drifted")
    for contact_index in range(3):
        block = rows[
            contact_index * len(CHANNELS) : (contact_index + 1) * len(CHANNELS)
        ]
        for channel_index, row in enumerate(block):
            carrier, labels = CHANNELS[channel_index]
            expected_degree = 5 - DERIVATIVE_ORDERS[carrier] // 2
            if (
                row["singled_H1_leg"] != contact_index + 1
                or row["carrier_id"] != carrier
                or row["label_order"] != [index + 1 for index in labels]
                or row["numerator_box_degree"] != expected_degree
                or row["single_endpoint_term_count"]
                != len(row["single_endpoint_terms"])
            ):
                raise ValueError("contact projection row metadata drifted")
            if any(
                sum(term["box_exponents"]) != expected_degree
                for term in row["single_endpoint_terms"]
            ):
                raise ValueError("contact projection lost box homogeneity")

        i28_sum: dict[tuple[int, ...], sp.Rational] = {}
        for row in block[7:10]:
            if row["carrier_id"] != "I28":
                raise ValueError("carrier ordering no longer exposes I28 section")
            for term in row["single_endpoint_terms"]:
                exponent = tuple(term["box_exponents"])
                i28_sum[exponent] = i28_sum.get(exponent, sp.S.Zero) + _from_q(
                    term["coefficient"]
                )
        if any(value != 0 for value in i28_sum.values()):
            raise ValueError("interpolated rows left the symmetric I28 section")


def _validate_unseen(
    rows: list[dict[str, Any]], entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    ledger = []
    for entry in entries:
        defects = []
        for row_index, row in enumerate(rows):
            contact_index = row_index // len(CHANNELS)
            channel_index = row_index % len(CHANNELS)
            expected = _from_q(
                entry["contacts"][contact_index][
                    "single_endpoint_coordinates"
                ][channel_index]
            )
            if _evaluate_row(row, entry["boxes"]) != expected:
                defects.append(row_index)
        if defects:
            raise ValueError(f"unseen contact projection defects: {defects}")
        ledger.append(
            {
                "boxes": entry["boxes"],
                "channel_defect_count": 0,
                "coordinate_digest": _canonical_digest(entry["contacts"]),
            }
        )
    return ledger


def build() -> dict[str, Any]:
    fixture = _load_fixture_ledger()
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    if (
        dependencies["physical_H2"]["claim_flags"][
            "ALGEBRAIC_CURVATURE_SQUARED_H2_IMPORTED"
        ]
        is not True
        or dependencies["covariant_Volterra_carrier"]["claim_flags"][
            "GENERIC_COVARIANT_VOLTERRA_CARRIER_COMPUTED"
        ]
        is not True
    ):
        raise ValueError("contact projection dependencies are not active")
    training = fixture["entries"][: len(PHYSICAL_MOMENTUM_FIXTURES)]
    unseen = fixture["entries"][len(PHYSICAL_MOMENTUM_FIXTURES) :]
    rows = _interpolate_rows(training)
    _validate_projection_rows(rows)
    unseen_ledger = _validate_unseen(rows, unseen)
    equal_box = fixture["equal_box_regression"]
    expected_equal_box = dependencies["mixed_equal_box_fixture"][
        "operational_H2"
    ]["bubble_rows"]
    expected_values = [row["left_endpoint_log_coefficient"] for row in expected_equal_box]
    if (
        equal_box["single_endpoint_coefficients"] != expected_values
        or equal_box["combined_all_contacts"]
        != dependencies["mixed_equal_box_fixture"]["mixed_H1_H2_endpoint"][
            "full_endpoint_log_coefficient"
        ]
    ):
        raise ValueError("generic contact formula lost equal-box regression")
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-h1-h2-contact-residue-projection-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_RESIDUE_PROJECTION",
        "result_state": "GENERIC_H1_H2_CONTACT_ENDPOINT_RESIDUES_PROJECTED_TO_FIVE_CARRIER_QUOTIENT",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": dependencies["physical_H2"]["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "generic scalar-flat nonexceptional momentum chart",
            "operator": "same-gauge rank-nine monic physical Hessian H0+H1+H2",
            "computed_row": "logarithmic endpoint residue of all three H1-H2 contact cells",
        },
        "endpoint_theorem": {
            "formula": "Res_i,left=-Tr[H2_jk H1_i(k_i,0)]/(2 (k_i^2)^2); Res_i,right=-Tr[H2_jk H1_i(k_i,-k_i)]/(2 (k_i^2)^2)",
            "left_right_equality": "EXACT_ON_ALL_30_FIXTURES",
            "loop_pair_term_status": "FINITE_AT_ENDPOINTS_AND_ZERO_IN_LOG_RESIDUE",
            "contact_count": 3,
            "endpoint_count": 6,
            "raw_channel_count_per_contact": len(CHANNELS),
            "quotient_dimension": 10,
        },
        "interpolation": {
            "training_fixture_count": len(training),
            "unseen_fixture_count": len(unseen),
            "common_box_denominator_exponents": [2, 2, 2],
            "numerator_degree_rule": "5-explicit_derivative_order/2",
            "unisolvence_prime": UNISOLVENCE_PRIME,
            "row_count": len(rows),
            "formula_digest": _canonical_digest(rows),
            "unseen_ledger": unseen_ledger,
        },
        "projection_rows": rows,
        "equal_box_regression": equal_box,
        "fixture_ledger": _reference(FIXTURE_OUTPUT),
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "claim_flags": {
            "GENERIC_H1_H2_CONTACT_ENDPOINT_KERNELS_EVALUATED": True,
            "ALL_THREE_CONTACT_CELLS_PROJECTED": True,
            "LEFT_RIGHT_ENDPOINT_EQUALITY_CERTIFIED": True,
            "GENERIC_CONTACT_SCALE_LOG_KERNELS_COMPUTED": True,
            "SYMMETRIC_I28_QUOTIENT_SECTION_PRESERVED": True,
            "GENERIC_CONTACT_FINITE_LOCAL_ROWS_FIXED": False,
            "RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED": False,
            "PHYSICAL_M14_CORNER_CLASS_DISPOSED": False,
            "PHYSICAL_THIRD_CURVATURE_FORM_FACTORS_COMPLETE": False,
            "QME_OR_ANOMALY_STATUS_CHANGED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "ASSEMBLE_TRIANGLE_AND_CONTACT_BOUNDARY_INCIDENCE_ON_COVARIANT_VOLTERRA_CARRIER_AND_DECIDE_M14",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate evaluates and projects the logarithmic endpoint residues of all three generic H1-H2 contact cells to the scalar-flat five-carrier quotient, proves left/right endpoint equality, fixes their single-scale logarithmic kernels, and reproduces the equal-box coefficient 2704/27. It does not fix finite local contact rows, assemble the renormalized triangle/contact incidence, dispose M14, complete a physical form factor, change the QME disposition, or certify a Lorentzian theory.",
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
            raise SystemExit("stored generic contact residue projection is stale")
        print("physical H1-H2 contact residue projection: PASS")
        return 0
    OUTPUT.write_text(rendered)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
