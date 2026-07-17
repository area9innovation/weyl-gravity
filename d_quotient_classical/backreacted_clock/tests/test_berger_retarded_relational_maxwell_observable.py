import json
import unittest

from d_quotient_classical.backreacted_clock import berger_retarded_relational_maxwell_observable as result


class RetardedRelationalObservableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = result.build()

    def test_retarded_redshift(self):
        self.assertTrue(self.payload["retarded_mode_preparation"]["actual_retarded_signal"])
        self.assertEqual(self.payload["relational_redshift"]["one_plus_z"], "2")

    def test_cutoff_source_is_exact_and_conserved(self):
        audit = self.payload["retarded_mode_preparation"]["exact_exterior_form_audit"]
        self.assertEqual(audit["Lorenz_three_form_components"], {})
        self.assertEqual(audit["current_closure_components"], {})
        self.assertEqual(audit["coefficient_matrix_determinant"], "-4*sqrt(10)/3")
        self.assertTrue(audit["nonzero_for_nonconstant_switch"])

    def test_preparation_support_and_D_equivariance_are_scoped(self):
        preparation = self.payload["retarded_mode_preparation"]
        self.assertEqual(preparation["support_category"], "SPATIALLY_GLOBAL_SPACETIME_COMPACT")
        switch = preparation["clock_dressed_switch_equivariance"]
        self.assertEqual(switch["equivariance_defect"], "0")
        self.assertFalse(switch["fixed_label_invariance"])

    def test_reduced_dynamics(self):
        block = self.payload["reduced_symplectic_dynamics"]
        self.assertEqual(block["poisson_bracket"], "{x,y}=-1/(32*pi**2)")
        self.assertTrue(block["nontrivial_tau_evolution"])
        self.assertEqual(
            self.payload["D_gauge_relational_evolution"]["bracket_scope"],
            "REDUCED_PROBE_MODE_POISSON_NOT_FULL_APPARATUS_DIRAC",
        )
        self.assertFalse(self.payload["flags"]["BERGER_FULL_APPARATUS_DIRAC_BRACKET"])

    def test_periodic_clock_is_lifted(self):
        clock = self.payload["periodic_clock_and_crossings"]
        self.assertFalse(clock["rotation_is_identity"])
        self.assertTrue(clock["repeated_crossings_handled"])
        self.assertIn("n in Z", clock["lifted_label"])

    def test_D_gauge_does_not_erase_relational_change(self):
        audit = self.payload["D_gauge_relational_evolution"]
        self.assertIn("delta_D O_A", audit["observable_invariance"])
        self.assertIn("nonzero", audit["family_evolution"])

    def test_localized_gate_stops_at_mixed_order(self):
        obstruction = self.payload["localized_apparatus_obstruction"]
        self.assertEqual(obstruction["first_missing_order"], "r*kappa=epsilon_R^2*kappa")
        self.assertFalse(self.payload["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"])

    def test_mutation_guard(self):
        mutant = json.loads(json.dumps(self.payload))
        mutant["flags"]["BERGER_LOCALIZED_EMITTER_RECEIVER_OBSERVABLE"] = True
        with self.assertRaises(AssertionError):
            result.verify(mutant)


if __name__ == "__main__":
    unittest.main()
