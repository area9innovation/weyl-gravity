from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_quadratic_minimal_bv


class CompensatedQuadraticMinimalBVTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        compensated_quadratic_minimal_bv.verify_certificate()

    def test_invariant_field_map_splits_stueckelberg_coordinate(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        theorem = result["action_and_field_theorem"]
        self.assertEqual(theorem["field_map_determinant"], "det F=1/v")
        self.assertIn("rho is absent", theorem["quadratic_split"])
        self.assertIn("singular at v=0", theorem["chart_boundary"])

    def test_minimal_bv_differential_is_nilpotent_and_cyclic(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        theorem = result["minimal_bv_theorem"]
        self.assertIn("q^2=0", theorem["exact_identities"])
        self.assertIn("q(-p)^T Omega+Omega q(p)=0", theorem["exact_identities"])
        self.assertEqual(theorem["total_dimension"], 32)

    def test_weyl_doublet_has_exact_contraction(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        contraction = result["weyl_doublet_contraction"]
        self.assertEqual(len(contraction["contractible_coordinates"]), 4)
        self.assertIn("i pi_cl=1-q s-s q", contraction["identities"])
        self.assertIn("nondegenerate", contraction["pairing_restriction"])

    def test_generic_rank_fixture_is_not_promoted_to_cohomology(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        fixture = result["minimal_bv_theorem"]["generic_off_shell_fixture"]
        self.assertEqual(fixture["q_rank"], 16)
        self.assertIn("not an on-shell", fixture["interpretation"])
        self.assertFalse(result["claim_flags"]["on_shell_one_particle_cohomology_computed"])

    def test_boundary_divergence_is_retained_for_bfv(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        action = result["action_and_field_theorem"]
        self.assertIn("BFV lift must restore", action["boundary_rule"])

    def test_berger_clock_is_imported_but_not_conflated(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        clock = result["berger_clock_coordination"]
        self.assertEqual(clock["next_gate"], "TOTAL_BERGER_D_PRESYMPLECTIC_AUDIT")
        self.assertIn("contextual import only", clock["effect_on_this_theorem"])
        self.assertFalse(result["claim_flags"]["berger_total_covariant_D_charge_computed"])

    def test_classical_import_freeze_remains_open(self) -> None:
        result = compensated_quadratic_minimal_bv.build_certificate()
        self.assertEqual(
            result["lifecycle_boundary"]["next_gate"],
            "COMPENSATED_CLASSICAL_IMPORT_FREEZE",
        )
        self.assertFalse(result["claim_flags"]["classical_import_freeze_complete"])
        self.assertFalse(result["claim_flags"]["green_hyperbolic_complex_constructed"])

    def test_forged_freeze_promotion_is_rejected(self) -> None:
        payload = compensated_quadratic_minimal_bv.build_certificate()
        payload["claim_flags"]["classical_import_freeze_complete"] = True
        with self.assertRaises(compensated_quadratic_minimal_bv.CompensatedQuadraticMinimalBVError):
            compensated_quadratic_minimal_bv._validate_contract(payload)

    def test_forged_berger_D_verdict_is_rejected(self) -> None:
        payload = compensated_quadratic_minimal_bv.build_certificate()
        payload["claim_flags"]["berger_total_covariant_D_charge_computed"] = True
        with self.assertRaises(compensated_quadratic_minimal_bv.CompensatedQuadraticMinimalBVError):
            compensated_quadratic_minimal_bv._validate_contract(payload)

    def test_forged_certificate_is_rejected(self) -> None:
        payload = compensated_quadratic_minimal_bv.build_certificate()
        payload["verdict"] = "FULL_CLASSICAL_FREEZE"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(
                compensated_quadratic_minimal_bv.CompensatedQuadraticMinimalBVError
            ):
                compensated_quadratic_minimal_bv.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
