from __future__ import annotations

from copy import deepcopy
import json
import unittest

from anomalies.regulated_slavnov_breaking_preflight import validate_regulated_breaking_export
from anomalies.repository_regulated_slavnov_breaking import OUTPUT, ROOT, build
from anomalies.verify_repository_regulated_slavnov_breaking import verify


class RepositoryRegulatedSlavnovBreakingTests(unittest.TestCase):
    def test_physical_breaking_is_obstructed(self) -> None:
        receipt = validate_regulated_breaking_export(build()[-1], repository_root=ROOT)
        self.assertEqual(receipt["classification"], "NONTRIVIAL")
        self.assertEqual(receipt["qme_disposition"], "OBSTRUCTED_STRICT_FIELD_CONTENT")

    def test_binding_and_disposition_mutations_are_rejected(self) -> None:
        value = build()[-1]
        mutant = deepcopy(value)
        mutant["insertion_decomposition"]["regulated_slavnov_action_artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_regulated_breaking_export(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["qme_disposition"]["status"] = "RESTORABLE_BY_LOCAL_COUNTERTERM"
        with self.assertRaisesRegex(ValueError, "invalid QME disposition"):
            validate_regulated_breaking_export(mutant, repository_root=ROOT)
        mutant = deepcopy(value)
        mutant["coefficients"]["ANOM_OMEGA_C2"]["numerator"] = 0
        with self.assertRaisesRegex(ValueError, "binding drifted"):
            validate_regulated_breaking_export(mutant, repository_root=ROOT)

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build()[-1])
        self.assertEqual(verify()["qme_disposition"], "OBSTRUCTED_STRICT_FIELD_CONTENT")


if __name__ == "__main__":
    unittest.main()
