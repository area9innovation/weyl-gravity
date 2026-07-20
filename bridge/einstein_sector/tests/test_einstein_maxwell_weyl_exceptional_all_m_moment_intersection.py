from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_all_m_moment_intersection import (
    ATLAS,
    OUTPUT,
    build_certificate,
    verify_output,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_exceptional_all_m_moment_intersection import (
    verify_certificate,
    verify_payload,
)


class ExceptionalAllMMomentIntersectionTests(unittest.TestCase):
    def test_generated_artifacts_current(self) -> None:
        verify_output()

    def test_independent_verifier(self) -> None:
        verify_certificate()

    def test_physical_intersection_is_origin_for_both_momentum_scopes(self) -> None:
        value = build_certificate()
        for theorem in value["physical_intersection_theorem"].values():
            self.assertEqual(
                theorem["physical_common_zero"],
                "x_ax,s=x_pol,s=Y_s=0 for every retained direction s",
            )

    def test_rank_one_complex_but_not_physical(self) -> None:
        value = build_certificate()
        disposition = value["complex_resonance_incidence"]["rank_one_disposition"]
        self.assertTrue(disposition["complex_resonance_incidence"].startswith("SURVIVES"))
        self.assertTrue(disposition["physical_Taub_slice"].startswith("ABSENT"))

    def test_atlas_is_fail_closed(self) -> None:
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        data = atlas["entries"][0]["mode_data"]
        self.assertEqual(data["taub_maps"]["status"], "CERTIFIED")
        self.assertEqual(data["second_order"]["bounded_or_finite_quasiperiodic"]["status"], "OBSTRUCTED")
        self.assertEqual(data["second_order"]["causal_retarded"]["status"], "NO_CERTIFIED_MAP")

    def test_sign_phase_and_rank_mutations_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text(encoding="utf-8"))
        sign_mutation = copy.deepcopy(value)
        sign_mutation["moment_maps"]["strict_sign"]["positive_coefficients"][3] = "22464<0"
        with self.assertRaises(AssertionError):
            verify_payload(sign_mutation)
        phase_mutation = copy.deepcopy(value)
        phase_mutation["classification"]["positive_and_negative_travel_directions_retained_separately"] = False
        with self.assertRaises(AssertionError):
            verify_payload(phase_mutation)
        rank_mutation = copy.deepcopy(value)
        rank_mutation["classification"]["rank_one_real_STF_stratum_absent"] = False
        with self.assertRaises(AssertionError):
            verify_payload(rank_mutation)


if __name__ == "__main__":
    unittest.main()
