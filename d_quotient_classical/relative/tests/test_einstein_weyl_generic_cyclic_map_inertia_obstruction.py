from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.relative.einstein_weyl_generic_cyclic_map_inertia_obstruction import build, validate
from d_quotient_classical.relative.verify_einstein_weyl_generic_cyclic_map_inertia_obstruction import verify


class GenericCyclicMapInertiaObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_both_parities_have_inertia_mismatch(self) -> None:
        for row in self.value["exact_inertia_blocks"].values():
            self.assertEqual(row["Einstein_inertia_lambda_ge_6"], [2, 0])
            self.assertEqual(row["restricted_Weyl_inertia_lambda_ge_6"], [1, 1])

    def test_honest_reformulations_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["noncyclic_off_shell_relative_triangle_obstructed"])
        self.assertFalse(classification["pairing_changed_relative_triangle_obstructed"])
        self.assertFalse(classification["exceptional_or_global_off_shell_maps_classified"])

    def test_overclaim_mutations_fail(self) -> None:
        for name in (
            "corrected_nonidentity_standard_pairing_map_exists_generic",
            "declared_chain_homotopy_cyclic_resolution_exists_generic",
            "standard_pairing_all_sector_cyclic_triangle_possible",
            "noncyclic_off_shell_relative_triangle_obstructed",
            "pairing_changed_relative_triangle_obstructed",
            "exceptional_or_global_off_shell_maps_classified",
            "Lorentzian_causal_or_quantum_claim",
        ):
            mutant = deepcopy(self.value)
            mutant["classification"][name] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
