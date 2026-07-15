import hashlib
import json
import unittest
from fractions import Fraction

from local_bv.algebra import canonical_sha256
from local_bv.lower_form_basis import (
    REPOSITORY_ROOT,
    _universal_coefficient,
    lower_form_carrier_analysis,
)
from local_bv.lower_form_basis_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class LowerFormBasisTests(unittest.TestCase):
    def test_candidate_and_boundary_carrier_counts(self) -> None:
        analysis = lower_form_carrier_analysis()
        self.assertEqual(
            analysis["counts"],
            {
                "universal_candidate_carriers": 40,
                "intrinsic_euler_carriers": 11,
                "exact_boundary_carriers": 13,
                "all_carriers": 64,
                "strict_lower_form_carriers": 55,
                "structurally_zero_euler_components": 2,
            },
        )
        self.assertEqual(
            analysis["total_complex_gates"][
                "LOWER_FORM_CANDIDATE_CARRIER_COVERAGE"
            ],
            "COMPLETE",
        )
        self.assertEqual(
            analysis["total_complex_gates"]["TOTAL_COMPLEX_EXHAUSTIVE"],
            "NOT_COMPUTED",
        )

    def test_universal_coefficients_and_total_degrees(self) -> None:
        self.assertEqual(
            [_universal_coefficient(order) for order in range(5)],
            [
                Fraction(1),
                Fraction(-1),
                Fraction(1, 2),
                Fraction(-1, 6),
                Fraction(1, 24),
            ],
        )
        for carrier in lower_form_carrier_analysis()["carriers"]:
            self.assertEqual(
                carrier["total_degree"],
                carrier["ghost_number"] + carrier["form_degree"],
            )
            payload = {
                key: value for key, value in carrier.items()
                if key != "carrier_sha256"
            }
            self.assertEqual(carrier["carrier_sha256"], canonical_sha256(payload))

    def test_dependencies_are_byte_and_canonically_bound(self) -> None:
        for artifact in lower_form_carrier_analysis()["source_artifacts"]:
            path = REPOSITORY_ROOT / artifact["path"]
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )
            self.assertEqual(artifact["canonical_sha256"], canonical_sha256(payload))

    def test_intrinsic_euler_zero_tail_is_retained(self) -> None:
        zeros = lower_form_carrier_analysis()["structural_zeros"]
        self.assertEqual(
            [(row["ghost_number"], row["form_degree"]) for row in zeros],
            [(4, 1), (5, 0)],
        )

    def test_schema_and_checked_in_certificate(self) -> None:
        certificate = build_certificate()
        self.assertFalse(
            validate_instance(certificate, json.loads(SCHEMA_PATH.read_text()))
        )
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)


if __name__ == "__main__":
    unittest.main()
