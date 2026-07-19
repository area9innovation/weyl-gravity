import hashlib
import json
import os
from pathlib import Path
import unittest

from bridge.einstein_sector.verify_weyl_maxwell_product_linfinity import verify


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WeylMaxwellProductLinfinityTests(unittest.TestCase):
    def test_portable_artifact_manifest_is_complete_and_content_addressed(self):
        certificate = json.loads(CERTIFICATE.read_text())
        self.assertEqual(certificate["claim_status"], "CERTIFIED_THROUGH_ARITY_THREE")
        self.assertEqual(certificate["executable_contract"]["row_count"], 40)
        for name in ("row_layout", "action", "q1", "q2", "q3", "pairing"):
            artifact = certificate["taylor_artifacts"][name]
            path = ROOT / artifact["path"]
            self.assertTrue(path.is_file(), name)
            self.assertEqual(_sha256(path), artifact["sha256"], name)

    @unittest.skipUnless(
        os.environ.get("RUN_WEYL_MAXWELL_HEAVY_VERIFY") == "1",
        "70-minute independent exact replay is an opt-in Tier-2 test",
    )
    def test_independent_payload_replay(self):
        value = verify()
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["row_count"], 40)
        self.assertTrue(all(not any(counts) for counts in value["defect_counts"].values()))
        self.assertEqual(value["cyclicity"]["unary_pairing_adjoint"], "PASS")
        self.assertEqual(value["cyclicity"]["higher_input_koszul_symmetry"], "PASS")
        self.assertEqual(value["cyclicity"]["higher_output_input_cyclicity"], "PASS")
        self.assertGreater(value["cyclicity"]["ordered_first_slot_transpose_counts"]["q1"], 0)
        self.assertGreater(value["cyclicity"]["ordered_first_slot_transpose_counts"]["q2"], 0)
        self.assertGreater(value["cyclicity"]["ordered_first_slot_transpose_counts"]["q3"], 0)


if __name__ == "__main__":
    unittest.main()
