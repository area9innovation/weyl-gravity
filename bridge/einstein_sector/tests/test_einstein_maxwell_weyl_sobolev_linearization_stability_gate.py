from __future__ import annotations

import copy
import json
import unittest

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_sobolev_linearization_stability_gate import (
    ATLAS_OUTPUT,
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_atlas,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_sobolev_linearization_stability_gate import (
    IndependentSobolevGateVerificationError,
    verify_certificate,
)


class SobolevLinearizationStabilityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_and_exact_import_count(self) -> None:
        jsonschema.Draft202012Validator(self.schema).validate(self.payload)
        self.assertEqual(len(self.payload["provenance"]["imported_artifacts"]), 5)

    def test_p_primary_fixture_and_shell(self) -> None:
        witness = self.payload["closed_range_obstruction"]
        self.assertEqual(witness["spatial_fixture"]["ell"], 2)
        self.assertEqual(witness["spatial_fixture"]["k"], 0)
        self.assertEqual(witness["frequency_squared"], "16/3")

    def test_normalized_approximate_kernel_limit(self) -> None:
        n = sp.symbols("n", positive=True, integer=True)
        bound = sp.sympify(
            self.payload["closed_range_obstruction"]["approximate_kernel"]["upper_bound"],
            locals={"n": n},
        )
        self.assertEqual(sp.limit(bound, n, sp.oo), 0)

    def test_closed_range_fredholm_and_inverse_fail_closed(self) -> None:
        result = self.payload["functional_analytic_consequences"]
        self.assertFalse(result["closed_range"])
        self.assertFalse(result["fredholm"])
        self.assertFalse(result["bounded_generalized_inverse"])

    def test_finite_exponential_polynomial_theorem_survives(self) -> None:
        finite = self.payload["surviving_finite_harmonic_statements"]
        self.assertEqual(finite["finite_exponential_polynomial_surjectivity"], "CERTIFIED_UNCHANGED")
        self.assertFalse(finite["sobolev_sufficiency"])

    def test_cauchy_constraint_gate_remains_open(self) -> None:
        self.assertEqual(self.payload["cauchy_constraint_gate"]["status"], "OPEN_SEPARATE_PROBLEM")
        self.assertFalse(self.payload["classification"]["five_dimensional_sobolev_adjoint_cokernel_certified"])

    def test_decisive_mutation_lifts_the_original_shell_zero(self) -> None:
        mutation = self.payload["closed_range_obstruction"]["mutation_control"]
        self.assertEqual(mutation["value_at_original_shell"], "3/19")
        self.assertTrue(mutation["original_approximate_kernel_rejected"])

    def test_atlas_is_fail_closed(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("certificate has not been generated")
        atlas = build_atlas(self.payload, DEFAULT_OUTPUT)
        self.assertEqual(atlas["entries"][0]["descriptions"]["nonlinear"], "OBSTRUCTED")
        self.assertEqual(atlas["entries"][0]["descriptions"]["causal"], "NO_CERTIFIED_MAP")

    def test_schema_rejects_sobolev_promotion(self) -> None:
        mutation = copy.deepcopy(self.payload)
        mutation["classification"]["sobolev_linearization_stability_promoted"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutation)

    def test_committed_payload_and_independent_verifier(self) -> None:
        if not DEFAULT_OUTPUT.exists() or not ATLAS_OUTPUT.exists():
            self.skipTest("generated artifacts have not been written")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_independent_verifier_rejects_evidence_hash_mutation(self) -> None:
        if not DEFAULT_OUTPUT.exists() or not ATLAS_OUTPUT.exists():
            self.skipTest("generated artifacts have not been written")
        mutation = copy.deepcopy(json.loads(ATLAS_OUTPUT.read_text(encoding="utf-8")))
        mutation["entries"][0]["evidence"][0]["sha256"] = "0" * 64
        temp = ATLAS_OUTPUT.with_suffix(".mutation-test.json")
        try:
            temp.write_text(json.dumps(mutation), encoding="utf-8")
            with self.assertRaises(IndependentSobolevGateVerificationError):
                verify_certificate(DEFAULT_OUTPUT, temp)
        finally:
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
