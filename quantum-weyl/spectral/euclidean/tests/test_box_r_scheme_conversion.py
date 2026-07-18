from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from box_r_scheme_conversion import build


def _fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _linear(value: dict[str, object]) -> tuple[Fraction, Fraction]:
    return _fraction(value["rational"]), _fraction(value["log_3_over_2"])


class BoxRSchemeConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_raw_coefficient(self) -> None:
        self.assertEqual(
            _linear(self.value["heat_kernel_row_reconstruction"]["raw_BoxR_coefficient"]),
            (Fraction(-159, 80), Fraction(7, 2)),
        )

    def test_scheme_shift(self) -> None:
        self.assertEqual(
            _linear(self.value["repository_scheme_conversion"]["raw_to_BoxR_zero_counterterm"]),
            (Fraction(-53, 320), Fraction(7, 24)),
        )

    def test_repository_local_r2(self) -> None:
        self.assertEqual(
            _linear(self.value["anomaly_induced_local_R2_cross_check"]["repository_BoxR_zero_coefficient"]),
            (Fraction(29, 120), Fraction()),
        )

    def test_r2_directions_are_distinct(self) -> None:
        self.assertTrue(self.value["distinct_R2_directions"]["conflation_forbidden"])
        self.assertEqual(
            self.value["decision"]["absolute_dressed_Rhat2_normalization"],
            "NOT_FIXED",
        )

    def test_nonlocal_form_factor_remains_open(self) -> None:
        self.assertEqual(self.value["decision"]["nonlocal_R2_form_factor"], "NOT_COMPUTED")
        self.assertFalse(self.value["claim_flags"]["NONLOCAL_R2_FORM_FACTOR_COMPUTED"])

    def test_convention_and_all_loop_guards(self) -> None:
        self.assertIn(
            "beta2=2c",
            self.value["external_analytic_input"]["C2_convention_guard"],
        )
        self.assertFalse(
            self.value["repository_scheme_conversion"]["all_loop_theory_equivalence"]
        )

    def test_emitted_certificate_matches(self) -> None:
        emitted = json.loads(
            (HERE / "certificates/WEYL_GRAVITON_BOX_R_SCHEME_CONVERSION.json").read_text()
        )
        self.assertEqual(emitted, self.value)


if __name__ == "__main__":
    unittest.main()
