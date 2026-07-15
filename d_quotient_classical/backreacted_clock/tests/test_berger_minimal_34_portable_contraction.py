from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock.verify_berger_minimal_34_portable_contraction import (
    verify_certificate,
)


class BergerMinimal34PortableContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = verify_certificate()

    def test_complete_minimal_contraction(self) -> None:
        self.assertEqual(self.payload["row_layout"]["total_rows"], 34)
        self.assertEqual(self.payload["row_layout"]["degree_ranks"], [5, 12, 12, 5])
        self.assertTrue(self.payload["flags"]["BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS"])

    def test_semantic_name(self) -> None:
        semantics = self.payload["operator_semantics"]
        self.assertEqual(semantics["portable_name"], "classical_unary_q1")
        self.assertTrue(semantics["not_quantum_loop_operator"])

    def test_quantum_wishlist_remains_fail_closed(self) -> None:
        flags = self.payload["flags"]
        for key in (
            "BERGER_NONMINIMAL_COMPLETION",
            "CLASSICAL_SUPPORT_LOCAL_Q2",
            "BERGER_LOCAL_D_ACTION_EQUIVARIANT",
            "BERGER_GENERAL_KOSZUL_TATE_EXPORT",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "BERGER_HADAMARD_DATA",
        ):
            self.assertFalse(flags[key])


if __name__ == "__main__":
    unittest.main()
