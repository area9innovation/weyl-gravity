from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bridge.einstein_sector import certificate


class EinsteinSectorCertificateTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        certificate.verify_certificate()

    def test_headline_classification_is_fail_closed(self) -> None:
        result = certificate.build_certificate()
        self.assertEqual(
            result["classification"]["einstein_as_exact_solution_sector"],
            "ESTABLISHED",
        )
        self.assertEqual(
            result["classification"]["einstein_observables_subset_reduced_conformal_observables"],
            "NOT_ESTABLISHED",
        )
        self.assertFalse(result["claim_flags"]["asymptotically_flat_scattering_recovered"])
        self.assertFalse(
            result["claim_flags"]["einstein_sector_causally_closed_at_null_infinity"]
        )
        self.assertFalse(result["claim_flags"]["lorentzian_quantum_theorem"])
        self.assertEqual(
            {row["status"] for row in result["next_theorem_commission"]["obligations"]},
            {"OPEN"},
        )

    def test_changed_residual_input_is_rejected(self) -> None:
        original_load = certificate._load

        def forged_load(path: Path):
            payload = original_load(path)
            if path == certificate.INPUTS["metric_to_residual"]:
                payload = copy.deepcopy(payload)
                payload["one_particle"]["h4"] = 1
            return payload

        with patch.object(certificate, "_load", side_effect=forged_load):
            with self.assertRaises(certificate.EinsteinSectorCertificateError):
                certificate.build_certificate()

    def test_altered_certificate_is_rejected(self) -> None:
        payload = certificate.build_certificate()
        payload["claim_flags"]["asymptotically_flat_scattering_recovered"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(certificate.EinsteinSectorCertificateError):
                certificate.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
