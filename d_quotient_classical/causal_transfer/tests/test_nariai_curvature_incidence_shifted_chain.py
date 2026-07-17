from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_curvature_incidence_shifted_chain import build
from d_quotient_classical.causal_transfer.verify_nariai_curvature_incidence_shifted_chain import verify


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-curvature-incidence-shifted-chain-v1.schema.json"


class NariaiCurvatureIncidenceShiftedChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = build()
        self.validator = Draft202012Validator(json.loads(SCHEMA.read_text()))

    def test_shifted_chain_and_saddle(self) -> None:
        checks = self.value["exact_checks"]
        self.assertTrue(checks["M_I_equals_minus_Phi1_K"])
        self.assertEqual(checks["shifted_chain_defect_nonzero_entries"], 0)
        self.assertEqual(checks["factorized_saddle_lower_defect_nonzero_entries"], 0)
        self.assertEqual(checks["factorized_saddle_upper_defect_nonzero_entries"], 0)

    def test_adjoint_replay_gate_is_scoped(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["pbw_parent_adjoint_replay_defect_rank"], 60)
        self.assertEqual(checks["pbw_parent_adjoint_replay_defect_nonzero_entries"], 60)
        self.assertFalse(self.value["flags"]["PARENT_FORMAL_SELF_ADJOINTNESS_NO_GO"])

    def test_independent_replay(self) -> None:
        verify()

    def test_witness_mutation_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_checks"]["pbw_parent_adjoint_replay_normalized_witness_value"] = "0"
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)

    def test_cyclic_cone_overpromotion_fails(self) -> None:
        mutated = deepcopy(self.value)
        mutated["flags"]["CYCLIC_CURVATURE_INCIDENCE_MAPPING_CONE"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(mutated)


if __name__ == "__main__":
    unittest.main()
