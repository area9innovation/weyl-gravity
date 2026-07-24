#!/usr/bin/env python3
"""Mutation tests for parent-resolvent and Krein boundaries."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_producer():
    spec = importlib.util.spec_from_file_location("resolvent_producer", HERE / "produce.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ParentResolventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_producer().exact_data()

    def test_metric_block_order_is_fixed(self):
        self.assertIn(
            "E^-1*A*E^-1",
            self.data["parent_resolvent"]["metric_block"],
        )

    def test_physical_pole_promotion_fails(self):
        self.assertFalse(
            self.data["claim_flags"]["physical_qnm_double_pole_established"]
        )

    def test_ringdown_promotion_fails(self):
        self.assertFalse(
            self.data["claim_flags"]["generalized_ringdown_established"]
        )

    def test_rw_simplicity_gate_is_open(self):
        self.assertFalse(
            self.data["claim_flags"]["generic_rw_module_simplicity_certified"]
        )
        self.assertFalse(
            self.data["claim_flags"][
                "only_plus_minus_identity_on_bach_spin_two_certified"
            ]
        )

    def test_nonlocal_c_is_not_excluded(self):
        joined = " ".join(self.data["does_not_establish"])
        self.assertIn("nonlocal", joined)

    def test_einstein_positive_graph_is_boundary(self):
        obstruction = self.data["positive_subspace_obstruction"]
        self.assertIn("||K||=1", obstruction["inclusion_requirement"])
        self.assertFalse(
            self.data["claim_flags"][
                "uniform_positive_einstein_containing_subspace_exists"
            ]
        )

    def test_schwarzschild_time_domain_gate_is_open(self):
        self.assertFalse(
            self.data["claim_flags"]["schwarzschild_retarded_evolution_certified"]
        )

    def test_parent_overlap_requires_commutator_audit(self):
        gate = self.data["experiment_specs"]["parent_overlap_audit"]["gate"]
        self.assertIn("commutator cancellation", gate)


if __name__ == "__main__":
    unittest.main()
