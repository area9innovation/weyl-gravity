from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_nonzero_characteristic_snapshot as snapshot


class CompensatedNonzeroCharacteristicSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = snapshot.build_certificate()

    def test_canonical_certificate_is_current(self) -> None:
        actual = json.loads(snapshot.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(actual, self.result)

    def test_generic_fiber_is_acyclic(self) -> None:
        self.assertEqual(
            self.result["branches"]["generic"]["cohomology_dimensions"],
            {"-1": 0, "0": 0, "1": 0, "2": 0},
        )

    def test_null_fiber_has_two_field_and_two_antifield_classes(self) -> None:
        branch = self.result["branches"]["massless"]
        self.assertEqual(branch["cohomology_dimensions"], {"-1": 0, "0": 2, "1": 2, "2": 0})
        self.assertEqual(branch["pairing_rank"], 4)
        self.assertEqual(branch["plus_contraction"]["inclusion"]["shape"], [32, 4])

    def test_second_root_has_five_field_and_five_antifield_classes(self) -> None:
        branch = self.result["branches"]["second_root"]
        self.assertEqual(branch["cohomology_dimensions"], {"-1": 0, "0": 5, "1": 5, "2": 0})
        self.assertEqual(branch["pairing_rank"], 10)
        self.assertEqual(branch["parameters"]["p_squared"], -1)

    def test_zero_fiber_is_ledgered_not_promoted(self) -> None:
        ledger = self.result["zero_momentum_ledger"]
        self.assertEqual(ledger["fiber_cohomology_dimensions"], {"-1": 4, "0": 10, "1": 10, "2": 4})
        self.assertEqual(ledger["status"], "RECORDED_NOT_PROMOTED")
        self.assertFalse(self.result["claim_flags"]["zero_momentum_global_modes_classified"])

    def test_odd_bv_pairing_is_not_promoted_to_physical_symplectic_form(self) -> None:
        self.assertIn("at -p", self.result["domain"]["formal_adjoint_pairing_rule"])
        self.assertFalse(self.result["claim_flags"]["physical_cauchy_symplectic_pairing_computed_here"])
        self.assertFalse(self.result["claim_flags"]["ordinary_graviton_hilbert_space_constructed"])

    def test_global_classical_freeze_remains_open(self) -> None:
        self.assertFalse(self.result["claim_flags"]["classical_import_freeze_complete"])
        self.assertEqual(
            self.result["result_state"],
            "SCOPED_EXACT_SNAPSHOT_CERTIFIED_GLOBAL_CLASSICAL_FREEZE_OPEN",
        )

    def test_forged_global_freeze_is_rejected_by_canonical_comparison(self) -> None:
        payload = json.loads(json.dumps(self.result))
        payload["claim_flags"]["classical_import_freeze_complete"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(snapshot.CharacteristicSnapshotError):
                snapshot.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
