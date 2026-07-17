from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_branch_carrier_architecture_preflight import (
    OUTPUT,
    SCHEMA,
    build,
    validate,
)
from transfer.verify_berger_branch_carrier_architecture_preflight import verify


class BergerBranchCarrierArchitecturePreflightTests(unittest.TestCase):
    def test_certificate_reproduces_and_validates(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build())
        self.assertEqual(value, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)

    def test_selection_and_quantum_ordering_are_separate(self) -> None:
        value = build()
        selection = value["selection_verdict"]
        self.assertEqual(selection["preferred_first_attempt"], "rank_46_STF2_graph_carrier")
        self.assertFalse(selection["rank_46_is_quantum_prerequisite"])
        self.assertTrue(selection["rank_46_is_Paper_11_interpretation_followup"])
        self.assertTrue(value["claim_flags"]["RANK_46_CARRIER_IMPORTED"])
        self.assertFalse(value["claim_flags"]["BRANCH_PROJECTOR_ACCEPTED"])
        self.assertEqual(
            value["quantum_critical_path"]["ordered_gates"][0],
            "REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING",
        )

    def test_mapping_cylinder_is_reuse_library_not_adapter(self) -> None:
        option = build()["architecture_options"]["covariant_curvature_mapping_cylinder"]
        self.assertEqual(option["prolonged_rows"], 386)
        self.assertEqual(option["causal_endpoint_rows"], 30)
        self.assertIn("BERGER_BRANCH_ADAPTER_ABSENT", option["current_disposition"])

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "BRANCH_PROJECTOR_ACCEPTED",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(build())
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
