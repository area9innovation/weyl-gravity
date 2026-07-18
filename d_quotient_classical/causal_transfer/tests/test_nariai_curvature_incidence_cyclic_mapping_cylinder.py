from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_curvature_incidence_cyclic_mapping_cylinder import build
from d_quotient_classical.causal_transfer.verify_nariai_curvature_incidence_cyclic_mapping_cylinder import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-cyclic-mapping-cylinder-v1.schema.json"


class NariaiCurvatureIncidenceCyclicMappingCylinderTests(unittest.TestCase):
    def setUp(self):
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_all_kernel_identities(self):
        checks = self.value["exact_checks"]
        for name in ("split_Q_squared", "prolonged_Q_squared", "split_odd_cyclic", "prolonged_odd_cyclic", "canonical_shear", "projection_inclusion_identity", "retract_identity", "homotopy_odd_cyclic"):
            self.assertTrue(checks[name], name)

    def test_locality_and_substitution(self):
        checks = self.value["exact_checks"]
        self.assertTrue(checks["no_inverse_operator_atoms"])
        self.assertTrue(checks["shifted_chain_substitution_exact"])
        self.assertTrue(checks["factorized_saddle_substitution_exact"])

    def test_independent_replay(self):
        verify()

    def test_retract_mutation_fails(self):
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["retract_identity"] = False
        with self.assertRaises(ValidationError): self.validator.validate(mutated)

    def test_endpoint_overpromotion_fails(self):
        mutated = deepcopy(self.value)
        mutated["flags"]["METRIC_BACH_ENDPOINT_CHAIN_EQUIVALENCE"] = True
        with self.assertRaises(ValidationError): self.validator.validate(mutated)


if __name__ == "__main__": unittest.main()
