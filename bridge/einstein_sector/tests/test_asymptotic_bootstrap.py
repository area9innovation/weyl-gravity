from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bridge.einstein_sector import asymptotic_bootstrap


class AsymptoticBootstrapTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        asymptotic_bootstrap.verify_certificate()

    def test_linearized_constraint_is_exact_and_full_claims_are_open(self) -> None:
        result = asymptotic_bootstrap.build_certificate()
        theorem = result["linearized_minkowski_theorem"]
        self.assertEqual(theorem["intertwining_defect"], [["0"] * 4, ["0"] * 4])
        self.assertEqual(theorem["bach_data_dimension_per_helicity"], 4)
        self.assertEqual(theorem["einstein_data_dimension_per_helicity"], 2)
        self.assertIn("also holds at q=0", theorem["algebraic_q_zero_extension"])
        self.assertTrue(result["claim_flags"]["flat_tt_bach_operator_derived"])
        self.assertTrue(result["claim_flags"]["linearized_minkowski_einstein_data_invariant"])
        self.assertTrue(
            result["claim_flags"]["bondi_bach_radiative_indicial_roots_classified"]
        )
        self.assertTrue(result["claim_flags"]["p0_boundary_metric_branch_identified"])
        self.assertTrue(
            result["claim_flags"][
                "fixed_boundary_metric_excludes_leading_p0_kinematically"
            ]
        )
        self.assertTrue(
            result["claim_flags"]["p1_same_falloff_bach_obstruction_identified"]
        )
        self.assertFalse(result["claim_flags"]["nonlinear_einstein_constraint_preserved"])
        self.assertFalse(result["claim_flags"]["helicity_two_scattering_space_recovered"])
        self.assertEqual(
            result["asymptotic_data_seed"]["radiative_class_rails"]
            ["soft_memory_extension"]["status"],
            "OPEN",
        )
        self.assertEqual(
            result["conformal_freedom_split"]["status"],
            "DISTINCTION_FIXED_BOUNDARY_INTERSECTION_OPEN",
        )
        self.assertEqual(
            result["bondi_bach_indicial_theorem"]["radiative_indicial_roots"],
            ["0", "1"],
        )
        self.assertEqual(
            result["bondi_bach_indicial_theorem"]["einstein_compatible_falloff"]
            ["einstein_subconstraint"],
            "kappa=0",
        )
        obligations = {row["id"]: row for row in result["obligation_status"]}
        self.assertEqual(obligations["AF-E4"]["status"], "PARTIAL")
        self.assertEqual(obligations["AF-E8"]["status"], "PARTIAL")

    def test_compact_cylinder_scope_is_required(self) -> None:
        original_load = asymptotic_bootstrap._load

        def forged_load(path: Path):
            payload = original_load(path)
            if path == asymptotic_bootstrap.INPUTS["cylinder_causal_transport"]:
                payload = copy.deepcopy(payload)
                payload["cylinder_specialization"]["cauchy_surface_compact"] = False
            return payload

        with patch.object(asymptotic_bootstrap, "_load", side_effect=forged_load):
            with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
                asymptotic_bootstrap.build_certificate()

    def test_indicial_causal_scope_is_required(self) -> None:
        original_load = asymptotic_bootstrap._load

        def forged_load(path: Path):
            payload = original_load(path)
            if path == asymptotic_bootstrap.INPUTS["bondi_bach_indicial"]:
                payload = copy.deepcopy(payload)
                payload["claim_flags"][
                    "boundary_condition_preserved_by_causal_green_operators"
                ] = True
            return payload

        with patch.object(asymptotic_bootstrap, "_load", side_effect=forged_load):
            with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
                asymptotic_bootstrap.build_certificate()

    def test_indicial_full_selection_promotion_is_rejected(self) -> None:
        original_load = asymptotic_bootstrap._load

        def forged_load(path: Path):
            payload = original_load(path)
            if path == asymptotic_bootstrap.INPUTS["bondi_bach_indicial"]:
                payload = copy.deepcopy(payload)
                payload["claim_flags"][
                    "fixed_boundary_metric_isolates_full_einstein_sector"
                ] = True
            return payload

        with patch.object(asymptotic_bootstrap, "_load", side_effect=forged_load):
            with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
                asymptotic_bootstrap.build_certificate()

    def test_false_scattering_promotion_is_rejected(self) -> None:
        payload = asymptotic_bootstrap.build_certificate()
        payload["claim_flags"]["helicity_two_scattering_space_recovered"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
                asymptotic_bootstrap.verify_certificate(path)

    def test_schema_contract_rejects_missing_obligation(self) -> None:
        payload = asymptotic_bootstrap.build_certificate()
        payload["obligation_status"].pop()
        with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
            asymptotic_bootstrap._validate_contract(payload)

    def test_schema_contract_rejects_forged_generator_hash(self) -> None:
        payload = asymptotic_bootstrap.build_certificate()
        payload["provenance"]["generator_sha256"] = "0" * 64
        with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
            asymptotic_bootstrap._validate_contract(payload)


if __name__ == "__main__":
    unittest.main()
