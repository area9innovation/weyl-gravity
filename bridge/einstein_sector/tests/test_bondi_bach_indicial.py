from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import bondi_bach_indicial


class BondiBachIndicialTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        bondi_bach_indicial.verify_certificate()

    def test_roots_and_boundary_roles(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        self.assertEqual(result["radiative_indicial_roots"], ["0", "1"])
        self.assertFalse(
            result["p1_einstein_compatible_falloff"]["boundary_metric_changed"]
        )
        self.assertTrue(result["p0_extra_bach_falloff"]["boundary_metric_changed"])
        self.assertEqual(
            result["kinematic_boundary_selection"]["status"],
            "KINEMATIC_LEADING_BRANCH_ONLY",
        )
        self.assertFalse(
            result["claim_flags"]["boundary_condition_preserved_by_causal_green_operators"]
        )
        self.assertEqual(
            result["series_recursions"]["leading_radiative_equation"],
            "4p(p-1) d_u^2 f_0=0",
        )
        self.assertEqual(
            result["series_recursions"]["machine_check"]["biwave_recurrence"],
            "PASS",
        )
        self.assertEqual(
            [term["field"] for term in result["series_recursions"]["wave_terms"]],
            ["d_u f_j", "f_(j-1)"],
        )

    def test_p1_is_compatible_not_identical_to_einstein(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        branch = result["p1_einstein_compatible_falloff"]
        self.assertEqual(branch["bach_next_recursion"], "4 d_u kappa=0")
        self.assertEqual(branch["einstein_subconstraint"], "kappa=0")
        self.assertIn("nonzero", branch["formal_extension"])
        self.assertTrue(
            result["claim_flags"]["p1_non_einstein_obstruction_identified"]
        )
        self.assertFalse(result["claim_flags"]["p1_falloff_proved_einstein"])
        self.assertFalse(
            result["claim_flags"]["fixed_boundary_metric_isolates_full_einstein_sector"]
        )

    def test_p0_wave_kernel_classification(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        branch = result["p0_extra_bach_falloff"]
        self.assertEqual(
            branch["wave_recursion_first_two_orders"],
            ["d_u f_0=0", "L f_0=0"],
        )
        self.assertTrue(result["claim_flags"]["p0_nonzero_L_wave_kernel_trivial"])

    def test_full_tensor_completion_is_fail_closed(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        gate = result["full_tensor_completion_gate"]
        self.assertEqual(gate["status"], "OPEN_FAIL_CLOSED")
        self.assertIn("linearized Bach rows", " ".join(gate["required_objects"]))
        self.assertFalse(
            result["claim_flags"]["full_tensor_bondi_recursion_constructed"]
        )

    def test_schema_and_generator_provenance_are_bound(self) -> None:
        result = bondi_bach_indicial.build_certificate()
        self.assertEqual(result["schema"], "pure-weyl-bondi-bach-indicial-v2")
        self.assertEqual(
            len(result["provenance"]["generator_sha256"]),
            64,
        )
        forged = json.loads(json.dumps(result))
        forged["provenance"]["generator_sha256"] = "0" * 64
        with self.assertRaises(bondi_bach_indicial.BondiBachIndicialError):
            bondi_bach_indicial._validate_contract(forged)

    def test_exact_single_term_coefficients(self) -> None:
        p, angular = bondi_bach_indicial.sp.symbols("p L")
        self.assertEqual(
            bondi_bach_indicial.biwave_coefficients(p, angular)[0],
            4 * p * (p - 1),
        )
        self.assertEqual(
            bondi_bach_indicial.biwave_coefficients(0, angular),
            (0, 0, angular * (angular - 2)),
        )

    def test_false_causal_promotion_is_rejected(self) -> None:
        payload = bondi_bach_indicial.build_certificate()
        payload["claim_flags"]["boundary_condition_preserved_by_causal_green_operators"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(bondi_bach_indicial.BondiBachIndicialError):
                bondi_bach_indicial.verify_certificate(path)

    def test_false_full_einstein_selection_is_rejected(self) -> None:
        payload = bondi_bach_indicial.build_certificate()
        payload["claim_flags"]["fixed_boundary_metric_isolates_full_einstein_sector"] = True
        with self.assertRaises(bondi_bach_indicial.BondiBachIndicialError):
            bondi_bach_indicial._validate_contract(payload)


if __name__ == "__main__":
    unittest.main()
