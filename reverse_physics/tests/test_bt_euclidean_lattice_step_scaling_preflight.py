"""Scoped and mutation tests for the BT step-scaling preflight."""

from __future__ import annotations

import copy
import json
import math
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    action_from_residuals,
    direct_local_delta_check,
    experiment,
    independent_residuals,
    local_proposal,
)
from reverse_physics.bt_euclidean_lattice_pilot import periodic_neighbors
from reverse_physics.bt_euclidean_lattice_step_scaling_preflight import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_lattice_step_scaling_preflight import (
    verify,
)


class LocalMetropolisTests(unittest.TestCase):
    def test_nonlinear_local_delta(self) -> None:
        self.assertLess(direct_local_delta_check(), 1e-12)

    def test_free_local_delta(self) -> None:
        neighbors = periodic_neighbors(3, 2)
        field = [math.sin(0.27 * index) / 8 for index in range(9)]
        residuals = independent_residuals(field, 0.0, neighbors)
        delta_action, _ = local_proposal(
            field, residuals, 4, -0.061, 0.0, neighbors
        )
        proposal = field.copy()
        proposal[4] -= 0.061
        direct = (
            action_from_residuals(
                independent_residuals(proposal, 0.0, neighbors), 0.0
            )
            - action_from_residuals(residuals, 0.0)
        )
        self.assertAlmostEqual(delta_action, direct, places=13)

    def test_smoke_runs_without_production_write(self) -> None:
        result = experiment(smoke=True)
        self.assertTrue(result["smoke"])
        self.assertEqual(len(result["runs"]), 2)
        self.assertLess(result["local_delta_direct_check_max_residual"], 1e-12)
        for run in result["runs"]:
            self.assertEqual(len(run["blocks"]), 4)
            self.assertGreater(run["acceptance_rate"], 0.5)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.certificate = json.load(handle)

    def test_deterministic_builder(self) -> None:
        rebuilt = build()
        self.assertTrue(rebuilt["checks"]["ok"])
        self.assertEqual(rebuilt, self.certificate)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def assert_mutation_rejected(self, mutate) -> None:
        changed = copy.deepcopy(self.certificate)
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(1, "LORENTZIAN-CAUSAL")
        )

    def test_mutation_continuum_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["disposition"].__setitem__(
                "continuum_limit", "ESTABLISHED"
            )
        )

    def test_mutation_run_summary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["runs"][2]["summary"]["mode_second_moment"].__setitem__(
                "estimate",
                cert["runs"][2]["summary"]["mode_second_moment"]["estimate"] + 0.01,
            )
        )

    def test_mutation_cross_sampler_score(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["cross_sampler_z_scores"]["L6"].__setitem__(
                "connected_mode_proxy_u", 0.0
            )
        )

    def test_mutation_observation_hash(self) -> None:
        def mutate(cert: dict) -> None:
            cert["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assert_mutation_rejected(mutate)

    def test_mutation_extra_top_level_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
