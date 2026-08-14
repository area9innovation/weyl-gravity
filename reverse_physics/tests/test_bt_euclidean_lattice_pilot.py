"""Tests and adversarial mutations for the BT Euclidean lattice pilot."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
import os
import subprocess
import tempfile
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CERT = os.path.join(
    REPO_ROOT, "reverse_physics", "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1.json",
)
PRODUCER = os.path.join(
    REPO_ROOT, "reverse_physics", "bt_euclidean_lattice_pilot.py",
)
VERIFIER = os.path.join(
    REPO_ROOT, "reverse_physics", "verify_bt_euclidean_lattice_pilot.py",
)
PYTHON = "/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3"


def load(path: str, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def set_path(document: dict, path: tuple[str, ...], value) -> None:
    cursor = document
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value


MUTATIONS = {
    "factor_three_removed": (
        ("auxiliary_normalization_audit", "derived_to_displayed_ratio"),
        {"numerator": 1, "denominator": 1},
    ),
    "displayed_coefficient_promoted": (
        ("auxiliary_normalization_audit", "classification"),
        "NORMALIZATION_CONSISTENT",
    ),
    "lorentzian_tag_added": (
        ("dependency_tags",),
        ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "LORENTZIAN-CAUSAL"],
    ),
    "continuum_promoted": (
        ("disposition", "continuum_limit"),
        "ESTABLISHED",
    ),
    "reflection_positivity_promoted": (
        ("disposition", "osterwalder_schrader_reflection_positivity"),
        "ESTABLISHED",
    ),
    "lorentzian_scattering_promoted": (
        ("disposition", "lorentzian_scattering"),
        "ESTABLISHED",
    ),
    "numeric_type_promoted": (
        ("numerical_pilot", "evidence_type"),
        "CONTINUUM_CERTIFIED",
    ),
    "zero_mode_unfixed": (
        ("finite_lattice_definition", "zero_mode_constraint"),
        "none",
    ),
    "normalizability_promoted_without_bound": (
        ("finite_lattice_definition", "normalizability", "classification"),
        "ASSUMED",
    ),
    "lattice_volume_changed": (
        ("numerical_pilot", "interacting_observation", "lattice", "volume"),
        4096,
    ),
    "warmup_erased": (
        ("numerical_pilot", "interacting_observation", "algorithm", "warmup_trajectories"),
        0,
    ),
    "acceptance_failed": (
        ("numerical_pilot", "interacting_observation", "acceptance_rate"),
        0.1,
    ),
    "producer_failure_erased": (
        ("checks", "ok"),
        False,
    ),
}


class TestExactLattice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = load(PRODUCER, "bt_euclidean_lattice_producer")
        cls.verifier = load(VERIFIER, "bt_euclidean_lattice_verifier")
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_normalization_is_derived_independently(self):
        self.assertTrue(all(
            self.verifier.independent_normalization().values()
        ))

    def test_gradient_matches_finite_differences(self):
        passed, residual = self.verifier.finite_difference_gradient_check()
        self.assertTrue(passed)
        self.assertLess(residual, 2e-8)

    def test_constant_shift_is_null_direction(self):
        adjacency = self.producer.periodic_neighbors(3, 2)
        field = [math.sin(i / 3) for i in range(9)]
        action, gradient, _ = self.producer.action_gradient(
            field, 0.4, adjacency
        )
        shifted_action, _, _ = self.producer.action_gradient(
            [value + 13 for value in field], 0.4, adjacency
        )
        self.assertAlmostEqual(action, shifted_action, places=12)
        self.assertAlmostEqual(sum(gradient), 0, places=12)

    def test_connected_graph_kernel_is_one_dimensional(self):
        self.assertTrue(self.verifier.independent_kernel_check())

    def test_spectrum_has_only_one_zero_mode(self):
        spectrum = self.verifier.independent_spectrum()
        self.assertEqual(spectrum[0], {
            "laplacian_eigenvalue": 0,
            "hessian_eigenvalue": 0,
            "multiplicity": 1,
        })
        self.assertEqual(sum(row["multiplicity"] for row in spectrum), 256)

    def test_pilot_graph_diameter(self):
        self.assertEqual(
            self.verifier.independent_diameter(self.verifier.graph(4, 4)), 8
        )

    def test_numerical_evidence_boundary(self):
        self.assertEqual(
            self.certificate["numerical_pilot"]["evidence_type"],
            "NUMERICAL_PILOT_OBSERVED",
        )
        disposition = self.certificate["disposition"]
        self.assertEqual(disposition["continuum_limit"], "NOT_ESTABLISHED")
        self.assertEqual(disposition["lorentzian_scattering"], "NOT_ESTABLISHED")


class TestExecutableRails(unittest.TestCase):
    def test_producer_reproduces_certificate(self):
        run = subprocess.run(
            [PYTHON, PRODUCER, "--check"], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
            env={**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"},
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS (24/24)", run.stdout)

    def test_independent_verifier_accepts_certificate(self):
        run = subprocess.run(
            [PYTHON, VERIFIER], cwd=REPO_ROOT,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("RESULT: PASS (22/22)", run.stdout)


class TestMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def reject_mutation(self, path: tuple[str, ...], value) -> None:
        mutation = copy.deepcopy(self.certificate)
        set_path(mutation, path, value)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8"
        ) as handle:
            json.dump(mutation, handle)
            handle.flush()
            run = subprocess.run(
                [PYTHON, VERIFIER, "--verify", handle.name], cwd=REPO_ROOT,
                text=True, capture_output=True, check=False,
            )
        self.assertNotEqual(run.returncode, 0, run.stdout + run.stderr)


def make_mutation_test(path: tuple[str, ...], value):
    def test(self):
        self.reject_mutation(path, value)
    return test


for mutation_name, (mutation_path, mutation_value) in MUTATIONS.items():
    setattr(
        TestMutations,
        f"test_{mutation_name}_mutation_rejected",
        make_mutation_test(mutation_path, mutation_value),
    )


if __name__ == "__main__":
    unittest.main()
