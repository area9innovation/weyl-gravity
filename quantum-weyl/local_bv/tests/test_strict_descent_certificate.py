import json
import unittest

from local_bv.schema_validation import validate_instance
from local_bv.strict_descent_certificate import (
    DATABASE_PATH,
    DATABASE_SCHEMA_PATH,
    DETAILED_PATH,
    SCHEMA_PATH,
    build_certificate,
    build_database,
)


class StrictDensityDescentCertificateTests(unittest.TestCase):
    def test_checked_in_artifacts_reproduce_exactly(self) -> None:
        self.assertEqual(json.loads(DETAILED_PATH.read_text()), build_certificate())
        self.assertEqual(json.loads(DATABASE_PATH.read_text()), build_database())

    def test_schemas_validate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        database_schema = json.loads(DATABASE_SCHEMA_PATH.read_text())
        self.assertFalse(validate_instance(build_certificate(), schema))
        self.assertFalse(validate_instance(build_database(), database_schema))

    def test_database_does_not_promote_euler_or_cohomology(self) -> None:
        database = build_database()
        entries = {entry["class_id"]: entry for entry in database["entries"]}
        self.assertEqual(
            entries["ANOM_OMEGA_E4"]["intrinsic_weyl_descent_status"],
            "PENDING_TYPE_A_TRANSGRESSION",
        )
        self.assertEqual(
            entries["ANOM_OMEGA_BOX_R"]["intrinsic_weyl_descent_status"],
            "TRIVIAL_WITH_PRIMITIVE",
        )
        self.assertEqual(
            entries["CT_C2"]["intrinsic_weyl_descent_status"],
            "STRICTLY_WEYL_INVARIANT",
        )
        self.assertEqual(
            entries["ANOM_OMEGA_C2"]["intrinsic_weyl_descent_status"],
            "TRIVIAL",
        )
        self.assertTrue(
            all(
                entry["diff_descent_status"] == "NONZERO_COMPLETE"
                for entry in entries.values()
            )
        )
        self.assertEqual(entries["ANOM_OMEGA_BOX_R"]["class_status"], "EXACT")
        self.assertEqual(entries["ANOM_OMEGA_C2"]["class_status"], "UNDECIDED")


if __name__ == "__main__":
    unittest.main()
