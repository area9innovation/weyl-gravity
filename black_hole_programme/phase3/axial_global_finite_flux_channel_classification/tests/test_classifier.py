from __future__ import annotations

import json
import struct
import unittest
from fractions import Fraction
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.affine_adapter import (
    AffineScalar,
    ComplexAffine,
    Interval,
    certify_whole_cell_inertia,
    determinant_excludes_zero,
    matrix_from_json,
    matrix_multiply,
    require_hermitian_enclosure,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.classifier import (
    classify_exact_cell,
    classify_populated_form,
    complex_hermitian_inertia,
)
from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.verify import (
    verify_document,
)


HERE = Path(__file__).resolve().parents[1]


def float_bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def rational(value: int | Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def affine_scalar(
    center: int | Fraction,
    linear: int | Fraction = 0,
    remainder: tuple[float, float] = (0.0, 0.0),
) -> dict:
    return {
        "center": rational(center),
        "linear": rational(linear),
        "remainder": [float_bits(remainder[0]), float_bits(remainder[1])],
    }


def complex_affine(
    real: int | Fraction,
    imag: int | Fraction = 0,
    *,
    real_linear: int | Fraction = 0,
    imag_linear: int | Fraction = 0,
    real_remainder: tuple[float, float] = (0.0, 0.0),
    imag_remainder: tuple[float, float] = (0.0, 0.0),
) -> dict:
    return {
        "re": affine_scalar(real, real_linear, real_remainder),
        "im": affine_scalar(imag, imag_linear, imag_remainder),
    }


def affine_diagonal(values: list[dict]) -> list:
    zero = complex_affine(0)
    return [
        [values[i] if i == j else zero for j in range(len(values))]
        for i in range(len(values))
    ]


def connection_from_traces(cminus: sp.Matrix, cplus: sp.Matrix) -> sp.Matrix:
    """Assemble infinity order XI0,XI1,XI2,XI3,EI0,EI2."""
    answer = sp.zeros(6, 3)
    for target, source in zip((0, 1, 4), range(3)):
        answer[target, :] = cminus[source, :]
    for target, source in zip((2, 3, 5), range(3)):
        answer[target, :] = cplus[source, :]
    return answer


class ExactClassifierTest(unittest.TestCase):
    def test_certificate_is_fail_closed(self) -> None:
        verify_document(json.loads((HERE / "certificate.json").read_text()))

    def test_positive_synthetic_cell_and_one_sided_relation(self) -> None:
        identity = sp.eye(3)
        result = classify_exact_cell(
            connection_from_traces(identity, identity),
            identity,
            identity,
            sp.zeros(3),
        )
        self.assertEqual(result.imin["physical_inertia"], (3, 0, 0))
        self.assertEqual(result.iplus["physical_inertia"], (3, 0, 0))
        self.assertEqual(
            result.imin["origins"]["additional"]["physical_quotient_dimension"],
            2,
        )
        self.assertEqual(
            result.imin["origins"]["einstein"]["physical_quotient_dimension"],
            1,
        )
        self.assertEqual(result.joint_kernel_dimension, 0)
        self.assertTrue(result.conservation_certified)
        self.assertTrue(result.one_sided_relation["J_isometry_certified"])
        self.assertFalse(result.one_sided_relation["full_scattering_matrix"])

    def test_indefinite_synthetic_cell(self) -> None:
        gram = sp.diag(1, -1, -1)
        result = classify_exact_cell(
            connection_from_traces(sp.eye(3), sp.eye(3)),
            gram,
            gram,
            sp.zeros(3),
        )
        self.assertEqual(result.imin["physical_inertia"], (1, 2, 0))
        self.assertEqual(result.iplus["physical_inertia"], (1, 2, 0))
        self.assertEqual(
            result.imin["origins"]["additional"][
                "restricted_pullback_inertia"
            ],
            (1, 1, 0),
        )
        self.assertEqual(
            result.imin["origins"]["einstein"][
                "restricted_pullback_inertia"
            ],
            (0, 1, 0),
        )
        self.assertEqual(result.imin["einstein_additional_mixed_rank"], 0)

    def test_einstein_additional_mixing_is_reported(self) -> None:
        gram = sp.Matrix(
            [
                [2, 0, 1 + sp.I],
                [0, -1, 2],
                [1 - sp.I, 2, 3],
            ]
        )
        result = classify_populated_form(sp.eye(3), gram)
        self.assertEqual(result["einstein_additional_mixed_rank"], 1)
        self.assertEqual(
            result["einstein_additional_mixed_block"],
            sp.Matrix([[1 + sp.I], [2]]),
        )
        self.assertEqual(
            result["origins"]["additional"]["restricted_pullback_inertia"],
            (1, 1, 0),
        )
        self.assertEqual(
            result["origins"]["einstein"]["restricted_pullback_inertia"],
            (1, 0, 0),
        )

    def test_radical_synthetic_cell(self) -> None:
        trace = sp.diag(1, 1, 0)
        gram = sp.diag(1, 0, 1)
        result = classify_populated_form(trace, gram)
        self.assertEqual(result["trace_rank"], 2)
        self.assertEqual(result["trace_kernel_dimension"], 1)
        self.assertEqual(result["pullback_rank"], 1)
        self.assertEqual(result["populated_radical_dimension"], 1)
        self.assertEqual(result["physical_quotient_dimension"], 1)
        self.assertEqual(result["physical_inertia"], (1, 0, 0))

    def test_offdiagonal_exact_inertia(self) -> None:
        self.assertEqual(
            complex_hermitian_inertia(sp.Matrix([[0, 1], [1, 0]])),
            (1, 1, 0),
        )

    def test_wrong_conservation_refused(self) -> None:
        identity = sp.eye(3)
        with self.assertRaisesRegex(ValueError, "current conservation"):
            classify_exact_cell(
                connection_from_traces(identity, identity),
                identity,
                identity,
                identity,
            )


class AffineCellAdapterTest(unittest.TestCase):
    def test_affine_product_keeps_quadratic_remainder(self) -> None:
        left = AffineScalar(Fraction(1), Fraction(1), Interval.point(0))
        right = AffineScalar(Fraction(1), Fraction(-1), Interval.point(0))
        product = left * right
        self.assertEqual(product.center, 1)
        self.assertEqual(product.linear, 0)
        self.assertEqual(product.remainder.hi, 0)
        self.assertEqual(product.remainder.lo, -Fraction(1, 512**2))

    def test_affine_containment_allows_rebased_center_and_linear(self) -> None:
        inner = AffineScalar(
            Fraction(1),
            Fraction(2),
            Interval(Fraction(-1, 100), Fraction(1, 100)),
        )
        outer = AffineScalar(
            Fraction(1001, 1000),
            Fraction(3),
            Interval(Fraction(-2, 100), Fraction(2, 100)),
        )
        self.assertTrue(outer.contains_affine(inner))
        narrow = AffineScalar(
            outer.center,
            outer.linear,
            Interval(Fraction(-1, 1000), Fraction(1, 1000)),
        )
        self.assertFalse(narrow.contains_affine(inner))

    def test_whole_cell_rank_and_inertia(self) -> None:
        matrix = matrix_from_json(
            affine_diagonal(
                [
                    complex_affine(2, real_linear=1),
                    complex_affine(-1, real_linear=1),
                    complex_affine(3),
                ]
            )
        )
        self.assertTrue(determinant_excludes_zero(matrix))
        witness = certify_whole_cell_inertia(matrix)
        self.assertEqual(witness.complex_inertia, (2, 1, 0))
        self.assertLess(witness.inverse_perturbation_bound, 1)

    def test_singular_cell_is_refused(self) -> None:
        matrix = matrix_from_json(
            affine_diagonal(
                [
                    complex_affine(0, real_linear=1),
                    complex_affine(1),
                    complex_affine(1),
                ]
            )
        )
        self.assertFalse(determinant_excludes_zero(matrix))
        with self.assertRaisesRegex(ValueError, "center form is singular"):
            certify_whole_cell_inertia(matrix)

    def test_nonhermitian_affine_coefficient_is_refused(self) -> None:
        matrix = matrix_from_json(
            [
                [complex_affine(1), complex_affine(1, imag=1)],
                [complex_affine(1, imag=1), complex_affine(1)],
            ]
        )
        with self.assertRaisesRegex(ValueError, "imaginary center"):
            require_hermitian_enclosure(matrix, "mutation")

    def test_affine_matrix_product(self) -> None:
        left = matrix_from_json(
            [[complex_affine(1, real_linear=1), complex_affine(0)]]
        )
        right = matrix_from_json(
            [[complex_affine(1, real_linear=-1)], [complex_affine(2)]]
        )
        product = matrix_multiply(left, right)
        self.assertEqual(product[0][0].re.center, 1)
        self.assertEqual(product[0][0].re.linear, 0)
        self.assertEqual(
            product[0][0].re.remainder.lo,
            -Fraction(1, 512**2),
        )


if __name__ == "__main__":
    unittest.main()
