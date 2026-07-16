from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_operator import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_operator import verify_certificate as verify_independently
import bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_operator as independent_verifier


class AxialOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_noether_and_adjoint_rails(self) -> None:
        self.assertTrue(self.payload["ungauged_Noether_lift"]["Noether_identities_verified"])
        self.assertTrue(self.payload["operator_algebra"]["formal_self_adjoint"])
        self.assertTrue(self.payload["rails"]["source_image_annihilation_replayed"])

    def test_invariant_factors_and_extra_quotient(self) -> None:
        factors = self.payload["operator_algebra"]["Smith_invariant_factors_over_F_omega"]
        self.assertEqual(factors[:2], ["1", "1"])
        self.assertEqual(self.payload["source_and_extra_modules"]["canonical_extra_quotient_away_from_resultant"], "Q_extra_ax=(F[omega]/(p))^2")
        self.assertEqual(self.payload["source_and_extra_modules"]["geometric_multiplicity_on_generic_extra_root"], 2)

    def test_particle_claim_remains_fail_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["extra_particle_certified"])
        self.assertFalse(self.payload["rails"]["off_shell_local_Green_current_verified"])
        self.assertFalse(self.payload["rails"]["full_Einstein_extra_Lee_Wald_matrix_verified"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])

    def test_extra_factor_mutation_is_rejected(self) -> None:
        mutated = json.loads(DEFAULT_OUTPUT.read_text())
        mutated["operator_algebra"]["Smith_invariant_factors_over_F_omega"][2] = "1"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(mutated))
            with mock.patch.object(independent_verifier, "CERTIFICATE", path):
                with self.assertRaises(AssertionError):
                    independent_verifier.verify_certificate()


if __name__ == "__main__":
    unittest.main()
