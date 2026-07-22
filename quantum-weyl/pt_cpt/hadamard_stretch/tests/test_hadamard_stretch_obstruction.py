from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


producer = _load("hadamard_stretch_obstruction", HERE / "hadamard_stretch_obstruction.py")
verifier = _load("verify_hadamard_stretch_obstruction", HERE / "verify_hadamard_stretch_obstruction.py")


class HadamardStretchObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((HERE / "certificates" / "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json").read_text())

    def test_producer_rebuilds_frozen_payload(self):
        self.assertEqual(producer.build_payload(), self.payload)

    def test_independent_verifier_accepts(self):
        verifier.validate(self.payload)

    def test_reduced_carrier_substitution_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["selected_complex"]["row_count"] = 26
        with self.assertRaises(AssertionError):
            verifier.validate(mutant)

    def test_zero_mode_promotion_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["claim_flags"]["BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER"] = True
        with self.assertRaises(AssertionError):
            verifier.validate(mutant)

    def test_full_bv_C_promotion_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["claim_flags"]["P2A_FULL_BV_C_OPERATOR_CERTIFIED"] = True
        with self.assertRaises(AssertionError):
            verifier.validate(mutant)

    def test_hadamard_promotion_is_rejected(self):
        mutant = copy.deepcopy(self.payload)
        mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
        with self.assertRaises(AssertionError):
            verifier.validate(mutant)


if __name__ == "__main__":
    unittest.main()
