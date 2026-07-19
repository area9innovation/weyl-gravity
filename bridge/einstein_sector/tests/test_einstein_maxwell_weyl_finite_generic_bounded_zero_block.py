from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_finite_generic_bounded_zero_block import OUTPUT, build


class FiniteGenericBoundedZeroBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = build()

    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.data)

    def test_homogeneous_mean_cokernel(self) -> None:
        block = self.data["homogeneous_bounded_operator"]
        self.assertEqual(block["zero_frequency_rank"], 0)
        self.assertEqual(len(block["bounded_dynamical_mean_cokernel_basis"]), 2)

    def test_source_map(self) -> None:
        pairings = self.data["source_pairings"]
        self.assertEqual(pairings["wilson_acceleration"]["value_on_complete_carrier"], "0")
        self.assertEqual(
            self.data["complete_static_output_decomposition"]["source_obstruction_map"],
            "(mu_H,mu_Px,mu_J1,mu_J2,mu_J3,R_c)",
        )

    def test_fail_closed_boundaries(self) -> None:
        flags = self.data["classification"]
        self.assertFalse(flags["generalized_zero_inputs_included"])
        self.assertFalse(flags["nonzero_frequency_resonance_ledger_classified"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
