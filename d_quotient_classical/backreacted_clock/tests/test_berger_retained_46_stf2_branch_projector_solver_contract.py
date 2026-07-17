from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_retained_46_stf2_branch_projector_solver_contract import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_46_stf2_branch_projector_solver_contract import (
    verify,
)


class Retained46STF2BranchProjectorSolverContractTests(unittest.TestCase):
    def test_contract_reproduces_and_verifies(self) -> None:
        value = build()
        validate(value)
        self.assertEqual(value, verify())
        self.assertEqual(
            value["declared_graph_ansatz"][
                "independent_coefficient_count_over_Q_sqrt10"
            ],
            225,
        )
        self.assertEqual(value["ordered_solver_stages"][-1]["name"], "BINARY_VERDICT")

    def test_graph_partition_is_complete(self) -> None:
        partition = build()["row_partition"]
        self.assertEqual(sorted(sum(partition.values(), [])), list(range(46)))
        self.assertEqual(len(partition["gravity_configuration_rows"]), 15)
        self.assertEqual(len(partition["gravity_equation_rows"]), 15)

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "BRANCH_PROJECTOR_ACCEPTED",
            "NORMALIZED_PROJECTOR_OBSTRUCTION_FOUND",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
        ):
            mutant = deepcopy(build())
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)

    def test_unrestricted_solver_is_forbidden(self) -> None:
        shortcuts = build()["declared_graph_ansatz"]["forbidden_shortcuts"]
        self.assertIn("unrestricted 46x46 polydifferential coefficient search", shortcuts)
        self.assertIn("numerical pseudoinverse", " ".join(shortcuts))


if __name__ == "__main__":
    unittest.main()
