from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
RESULT = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
CHECK = module("strict_local_q1_q2_check", HERE / "check_strict_local_q1_q2_identity.py")
VERIFY = module("strict_local_q1_q2_verify", HERE / "verify_strict_local_q1_q2_identity.py")


class StrictLocalQ1Q2IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())
        cls.report = (HERE / "REPORT_STRICT_LOCAL_Q1_Q2_IDENTITY_V1.md").read_text()

    def test_repository_result_with_exact_replay(self) -> None:
        self.assertEqual(CHECK.check(self.value), [])

    def test_schema_and_report_boundary(self) -> None:
        self.assertEqual(VERIFY.verify(self.value, self.report), [])

    def test_channel_multiplier_mutation_fails_closed(self) -> None:
        value = copy.deepcopy(self.value)
        value["channel_inventory"]["channels"][0]["paths"][0]["multiplier"] *= -1
        errors = CHECK.check(value, replay_exact=False)
        self.assertTrue(any("inventory drift" in error for error in errors))

    def test_fixture_promotion_or_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["exact_receiver"]["fixture_records"][0]["rows"][0]["defect_zero"] = False
        errors = CHECK.check(value, replay_exact=False)
        self.assertTrue(any("fixture rows" in error for error in errors))

    def test_D_promotion_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["claim_flags"]["D_Q2_DERIVATION_REPLAYED"] = True
        self.assertTrue(any("claim flags" in error for error in CHECK.check(value, replay_exact=False)))

    def test_proof_helper_boundary_mutation_fails(self) -> None:
        value = copy.deepcopy(self.value)
        value["proof_basis"]["legacy_matrix_cartan_helper_used"] = True
        self.assertTrue(any("proof status" in error for error in CHECK.check(value, replay_exact=False)))

    def test_report_boundary_mutation_fails(self) -> None:
        report = self.report.replace("Gate A remains fail closed", "Gate A passed")
        self.assertTrue(any("report missing" in error for error in VERIFY.verify(self.value, report)))


if __name__ == "__main__":
    unittest.main()
