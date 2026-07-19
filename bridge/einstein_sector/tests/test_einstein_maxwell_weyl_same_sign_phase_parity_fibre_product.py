import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_same_sign_phase_parity_fibre_product import OUTPUT, build


class SameSignPhaseParityFibreProductTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_exact_formula_does_not_promote_real_components(self) -> None:
        flags = build()["classification"]
        self.assertTrue(flags["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"])
        self.assertTrue(flags["all_relative_phases_and_both_parities_retained_in_formula"])
        self.assertFalse(flags["all_six_real_hermitian_phase_parity_intersections_decomposed"])


if __name__ == "__main__":
    unittest.main()
