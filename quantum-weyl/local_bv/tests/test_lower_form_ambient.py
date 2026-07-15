import json
import unittest

from local_bv.algebra import canonical_sha256
from local_bv.lower_form_ambient import (
    ambient_lower_form_signature_analysis,
    ambient_signatures,
)
from local_bv.lower_form_ambient_certificate import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    build_certificate,
)
from local_bv.schema_validation import validate_instance


class AmbientLowerFormSignatureTests(unittest.TestCase):
    def test_total_degree_counts_are_frozen(self) -> None:
        analysis = ambient_lower_form_signature_analysis()
        self.assertEqual(
            analysis["totals"],
            {
                "coarse_signature_count": 2480,
                "refined_signature_count": 720,
                "rejected_signature_count": 1760,
            },
        )
        self.assertEqual(
            [
                (row["parity"], row["total_degree"], row["refined_signature_count"])
                for row in analysis["manifests"]
            ],
            [
                ("even", 3, 22),
                ("even", 4, 51),
                ("even", 5, 105),
                ("even", 6, 183),
                ("odd", 3, 20),
                ("odd", 4, 51),
                ("odd", 5, 105),
                ("odd", 6, 183),
            ],
        )

    def test_every_signature_satisfies_exact_gradings_and_hash(self) -> None:
        for manifest in ambient_lower_form_signature_analysis()["manifests"]:
            for row in manifest["signatures"]:
                self.assertEqual(row["ghost_number"] + row["form_degree"], row["total_degree"])
                self.assertEqual(row["total_form_engineering_dimension"], 0)
                payload = {
                    key: value for key, value in row.items()
                    if key != "signature_sha256"
                }
                self.assertEqual(row["signature_sha256"], canonical_sha256(payload))

    def test_grassmann_and_seed_rejections_are_present(self) -> None:
        rows = ambient_signatures(4, "even")
        reasons = {row["refinement_reason"] for row in rows if row["refinement_status"] == "REJECTED"}
        self.assertIn(
            "insufficient Weyl-ghost derivatives force two undifferentiated scalar ghosts and hence vanish by Grassmann oddness",
            reasons,
        )
        self.assertIn(
            "tensor derivatives have no curvature seed because nabla g=0",
            reasons,
        )

    def test_invalid_bounds_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "total degree"):
            ambient_signatures(2, "even")
        with self.assertRaisesRegex(ValueError, "parity"):
            ambient_signatures(4, "mixed")

    def test_schema_and_checked_in_certificate(self) -> None:
        certificate = build_certificate()
        self.assertFalse(validate_instance(certificate, json.loads(SCHEMA_PATH.read_text())))
        self.assertEqual(json.loads(OUTPUT_PATH.read_text()), certificate)


if __name__ == "__main__":
    unittest.main()
