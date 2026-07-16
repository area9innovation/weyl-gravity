from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "ppwave_branch_transfer_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("ppwave_branch_transfer_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORTER = sys.modules[CERT.build_import.__module__]


class PPWaveBranchTransferImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORTER._git_json(IMPORTER.CERTIFICATE_RELATIVE)
        cls.schema = IMPORTER._git_json(IMPORTER.SCHEMA_RELATIVE)

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), CERT.build_certificate())

    def test_actual_branch_mixing_table_is_zero(self) -> None:
        result = CERT.build_certificate()
        bracket = result["transferred_bracket"]
        self.assertEqual(bracket["Einstein_Einstein"], "0")
        self.assertEqual(bracket["Einstein_extraWeyl"], "0")
        self.assertEqual(bracket["extraWeyl_extraWeyl"], "0")
        self.assertTrue(bracket["homotopy_independent"])

    def test_support_local_and_full_theory_boundary(self) -> None:
        result = CERT.build_certificate()
        self.assertTrue(result["support_local_block"]["arbitrary_profile_not_mode_truncated"])
        self.assertFalse(result["support_local_block"]["full_BV_block"])
        self.assertTrue(result["claim_flags"]["ALIGNED_PPWAVE_BRANCHES_CLOSE"])
        self.assertFalse(result["claim_flags"]["NONALIGNED_BRANCH_MIXING_CLASSIFIED"])
        self.assertFalse(result["claim_flags"]["FULL_SUPPORT_LOCAL_BV_Q2"])

    def test_mutations_fail_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["flags"]["FULL_SUPPORT_LOCAL_BV_Q2"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            IMPORTER.validate_bridge_payload(forged, self.schema)

        forged = deepcopy(self.payload)
        forged["restricted_nonlinear_tensor"]["q2_entries"]["Einstein_extraWeyl"] = "1"
        with self.assertRaisesRegex(ValueError, "q2 coefficients"):
            IMPORTER.validate_bridge_payload(forged, self.schema)

        forged = deepcopy(self.payload)
        forged["branch_representatives"]["extra_Weyl"]["Ricci_flat"] = True
        with self.assertRaisesRegex(ValueError, "branch labels"):
            IMPORTER.validate_bridge_payload(forged, self.schema)


if __name__ == "__main__":
    unittest.main()
