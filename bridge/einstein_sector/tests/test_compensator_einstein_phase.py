from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensator_einstein_phase


class CompensatorEinsteinPhaseTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        compensator_einstein_phase.verify_certificate()

    def test_constant_frame_generates_eh_and_consistent_lambda(self) -> None:
        result = compensator_einstein_phase.build_certificate()
        background = result["constant_background_theorem"]
        self.assertEqual(background["induced_eh_coefficient"], "c1=zeta v^2")
        self.assertIn("R=4 Lambda_eff", background["consistency_identity"])
        self.assertIn("lambda=0", background["flat_vacuum"])

    def test_compensator_is_stueckelberg_not_clock(self) -> None:
        result = compensator_einstein_phase.build_certificate()
        frame = result["weyl_frame_theorem"]
        coordination = result["scalar_clock_coordination"]
        self.assertIn("sets varphi to zero", frame["unitary_frame"])
        self.assertIn("no monotone relational time", coordination["why_not_a_clock"])
        self.assertEqual(coordination["imported_status"], "OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER")
        self.assertTrue(result["claim_flags"]["scalar_clock_vertical_slice_imported"])
        self.assertFalse(result["claim_flags"]["constant_compensator_is_monotone_clock"])

    def test_tt_pairing_is_repaired_but_extra_root_remains(self) -> None:
        result = compensator_einstein_phase.build_certificate()
        tt = result["flat_tt_factorization"]
        self.assertEqual(tt["branch_symplectic_normalizations"]["massless"], "K'(0)=c1/2=zeta v^2/2")
        self.assertEqual(len(tt["roots"]), 2)
        self.assertIn("opposite residues", tt["relative_signature"])
        self.assertTrue(result["claim_flags"]["extra_massive_spin2_branch_present"])
        self.assertFalse(result["claim_flags"]["full_theory_equals_pure_einstein_gravity"])

    def test_pure_weyl_limit_reproduces_degenerate_root(self) -> None:
        result = compensator_einstein_phase.build_certificate()
        self.assertIn("K->(alpha/2)y^2", result["flat_tt_factorization"]["pure_weyl_limit"])
        self.assertTrue(result["claim_flags"]["pure_weyl_limit_coalesces_and_pairing_vanishes"])

    def test_forged_causal_promotion_is_rejected(self) -> None:
        payload = compensator_einstein_phase.build_certificate()
        payload["claim_flags"]["massive_branch_causally_excluded"] = True
        with self.assertRaises(compensator_einstein_phase.CompensatorEinsteinPhaseError):
            compensator_einstein_phase._validate_contract(payload)

    def test_forged_scalar_clock_claim_is_rejected(self) -> None:
        payload = compensator_einstein_phase.build_certificate()
        payload["claim_flags"]["backreacted_or_composite_clock_model_constructed"] = True
        with self.assertRaises(compensator_einstein_phase.CompensatorEinsteinPhaseError):
            compensator_einstein_phase._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = compensator_einstein_phase.build_certificate()
        payload["verdict"] = "PURE_EINSTEIN"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(compensator_einstein_phase.CompensatorEinsteinPhaseError):
                compensator_einstein_phase.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
