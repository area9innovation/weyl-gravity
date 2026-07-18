#!/usr/bin/env python3
"""Project the exact ghost n=3 triangle onto the scalar-flat CPT carriers."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
QROOT = HERE.parents[1]
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-five-carrier-projection-v1.schema.json"
DEPENDENCIES = {
    "triangle": HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
    "carrier_manifest": QROOT / "transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "K_Ricci_crosswalk": QROOT / "transfer/certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json",
}

Permutation = tuple[int, int, int]
Exponent4 = tuple[int, int, int, int]
ZERO_EXPONENT: Exponent4 = (0, 0, 0, 0)
A1, A2 = sp.symbols("alpha1 alpha2")

CHANNELS: tuple[tuple[str, Permutation], ...] = (
    ("I10", (0, 1, 2)),
    ("I24", (0, 1, 2)),
    ("I24", (1, 0, 2)),
    ("I24", (2, 0, 1)),
    ("I25", (0, 1, 2)),
    ("I25", (1, 0, 2)),
    ("I25", (2, 0, 1)),
    ("I28", (0, 1, 2)),
    ("I28", (0, 2, 1)),
    ("I28", (1, 2, 0)),
    ("I29", (0, 1, 2)),
)
DERIVATIVE_ORDERS = {"I10": 0, "I24": 2, "I25": 2, "I28": 4, "I29": 6}

# The ten invariant triples are unisolvent for homogeneous box polynomials
# through degree three.  Momenta are retained as the stronger reproducible
# fixture because they also determine exact TT evaluation bases.
MOMENTUM_FIXTURES: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...] = (
    ((1, -1, -2, -2), (-2, 1, 0, 2)),
    ((1, 1, -2, 0), (0, 0, 1, 1)),
    ((1, 0, 0, 0), (-2, 1, 1, 0)),
    ((1, -1, 2, -1), (-2, 1, -2, -1)),
    ((-1, 1, 2, 0), (2, 0, 0, 0)),
    ((-1, 0, -1, -2), (-2, 0, 0, -1)),
    ((2, -1, 0, 1), (-1, -1, 2, -2)),
    ((1, 2, -1, -2), (-1, -1, 2, 1)),
    ((2, 0, 0, -1), (1, 1, -2, -1)),
    ((2, 0, -2, 1), (0, -1, 2, -1)),
)


def _q(value: Fraction | int | sp.Rational) -> dict[str, int]:
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
        "result_id": str(value["result_id"]),
        "sha256": _sha256(path),
    }


def _homogeneous_monomials(degree: int, variables: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        exponent
        for exponent in itertools.product(range(degree + 1), repeat=variables)
        if sum(exponent) == degree
    )


def _poly_multiply(
    left: dict[Exponent4, sp.Expr],
    right: dict[Exponent4, sp.Expr],
) -> dict[Exponent4, sp.Expr]:
    result: dict[Exponent4, sp.Expr] = {}
    for left_exp, left_value in left.items():
        for right_exp, right_value in right.items():
            exponent = tuple(
                left_exp[index] + right_exp[index] for index in range(4)
            )
            result[exponent] = result.get(exponent, sp.S.Zero) + left_value * right_value
    return {exponent: value for exponent, value in result.items() if value != 0}


def _bilinear_polynomial(
    left_shift: sp.Matrix,
    matrix: sp.Matrix,
    right_shift: sp.Matrix,
) -> dict[Exponent4, sp.Expr]:
    result: dict[Exponent4, sp.Expr] = {
        ZERO_EXPONENT: (left_shift.T * matrix * right_shift)[0]
    }
    linear = matrix * right_shift + matrix.T * left_shift
    for index, coefficient in enumerate(linear):
        exponent = [0, 0, 0, 0]
        exponent[index] = 1
        key = tuple(exponent)
        result[key] = result.get(key, sp.S.Zero) + coefficient
    for left_index in range(4):
        for right_index in range(4):
            exponent = [0, 0, 0, 0]
            exponent[left_index] += 1
            exponent[right_index] += 1
            key = tuple(exponent)
            result[key] = result.get(key, sp.S.Zero) + matrix[left_index, right_index]
    return {exponent: value for exponent, value in result.items() if value != 0}


def _sector_polynomial(
    bits: tuple[int, int, int],
    shifts: list[sp.Matrix],
    tensors: list[sp.Matrix],
) -> dict[Exponent4, sp.Expr]:
    first, second, third = tensors
    r0, r1, r2 = shifts
    if bits == (0, 0, 0):
        return {ZERO_EXPONENT: sp.trace(first * second * third)}
    if bits == (1, 0, 0):
        return _bilinear_polynomial(r0, first * second * third, r0)
    if bits == (0, 1, 0):
        return _bilinear_polynomial(r1, second * third * first, r1)
    if bits == (0, 0, 1):
        return _bilinear_polynomial(r2, third * first * second, r2)
    if bits == (1, 1, 0):
        return _poly_multiply(
            _bilinear_polynomial(r0, first, r1),
            _bilinear_polynomial(r1, second * third, r0),
        )
    if bits == (1, 0, 1):
        return _poly_multiply(
            _bilinear_polynomial(r0, first * second, r2),
            _bilinear_polynomial(r2, third, r0),
        )
    if bits == (0, 1, 1):
        return _poly_multiply(
            _bilinear_polynomial(r1, second, r2),
            _bilinear_polynomial(r2, third * first, r1),
        )
    return _poly_multiply(
        _poly_multiply(
            _bilinear_polynomial(r0, first, r1),
            _bilinear_polynomial(r1, second, r2),
        ),
        _bilinear_polynomial(r2, third, r0),
    )


def _wick_coefficient(
    polynomial: dict[Exponent4, sp.Expr], pair_count: int
) -> sp.Expr:
    result = sp.S.Zero
    for exponent, coefficient in polynomial.items():
        if sum(exponent) != 2 * pair_count:
            continue
        pairing_count = 1
        for power in exponent:
            if power % 2:
                pairing_count = 0
                break
            for value in range(power - 1, 0, -2):
                pairing_count *= value
        result += coefficient * pairing_count
    return result


def _triangle_value(
    momenta: list[sp.Matrix],
    tensors: list[sp.Matrix],
    alpha1: sp.Expr,
    alpha2: sp.Expr,
) -> tuple[sp.Expr, sp.Expr]:
    alpha0 = 1 - alpha1 - alpha2
    k1, k2, k3 = momenta
    delta = (
        alpha0 * alpha1 * k1.dot(k1)
        + alpha1 * alpha2 * k2.dot(k2)
        + alpha2 * alpha0 * k3.dot(k3)
    )
    shifts = [
        -alpha1 * k1 + alpha2 * k3,
        (1 - alpha1) * k1 + alpha2 * k3,
        -alpha1 * k1 - (1 - alpha2) * k3,
    ]
    result = sp.S.Zero
    for bits in itertools.product((0, 1), repeat=3):
        projector_count = sum(bits)
        polynomial = _sector_polynomial(bits, shifts, tensors)
        alpha_weight = (
            (alpha0 if bits[0] else 1)
            * (alpha1 if bits[1] else 1)
            * (alpha2 if bits[2] else 1)
        )
        for pair_count in range(projector_count + 1):
            result += (
                (-sp.Rational(1, 3)) ** projector_count
                * alpha_weight
                * sp.Rational(
                    sp.factorial(projector_count - pair_count), 2**pair_count
                )
                * delta ** (pair_count - projector_count - 1)
                * _wick_coefficient(polynomial, pair_count)
            )
    return -sp.Rational(8, 3) * result, delta


def _transverse_tracefree_basis(momentum: sp.Matrix) -> list[sp.Matrix]:
    raw = sp.Matrix([list(momentum)]).nullspace()
    orthogonal: list[sp.Matrix] = []
    for vector in raw:
        reduced = vector
        for previous in orthogonal:
            reduced -= previous * (previous.dot(reduced) / previous.dot(previous))
        orthogonal.append(reduced)
    projectors = [vector * vector.T / vector.dot(vector) for vector in orthogonal]
    return [
        projectors[0] - projectors[1],
        projectors[0] - projectors[2],
        orthogonal[0] * orthogonal[1].T + orthogonal[1] * orthogonal[0].T,
        orthogonal[0] * orthogonal[2].T + orthogonal[2] * orthogonal[0].T,
        orthogonal[1] * orthogonal[2].T + orthogonal[2] * orthogonal[1].T,
    ]


def _carrier_value(
    carrier: str,
    momenta: list[sp.Matrix],
    tensors: list[sp.Matrix],
    labels: Permutation,
) -> sp.Expr:
    k1, k2, k3 = [momenta[index] for index in labels]
    first, second, third = [tensors[index] for index in labels]
    if carrier == "I10":
        return sp.trace(first * second * third)
    if carrier == "I24":
        return -(k2.T * first * k3)[0] * sp.trace(second * third)
    if carrier == "I25":
        return -((second * k3).T * first * (third * k2))[0]
    if carrier == "I28":
        return (k1.T * third * k2)[0] * (k3.T * first * second * k3)[0]
    if carrier == "I29":
        return -(
            (k2.T * first * k2)[0]
            * (k3.T * second * k3)[0]
            * (k1.T * third * k1)[0]
        )
    raise ValueError(f"unknown carrier: {carrier}")


def _fixture_momenta(
    fixture: tuple[tuple[int, ...], tuple[int, ...]]
) -> list[sp.Matrix]:
    first, second = [sp.Matrix(value) for value in fixture]
    return [first, second, -first - second]


def _carrier_system(
    momenta: list[sp.Matrix],
) -> tuple[list[tuple[int, int, int]], sp.Matrix, tuple[int, ...], sp.Matrix]:
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices = list(itertools.product(range(5), repeat=3))
    matrix = sp.Matrix(
        [
            [
                _carrier_value(
                    carrier,
                    momenta,
                    [bases[index][choice[index]] for index in range(3)],
                    labels,
                )
                for carrier, labels in CHANNELS
            ]
            for choice in choices
        ]
    )
    if matrix.rank() != 10:
        raise ValueError("scalar-flat carrier evaluation rank drifted")
    pivot_rows = matrix.T.rref()[1]
    gauge_row = [0] * 7 + [1, 1, 1, 0]
    square = sp.Matrix([list(matrix.row(index)) for index in pivot_rows] + [gauge_row])
    if square.rank() != 11:
        raise ValueError("I28 symmetric-section gauge failed to complete the carrier solve")
    return choices, matrix, pivot_rows, square.inv()


def _fixture_coordinate_polynomials(
    fixture: tuple[tuple[int, ...], tuple[int, ...]]
) -> tuple[tuple[int, int, int], list[sp.Poly], dict[str, Any]]:
    momenta = _fixture_momenta(fixture)
    bases = [_transverse_tracefree_basis(momentum) for momentum in momenta]
    choices, matrix, pivot_rows, inverse = _carrier_system(momenta)
    values = []
    delta = None
    for row_index in pivot_rows:
        choice = choices[row_index]
        value, delta = _triangle_value(
            momenta,
            [bases[index][choice[index]] for index in range(3)],
            A1,
            A2,
        )
        values.append(value)
    assert delta is not None
    coordinates = inverse * sp.Matrix(values + [0])
    polynomials = []
    for coordinate in coordinates:
        numerator = sp.cancel(coordinate * delta**4)
        fraction_numerator, fraction_denominator = sp.fraction(numerator)
        if fraction_denominator != 1:
            raise ValueError("projected common-Delta numerator is not polynomial")
        polynomial = sp.Poly(sp.expand(fraction_numerator), A1, A2)
        if polynomial.total_degree() > 9:
            raise ValueError("alpha degree exceeded the sector-count bound")
        polynomials.append(polynomial)
    boxes = tuple(int(momentum.dot(momentum)) for momentum in momenta)
    return boxes, polynomials, {
        "momenta": [list(map(int, momentum)) for momentum in momenta],
        "box_invariants": list(boxes),
        "carrier_matrix_shape": list(matrix.shape),
        "carrier_matrix_rank": matrix.rank(),
        "pivot_tensor_rows": list(pivot_rows),
        "gauge_completed_rank": 11,
    }


def _interpolate_rows(
    fixture_rows: list[tuple[tuple[int, int, int], list[sp.Poly]]]
) -> list[dict[str, Any]]:
    output = []
    for channel_index, (carrier, labels) in enumerate(CHANNELS):
        derivative_order = DERIVATIVE_ORDERS[carrier]
        box_degree = 3 - derivative_order // 2
        box_monomials = _homogeneous_monomials(box_degree, 3)
        box_matrix = sp.Matrix(
            [
                [
                    sp.prod(boxes[index] ** exponent[index] for index in range(3))
                    for exponent in box_monomials
                ]
                for boxes, _ in fixture_rows
            ]
        )
        if box_matrix.rank() != len(box_monomials):
            raise ValueError(f"box interpolation basis is not unisolvent for {carrier}")
        pivot_rows = box_matrix.T.rref()[1]
        square = sp.Matrix([list(box_matrix.row(index)) for index in pivot_rows])
        inverse = square.inv()
        alpha_monomials = sorted(
            {
                exponent
                for _, polynomials in fixture_rows
                for exponent, _ in polynomials[channel_index].terms()
            }
        )
        terms = []
        for alpha_exponents in alpha_monomials:
            values = sp.Matrix(
                [
                    polynomials[channel_index].coeff_monomial(alpha_exponents)
                    for _, polynomials in fixture_rows
                ]
            )
            coefficients = inverse * sp.Matrix([values[index] for index in pivot_rows])
            if box_matrix * coefficients != values:
                raise ValueError(f"box interpolation residual for {carrier} {labels}")
            for box_exponents, coefficient in zip(box_monomials, coefficients):
                if coefficient:
                    terms.append(
                        {
                            "alpha_exponents": list(alpha_exponents),
                            "box_exponents": list(box_exponents),
                            "coefficient": _q(coefficient),
                        }
                    )
        output.append(
            {
                "channel_id": f"{carrier}_{''.join(str(index + 1) for index in labels)}",
                "carrier_id": carrier,
                "label_order": [index + 1 for index in labels],
                "explicit_derivative_order": derivative_order,
                "form_factor_box_homogeneity": -(1 + derivative_order // 2),
                "common_denominator_power": 4,
                "numerator_box_degree": box_degree,
                "maximum_alpha_degree": max(
                    (sum(term["alpha_exponents"]) for term in terms), default=0
                ),
                "term_count": len(terms),
                "terms": terms,
            }
        )
    return output


def _term_map(row: dict[str, Any]) -> dict[tuple[int, ...], sp.Rational]:
    return {
        tuple(term["alpha_exponents"] + term["box_exponents"]): _from_q(
            term["coefficient"]
        )
        for term in row["terms"]
    }


def _validate_projection_rows(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 11:
        raise ValueError("raw projection channel count drifted")
    for row, (carrier, labels) in zip(rows, CHANNELS):
        if row["carrier_id"] != carrier or row["label_order"] != [index + 1 for index in labels]:
            raise ValueError("projection channel order drifted")
        if row["numerator_box_degree"] != 3 - DERIVATIVE_ORDERS[carrier] // 2:
            raise ValueError("projection box degree drifted")
        if any(
            sum(term["box_exponents"]) != row["numerator_box_degree"]
            or sum(term["alpha_exponents"]) > 9
            for term in row["terms"]
        ):
            raise ValueError("projection term grading drifted")
    i28_maps = [_term_map(row) for row in rows[7:10]]
    keys = set().union(*(row.keys() for row in i28_maps))
    if any(sum(row.get(key, sp.S.Zero) for row in i28_maps) != 0 for key in keys):
        raise ValueError("symmetric I28 component was not removed")


def build() -> dict[str, Any]:
    dependencies = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    triangle = dependencies["triangle"]
    manifest = dependencies["carrier_manifest"]
    crosswalk = dependencies["K_Ricci_crosswalk"]
    if (
        triangle["claim_flags"]["GENERIC_GHOST_N3_NONZERO_MOMENTUM_PARAMETRIC_KERNEL_COMPUTED"]
        is not True
        or manifest["quotient_module"]["generic_label_orbit_dimension"] != 10
        or manifest["claim_flags"]["SCALAR_FLAT_I29_REVERSAL_IDENTITY_REPLAYED"]
        is not True
        or crosswalk["claim_flags"]["CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED"]
        is not True
    ):
        raise ValueError("five-carrier projection dependency drifted")

    fixture_data = [_fixture_coordinate_polynomials(fixture) for fixture in MOMENTUM_FIXTURES]
    projection_rows = _interpolate_rows(
        [(boxes, polynomials) for boxes, polynomials, _ in fixture_data]
    )
    _validate_projection_rows(projection_rows)
    formula_digest = hashlib.sha256(
        json.dumps(projection_rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-five-carrier-projection-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION",
        "result_state": "N3_GHOST_TRIANGLE_PROJECTED_TO_SCALAR_FLAT_FIVE_CARRIER_QUOTIENT",
        "lifecycle_state": "N3_PARAMETRIC_CARRIER_PROJECTION_COMPUTED_N1_N2_AND_PHYSICAL_BLOCKS_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": triangle["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "curvature_order": 3,
            "background": "generic nonexceptional momenta on the noncompact asymptotically flat scalar-flat K/Ricci carrier",
            "input_block": "three W=-2 Ric insertions in the flat Endo alpha=-1/2 ghost kernel",
            "output": "exact Feynman-simplex integrands for the five CPT carrier labels in the symmetric-I28 quotient section",
        },
        "convention": {
            "alpha0": "1-alpha1-alpha2",
            "Delta": "alpha0*alpha1*x1+alpha1*alpha2*x2+alpha2*alpha0*x3",
            "box_invariants": "xi=ki^2 with k1+k2+k3=0",
            "channel_formula": "Gamma_channel(alpha,x)=N_channel(alpha1,alpha2,x1,x2,x3)/Delta^4",
            "overall_loop_prefactor": "(4*pi)^-2",
            "W_and_Tr_log_multiplier": "-8/3 already included in every numerator",
            "Fourier_derivative_convention": "nabla acting on labelled carrier i contributes +i*ki; the displayed carrier evaluations include the resulting even-derivative signs",
        },
        "quotient_section": {
            "raw_effective_channel_count": 11,
            "quotient_dimension": 10,
            "raw_channel_order": [
                f"{carrier}_{''.join(str(index + 1) for index in labels)}"
                for carrier, labels in CHANNELS
            ],
            "gauge_condition": "Gamma_I28_123+Gamma_I28_132+Gamma_I28_231=0",
            "relation": "CPT-IV (A.35) is the unique carrier null row; the gauge removes its symmetric I28 component",
            "I29_policy": "source-generic C3 provenance retained; effective scalar-flat S3 reversal identity applied",
        },
        "interpolation_certificate": {
            "box_degree_bound": "common Delta^-4 numerator has box degree 3-d/2 for a carrier with d explicit derivatives",
            "alpha_degree_bound": "sector with s longitudinal projectors has common-denominator alpha degree at most s+6<=9",
            "momentum_fixture_count": len(fixture_data),
            "maximum_box_monomial_count": len(_homogeneous_monomials(3, 3)),
            "degree_three_box_evaluation_rank": 10,
            "fixtures": [row for _, _, row in fixture_data],
        },
        "projection_rows": projection_rows,
        "formula_digest": formula_digest,
        "coefficient_disposition": {
            "ghost_n3_five_carrier_parametric_contribution": "COMPUTED",
            "ghost_n1_curved_Endo_trace": "NOT_COMPUTED",
            "ghost_n2_curved_Endo_trace": "NOT_COMPUTED",
            "complete_ghost_third_curvature_functions": "NOT_COMPUTED",
            "physical_fourth_order_Hessian_functions": "NOT_COMPUTED",
            "complete_repository_third_curvature_functions": "NOT_COMPUTED",
        },
        "claim_flags": {
            "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED": True,
            "GENERIC_GHOST_N3_SCALAR_FLAT_QUOTIENT_SECTION_EXACT": True,
            "GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED": False,
            "GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": "COMPUTE_CURVED_ENDO_N1_N2_INSERTION_TRACES_AND_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate projects the already certified generic nonexceptional-momentum three-Ricci Endo ghost triangle onto the complete scalar-flat parity-even CPT carrier quotient. It gives exact rational Feynman-simplex integrands for I10, the three I24 orientations, the three I25 orientations, the symmetric-section coordinates of I28, and the effective-S3 I29 row. The common Delta^-4 numerator is reconstructed exactly from a box-unisolvent ten-momentum set under the proved homogeneity and alpha-degree bounds; CPT-IV (A.35) fixes the quotient gauge. This computes only the n=3 ghost contribution. It does not compute the curved-Endo n=1 or n=2 insertion traces, the complete ghost determinant, the generic physical fourth-order Hessian kernel, the complete repository third-curvature functions or coefficients, the parity-odd derivative sector, finite normalizations, Gamma1/Q1, residual transfer, Lorentzian QME, Hadamard, particle, positivity, scattering, or unitarity results."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    _validate_projection_rows(value["projection_rows"])
    digest = hashlib.sha256(
        json.dumps(
            value["projection_rows"], sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("five-carrier projection formula digest drifted")
    flags = value["claim_flags"]
    true_flags = {
        "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED",
        "GENERIC_GHOST_N3_SCALAR_FLAT_QUOTIENT_SECTION_EXACT",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("five-carrier projection crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale generic ghost n=3 five-carrier projection: {OUTPUT}")
    print("GENERIC GHOST N3 FIVE-CARRIER PROJECTION: EXACT PARAMETRIC QUOTIENT; N1/N2 OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
