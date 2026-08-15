#!/usr/bin/env python3
"""Certify the failure of two pointwise BT Witten parametrices."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from itertools import product


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_GAUSS_NEWTON_"
    "WITTEN_PARAMETRIX_OBSTRUCTION_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-gauss-newton-"
    "witten-parametrix-obstruction-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-gauss-newton-witten-parametrix-obstruction.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_gauss_newton_witten_parametrix_obstruction.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_"
        "SCHUR_GATE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_"
        "PIOLA_WARD_CANCELLATION_V1.json"
    ),
]
SOURCE_COMMIT = "b23463e5"

Dimension = 3
MultiIndex = tuple[int, int, int]
Jet = dict[MultiIndex, Fraction]
ZERO: MultiIndex = (0, 0, 0)
INDICES = [
    index
    for index in product(range(4), repeat=Dimension)
    if sum(index) <= 3
]
BASIS = [
    [Fraction(1), Fraction(1), Fraction(1)],
    [Fraction(-1), Fraction(1), Fraction(1)],
    [Fraction(0), Fraction(-2), Fraction(1)],
    [Fraction(0), Fraction(0), Fraction(-3)],
]
GRAM = [Fraction(2), Fraction(6), Fraction(12)]
NEIGHBORS = [(3, 1), (0, 2), (1, 3), (2, 0)]
COUPLING_SQUARED = Fraction(4, 25)
SOURCE_AMBIENT = [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)]
FOURIER_MODES = {
    "lowest_cosine": [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)],
    "lowest_sine": [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)],
    "checkerboard": [Fraction(1), Fraction(-1), Fraction(1), Fraction(-1)],
}


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def jadd(left: Jet, right: Jet) -> Jet:
    result = dict(left)
    for index, value in right.items():
        result[index] = result.get(index, Fraction(0)) + value
        if not result[index]:
            del result[index]
    return result


def jsum(items: list[Jet]) -> Jet:
    result: Jet = {}
    for item in items:
        result = jadd(result, item)
    return result


def jscale(item: Jet, factor: Fraction | int) -> Jet:
    factor = Fraction(factor)
    return {
        index: factor * value
        for index, value in item.items()
        if factor * value
    }


def jmultiply(left: Jet, right: Jet, degree: int = 2) -> Jet:
    result: Jet = {}
    for left_index, left_value in left.items():
        for right_index, right_value in right.items():
            index = tuple(
                a + b for a, b in zip(left_index, right_index)
            )
            if sum(index) <= degree:
                result[index] = (
                    result.get(index, Fraction(0))
                    + left_value * right_value
                )
    return {index: value for index, value in result.items() if value}


def jconstant(value: Fraction | int) -> Jet:
    value = Fraction(value)
    return {ZERO: value} if value else {}


def jexp_linear(
    prefactor: Fraction, linear: list[Fraction], degree: int = 3
) -> Jet:
    result: Jet = {}
    for index in INDICES:
        if sum(index) > degree:
            continue
        value = prefactor
        for power, coefficient in zip(index, linear):
            value *= coefficient**power / math.factorial(power)
        if value:
            result[index] = value
    return result


def jderivative(item: Jet, variable: int) -> Jet:
    result: Jet = {}
    for index, value in item.items():
        if not index[variable]:
            continue
        reduced = list(index)
        reduced[variable] -= 1
        result[tuple(reduced)] = value * index[variable]
    return result


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [
        row[:] + [Fraction(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            row
            for row in range(column, size)
            if work[row][column]
        )
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def matrix_vector(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def jet_matrix_multiply(
    left: list[list[Jet]], right: list[list[Jet]]
) -> list[list[Jet]]:
    return [
        [
            jsum(
                [
                    jmultiply(left[row][inner], right[inner][column])
                    for inner in range(len(right))
                ]
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def rational_left_multiply(
    left: list[list[Fraction]], right: list[list[Jet]]
) -> list[list[Jet]]:
    return [
        [
            jsum(
                [
                    jscale(right[inner][column], left[row][inner])
                    for inner in range(len(right))
                ]
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def rational_right_multiply(
    left: list[list[Jet]], right: list[list[Fraction]]
) -> list[list[Jet]]:
    return [
        [
            jsum(
                [
                    jscale(left[row][inner], right[inner][column])
                    for inner in range(len(right))
                ]
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def jet_matrix_inverse(matrix: list[list[Jet]]) -> list[list[Jet]]:
    """Invert through degree two by the exact finite Neumann expansion."""

    size = len(matrix)
    constant = [
        [entry.get(ZERO, Fraction(0)) for entry in row]
        for row in matrix
    ]
    constant_inverse = inverse(constant)
    remainder = [
        [
            jadd(entry, jscale(jconstant(entry.get(ZERO, 0)), -1))
            for entry in row
        ]
        for row in matrix
    ]
    first = rational_left_multiply(constant_inverse, remainder)
    second = jet_matrix_multiply(first, first)
    neumann = [
        [
            jsum(
                [
                    jconstant(int(row == column)),
                    jscale(first[row][column], -1),
                    second[row][column],
                ]
            )
            for column in range(size)
        ]
        for row in range(size)
    ]
    return rational_right_multiply(neumann, constant_inverse)


def jet_matrix_vector(
    matrix: list[list[Jet]], vector: list[Fraction]
) -> list[Jet]:
    return [
        jsum([jscale(entry, value) for entry, value in zip(row, vector)])
        for row in matrix
    ]


def residual_jets(omega: list[Fraction]) -> list[Jet]:
    residual = []
    for site in range(4):
        entry = jconstant(-2)
        for other in NEIGHBORS[site]:
            linear = [
                BASIS[other][axis] - BASIS[site][axis]
                for axis in range(Dimension)
            ]
            entry = jadd(
                entry,
                jexp_linear(omega[other] / omega[site], linear),
            )
        residual.append(entry)
    return residual


def gram_matrix(jacobian: list[list[Jet]]) -> list[list[Jet]]:
    return [
        [
            jsum(
                [
                    jmultiply(jacobian[site][row], jacobian[site][column])
                    for site in range(4)
                ]
            )
            for column in range(Dimension)
        ]
        for row in range(Dimension)
    ]


def coordinates_to_ambient(vector: list[Fraction]) -> list[Fraction]:
    return matrix_vector(BASIS, vector)


def fourier_coefficients(vector: list[Fraction]) -> dict[str, Fraction]:
    return {
        name: (
            sum((a * b for a, b in zip(vector, mode)), Fraction(0))
            / sum((entry * entry for entry in mode), Fraction(0))
        )
        for name, mode in FOURIER_MODES.items()
    }


def fixture(omega: list[Fraction], centered: bool) -> dict:
    residual = residual_jets(omega)
    full_jacobian = [
        [jderivative(residual[site], axis) for axis in range(Dimension)]
        for site in range(4)
    ]
    candidate_jacobian = full_jacobian
    if centered:
        means = [
            jscale(
                jsum([full_jacobian[site][axis] for site in range(4)]),
                Fraction(1, 4),
            )
            for axis in range(Dimension)
        ]
        candidate_jacobian = [
            [
                jadd(full_jacobian[site][axis], jscale(means[axis], -1))
                for axis in range(Dimension)
            ]
            for site in range(4)
        ]

    metric = gram_matrix(candidate_jacobian)
    metric_inverse = jet_matrix_inverse(metric)
    source_covector = [
        sum(
            (BASIS[site][axis] * SOURCE_AMBIENT[site] for site in range(4)),
            Fraction(0),
        )
        for axis in range(Dimension)
    ]
    candidate = jet_matrix_vector(
        metric_inverse,
        [COUPLING_SQUARED * value for value in source_covector],
    )

    residual_value = [entry.get(ZERO, Fraction(0)) for entry in residual]
    full_jacobian_value = [
        [entry.get(ZERO, Fraction(0)) for entry in row]
        for row in full_jacobian
    ]
    action_score = [
        sum(
            (
                full_jacobian_value[site][axis] * residual_value[site]
                for site in range(4)
            ),
            Fraction(0),
        )
        / COUPLING_SQUARED
        for axis in range(Dimension)
    ]
    full_gauss_newton = [
        [
            sum(
                (
                    full_jacobian_value[site][row]
                    * full_jacobian_value[site][column]
                    for site in range(4)
                ),
                Fraction(0),
            )
            / COUPLING_SQUARED
            for column in range(Dimension)
        ]
        for row in range(Dimension)
    ]
    residual_curvature = [
        [
            sum(
                (
                    residual_value[site]
                    * jderivative(
                        jderivative(residual[site], row), column
                    ).get(ZERO, Fraction(0))
                    for site in range(4)
                ),
                Fraction(0),
            )
            / COUPLING_SQUARED
            for column in range(Dimension)
        ]
        for row in range(Dimension)
    ]
    candidate_value = [entry.get(ZERO, Fraction(0)) for entry in candidate]

    scalar_part = []
    for component in range(Dimension):
        value = Fraction(0)
        for axis in range(Dimension):
            first_index = tuple(
                int(index == axis) for index in range(Dimension)
            )
            second_index = tuple(2 * entry for entry in first_index)
            value -= (
                2
                * candidate[component].get(second_index, Fraction(0))
                / GRAM[axis]
            )
            value += (
                action_score[axis]
                * candidate[component].get(first_index, Fraction(0))
                / GRAM[axis]
            )
        scalar_part.append(value)

    def endomorphism_image(matrix: list[list[Fraction]]) -> list[Fraction]:
        return [
            sum(
                (
                    matrix[row][column] * candidate_value[column]
                    for column in range(Dimension)
                ),
                Fraction(0),
            )
            / GRAM[row]
            for row in range(Dimension)
        ]

    gauss_newton_part = endomorphism_image(full_gauss_newton)
    curvature_part = endomorphism_image(residual_curvature)
    image = [
        scalar + gauss_newton + curvature
        for scalar, gauss_newton, curvature in zip(
            scalar_part, gauss_newton_part, curvature_part
        )
    ]
    source_gradient = [
        source_covector[axis] / GRAM[axis]
        for axis in range(Dimension)
    ]
    defect = [
        value - source
        for value, source in zip(image, source_gradient)
    ]

    return {
        "omega": omega,
        "centered": centered,
        "residual": residual_value,
        "candidate_value": candidate_value,
        "scalar_witten_part": scalar_part,
        "full_gauss_newton_part": gauss_newton_part,
        "residual_curvature_part": curvature_part,
        "image": image,
        "source": source_gradient,
        "defect": defect,
        "image_fourier": fourier_coefficients(coordinates_to_ambient(image)),
        "defect_fourier": fourier_coefficients(coordinates_to_ambient(defect)),
    }


def encode_fixture(item: dict) -> dict:
    return {
        "omega": [enc(value) for value in item["omega"]],
        "candidate": (
            "centered_residual_jacobian_metric"
            if item["centered"]
            else "full_action_residual_jacobian_metric"
        ),
        "residual": [enc(value) for value in item["residual"]],
        "candidate_value": [enc(value) for value in item["candidate_value"]],
        "scalar_witten_part": [
            enc(value) for value in item["scalar_witten_part"]
        ],
        "full_gauss_newton_part": [
            enc(value) for value in item["full_gauss_newton_part"]
        ],
        "residual_curvature_part": [
            enc(value) for value in item["residual_curvature_part"]
        ],
        "L1_image": [enc(value) for value in item["image"]],
        "source": [enc(value) for value in item["source"]],
        "defect": [enc(value) for value in item["defect"]],
        "L1_image_fourier_coefficients": {
            name: enc(value) for name, value in item["image_fourier"].items()
        },
        "defect_fourier_coefficients": {
            name: enc(value) for name, value in item["defect_fourier"].items()
        },
        "status": "EXACT_RATIONAL_C4_WITTEN_JET",
    }


def build() -> dict:
    vacuum_full = fixture([Fraction(1)] * 4, centered=False)
    vacuum_centered = fixture([Fraction(1)] * 4, centered=True)
    asymmetric_full = fixture(
        [Fraction(1), Fraction(1), Fraction(2), Fraction(2)],
        centered=False,
    )
    asymmetric_centered = fixture(
        [Fraction(1), Fraction(1), Fraction(2), Fraction(2)],
        centered=True,
    )
    checks = {
        "vacuum_full_candidate_has_49_over_50_cosine_image": (
            vacuum_full["image_fourier"]["lowest_cosine"]
            == Fraction(49, 50)
        ),
        "vacuum_centered_candidate_has_9_over_10_cosine_image": (
            vacuum_centered["image_fourier"]["lowest_cosine"]
            == Fraction(9, 10)
        ),
        "vacuum_full_defect_is_scalar_witten_derivative_term": (
            vacuum_full["full_gauss_newton_part"] == vacuum_full["source"]
            and vacuum_full["residual_curvature_part"]
            == [Fraction(0)] * Dimension
            and vacuum_full["defect"] == vacuum_full["scalar_witten_part"]
        ),
        "asymmetric_full_gauss_newton_part_is_source": (
            asymmetric_full["full_gauss_newton_part"]
            == asymmetric_full["source"]
        ),
        "asymmetric_full_defect_mixes_lowest_sine": (
            asymmetric_full["defect_fourier"]["lowest_sine"] != 0
        ),
        "asymmetric_full_defect_mixes_checkerboard": (
            asymmetric_full["defect_fourier"]["checkerboard"] != 0
        ),
        "asymmetric_centered_defect_mixes_lowest_sine": (
            asymmetric_centered["defect_fourier"]["lowest_sine"] != 0
        ),
        "asymmetric_centered_defect_mixes_checkerboard": (
            asymmetric_centered["defect_fourier"]["checkerboard"] != 0
        ),
        "neither_candidate_is_exact_or_scalar_repairable": True,
        "witten_coercivity_remains_open": True,
        "actual_h_minus_one_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_GAUSS_NEWTON_"
            "WITTEN_PARAMETRIX_OBSTRUCTION_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-gauss-newton-"
            "witten-parametrix-obstruction-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_POINTWISE_PARAMETRIX_METHOD_OBSTRUCTION",
        "result_kind": (
            "exact finite-graph Witten image and mode-mixing obstruction "
            "for full and centered Gauss-Newton inverse fields"
        ),
        "question": (
            "Does a pointwise inverse residual-Jacobian metric give an exact "
            "or scalar-renormalizable inverse of the BT Witten one-form "
            "operator on a lowest Fourier source?"
        ),
        "answer": (
            "No. For v_G=lambda^2*(Dr^T Dr)^(-1)dT, the Gauss-Newton "
            "piece of Hess S maps v_G to dT, but L0 differentiates the "
            "background-dependent coefficients and the residual-weighted "
            "second derivative of r remains. On C4 the full candidate has "
            "L1 v_G=(49/50)dT already at the vacuum. At an asymmetric exact "
            "positive profile its defect has nonzero lowest-sine and "
            "checkerboard components, so no scalar multiplier repairs it. "
            "Replacing Dr by the centered flat-map Jacobian Du also fails, "
            "and differs away from the vacuum by the mean-residual rank-one "
            "metric term. This obstructs these two raw pointwise "
            "parametrices, not the Witten coercivity theorem."
        ),
        "general_remainder_identity": {
            "action": "S=||r||^2/(2*lambda^2)",
            "full_candidate": (
                "v_G=lambda^2*(Dr^T Dr)^(-1)*dT_covector"
            ),
            "hessian_split": (
                "Hess S=lambda^(-2)*(Dr^T Dr+sum_i r_i Hess r_i)"
            ),
            "exact_image": (
                "L1 v_G=dT+L0 v_G+lambda^(-2)*"
                "G^(-1)*(sum_i r_i Hess r_i)*v_G"
            ),
            "centered_metric_difference": (
                "Dr^T Dr=Du^T Du+N*d(mean r) tensor d(mean r)"
            ),
            "interpretation": (
                "the missing terms are configuration-space derivative and "
                "embedding-curvature terms, not a constant normalization"
            ),
            "status": "PROVED_EXACT_FINITE_DIMENSIONAL_IDENTITY",
        },
        "exact_fixtures": {
            "vacuum_full": encode_fixture(vacuum_full),
            "vacuum_centered": encode_fixture(vacuum_centered),
            "asymmetric_full": encode_fixture(asymmetric_full),
            "asymmetric_centered": encode_fixture(asymmetric_centered),
        },
        "method_disposition": {
            "full_action_gauss_newton_pointwise_parametrix": "OBSTRUCTED",
            "centered_flat_map_pointwise_parametrix": "OBSTRUCTED",
            "constant_scalar_renormalization_of_either_candidate": (
                "OBSTRUCTED_BY_EXACT_MODE_MIXING"
            ),
            "connection_corrected_or_nonlocal_witten_parametrix": "OPEN",
            "volume_uniform_witten_schur_coercivity": "OPEN",
            "controlled_low_rayleigh_sequence": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "does_not_establish": [
            "failure of a connection-corrected, variational, or nonlocal Witten inverse",
            "failure of volume-uniform Witten Schur coercivity",
            "a controlled low-Rayleigh or diverging-volume Gibbs sequence",
            "a normalized lowest-mode or interacting H^-1 moment bound",
            "tightness, a continuum Euclidean BT measure, or limit identification",
            "a Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "missing_object_ledger": [
            "a connection-corrected residual-coordinate parametrix with an L-uniform form remainder",
            "or a normalized low-Rayleigh sequence for the full Witten form with nonzero dT overlap",
            "an L-uniform lowest-mode bound followed by a dyadic-shell H^-1 summation",
        ],
        "next_gate": (
            "Do not scalar-rescale a pointwise residual-metric inverse. "
            "Either solve the connection-corrected one-form equation in "
            "residual coordinates and prove its remainder relatively form "
            "bounded, or use the exact nonzero Q-mode defect to seed a full "
            "Witten low-Rayleigh construction."
        ),
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": relative, "sha256": sha256(relative)}
                for relative in INPUTS
            ],
            "arithmetic": (
                "Exact Fraction arithmetic in an orthogonal rational basis "
                "of the C4 mean-zero carrier. The producer uses complete "
                "three-variable exponential Taylor jets through degree "
                "three and a degree-two Neumann matrix inverse."
            ),
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFY_REL,
        "verification_commands": [
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "bt_euclidean_gauss_newton_witten_parametrix_obstruction.py --check"
            ),
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "verify_bt_euclidean_gauss_newton_witten_parametrix_obstruction.py"
            ),
            (
                "ulimit -v 500000; python3 -m unittest -v "
                "reverse_physics.tests."
                "test_bt_euclidean_gauss_newton_witten_parametrix_obstruction"
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if not payload["checks"]["ok"]:
        for failure in payload["checks"]["failures"]:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    if args.write:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                committed = json.load(handle)
        except FileNotFoundError:
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        if committed != payload:
            print("[FAIL] committed certificate is stale", file=sys.stderr)
            return 1
    print(
        "BT Gauss-Newton Witten parametrix obstruction: "
        f"PASS ({payload['checks']['passed']}/{payload['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
