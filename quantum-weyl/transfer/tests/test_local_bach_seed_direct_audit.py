from __future__ import annotations

from copy import deepcopy
import json
import sys
import unittest
from pathlib import Path


QUANTUM_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(QUANTUM_ROOT))
TRANSFER_ROOT = QUANTUM_ROOT / "transfer"

from transfer.local_bach_seed_direct_audit import (
    OUTPUT_PATH,
    SCHEMA_PATH,
    validate_direct_audit,
)
from transfer.local_bach_seed_lift import OUTPUT_PATH as SEED_CERTIFICATE_PATH


class LocalBachSeedDirectAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        cls.seed = json.loads(SEED_CERTIFICATE_PATH.read_text(encoding="utf-8"))

    def test_checked_in_direct_audit_is_semantically_valid(self) -> None:
        validate_direct_audit(self.audit, self.seed)

    def test_eight_probes_are_direct_curvature_executions(self) -> None:
        results = self.audit["direct_probe_results"]
        self.assertEqual(len(results), 8)
        self.assertTrue(
            all(
                result["execution_kind"] == "DIRECT_EXACT_CURVATURE_ENGINE"
                for result in results
            )
        )

    def test_reverse_claim_remains_slice_only(self) -> None:
        checks = self.audit["checks"]
        self.assertEqual(checks["reverse_slice_density_adjoint"], "VERIFIED_EXACT")
        self.assertIn("NOT_COMPUTED", checks["reverse_local_taub_density"])

    def test_hash_consistent_direct_density_tamper_is_rejected(self) -> None:
        audit = deepcopy(self.audit)
        audit["direct_probe_results"][0]["local_radial_density"] = "Integer(0)"
        with self.assertRaisesRegex(ValueError, "measure identity"):
            validate_direct_audit(audit, self.seed)

    def test_schema_receipt_is_present(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "local-bach-seed-direct-audit-v1.schema.json")


if __name__ == "__main__":
    unittest.main()
