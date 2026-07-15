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
        self.assertTrue(result["claim_flags"]["linearized_minkowski_einstein_data_invariant"])
        self.assertFalse(result["claim_flags"]["nonlinear_einstein_constraint_preserved"])
        self.assertFalse(result["claim_flags"]["helicity_two_scattering_space_recovered"])

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

    def test_false_scattering_promotion_is_rejected(self) -> None:
        payload = asymptotic_bootstrap.build_certificate()
        payload["claim_flags"]["helicity_two_scattering_space_recovered"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(asymptotic_bootstrap.AsymptoticBootstrapError):
                asymptotic_bootstrap.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
