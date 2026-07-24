from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .audit import PACKAGE, AuditError, build_certificate
from .verify import verify_certificate


ROOT = Path(__file__).resolve().parents[3]


class ClassificationTest(unittest.TestCase):
    def test_current_certificate_passes(self) -> None:
        verify_certificate(ROOT)

    def _reject(self, mutate) -> None:
        certificate = build_certificate(ROOT)
        mutate(certificate)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "certificate.json"
            path.write_text(json.dumps(certificate), encoding="utf-8")
            with self.assertRaises(AuditError):
                verify_certificate(ROOT, path)

    def test_wrong_joint_interval_is_rejected(self) -> None:
        self._reject(lambda c: c["scope"].update(joint_pilot_interval=["1/2", "129/256"]))

    def test_wrong_outgoing_inertia_is_rejected(self) -> None:
        self._reject(
            lambda c: c["finite_flux_spaces"]["outgoing_Iplus"].update(inertia=[2, 1, 0])
        )

    def test_radial_cover_promoted_to_physical_connection_is_rejected(self) -> None:
        self._reject(
            lambda c: c["radial_connection_pilot"].update(
                interpretation="physical horizon-to-infinity connection"
            )
        )

    def test_explicit_tplus_overclaim_is_rejected(self) -> None:
        self._reject(
            lambda c: c["claim_flags"].update(explicit_Tplus_entries_established=True)
        )

    def test_time_domain_overclaim_is_rejected(self) -> None:
        self._reject(lambda c: c["claim_flags"].update(time_domain_or_quantum_claim=True))

    def test_import_hash_drift_is_rejected(self) -> None:
        self._reject(lambda c: c["imports"][0].update(sha256="0" * 64))


if __name__ == "__main__":
    unittest.main()
