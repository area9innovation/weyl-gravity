from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from d_quotient_classical.compensator.complex_compensator_action_quartet_preflight import (
    build,
    validate,
)
from d_quotient_classical.compensator.verify_complex_compensator_action_quartet_preflight import (
    verify,
)


def _rehash_matrix(record: dict[str, object]) -> None:
    canonical = {
        "row_count": record["row_count"],
        "column_count": record["column_count"],
        "entries": record["entries"],
    }
    record["sha256"] = hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


class ComplexCompensatorActionQuartetPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_producer_and_independent_replay_agree(self) -> None:
        validate(self.value)
        verify(self.value)

    def test_independent_polar_coefficients_are_not_relocked(self) -> None:
        signs = self.value["sign_and_regularity_classification"]
        self.assertTrue(signs["formal_polar_family"]["simultaneously_feasible"])
        self.assertFalse(
            signs["Cartesian_analytic_complex_scalar_subfamily"][
                "simultaneously_positive"
            ]
        )
        self.assertEqual(
            signs["Cartesian_analytic_complex_scalar_subfamily"][
                "product_identity"
            ],
            "M_P^2 Z_theta=-kappa_Phi^2 f^4/6",
        )

    def test_wrong_positive_fixture_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["sign_and_regularity_classification"]["formal_polar_family"][
            "exact_fixture"
        ]["kappa_theta"] = -1
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_quartet_sign_mutation_is_rejected_after_rehash(self) -> None:
        mutant = deepcopy(self.value)
        matrix = mutant["sparse_operators"]["Weyl_quartet"]["Q_W"]
        matrix["entries"][1]["coefficient"]["numerator"] = -1
        _rehash_matrix(matrix)
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_hbar_wess_zumino_promotion_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["Wess_Zumino_lifecycle"]["classical_action_contains_WZ"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_local_U1_without_connection_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["internal_symmetry_classification"]["LOCAL"]["included_here"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_R_squared_basis_omission_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["action_basis"]["bulk_four_derivative_curvature_basis"].remove(
            "R(g_hat)^2"
        )
        with self.assertRaises(AssertionError):
            verify(mutant)

    def test_spontaneous_breaking_and_hadamard_promotions_are_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["reduced_action"]["rho_equals_f_is"] = (
            "SPONTANEOUS_WEYL_BREAKING"
        )
        with self.assertRaises(AssertionError):
            verify(mutant)
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["HADAMARD_STATE"] = True
        with self.assertRaises(AssertionError):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
