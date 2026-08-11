from __future__ import annotations

import copy
import unittest

from foundations.check_low_hanging_cell_closure import check
from foundations.verify_low_hanging_cell_closure import (
    CUBE, H04, IMPORT_GATE, MODE, REPORT, RESULT, load, verify,
)


class LowHangingCellClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()
        cls.cube = load(CUBE)
        cls.mode = load(MODE)
        cls.h04 = load(H04)
        cls.import_gate = load(IMPORT_GATE)

    def run_verify(self, **changes):
        arguments = {
            "result": copy.deepcopy(self.result),
            "report": self.report,
            "cube": copy.deepcopy(self.cube),
            "mode": copy.deepcopy(self.mode),
            "h04": copy.deepcopy(self.h04),
            "import_gate": copy.deepcopy(self.import_gate),
        }
        arguments.update(changes)
        return verify(**arguments)[0]

    def test_repository_result_passes(self):
        self.assertEqual(self.run_verify(), [])

    def test_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_digest"] = "0" * 64
        self.assertTrue(check(result)[0])

    def test_promotion_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["promotions"][0]["old_status"] = "PRIORITY_GAP"
        self.assertTrue(check(result)[0])

    def test_remaining_cell_removed_fails(self):
        result = copy.deepcopy(self.result)
        result["remaining_assessed_open_cells"].pop()
        self.assertTrue(check(result)[0])

    def test_unapplied_promotion_fails(self):
        cube = copy.deepcopy(self.cube)
        cell = next(item for item in cube["cells"] if item["foundation"] == "FINITE_DISCRETE" and item["carrier"] == "FINITE_EXACT" and item["obligation"] == "DYNAMICS_PROPAGATION")
        cell["status"] = "PRIORITY_GAP"
        self.assertTrue(self.run_verify(cube=cube))

    def test_h04_completion_mutation_fails(self):
        h04 = copy.deepcopy(self.h04)
        h04["claim_flags"]["COHOMOLOGY_COMPLETE"] = False
        self.assertTrue(self.run_verify(h04=h04))

    def test_classical_freeze_promotion_fails(self):
        import_gate = copy.deepcopy(self.import_gate)
        import_gate["gate_a_status"] = "PASSED"
        self.assertTrue(self.run_verify(import_gate=import_gate))

    def test_finite_witness_mutation_fails(self):
        mode = copy.deepcopy(self.mode)
        mode["finite_exact_witness"]["matrix_units"] = 323
        self.assertTrue(self.run_verify(mode=mode))

    def test_lorentzian_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["lorentzian_certified"] = True
        self.assertTrue(self.run_verify(result=result))

    def test_unmapped_exhaustion_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["all_216_cells_assessed"] = True
        self.assertTrue(self.run_verify(result=result))


if __name__ == "__main__":
    unittest.main()
