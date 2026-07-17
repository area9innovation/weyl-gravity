from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock.berger_extended_rod_memory_maxwell_unary_gate import (
    OUTPUT,
    SCHEMA,
    build,
    memory_maxwell_template,
    rod_stress_witness,
    DETECTOR_INPUT,
)
from d_quotient_classical.backreacted_clock.verify_berger_extended_rod_memory_maxwell_unary_gate import verify


class BergerExtendedRodMemoryMaxwellUnaryGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_declared_rods_have_exact_nonzero_stress(self) -> None:
        witness = rod_stress_witness(json.loads(DETECTOR_INPUT.read_text()))
        self.assertEqual(witness["energy_density_T00"], "3/2")
        self.assertEqual(
            witness["stress_tensor"],
            [["3/2", "0", "0", "0"], ["0", "-1/2", "0", "0"], ["0", "0", "-1/2", "0"], ["0", "0", "0", "-1/2"]],
        )

    def test_memory_maxwell_retarded_formula_is_exact(self) -> None:
        template = memory_maxwell_template()
        self.assertEqual(template["left_inverse_defect_count"], 0)
        self.assertEqual(template["right_inverse_defect_count"], 0)
        self.assertTrue(template["formal_self_adjoint"])

    def test_gate_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["ROD_TADPOLE_EXACT_NONZERO"])
        self.assertTrue(flags["MEMORY_MAXWELL_RETARDED_BLOCK_FORMULA_PROVED"])
        self.assertFalse(flags["EXTENDED_APPARATUS_Q1_CERTIFIED"])
        self.assertFalse(flags["EXTENDED_RETARDED_GREEN_CERTIFIED"])
        self.assertEqual(
            self.value["next_gate"],
            "EXPORT_GLOBAL_ROD_Q0_AND_COMPACT_ADJOINT_KERNEL_BEFORE_BACKREACTED_BACKGROUND",
        )

    def test_strict_schema_and_persisted_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(json.loads(OUTPUT.read_text()), self.value)
        mutant = deepcopy(self.value)
        mutant["unexpected"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
