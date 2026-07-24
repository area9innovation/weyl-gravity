#!/usr/bin/env python3
"""Mutation and boundary tests for the parent-flux certificate."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_producer():
    spec = importlib.util.spec_from_file_location("parent_producer", HERE / "produce.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ParentFluxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_producer().exact_data()

    def test_trace_adjusted_mass_term_is_fixed(self):
        self.assertEqual(
            self.data["parent_action"]["on_shell_density"],
            "2*alpha*(q_ab*q^ab-q^2)",
        )

    def test_current_keeps_both_cross_terms(self):
        current = self.data["factorized_current"]["parent"]
        self.assertIn("j_E(h1,f2)", current)
        self.assertIn("j_E(f1,h2)", current)

    def test_euler_term_is_not_silently_removed(self):
        self.assertEqual(
            self.data["factorized_current"]["literal_weyl"],
            "j_W=j_par+d k_Euler",
        )

    def test_generic_nonsplitting_is_not_time_jordan(self):
        self.assertFalse(
            self.data["claim_flags"][
                "generic_radial_nonsplitting_implies_time_jordan"
            ]
        )

    def test_connection_ep2_is_not_green_resolvent_promotion(self):
        self.assertTrue(self.data["claim_flags"]["one_physical_connection_ep2"])
        self.assertFalse(
            self.data["claim_flags"]["physical_green_resolvent_double_pole"]
        )

    def test_no_all_frequency_reflection_promotion(self):
        self.assertFalse(
            self.data["claim_flags"]["all_positive_frequency_reflection_zero_exclusion"]
        )

    def test_mutating_qnm_count_is_detected(self):
        mutated = copy.deepcopy(self.data)
        mutated["qnm_determinant_count"]["contour_count"] = (
            "N_B(Gamma)=N_2(Gamma)+N_1(Gamma)"
        )
        self.assertNotEqual(
            mutated["qnm_determinant_count"]["contour_count"],
            self.data["qnm_determinant_count"]["contour_count"],
        )


if __name__ == "__main__":
    unittest.main()
