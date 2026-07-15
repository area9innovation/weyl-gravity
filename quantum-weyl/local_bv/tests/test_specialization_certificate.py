import json
import unittest

from local_bv.schema_validation import validate_instance
from local_bv.specialization_certificate import (
    DETAILED_PATH,
    RESULT_PATH,
    SCHEMA_PATH,
    build_certificate,
    build_result_envelope,
)


class SpecializationCertificateTests(unittest.TestCase):
    def test_detailed_certificate_is_reproducible(self) -> None:
        self.assertEqual(
            json.loads(DETAILED_PATH.read_text(encoding="utf-8")),
            build_certificate(),
        )

    def test_common_result_envelope_is_reproducible(self) -> None:
        self.assertEqual(
            json.loads(RESULT_PATH.read_text(encoding="utf-8")),
            build_result_envelope(),
        )

    def test_detailed_certificate_satisfies_enforced_schema(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        certificate = build_certificate()
        self.assertEqual(validate_instance(certificate, schema), [])
        certificate["universal_import"]["quotient_dimension"] = 9
        self.assertIn(
            "$.universal_import.quotient_dimension: value differs from const",
            validate_instance(certificate, schema),
        )

    def test_claim_boundary_remains_fail_closed(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["classical_commit"], "UNFROZEN")
        self.assertEqual(
            certificate["checks"]["four_dimensional_schouten_quotient"],
            "NOT_COMPUTED",
        )
        self.assertEqual(
            certificate["checks"]["local_cohomology_H_s_mod_d"],
            "NOT_COMPUTED",
        )


if __name__ == "__main__":
    unittest.main()
