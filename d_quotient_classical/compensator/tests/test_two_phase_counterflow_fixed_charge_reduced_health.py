import copy
import unittest

from d_quotient_classical.compensator import two_phase_counterflow_fixed_charge_reduced_health as producer


class FixedChargeReducedHealthTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self):
        producer.check()

    def test_relative_clock_is_removed(self):
        certificate, payload = producer.build()
        self.assertEqual(payload["derived_fixed_charge_fibre"]["quotient"]["relative_clock_dimension"], 0)
        self.assertFalse(certificate["terminal_verdict"]["positive_relative_clock_survives"])

    def test_clock_survival_mutation_is_rejected(self):
        certificate, payload = producer.build()
        mutant = copy.deepcopy(payload)
        mutant["derived_fixed_charge_fibre"]["quotient"]["relative_clock_dimension"] = 1
        with self.assertRaises(AssertionError):
            producer.validate(certificate, mutant)

    def test_raw_D_K_identification_mutation_is_rejected(self):
        certificate, payload = producer.build()
        mutant = copy.deepcopy(payload)
        mutant["charge_ledger"]["fixed_Q_rel_fibre"]["D_identified_with_K_before_reduction"] = True
        with self.assertRaises(AssertionError):
            producer.validate(certificate, mutant)


if __name__ == "__main__":
    unittest.main()
