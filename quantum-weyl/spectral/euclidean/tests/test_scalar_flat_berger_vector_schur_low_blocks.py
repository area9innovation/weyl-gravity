from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE.parent / "verify_scalar_flat_berger_vector_schur_low_blocks.py"
SPEC = importlib.util.spec_from_file_location("verify_berger_vector_schur_low_blocks", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CERTIFICATE = HERE.parent / "certificates/SCALAR_FLAT_BERGER_VECTOR_SCHUR_LOW_BLOCKS.json"
ORACLE = HERE.parent / "generated/scalar_flat_berger_vector_schur_low_blocks_v1/blocks.json"


class ScalarFlatBergerVectorSchurLowBlocksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE.read_text())
        cls.oracle = json.loads(ORACLE.read_text())

    def assert_rejected(self, certificate: dict, oracle: dict) -> None:
        with self.assertRaises((AssertionError, ValueError)):
            MODULE.verify(certificate, oracle)

    def test_independent_low_block_replay(self) -> None:
        MODULE.verify(copy.deepcopy(self.certificate), copy.deepcopy(self.oracle))

    def test_spin_half_derivative_mutation_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        oracle = copy.deepcopy(self.oracle)
        block = next(row for row in oracle["blocks"] if row["n"] == 0 and row["twice_j"] == 1)
        block["S_L_first_derivative_at_zero"][0][0] = "-63/81"
        self.assert_rejected(certificate, oracle)

    def test_hodge_ward_mutation_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        oracle = copy.deepcopy(self.oracle)
        block = next(row for row in oracle["blocks"] if row["n"] == 1 and row["twice_j"] == 2)
        block["F_matrix"][0][0] = "999"
        self.assert_rejected(certificate, oracle)

    def test_killing_kernel_mutation_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        oracle = copy.deepcopy(self.oracle)
        oracle["priming"]["A_at_one_zero_dimension_with_left_multiplicity"] = 4
        self.assert_rejected(certificate, oracle)

    def test_high_mode_promotion_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        certificate["claim_flags"]["UNIFORM_HIGH_MODE_ESTIMATE_COMPUTED"] = True
        self.assert_rejected(certificate, copy.deepcopy(self.oracle))

    def test_qme_promotion_rejected(self) -> None:
        certificate = copy.deepcopy(self.certificate)
        certificate["claim_flags"]["QME_OR_LORENTZIAN_PROMOTED"] = True
        self.assert_rejected(certificate, copy.deepcopy(self.oracle))


if __name__ == "__main__":
    unittest.main()
