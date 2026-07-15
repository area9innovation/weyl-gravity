from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))

from transfer.local_bach_seed_lift import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    _canonical_hash,
    build_certificate,
    validate_certificate,
)


class LocalBachSeedLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate(4)

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.certificate)

    def test_two_direct_local_channels_reach_residual_q2_entries(self) -> None:
        channels = self.certificate["seed_payload"]["direct_local_channels"]
        self.assertEqual(len(channels), 2)
        self.assertEqual(
            {channel["residual_kernel_label"] for channel in channels},
            {"K-_1/2_-1/2", "K+_1/2_-1/2"},
        )
        for channel in channels:
            self.assertEqual(
                channel["integrated_taub_charge"],
                channel["raw_residual_kernel_entry"],
            )
            self.assertEqual(
                channel["checks"]["local_density_integrates_to_taub_charge"],
                "VERIFIED_EXACT",
            )

    def test_reverse_and_parity_completion_is_integrated_only(self) -> None:
        completion = self.certificate["seed_payload"]["integrated_reverse_completion"]
        self.assertEqual(completion["dagger_relation"], "VERIFIED_EXACT")
        self.assertEqual(completion["parity_seed_equality"], "VERIFIED_EXACT")
        self.assertFalse(completion["support_local_density_available_for_reverse_channels"])
        self.assertEqual(
            completion["reverse_local_taub_density_status"],
            "NOT_COMPUTED_MISSING_REVERSE_GAUGE_PROBES",
        )

    def test_full_local_bv_lift_remains_blocked(self) -> None:
        checks = self.certificate["checks"]
        self.assertEqual(checks["full_support_local_q2"], "NOT_COMPUTED")
        self.assertEqual(checks["ghost_completion"], "NOT_COMPUTED")
        self.assertEqual(checks["antifield_completion"], "NOT_COMPUTED")
        self.assertIn("NOT_COMPUTED", checks["local_q1_q2_chain_identity"])
        self.assertTrue(
            any("HT1b is not complete" in guard for guard in self.certificate["claim_guards"])
        )

    def test_schema_receipt_is_present(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "local-bach-seed-lift-v2.schema.json")

    def test_payload_hash_tamper_is_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        certificate["seed_payload"]["direct_local_channels"][0]["local_radial_density"] = "Integer(0)"
        with self.assertRaisesRegex(ValueError, "payload hash"):
            validate_certificate(certificate)

    def test_hash_consistent_density_tamper_is_semantically_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        certificate["seed_payload"]["direct_local_channels"][0]["local_radial_density"] = "Integer(0)"
        certificate["seed_payload_sha256"] = _canonical_hash(certificate["seed_payload"])
        with self.assertRaisesRegex(ValueError, "measured integrand"):
            validate_certificate(certificate)

    def test_hash_consistent_normalization_tamper_is_semantically_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        channel = certificate["seed_payload"]["direct_local_channels"][0]
        channel["raw_ck_to_canonical_scale"] = "Integer(1)"
        certificate["seed_payload_sha256"] = _canonical_hash(certificate["seed_payload"])
        with self.assertRaisesRegex(ValueError, "normalization identity"):
            validate_certificate(certificate)

    def test_false_full_lift_promotion_is_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        certificate["checks"]["full_support_local_q2"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate_certificate(certificate)

    def test_upstream_hash_tamper_is_rejected(self) -> None:
        certificate = deepcopy(self.certificate)
        first = next(iter(certificate["provenance"]["upstream_sha256"]))
        certificate["provenance"]["upstream_sha256"][first] = "0" * 64
        with self.assertRaisesRegex(ValueError, "content hash"):
            validate_certificate(certificate)


if __name__ == "__main__":
    unittest.main()
