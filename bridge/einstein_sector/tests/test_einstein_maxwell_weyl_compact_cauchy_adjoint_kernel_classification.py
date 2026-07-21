from __future__ import annotations

import copy
import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification import ATLAS_OUTPUT, DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification import IndependentAdjointKernelVerificationError, verify_certificate


class CompactCauchyAdjointKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_certificate()
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema(self):
        jsonschema.Draft202012Validator(self.schema).validate(self.payload)

    def test_exactly_five(self):
        self.assertEqual(self.payload["classification"]["adjoint_kernel_dimension"], 5)
        self.assertTrue(self.payload["classification"]["exactly_five_lifted_stabilizers"])

    def test_complete_strata(self):
        self.assertEqual(len(self.payload["harmonic_decomposition"]), 5)
        self.assertEqual(sum(x["real_dimension"] for x in self.payload["harmonic_decomposition"]), 5)

    def test_rotations_are_lifted(self):
        self.assertEqual(self.payload["exact_block_checks"]["rotation_bundle_lift_null_vector"], ["-1/P", "1"])

    def test_constant_u1_not_charge(self):
        self.assertFalse(self.payload["classification"]["constant_U1_is_sixth_taub_charge"])

    def test_preserves_semifredholm_boundary(self):
        self.assertFalse(self.payload["classification"]["two_sided_fredholm_claim"])

    def test_exceptional_ell2_rejected(self):
        self.assertEqual(self.payload["mutation_controls"]["insert_ell2_coexact"]["obstruction"], "lambda-2=4")

    def test_schema_rejects_six(self):
        mutated = copy.deepcopy(self.payload)
        mutated["classification"]["adjoint_kernel_dimension"] = 6
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.schema).validate(mutated)

    def test_generated_payload_and_independent_verifier(self):
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_atlas_hash_mutation(self):
        mutated = copy.deepcopy(json.loads(ATLAS_OUTPUT.read_text(encoding="utf-8")))
        mutated["entries"][0]["evidence"][0]["sha256"] = "0" * 64
        temp = ATLAS_OUTPUT.with_suffix(".mutation-test.json")
        try:
            temp.write_text(json.dumps(mutated), encoding="utf-8")
            with self.assertRaises(IndependentAdjointKernelVerificationError):
                verify_certificate(DEFAULT_OUTPUT, temp)
        finally:
            temp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
