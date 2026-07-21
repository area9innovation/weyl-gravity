from __future__ import annotations

import copy
import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_bounded_cone_real_locus_gate import (
    ATLAS,
    OUTPUT,
    build_certificate,
    verify_output,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_global_bounded_cone_real_locus_gate import (
    verify_certificate,
    verify_payload,
)


class GlobalBoundedConeRealLocusGateTests(unittest.TestCase):
    def test_generated_outputs_current(self) -> None:
        verify_output()

    def test_independent_verifier(self) -> None:
        verify_certificate()

    def test_candidate18_is_fail_closed(self) -> None:
        value = build_certificate()
        self.assertEqual(value["selected_invariant_gate"]["candidate_index"], 18)
        self.assertFalse(
            value["classification"]["candidate18_complete_real_fixed_occupation_fibre_classified"]
        )
        self.assertFalse(value["classification"]["unrestricted_global_real_common_zero_classified"])

    def test_real_and_complex_carriers_are_not_conflated(self) -> None:
        value = build_certificate()
        gate = value["selected_invariant_gate"]
        self.assertEqual(gate["ambient_real_dimension"], 60)
        self.assertEqual(gate["complex_dimension"], 22)
        self.assertEqual(gate["real_minor_equations_total"], 40)
        self.assertFalse(value["classification"]["complex_variety_substituted_for_real_locus"])

    def test_atlas_stays_open(self) -> None:
        atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
        entry = atlas["entries"][0]
        self.assertEqual(entry["descriptions"]["nonlinear"], "OPEN")
        self.assertEqual(
            entry["mode_data"]["second_order"]["bounded_or_finite_quasiperiodic"]["status"],
            "OPEN",
        )

    def test_false_promotions_are_rejected(self) -> None:
        value = json.loads(OUTPUT.read_text(encoding="utf-8"))
        real_promotion = copy.deepcopy(value)
        real_promotion["classification"]["candidate18_complete_real_fixed_occupation_fibre_classified"] = True
        with self.assertRaises(AssertionError):
            verify_payload(real_promotion)
        global_promotion = copy.deepcopy(value)
        global_promotion["classification"]["unrestricted_global_real_common_zero_classified"] = True
        with self.assertRaises(AssertionError):
            verify_payload(global_promotion)


if __name__ == "__main__":
    unittest.main()
