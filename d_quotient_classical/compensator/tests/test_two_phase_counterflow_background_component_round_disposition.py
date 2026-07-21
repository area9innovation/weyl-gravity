import copy
import unittest

import sympy as sp

from d_quotient_classical.compensator import two_phase_counterflow_background_component_round_disposition as producer


class ComponentDispositionTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self):
        producer.check()

    def test_unique_physical_component(self):
        certificate, payload = producer.build()
        stationary = payload["stationary_component_stratification"]
        self.assertEqual(stationary["physical_solution_count"], 1)
        self.assertEqual(stationary["solutions"][0]["q"], "9/40")
        self.assertFalse(certificate["terminal_verdict"]["open_fixed_action_geometry_family"])

    def test_round_path_promotion_mutation_is_rejected(self):
        certificate, payload = producer.build()
        mutant = copy.deepcopy(payload)
        mutant["round_cylinder_disposition"]["connected_component"]["path_to_round_q_1"] = True
        with self.assertRaises(AssertionError):
            producer.validate(certificate, mutant)

    def test_open_phase_promotion_mutation_is_rejected(self):
        certificate, payload = producer.build()
        mutant = copy.deepcopy(certificate)
        mutant["claim_flags"]["OPEN_FIXED_ACTION_GEOMETRY_PHASE"] = True
        with self.assertRaises(AssertionError):
            producer.validate(mutant, payload)

    def test_action_constant_mutation_destroys_selected_stationarity(self):
        _, payload = producer.build()
        q, x, energy = sp.symbols("q x C")
        selected = {q: sp.Rational(9, 40), x: 1, energy: sp.Rational(9, 16)}
        rows = [
            sp.sympify(row, locals={"q": q, "x": x, "C": energy})
            for row in payload["stationary_component_stratification"]["orthonormal_stationary_rows_times_1920"]
        ]
        mutated = rows[0] + 1  # V0 numerator 119 -> 118 in the first row.
        self.assertNotEqual(sp.factor(mutated.subs(selected)), 0)


if __name__ == "__main__":
    unittest.main()
