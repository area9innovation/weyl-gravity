#!/usr/bin/env python3
"""Independent univariate-jet verifier for the BT Witten obstruction."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_GAUSS_NEWTON_"
    "WITTEN_PARAMETRIX_OBSTRUCTION_V1.json"
)
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
BASIS = [
    [Fraction(1), Fraction(1), Fraction(1)],
    [Fraction(-1), Fraction(1), Fraction(1)],
    [Fraction(0), Fraction(-2), Fraction(1)],
    [Fraction(0), Fraction(0), Fraction(-3)],
]
GRAM = [Fraction(2), Fraction(6), Fraction(12)]
NEIGHBORS = [(3, 1), (0, 2), (1, 3), (2, 0)]
LAMBDA_SQUARED = Fraction(4, 25)
SOURCE = [Fraction(1), Fraction(0), Fraction(-1), Fraction(0)]
MODES = {
    "lowest_cosine": SOURCE,
    "lowest_sine": [Fraction(0), Fraction(1), Fraction(0), Fraction(-1)],
    "checkerboard": [Fraction(1), Fraction(-1), Fraction(1), Fraction(-1)],
}


@dataclass(frozen=True)
class D2:
    """Value, first derivative, and second derivative in one variable."""

    value: Fraction
    first: Fraction = Fraction(0)
    second: Fraction = Fraction(0)

    def __add__(self, other: D2 | Fraction | int) -> D2:
        other = lift(other)
        return D2(
            self.value + other.value,
            self.first + other.first,
            self.second + other.second,
        )

    __radd__ = __add__

    def __neg__(self) -> D2:
        return D2(-self.value, -self.first, -self.second)

    def __sub__(self, other: D2 | Fraction | int) -> D2:
        return self + (-lift(other))

    def __rsub__(self, other: D2 | Fraction | int) -> D2:
        return lift(other) - self

    def __mul__(self, other: D2 | Fraction | int) -> D2:
        other = lift(other)
        return D2(
            self.value * other.value,
            self.first * other.value + self.value * other.first,
            self.second * other.value
            + 2 * self.first * other.first
            + self.value * other.second,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> D2:
        value = self.value
        return D2(
            1 / value,
            -self.first / value**2,
            2 * self.first**2 / value**3 - self.second / value**2,
        )

    def __truediv__(self, other: D2 | Fraction | int) -> D2:
        return self * lift(other).reciprocal()

    def __rtruediv__(self, other: D2 | Fraction | int) -> D2:
        return lift(other) * self.reciprocal()


def lift(value: D2 | Fraction | int) -> D2:
    return value if isinstance(value, D2) else D2(Fraction(value))


def exp_linear(prefactor: Fraction, slope: Fraction) -> D2:
    return D2(prefactor, prefactor * slope, prefactor * slope**2)


def inverse(matrix: list[list[D2]]) -> list[list[D2]]:
    size = len(matrix)
    work = [
        row[:] + [D2(Fraction(int(i == j))) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            row
            for row in range(column, size)
            if work[row][column].value
        )
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [entry / pivot_value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def matvec(
    matrix: list[list[Fraction]], vector: list[Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def candidate_axis_jets(
    omega: list[Fraction], centered: bool, path_axis: int
) -> list[D2]:
    jacobian: list[list[D2]] = []
    for site in range(4):
        row = []
        for derivative_axis in range(3):
            entry = D2(Fraction(0))
            for other in NEIGHBORS[site]:
                path_slope = (
                    BASIS[other][path_axis] - BASIS[site][path_axis]
                )
                derivative_slope = (
                    BASIS[other][derivative_axis]
                    - BASIS[site][derivative_axis]
                )
                entry += (
                    exp_linear(omega[other] / omega[site], path_slope)
                    * derivative_slope
                )
            row.append(entry)
        jacobian.append(row)
    if centered:
        means = [
            sum((jacobian[site][axis] for site in range(4)), D2(Fraction(0)))
            / 4
            for axis in range(3)
        ]
        jacobian = [
            [jacobian[site][axis] - means[axis] for axis in range(3)]
            for site in range(4)
        ]
    metric = [
        [
            sum(
                (
                    jacobian[site][row] * jacobian[site][column]
                    for site in range(4)
                ),
                D2(Fraction(0)),
            )
            for column in range(3)
        ]
        for row in range(3)
    ]
    metric_inverse = inverse(metric)
    source_covector = [
        sum(
            (BASIS[site][axis] * SOURCE[site] for site in range(4)),
            Fraction(0),
        )
        for axis in range(3)
    ]
    return [
        sum(
            (
                metric_inverse[row][column]
                * LAMBDA_SQUARED
                * source_covector[column]
                for column in range(3)
            ),
            D2(Fraction(0)),
        )
        for row in range(3)
    ]


def direct_action_data(omega: list[Fraction]) -> dict:
    residual = []
    jacobian = []
    residual_hessian = []
    for site in range(4):
        residual_entry = Fraction(-2)
        jacobian_row = [Fraction(0)] * 3
        hessian_rows = [[Fraction(0)] * 3 for _ in range(3)]
        for other in NEIGHBORS[site]:
            weight = omega[other] / omega[site]
            difference = [
                BASIS[other][axis] - BASIS[site][axis]
                for axis in range(3)
            ]
            residual_entry += weight
            for row in range(3):
                jacobian_row[row] += weight * difference[row]
                for column in range(3):
                    hessian_rows[row][column] += (
                        weight * difference[row] * difference[column]
                    )
        residual.append(residual_entry)
        jacobian.append(jacobian_row)
        residual_hessian.append(hessian_rows)
    score = [
        sum(
            (jacobian[site][axis] * residual[site] for site in range(4)),
            Fraction(0),
        )
        / LAMBDA_SQUARED
        for axis in range(3)
    ]
    gauss_newton = [
        [
            sum(
                (
                    jacobian[site][row] * jacobian[site][column]
                    for site in range(4)
                ),
                Fraction(0),
            )
            / LAMBDA_SQUARED
            for column in range(3)
        ]
        for row in range(3)
    ]
    curvature = [
        [
            sum(
                (
                    residual[site]
                    * residual_hessian[site][row][column]
                    for site in range(4)
                ),
                Fraction(0),
            )
            / LAMBDA_SQUARED
            for column in range(3)
        ]
        for row in range(3)
    ]
    return {
        "residual": residual,
        "score": score,
        "gauss_newton": gauss_newton,
        "curvature": curvature,
    }


def reconstruct(omega: list[Fraction], centered: bool) -> dict:
    axis_jets = [
        candidate_axis_jets(omega, centered, axis) for axis in range(3)
    ]
    candidate = [axis_jets[0][component].value for component in range(3)]
    action = direct_action_data(omega)
    scalar = []
    for component in range(3):
        value = Fraction(0)
        for axis in range(3):
            value -= axis_jets[axis][component].second / GRAM[axis]
            value += (
                action["score"][axis]
                * axis_jets[axis][component].first
                / GRAM[axis]
            )
        scalar.append(value)

    def image(matrix: list[list[Fraction]]) -> list[Fraction]:
        return [
            sum(
                (
                    matrix[row][column] * candidate[column]
                    for column in range(3)
                ),
                Fraction(0),
            )
            / GRAM[row]
            for row in range(3)
        ]

    gauss_newton = image(action["gauss_newton"])
    curvature = image(action["curvature"])
    total = [
        a + b + c for a, b, c in zip(scalar, gauss_newton, curvature)
    ]
    source_covector = [
        sum(
            (BASIS[site][axis] * SOURCE[site] for site in range(4)),
            Fraction(0),
        )
        for axis in range(3)
    ]
    source = [source_covector[axis] / GRAM[axis] for axis in range(3)]
    defect = [value - target for value, target in zip(total, source)]

    def fourier(vector: list[Fraction]) -> dict[str, Fraction]:
        ambient = matvec(BASIS, vector)
        return {
            name: (
                sum((a * b for a, b in zip(ambient, mode)), Fraction(0))
                / sum((entry * entry for entry in mode), Fraction(0))
            )
            for name, mode in MODES.items()
        }

    return {
        "residual": action["residual"],
        "candidate_value": candidate,
        "scalar_witten_part": scalar,
        "full_gauss_newton_part": gauss_newton,
        "residual_curvature_part": curvature,
        "L1_image": total,
        "source": source,
        "defect": defect,
        "L1_image_fourier_coefficients": fourier(total),
        "defect_fourier_coefficients": fourier(defect),
    }


def compare_fixture(recorded: dict, expected: dict) -> bool:
    for name in (
        "residual",
        "candidate_value",
        "scalar_witten_part",
        "full_gauss_newton_part",
        "residual_curvature_part",
        "L1_image",
        "source",
        "defect",
    ):
        if [decode(value) for value in recorded[name]] != expected[name]:
            return False
    for name in (
        "L1_image_fourier_coefficients",
        "defect_fourier_coefficients",
    ):
        decoded = {key: decode(value) for key, value in recorded[name].items()}
        if decoded != expected[name]:
            return False
    return True


def verify(certificate: dict) -> tuple[bool, list[str]]:
    checks: list[tuple[str, bool]] = []
    checks.append((
        "identity",
        certificate.get("certificate")
        == (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_GAUSS_NEWTON_"
            "WITTEN_PARAMETRIX_OBSTRUCTION_V1"
        ),
    ))
    checks.append((
        "dependency_tags",
        certificate.get("dependency_tags")
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
    ))
    fixtures = certificate.get("exact_fixtures", {})
    specifications = {
        "vacuum_full": ([Fraction(1)] * 4, False),
        "vacuum_centered": ([Fraction(1)] * 4, True),
        "asymmetric_full": (
            [Fraction(1), Fraction(1), Fraction(2), Fraction(2)],
            False,
        ),
        "asymmetric_centered": (
            [Fraction(1), Fraction(1), Fraction(2), Fraction(2)],
            True,
        ),
    }
    for name, (omega, centered) in specifications.items():
        try:
            expected = reconstruct(omega, centered)
            passed = compare_fixture(fixtures[name], expected)
        except (KeyError, TypeError, ZeroDivisionError, StopIteration):
            passed = False
        checks.append((f"independent_{name}", passed))
    disposition = certificate.get("method_disposition", {})
    checks.extend([
        (
            "full_candidate_obstructed",
            disposition.get("full_action_gauss_newton_pointwise_parametrix")
            == "OBSTRUCTED",
        ),
        (
            "centered_candidate_obstructed",
            disposition.get("centered_flat_map_pointwise_parametrix")
            == "OBSTRUCTED",
        ),
        (
            "corrected_candidate_open",
            disposition.get("connection_corrected_or_nonlocal_witten_parametrix")
            == "OPEN",
        ),
        (
            "coercivity_open",
            disposition.get("volume_uniform_witten_schur_coercivity")
            == "OPEN",
        ),
        (
            "h_minus_one_open",
            disposition.get("actual_interacting_h_minus_one_second_moment")
            == "OPEN",
        ),
        (
            "lorentzian_closed",
            disposition.get("lorentzian_transfer") == "NOT_ESTABLISHED",
        ),
    ])
    provenance = certificate.get("provenance", {}).get("inputs", [])
    checks.append((
        "input_hashes",
        provenance
        == [{"path": path, "sha256": sha256(path)} for path in INPUTS],
    ))
    checks.extend([
        ("schema_path", certificate.get("schema") == SCHEMA_REL),
        ("report_path", certificate.get("report") == REPORT_REL),
        (
            "verifier_path",
            certificate.get("independent_verifier") == VERIFY_REL,
        ),
    ])
    declared = certificate.get("checks", {})
    checks.append((
        "declared_checks",
        declared.get("ok") is True
        and declared.get("passed") == declared.get("total")
        and declared.get("failures") == [],
    ))
    failures = [name for name, passed in checks if not passed]
    return not failures, failures


def main() -> int:
    try:
        with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
            certificate = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 1
    ok, failures = verify(certificate)
    if not ok:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1
    print("BT Gauss-Newton Witten parametrix independent verifier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
