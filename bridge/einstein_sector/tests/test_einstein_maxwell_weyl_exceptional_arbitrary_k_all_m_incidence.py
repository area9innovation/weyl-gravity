from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence import (
    ATLAS,
    OUTPUT,
    build_certificate,
    verify_output,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence import (
    verify_certificate,
    verify_payload,
)


class ExceptionalArbitraryKAllMIncidenceTests(unittest.TestCase):
    def test_generated_artifacts_current(self) -> None:
        verify_output()

    def test_independent_verifier(self) -> None:
        verify_certificate()

    def test_exact_incidence_strata(self) -> None:
        value = build_certificate()
        self.assertEqual(
            [item["rank_Y"] for item in value["incidence_theorem"]["rank_strata"]],
            [3, 2, 1, 0],
        )
        self.assertEqual(
            value["incidence_theorem"]["necessary_and_sufficient_locked_carrier_incidence"],
            "conj(x_ax),conj(x_pol) belong to ker(Y)",
        )

    def test_atlas_remains_fail_closed(self) -> None:
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        mode_data = atlas["entries"][0]["mode_data"]
        self.assertEqual(mode_data["resonance"]["status"], "CERTIFIED")
        self.assertEqual(mode_data["taub_maps"]["status"], "OPEN")
        self.assertEqual(
            mode_data["second_order"]["bounded_or_finite_quasiperiodic"]["status"],
            "OPEN",
        )

    def test_rank_and_coefficient_mutations_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text(encoding="utf-8"))
        rank_mutation = copy.deepcopy(value)
        rank_mutation["representation_theorem"]["Hom_SO3_dimension"] = 2
        with self.assertRaises(AssertionError):
            verify_payload(rank_mutation)
        coefficient_mutation = copy.deepcopy(value)
        coefficient_mutation["all_m_functionals"]["axial_output"] = "R_ax(k)=0"
        with self.assertRaises(AssertionError):
            verify_payload(coefficient_mutation)


if __name__ == "__main__":
    unittest.main()
