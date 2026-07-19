from __future__ import annotations

import json
import unittest

from bridge.einstein_sector import einstein_maxwell_weyl_complete_global_twist_fixed_ell_bounded_cone as theorem


class CompleteGlobalTwistFixedEllTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(theorem.OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_successor_is_acyclic(self) -> None:
        self.assertTrue(self.value["acyclic_dependency_audit"]["successor_is_separate"])
        self.assertTrue(self.value["acyclic_dependency_audit"]["successor_absent_from_transitive_predecessors"])
        self.assertGreater(self.value["acyclic_dependency_audit"]["transitive_dependency_edge_count"], 0)

    def test_union_complete(self) -> None:
        self.assertTrue(self.value["complete_bounded_zero_locus"]["union_is_necessary_and_sufficient"])

    def test_wave_stratum(self) -> None:
        wave = self.value["complete_bounded_zero_locus"]["wave_stratum"]
        self.assertIn("a=b=d=Q_e=B=0", wave)
        self.assertIn("c,W_x,A arbitrary", wave)

    def test_pairwise_coverage(self) -> None:
        self.assertEqual(set(self.value["pairwise_sufficiency"]), {"wave_wave", "A_wave", "c_wave", "W_x_wave", "static_pairs", "assembly"})

    def test_larger_scopes_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["finite_multi_ell_twist_cone_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
