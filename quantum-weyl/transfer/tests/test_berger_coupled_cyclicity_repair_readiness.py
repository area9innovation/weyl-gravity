from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError
from local_bv.schema_validation import validate_instance
from transfer.berger_coupled_cyclicity_repair_acceptance import INPUT_SCHEMA, _classify, evaluate
from transfer.berger_coupled_cyclicity_repair_readiness import ACCEPTED_FIXTURE, FIXTURE, HERE, build
from transfer.berger_coupled_cyclicity_repair_readiness_certificate import OUTPUT
from transfer.verify_berger_coupled_cyclicity_repair_readiness import SCHEMA, verify


class BergerCoupledCyclicityRepairReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.fixture, cls.accepted_fixture = build()

    def test_real_obstructed_baseline_is_rejected(self) -> None:
        result = evaluate(self.fixture)
        self.assertEqual(result["verdict"], "REJECTED_EXACT_ALGEBRAIC_DEFECT")
        diagnostics = result["diagnostics"]
        self.assertEqual(diagnostics["full_q1_q2_defect_count"], 0)
        self.assertEqual(diagnostics["full_cyclicity_defect_count"], 1234)
        self.assertEqual(diagnostics["retained_q1_q2_defect_count"], 0)
        self.assertEqual(diagnostics["retained_cyclicity_defect_count"], 953)

    def test_acceptance_predicate_is_binary_and_fail_closed(self) -> None:
        result = evaluate(self.accepted_fixture)
        self.assertEqual(result["verdict"], "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR")
        diagnostics = result["diagnostics"]
        self.assertEqual(diagnostics["full_overlay_coefficient_count"], 1890)
        self.assertEqual(diagnostics["retained_transfer_coefficient_count"], 1474)
        self.assertEqual(_classify(diagnostics), "ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR")
        diagnostics = deepcopy(diagnostics)
        diagnostics["retained_cyclicity_defect_count"] = 1
        self.assertEqual(_classify(diagnostics), "REJECTED_EXACT_ALGEBRAIC_DEFECT")

    def test_manifest_mutations_are_rejected(self) -> None:
        schema = json.loads(INPUT_SCHEMA.read_text())
        mutant = deepcopy(self.fixture)
        mutant["classical_commit"] = 1.5
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.fixture)
        mutant["artifacts"]["carrier"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            evaluate(mutant)
        mutant = deepcopy(self.fixture)
        mutant["artifacts"]["carrier"]["path"] = mutant["artifacts"]["coupled_q2_payload"]["path"]
        with self.assertRaises(ValueError):
            evaluate(mutant)

    def test_persisted_outputs_and_strict_schemas(self) -> None:
        certificate, fixture, accepted_fixture = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        self.assertEqual(json.loads(FIXTURE.read_text()), fixture)
        self.assertEqual(json.loads(ACCEPTED_FIXTURE.read_text()), accepted_fixture)
        self.assertFalse(validate_instance(certificate, json.loads(SCHEMA.read_text())))
        self.assertFalse(validate_instance(fixture, json.loads(INPUT_SCHEMA.read_text())))
        self.assertFalse(validate_instance(accepted_fixture, json.loads(INPUT_SCHEMA.read_text())))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build()[0])


if __name__ == "__main__":
    unittest.main()
