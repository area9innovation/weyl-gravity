"""Falsification tests for the G0 Hamiltonian-privilege separation.

These target the claim, not the implementation: each test is designed so that
a plausible way of being wrong makes it fail.  In particular the mutation tests
confirm the verifier is not a rubber stamp.
"""

from __future__ import annotations

import json
import unittest
from fractions import Fraction

from reverse_physics import carriers
from reverse_physics.exact_linalg import rank_bareiss, rank_fraction
from reverse_physics.hamiltonian_privilege_linear_g0 import (
    OUTPUT,
    build,
    implies,
    is_hamiltonian,
    is_liouville,
    is_marginal,
    solution_dimension,
)
from reverse_physics.verify_hamiltonian_privilege_linear_g0 import (
    hamiltonian_lie_relation,
    leibniz_determinant,
    marginal_spanning_set,
    sl_spanning_set,
    sp_spanning_set,
)


class TestKnownDimensions(unittest.TestCase):
    """The three dimensions have closed forms; check against them, not against
    the code's own output."""

    def test_symplectic_dimension_matches_n_times_2n_plus_1(self):
        for dof in (1, 2):
            self.assertEqual(solution_dimension("symplectic", dof), dof * (2 * dof + 1))

    def test_liouville_dimension_matches_4n_squared_minus_1(self):
        for dof in (1, 2):
            self.assertEqual(solution_dimension("liouville", dof), 4 * dof * dof - 1)

    def test_marginal_dimension_matches_4n_squared_minus_n(self):
        for dof in (1, 2):
            self.assertEqual(solution_dimension("marginal", dof), 4 * dof * dof - dof)

    def test_two_dof_numbers_are_ten_fourteen_fifteen(self):
        self.assertEqual(solution_dimension("symplectic", 2), 10)
        self.assertEqual(solution_dimension("marginal", 2), 14)
        self.assertEqual(solution_dimension("liouville", 2), 15)


class TestSeparation(unittest.TestCase):
    def test_one_dof_collapses_the_distinction(self):
        self.assertEqual(solution_dimension("symplectic", 1), solution_dimension("liouville", 1))

    def test_two_dof_separates(self):
        self.assertNotEqual(solution_dimension("symplectic", 2), solution_dimension("liouville", 2))

    def test_marginal_is_necessary(self):
        # implied by Hamiltonian structure ...
        self.assertTrue(implies("marginal", "symplectic", 2))
        # ... and a strict, non-vacuous strengthening of Liouville.
        self.assertLess(solution_dimension("marginal", 2), solution_dimension("liouville", 2))

    def test_marginal_is_not_sufficient(self):
        self.assertFalse(implies("symplectic", "marginal", 2))
        gap = solution_dimension("marginal", 2) - solution_dimension("symplectic", 2)
        self.assertEqual(gap, 4)

    def test_inclusion_chain_holds_in_the_stated_direction_only(self):
        self.assertTrue(implies("liouville", "symplectic", 2))
        self.assertTrue(implies("liouville", "marginal", 2))
        self.assertFalse(implies("marginal", "liouville", 2))


class TestWitnesses(unittest.TestCase):
    def test_separating_witness_separates(self):
        matrix = carriers.witness_marginal_not_hamiltonian()
        self.assertTrue(is_marginal(matrix, 2))
        self.assertTrue(is_liouville(matrix, 2))
        self.assertFalse(is_hamiltonian(matrix, 2))

    def test_global_witness_is_liouville_but_not_marginal(self):
        matrix = carriers.witness_global_not_marginal()
        self.assertTrue(is_liouville(matrix, 2))
        self.assertFalse(is_marginal(matrix, 2))

    def test_control_is_hamiltonian_so_predicates_are_not_vacuous(self):
        matrix = carriers.witness_hamiltonian_control()
        self.assertTrue(is_hamiltonian(matrix, 2))
        self.assertTrue(is_marginal(matrix, 2))
        self.assertTrue(is_liouville(matrix, 2))

    def test_the_two_hamiltonian_predicates_agree_on_a_spanning_set(self):
        size = 4
        for vector in sp_spanning_set(2) + marginal_spanning_set(2) + sl_spanning_set(2):
            matrix = [[vector[size * i + j] for j in range(size)] for i in range(size)]
            self.assertEqual(
                is_hamiltonian(matrix, 2),
                hamiltonian_lie_relation(matrix, 2),
                msg=f"predicates disagree on {matrix}",
            )


class TestRailIndependence(unittest.TestCase):
    def test_both_rank_routines_agree_on_every_spanning_set(self):
        for dof in (1, 2):
            for factory in (sp_spanning_set, marginal_spanning_set, sl_spanning_set):
                vectors = factory(dof)
                self.assertEqual(rank_fraction(vectors), rank_bareiss(vectors))

    def test_both_determinant_routines_agree(self):
        from reverse_physics.exact_linalg import add, determinant, identity

        flow = add(identity(4), carriers.witness_marginal_not_hamiltonian())
        self.assertEqual(determinant(flow), leibniz_determinant(flow))
        self.assertEqual(leibniz_determinant(flow), 1)

    def test_bareiss_handles_denominators(self):
        rows = [[Fraction(1, 3), Fraction(2, 5)], [Fraction(2, 3), Fraction(4, 5)]]
        self.assertEqual(rank_bareiss(rows), 1)
        self.assertEqual(rank_fraction(rows), 1)


class TestMutationsAreCaught(unittest.TestCase):
    """If these pass trivially the verifier proves nothing."""

    def test_a_non_marginal_matrix_is_rejected(self):
        matrix = carriers.from_blocks({(0, 0): [[1, 0], [0, 0]]}, dof=2)
        self.assertFalse(is_marginal(matrix, 2))
        self.assertFalse(is_liouville(matrix, 2))

    def test_perturbing_the_control_breaks_hamiltonicity(self):
        matrix = carriers.witness_hamiltonian_control()
        matrix[0][2] += Fraction(1)
        self.assertFalse(is_hamiltonian(matrix, 2))
        self.assertFalse(hamiltonian_lie_relation(matrix, 2))

    def test_dropping_a_symplectic_constraint_row_changes_the_dimension(self):
        from reverse_physics.hamiltonian_privilege_linear_g0 import symplectic_constraints

        rows = symplectic_constraints(2)
        self.assertEqual(16 - rank_fraction(rows), 10)
        self.assertNotEqual(16 - rank_fraction(rows[:-1]), 10)


class TestCertificateIsCurrent(unittest.TestCase):
    def test_certificate_on_disk_matches_the_generator(self):
        self.assertTrue(OUTPUT.exists(), "certificate has not been written")
        expected = json.dumps(build(), indent=2, sort_keys=True) + "\n"
        self.assertEqual(OUTPUT.read_text(encoding="utf-8"), expected)

    def test_certificate_declares_its_boundary(self):
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertFalse(payload["claim_flags"]["MARGINAL_CONDITION_SUFFICIENT"])
        self.assertFalse(payload["claim_flags"]["GENERAL_N_DOF_COVERED"])
        self.assertFalse(payload["claim_flags"]["QUANTUM_CLAIM"])
        self.assertTrue(payload["does_not_establish"])
        # The two tag namespaces must not leak into each other.
        self.assertTrue(all(tag.startswith("RP-") for tag in payload["assumption_tags"]["consumed"]))
        self.assertTrue(all(not tag.startswith("RP-") for tag in payload["dependency_tags"]))


if __name__ == "__main__":
    unittest.main()
