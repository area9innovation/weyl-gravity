import json
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.backreacted_clock import berger_portable_coupled_64_unary_pairing_sdr as result


class BergerPortableCoupled64UnaryPairingSDRTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = result.build()

    def test_portable_carrier_and_persisted_outputs(self):
        result.verify(self.certificate)
        self.assertEqual(json.loads(result.CERTIFICATE_PATH.read_text()), self.certificate)
        self.assertEqual(result.REPORT_PATH.read_text(), result._report(self.certificate))
        self.assertEqual(self.certificate["full_complex"]["degree_ranks"], [6, 26, 26, 6])
        self.assertEqual(self.certificate["retained_complex"]["degree_ranks"], [4, 14, 14, 4])
        self.assertTrue(all(self.certificate["exact_checks"].values()))

    def test_Maxwell_rows_survive_the_algebraic_sdr(self):
        full = self.certificate["full_complex"]["component_rows"]
        retained = self.certificate["retained_complex"]["component_rows"]
        self.assertEqual([row["row_id"] for row in retained[26:]], [row["row_id"] for row in full[54:]])
        self.assertEqual(
            self.certificate["contraction"]["Maxwell_leg"],
            "identity; no Maxwell physical or gauge row is removed",
        )
        self.assertFalse(self.certificate["flags"]["MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO"])
        self.assertTrue(self.certificate["flags"]["CLASSICAL_MAXWELL_CAUSAL_TRANSFER_DEPENDENCY_PINNED"])
        self.assertFalse(
            self.certificate["flags"]["MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER"]
        )

    def test_schema_and_mutations(self):
        schema = json.loads(result.SCHEMA_PATH.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.certificate)
        mutant = deepcopy(self.certificate)
        mutant["flags"]["MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["retained_complex"]["degree_ranks"] = [3, 15, 14, 4]
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)

    def test_forbidden_promotions_rejected(self):
        for flag in (
            "MAXWELL_PHOTON_COHOMOLOGY_CONTRACTED_TO_ZERO",
            "MAXWELL_CAUSAL_CONTRACTION_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
            "TRANSFERRED_MIXED_VERTEX_ESTABLISHED_BY_THIS_LOCAL_CARRIER",
            "LORENTZIAN_CERTIFIED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.certificate)
            mutant["flags"][flag] = True
            with self.assertRaises(AssertionError):
                result.verify(mutant)


if __name__ == "__main__":
    unittest.main()
