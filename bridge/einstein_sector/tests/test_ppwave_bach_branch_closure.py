from __future__ import annotations

from copy import deepcopy
import unittest

from bridge.einstein_sector.ppwave_bach_branch_closure import (
    PPWaveClosureError,
    build_certificate,
    verify_payload,
)


class PPWaveBachBranchClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_exact_support_local_bach_identity(self) -> None:
        equations = self.payload["exact_field_equations"]
        self.assertTrue(equations["bach_is_exactly_linear_in_H"])
        self.assertEqual(equations["bach_equation"], "Delta_perp^2 H=0")

    def test_actual_branches_and_mixed_closure(self) -> None:
        branches = self.payload["branch_representatives"]
        self.assertTrue(branches["Einstein"]["Ricci_flat"])
        self.assertFalse(branches["extra_Weyl"]["Ricci_flat"])
        self.assertTrue(branches["extra_Weyl"]["Bach_flat"])
        self.assertTrue(branches["sum_is_exact_Bach_solution"])

    def test_restricted_q2_and_ell2_vanish(self) -> None:
        self.assertTrue(
            self.payload["restricted_nonlinear_tensor"][
                "q2_identically_zero_for_arbitrary_ppwave_profiles"
            ]
        )
        self.assertEqual(
            self.payload["transfer_disposition"]["restricted_ell2"],
            "pi_cl q2(iota_cl tensor iota_cl)=0",
        )

    def test_scope_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.payload)
        mutant["flags"]["FULL_SUPPORT_LOCAL_BV_Q2"] = True
        with self.assertRaisesRegex(PPWaveClosureError, "boundary crossed"):
            verify_payload(mutant)


if __name__ == "__main__":
    unittest.main()
