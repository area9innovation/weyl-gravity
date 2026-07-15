from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_sourced_defect_chain_map as chain_map


class CompensatedSourcedDefectChainMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = chain_map.build_certificate()

    def test_canonical_certificate_is_current(self) -> None:
        actual = json.loads(chain_map.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(actual, self.result)

    def test_obstruction_and_defect_squares_commute(self) -> None:
        theorem = self.result["chain_map_theorem"]
        self.assertEqual(
            theorem["obstruction_square"],
            "W_B Q_ext = diag((p_squared/2)I4,0) W_source",
        )
        self.assertEqual(
            theorem["defect_square"],
            "div Delta = -(1/c1) projection_div W_source",
        )
        self.assertTrue(self.result["claim_flags"]["bach_obstruction_chain_map_exact"])
        self.assertTrue(self.result["claim_flags"]["einstein_defect_chain_map_exact"])

    def test_full_sourced_residual_is_reconstructed(self) -> None:
        theorem = self.result["chain_map_theorem"]
        self.assertIn("E_EW=", theorem["residual_identity"])
        self.assertEqual(
            theorem["same_source_closure"],
            "Delta=0 is Einstein--Weyl on shell if and only if Q(T)=0",
        )

    def test_ward_cycles_are_not_generically_compatible(self) -> None:
        generic = self.result["compatible_source_fibers"]["generic"]
        self.assertEqual(generic["ward_cycle_dimension"], 6)
        self.assertEqual(generic["compatible_source_dimension"], 1)
        self.assertFalse(self.result["claim_flags"]["arbitrary_ward_cycle_is_einstein_compatible"])

    def test_null_compatible_source_kernel_is_exact(self) -> None:
        null = self.result["compatible_source_fibers"]["null"]
        self.assertEqual(null["ward_cycle_dimension"], 6)
        self.assertEqual(null["compatible_source_dimension"], 5)
        self.assertEqual(null["compatible_source_inclusion"]["shape"], [11, 5])

    def test_zero_symbol_is_only_a_fiber_ledger(self) -> None:
        zero = self.result["compatible_source_fibers"]["zero"]
        self.assertEqual(zero["compatible_source_dimension"], 10)
        self.assertEqual(zero["name"], "zero_symbol_ledger")
        self.assertIn("symbol fibers", self.result["scope_guards"][1])

    def test_external_source_complex_is_not_promoted_to_matter_bv(self) -> None:
        classification = self.result["classification"]
        self.assertIn("no declared kinetic equations", classification["not_a_bv_complex_reason"])
        self.assertFalse(self.result["claim_flags"]["matter_inclusive_bv_complex_constructed"])
        self.assertFalse(self.result["claim_flags"]["berger_matter_bv_lift_constructed"])
        self.assertFalse(self.result["claim_flags"]["lorentzian_causal_claim"])

    def test_berger_minimal_sdr_is_context_only(self) -> None:
        self.assertTrue(self.result["claim_flags"]["berger_minimal_clock_sdr_imported"])
        self.assertIn("eight-row", self.result["classification"]["berger_context"])
        self.assertIn("retained 26-row", self.result["classification"]["berger_context"])
        self.assertFalse(self.result["claim_flags"]["berger_matter_bv_lift_constructed"])

    def test_forged_matter_bv_promotion_is_rejected(self) -> None:
        payload = json.loads(json.dumps(self.result))
        payload["claim_flags"]["matter_inclusive_bv_complex_constructed"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(chain_map.SourcedDefectChainMapError):
                chain_map.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
