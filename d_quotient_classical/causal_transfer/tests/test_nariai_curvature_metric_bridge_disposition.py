from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.causal_transfer.nariai_curvature_metric_bridge_disposition import build, validate
from d_quotient_classical.causal_transfer.verify_nariai_curvature_metric_bridge_disposition import verify


class NariaiCurvatureMetricBridgeDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_independent_replay(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())

    def test_rejected_and_selected_carriers_are_distinct(self) -> None:
        self.assertEqual(self.value["rejected_direct_bridge"]["status"], "OBSTRUCTED")
        self.assertEqual(self.value["authoritative_same_background_bridge"]["status"], "CERTIFIED")
        self.assertEqual(self.value["bridge_disposition"]["direct_incidence_cylinder_to_metric_map"], "NO_CERTIFIED_MAP")

    def test_normalized_obstruction_is_retained(self) -> None:
        self.assertEqual(self.value["rejected_direct_bridge"]["normalized_lower_bound"], "6-1=5 missing noncontractible reducibility directions")
        self.assertFalse(self.value["rejected_direct_bridge"]["equation_identity_only_contractible_repair_sufficient"])

    def test_overclaims_are_rejected(self) -> None:
        for flag in (
            "NORMAL_TRACTOR_CYLINDER_METRIC_BRIDGE",
            "NORMAL_TRACTOR_CYLINDER_METRIC_QUASI_ISOMORPHISM",
            "OPEN_BACH_FLAT_METRIC_PARENT_BRIDGE",
            "NONLINEAR_EXTENSION",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
