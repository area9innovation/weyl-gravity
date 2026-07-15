import json
import unittest

from local_bv.certificate import CERTIFICATE_PATH, build_certificate, rendered_certificate


class CertificateTests(unittest.TestCase):
    def test_checked_in_certificate_is_reproducible(self) -> None:
        self.assertEqual(CERTIFICATE_PATH.read_text(encoding="utf-8"), rendered_certificate())

    def test_certificate_is_fail_closed_and_local_algebraic(self) -> None:
        certificate = build_certificate()
        self.assertEqual(certificate["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(certificate["classical_commit"], "NOT_FROZEN")
        self.assertEqual(certificate["checks"]["local_cohomology_H_s_mod_d"], "NOT_COMPUTED")
        self.assertEqual(certificate["checks"]["antifield_rows"], "BLOCKED")
        self.assertTrue(certificate["not_computed"])
        json.dumps(certificate, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
