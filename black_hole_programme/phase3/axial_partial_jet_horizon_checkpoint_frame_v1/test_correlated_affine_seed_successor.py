#!/usr/bin/env python3
"""Tests for the content-addressed correlated seed successor."""
from __future__ import annotations

import json
import sys
import unittest
from fractions import Fraction

from . import correlated_affine_seed_successor as rail

sys.set_int_max_str_digits(0)


class CorrelatedAffineSeedSuccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(rail.RUN.read_text())

    def test_content_chain(self) -> None:
        self.assertTrue(
            rail.model_chain_valid(
                self.result["initial_model"], self.result["successor_model"]
            )
        )

    def test_coefficient_mutation_is_detected(self) -> None:
        mutant = json.loads(json.dumps(self.result["initial_model"]))
        mutant["polynomial_coefficients"][0]["values"][0] = "1"
        self.assertFalse(rail.model_content_valid(mutant))

    def test_shared_parameter_and_remainder(self) -> None:
        for key in ("initial_model", "successor_model"):
            model = self.result[key]
            self.assertTrue(
                model["dual_tau_state"][
                    "same_omega_parameter_for_both_rails"
                ]
            )
            self.assertEqual(
                model["shared_noise_domain"][
                    "independent_component_noise_symbols"
                ],
                0,
            )
            self.assertFalse(
                model["residual_norm_ball"]["componentwise_independent_boxes"]
            )

    def test_initial_pivot_is_exact(self) -> None:
        pivot = self.result["initial_model"]["pivot_constraints"]
        self.assertEqual(pivot["exact_base_pivot"], "1")
        self.assertEqual(pivot["exact_tangent_pivot"], "0")
        self.assertTrue(pivot["residual_zero_on_pivot_coordinates"])

    def test_successor_pivot_excludes_zero(self) -> None:
        lower = Fraction(
            self.result["successor_normalization"][
                "full_denominator_modulus_lower"
            ]
        )
        self.assertGreater(lower, 0)

    def test_scope_is_one_substep_only(self) -> None:
        flags = self.result["claim_flags"]
        self.assertTrue(flags["one_radial_taylor_step_certified"])
        self.assertFalse(flags["next_base_panel_completed"])
        self.assertFalse(flags["r4_reached"])
        self.assertFalse(flags["H4_certified"])


if __name__ == "__main__":
    unittest.main()
