from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import struct
import unittest

from black_hole_programme.phase3.axial_global_finite_flux_channel_classification.taylor2_adapter import (
    IVTAYLOR_V2_SOURCE_COMMIT,
    complex_to_realified_affine,
    flatten_taylor_matrix,
    flatten_taylor_scalar,
    realified_to_complex_affine,
)

FIXTURE = Path(__file__).with_name("fixtures") / "ivtaylor_degree2_v2_gate.json"


def bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def interval(value: dict) -> tuple[Fraction, Fraction]:
    return tuple(
        Fraction.from_float(
            struct.unpack(">d", int(endpoint, 16).to_bytes(8, "big"))[0]
        )
        for endpoint in value["remainder"]
    )


def scalar(
    center: str,
    linear: str = "0/1",
    lo: float = 0.0,
    hi: float = 0.0,
) -> dict:
    return {
        "center": center,
        "linear": linear,
        "remainder": [bits(lo), bits(hi)],
    }


class Taylor2AdapterTests(unittest.TestCase):
    def test_positive_quadratic_moves_to_nonnegative_remainder(self) -> None:
        value = flatten_taylor_scalar("1/3", "2/5", "7/11", [bits(0.0), bits(0.0)])
        lo, hi = interval(value)
        self.assertLessEqual(lo, 0)
        self.assertGreaterEqual(hi, Fraction(7, 11))
        self.assertEqual(value["center"], "1/3")
        self.assertEqual(value["linear"], "2/5")

    def test_negative_quadratic_moves_to_nonpositive_remainder(self) -> None:
        value = flatten_taylor_scalar("0", "0", "-7/11", [bits(0.0), bits(0.0)])
        lo, hi = interval(value)
        self.assertLessEqual(lo, Fraction(-7, 11))
        self.assertGreaterEqual(hi, 0)

    def test_outward_rounding_contains_non_dyadic_sum(self) -> None:
        value = flatten_taylor_scalar(
            "0", "0", "1/10", [bits(-0.2), bits(0.3)]
        )
        lo, hi = interval(value)
        self.assertLessEqual(lo, Fraction.from_float(-0.2))
        self.assertGreaterEqual(hi, Fraction.from_float(0.3) + Fraction(1, 10))

    def test_matrix_schema_and_shape_are_fail_closed(self) -> None:
        document = {
            "schema": "ivtaylor-degree2-v2",
            "generator": 7315,
            "degree": 2,
            "rows": 1,
            "cols": 1,
            "refusal_code": 0,
            "coefficients": [[["1"]], [["2"]], [["3"]]],
            "remainder_bits": [[[bits(0.0), bits(0.0)]]],
        }
        flattened = flatten_taylor_matrix(document)
        self.assertEqual(flattened[0][0]["center"], "1/1")
        wrong_schema = dict(document, schema="ivtaylor-degree2-v1")
        with self.assertRaisesRegex(ValueError, "schema"):
            flatten_taylor_matrix(wrong_schema)
        wrong_degree = dict(document, degree=2.0)
        with self.assertRaisesRegex(ValueError, "accepted"):
            flatten_taylor_matrix(wrong_degree)
        broken = dict(document, refusal_code=8)
        with self.assertRaisesRegex(ValueError, "accepted"):
            flatten_taylor_matrix(broken)
        wrong_generator = dict(document, generator=99)
        with self.assertRaisesRegex(ValueError, "generator"):
            flatten_taylor_matrix(wrong_generator)
        nonintegral_generator = dict(document, generator=7315.0)
        with self.assertRaisesRegex(ValueError, "generator"):
            flatten_taylor_matrix(nonintegral_generator)
        wrong_shape = dict(document, rows=2)
        with self.assertRaisesRegex(ValueError, "shape"):
            flatten_taylor_matrix(wrong_shape)
        noncanonical = dict(
            document, coefficients=[[["1/1"]], [["2"]], [["3"]]]
        )
        with self.assertRaisesRegex(ValueError, "canonical"):
            flatten_taylor_matrix(noncanonical)
        numeric_coefficient = dict(
            document, coefficients=[[[1]], [["2"]], [["3"]]]
        )
        with self.assertRaisesRegex(ValueError, "rational string"):
            flatten_taylor_matrix(numeric_coefficient)
        malformed_bits = dict(
            document, remainder_bits=[[["0", bits(0.0)]]]
        )
        with self.assertRaisesRegex(ValueError, "fixed-width"):
            flatten_taylor_matrix(malformed_bits)
        uppercase_bits = dict(
            document, remainder_bits=[[["Bff0000000000000", bits(0.0)]]]
        )
        with self.assertRaisesRegex(ValueError, "lowercase"):
            flatten_taylor_matrix(uppercase_bits)
        nonfinite_bits = dict(
            document, remainder_bits=[[["7ff0000000000000", bits(0.0)]]]
        )
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            flatten_taylor_matrix(nonfinite_bits)
        reversed_bits = dict(
            document, remainder_bits=[[[bits(1.0), bits(-1.0)]]]
        )
        with self.assertRaisesRegex(ValueError, "reversed"):
            flatten_taylor_matrix(reversed_bits)
        extra_field = dict(document, undocumented=True)
        with self.assertRaisesRegex(ValueError, "fields"):
            flatten_taylor_matrix(extra_field)

    def test_direct_forge_v2_json_fixture(self) -> None:
        # Exact stdout oracle from the pinned Tango Forge producer.
        self.assertEqual(
            IVTAYLOR_V2_SOURCE_COMMIT,
            "2e2461eada037d18794952d466ca584e07cc33f4",
        )
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        flattened = flatten_taylor_matrix(document)[0][0]
        self.assertEqual(flattened["center"], "7/1")
        self.assertEqual(flattened["linear"], "3/1")
        self.assertEqual(interval(flattened), (Fraction(-1, 4), Fraction(1, 2)))

    def test_realified_round_trip(self) -> None:
        complex_matrix = [
            [
                {"re": scalar("2/1", "1/3"), "im": scalar("-5/1", "2/7")}
            ]
        ]
        realified = complex_to_realified_affine(complex_matrix)
        recovered = realified_to_complex_affine(realified)
        self.assertEqual(recovered, complex_matrix)

    def test_duplicate_block_drift_is_enclosed(self) -> None:
        matrix = [
            [scalar("1/1"), scalar("-2/1")],
            [scalar("2/1"), scalar("1/1", lo=-0.25, hi=0.25)],
        ]
        recovered = realified_to_complex_affine(matrix)[0][0]
        rlo, rhi = interval(recovered["re"])
        self.assertLessEqual(rlo, Fraction(-1, 4))
        self.assertGreaterEqual(rhi, Fraction(1, 4))
        self.assertEqual(recovered["im"]["center"], "2/1")

    def test_duplicate_center_and_linear_drift_are_enclosed(self) -> None:
        matrix = [
            [scalar("1/1", "2/1"), scalar("-4/1", "-6/1")],
            [scalar("3/1", "5/1"), scalar("7/1", "11/1")],
        ]
        recovered = realified_to_complex_affine(matrix)[0][0]
        rlo, rhi = interval(recovered["re"])
        # Canonical top-left is 1+2e; duplicate bottom-right is 7+11e,
        # so its offset 6+9e requires [-3,15] in the outer remainder.
        self.assertLessEqual(rlo, Fraction(-3))
        self.assertGreaterEqual(rhi, Fraction(15))
        ilo, ihi = interval(recovered["im"])
        # Bottom-left is 3+5e and -top-right is 4+6e.
        self.assertLessEqual(ilo, Fraction(0))
        self.assertGreaterEqual(ihi, Fraction(2))

    def test_odd_realified_shape_refuses(self) -> None:
        with self.assertRaisesRegex(ValueError, "even"):
            realified_to_complex_affine([[scalar("0/1")]])


if __name__ == "__main__":
    unittest.main()
