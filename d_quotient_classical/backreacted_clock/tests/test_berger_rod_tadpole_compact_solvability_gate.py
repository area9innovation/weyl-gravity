from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_rod_tadpole_compact_solvability_gate as result


class BergerRodTadpoleCompactSolvabilityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = result.build()

    def test_constant_mode_is_exact(self) -> None:
        exact = self.payload["constant_mode_screen"]["exact_data"]
        self.assertEqual(exact["constant_hessian_rank"], 7)
        self.assertEqual(exact["augmented_rank"], 7)
        self.assertEqual(exact["adjoint_kernel_pairings"], ["0", "0", "0"])
        self.assertEqual(exact["equation_residual_H_Phi2_plus_q0"], ["0"] * 10)
        self.assertEqual(
            exact["canonical_Phi2"],
            ["496/63", "0", "0", "0", "-32/7", "0", "0", "-32/7", "0", "-256/63"],
        )

    def test_compact_verdict_remains_fail_closed(self) -> None:
        verdict = self.payload["binary_scientific_verdict"]
        self.assertEqual(verdict["verdict"], "INPUT_BLOCKED")
        self.assertIsNone(verdict["compact_rod_branch_exists"])
        self.assertIsNone(verdict["compact_rod_branch_obstructed"])
        self.assertFalse(self.payload["flags"]["COMPACT_TAUB_PROJECTION_COMPUTED"])

    def test_persisted_outputs(self) -> None:
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.payload)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.payload))

    def test_schema_and_semantic_mutations(self) -> None:
        schema = json.loads(result.SCHEMA_PATH.read_text())
        mutant = deepcopy(self.payload)
        mutant["binary_scientific_verdict"]["verdict"] = "BRANCH_EXISTS"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        for key in (
            "COMPACT_TAUB_PROJECTION_COMPUTED",
            "PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED",
            "PERTURBATIVE_BACKREACTED_ROD_BRANCH_OBSTRUCTED",
        ):
            mutant = deepcopy(self.payload)
            mutant["flags"][key] = True
            with self.assertRaises(AssertionError):
                result.verify(mutant)


if __name__ == "__main__":
    unittest.main()
