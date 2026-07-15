from __future__ import annotations

import unittest

import sympy as sp

from bridge.taub_moment_map.compact_d_charge import CompactCylinderDChargeAudit


class CompactCylinderDChargeTests(unittest.TestCase):
    def test_lowest_mode_counterexamples_are_exact(self) -> None:
        audit = CompactCylinderDChargeAudit.build(4)
        self.assertEqual(audit.mode("E", 2).reduced_charge_kernel, -1)
        self.assertEqual(audit.mode("A", 3).reduced_charge_kernel, sp.Rational(3, 2))
        self.assertEqual(audit.mode("L", 4).reduced_charge_kernel, 2)

    def test_both_chiralities_have_the_same_charge(self) -> None:
        audit = CompactCylinderDChargeAudit.build(5)
        for branch, energy in (("E", 2), ("A", 3), ("L", 4)):
            self.assertEqual(
                audit.mode(branch, energy, 1).reduced_charge_kernel,
                audit.mode(branch, energy, -1).reduced_charge_kernel,
            )

    def test_inventory_is_not_a_finite_module_claim(self) -> None:
        audit = CompactCylinderDChargeAudit.build(6)
        self.assertEqual(audit.dimension, 470)
        self.assertEqual(
            audit.all_energy_formula(), {"E": "-n/2", "A": "n/2", "L": "n/2"}
        )


if __name__ == "__main__":
    unittest.main()
