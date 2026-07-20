from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import (
    two_field_charge_matrix_preflight as producer,
)
from d_quotient_classical.compensator import (
    verify_two_field_charge_matrix_preflight as verifier,
)


class TwoFieldChargeMatrixPreflightTest(unittest.TestCase):
    def test_exact_producer(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_replay(self) -> None:
        verifier.verify()

    def test_import_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORTS)
        mutated["one_field_preflight"]["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORTS", mutated):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_noncanonical_charge_selection_rejected(self) -> None:
        payload = producer.build()
        payload["charge_lattice"]["selected_preflight_case"]["Q"] = [["1"], ["1"]]
        with self.assertRaisesRegex(AssertionError, "noncanonical"):
            producer.validate_payload(payload)

    def test_reducibility_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["positivity_and_gauge_rank"]["complete_healthy_strata"][
            "b1=b2=a_and_s2_zero"
        ]["reducibility_vector_(omega,eta,gamma)"] = ["0", "1", "0"]
        with self.assertRaisesRegex(AssertionError, "trichotomy"):
            producer.validate_payload(payload)

    def test_clock_gauging_removed_rejected(self) -> None:
        payload = producer.build()
        payload["positivity_and_gauge_rank"]["complete_healthy_strata"][
            "b1=b2=a_and_s2_nonzero"
        ] = "healthy independent clock"
        with self.assertRaisesRegex(AssertionError, "trichotomy"):
            producer.validate_payload(payload)

    def test_selected_action_rejected(self) -> None:
        payload = producer.build()
        payload["terminal_verdict"]["selected_action"] = True
        with self.assertRaisesRegex(AssertionError, "promotion"):
            producer.validate_payload(payload)

    def test_quantum_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["claim_flags"]["HADAMARD_OR_QUANTUM"] = True
        with self.assertRaisesRegex(AssertionError, "promotion"):
            producer.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
