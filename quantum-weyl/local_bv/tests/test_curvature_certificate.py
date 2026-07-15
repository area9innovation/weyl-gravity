import json
import unittest

from local_bv.curvature_certificate import (
    DETAILED_PATH,
    RESULT_PATH,
    build_certificate,
    build_result_envelope,
)


class CurvatureCertificateTests(unittest.TestCase):
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

    def test_certificate_is_fail_closed(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(certificate["classical_commit"], "UNFROZEN")
        self.assertEqual(certificate["quadratic_curvature"]["quotient_dimension"], 3)
        self.assertEqual(certificate["quadratic_curvature"]["pivot_columns"], [2])
        self.assertEqual(certificate["quadratic_curvature"]["free_columns"], [0, 1, 3])
        self.assertEqual(len(certificate["quadratic_curvature"]["canonical_basis"]), 4)
        self.assertEqual(
            certificate["checks"]["local_cohomology_H_s_mod_d"],
            "NOT_COMPUTED",
        )
        self.assertEqual(certificate["checks"]["antifield_rows"], "BLOCKED")
        self.assertTrue(certificate["not_computed"])


if __name__ == "__main__":
    unittest.main()
