import json
import unittest

from local_bv.differential_hodge_certificate import (
    DETAILED_PATH,
    RESULT_PATH,
    build_certificate,
    build_result_envelope,
)


class DifferentialHodgeCertificateTests(unittest.TestCase):
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
        derivative = certificate["one_derivative_curvature"]
        self.assertEqual(certificate["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(certificate["classical_commit"], "UNFROZEN")
        self.assertEqual(derivative["raw_pairing_count"], 945)
        self.assertEqual(derivative["quotient_dimension"], 4)
        self.assertFalse(derivative["ibp_or_commutator_reduction_applied"])
        self.assertEqual(
            certificate["checks"]["local_cohomology_H_s_mod_d"],
            "NOT_COMPUTED",
        )
        self.assertEqual(certificate["checks"]["antifield_rows"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
