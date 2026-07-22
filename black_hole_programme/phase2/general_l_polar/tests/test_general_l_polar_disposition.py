"""Mutation tests for the generic-ell polar disposition."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from black_hole_programme.phase2.general_l_polar import general_l_polar_disposition as producer
from black_hole_programme.phase2.general_l_polar import verify_general_l_polar_disposition as verifier


class GeneralLPolarDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(producer.OUTPUT.read_text(encoding="utf-8"))

    def reject(self, path: tuple[object, ...], value: object) -> None:
        candidate = verifier.mutated(self.payload, path, value)
        with self.assertRaises(Exception):
            verifier.verify_payload(candidate)

    def test_independent_verifier_accepts(self) -> None:
        verifier.verify_payload(self.payload)
        verifier.verify_atlas(self.payload)

    def test_generated_paths_exist(self) -> None:
        self.assertTrue(producer.OUTPUT.exists())
        self.assertTrue(producer.ATLAS.exists())

    def test_tensor_norm_mutation_rejected(self) -> None:
        self.reject(
            ("exact_symbolic_lambda_result", "harmonic_conventions", "integrated_norms_relative_to_NLambda", "STF_tensor"),
            "Lambda*(Lambda+2)/2",
        )

    def test_pivot_mutation_rejected(self) -> None:
        self.reject(
            ("exact_symbolic_lambda_result", "bianchi_cascade", "pivot_coefficients"),
            ["-Lambda/r**2", "-Lambda/r**2", "-Lambda/(2*r**2)"],
        )

    def test_operator_demotion_rejected(self) -> None:
        self.reject(("claim_flags", "generic_polar_operator_rows_certified"), False)

    def test_reconstruction_denominator_mutation_rejected(self) -> None:
        self.reject(
            ("exact_symbolic_lambda_result", "ricci_to_metric_reconstruction", "denominator_ledger", "pure_representation_factors"),
            ["Lambda"],
        )

    def test_literal_current_demotion_rejected(self) -> None:
        self.reject(("claim_flags", "generic_polar_literal_current_certified"), False)

    def test_depth2_pilot_demotion_rejected(self) -> None:
        self.reject(("claim_flags", "generic_polar_depth2_branch_pilot_certified"), False)

    def test_pivot_wall_promotion_rejected(self) -> None:
        self.reject(
            ("exact_symbolic_lambda_result", "bounded_sourced_lift_depth2_pilot", "rref_pivot_denominator_audit"),
            "NO_ADDITIONAL_WALLS",
        )

    def test_plain_package_import(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-c", "import black_hole_programme.phase2.general_l_polar.literal_current"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_slice_component_mutation_rejected(self) -> None:
        self.reject(("exact_symbolic_lambda_result", "literal_lee_wald_current", "component"), "F^r=omega^1")

    def test_carrier_power_mutation_rejected(self) -> None:
        self.reject(("exact_symbolic_lambda_result", "generic_carrier_asymptotics", "lambda_independent"), False)

    def test_ell2_promotion_rejected(self) -> None:
        self.reject(("claim_flags", "ell2_promoted_to_generic"), True)

    def test_axial_coupling_rejected(self) -> None:
        self.reject(("claim_flags", "axial_theorem_modified"), True)

    def test_timeout_obstruction_rejected(self) -> None:
        self.reject(("claim_flags", "timeout_called_obstruction"), True)

    def test_false_done_rejected(self) -> None:
        self.reject(("next_gate", "disposition"), "DONE")

    def test_import_hash_mutation_rejected(self) -> None:
        self.reject(("provenance", "imported_artifacts", 0, "sha256"), "0" * 64)


if __name__ == "__main__":
    unittest.main()
