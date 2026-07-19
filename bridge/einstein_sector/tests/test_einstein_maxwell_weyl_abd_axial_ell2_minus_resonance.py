"""Tests for the axial ell2 Einstein-minus global resonance theorem."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_abd_axial_ell2_minus_resonance import OUTPUT, build


class AxialEll2MinusGlobalResonanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_direct_source_inventory(self) -> None:
        self.assertEqual(set(self.value["direct_source"]["rows"]), {"a", "b", "d"})

    def test_nonzero_branch_zero_locus(self) -> None:
        self.assertEqual(self.value["bounded_zero_locus"]["nonzero_wave_branch"], "z!=0 implies a=b=d=0")

    def test_scope_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["other_parity_or_branch_classified"])
        self.assertFalse(self.value["classification"]["complete_bounded_cone_solved"])


if __name__ == "__main__":
    unittest.main()
