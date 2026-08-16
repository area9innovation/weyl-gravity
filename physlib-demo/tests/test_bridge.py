from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_bridge", DEMO / "check_bridge.py")
CHECKER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECKER)


class PhyslibBridgeCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = json.loads(CHECKER.CERTIFICATE.read_text())

    def test_certificate_passes(self) -> None:
        errors, _ = CHECKER.check(self.result)
        self.assertEqual(errors, [])

    def test_causal_overpromotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["dependency_tags"].append("LORENTZIAN-CAUSAL")
        errors, _ = CHECKER.check(mutated)
        self.assertIn("dependency boundary", errors)

    def test_false_formalization_flag_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["claim_flags"]["GREEN_HOMOTOPY_FORMALIZED"] = True
        errors, _ = CHECKER.check(mutated)
        self.assertIn("claim flags", errors)

    def test_source_hash_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["provenance"]["lean_source"]["sha256"] = "0" * 64
        errors, _ = CHECKER.check(mutated)
        self.assertIn("Lean source hash", errors)

    def test_physlib_pin_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["toolchain"]["physlib_commit"] = "0" * 40
        errors, _ = CHECKER.check(mutated)
        self.assertIn("Physlib manifest pin", errors)


if __name__ == "__main__":
    unittest.main()
