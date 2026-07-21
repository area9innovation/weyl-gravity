from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

from jsonschema import ValidationError


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE.parent / "verify_normalized_schur_pseudodifferential_variation.py"
SPEC = importlib.util.spec_from_file_location("verify_normalized_schur_pseudodifferential_variation", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CERTIFICATE = HERE.parent / "certificates/NORMALIZED_SCHUR_PSEUDODIFFERENTIAL_VARIATION.json"
MANIFEST = HERE.parent / "generated/normalized_schur_pseudodifferential_variation_v1/operator_words.json"


class NormalizedSchurPseudodifferentialVariationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE.read_text())
        cls.manifest = json.loads(MANIFEST.read_text())

    def assert_rejected(self, certificate: dict, manifest: dict) -> None:
        with self.assertRaises((AssertionError, ValueError, ValidationError)):
            MODULE.verify(certificate, manifest)

    def test_independent_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.certificate), copy.deepcopy(self.manifest))

    def test_wrong_sign_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["schur_variations"][0]["taylor_coefficient"] = "1/3"
        self.assert_rejected(copy.deepcopy(self.certificate), manifest)

    def test_noncommuting_reorder_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["schur_variations"][0]["operator_word"] = ["delta", "W", "G", "G", "d"]
        self.assert_rejected(copy.deepcopy(self.certificate), manifest)

    def test_order_zero_surrogate_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["schur_variations"][0]["ward_reduced_word"] = ["DeltaInv", "delta", "W", "d"]
        self.assert_rejected(copy.deepcopy(self.certificate), manifest)

    def test_frozen_moving_projector_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["moving_projector_control"]["full_projector_formula"] = manifest["moving_projector_control"]["naive_fixed_projector_term"]
        self.assert_rejected(copy.deepcopy(self.certificate), manifest)

    def test_berger_mutation_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["berger_low_block_control"]["correct_first_variation"] = "4/9"
        self.assert_rejected(copy.deepcopy(self.certificate), manifest)

    def test_global_determinant_promotion_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        certificate["claim_flags"]["GLOBAL_FINITE_DETERMINANT_COMPUTED"] = True
        self.assert_rejected(certificate, copy.deepcopy(self.manifest))

    def test_qme_promotion_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        certificate["claim_flags"]["QME_OR_LORENTZIAN_PROMOTED"] = True
        self.assert_rejected(certificate, copy.deepcopy(self.manifest))


if __name__ == "__main__":
    unittest.main()
