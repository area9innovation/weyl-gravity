from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import (
    complex_scale_u1_connection_preflight as producer,
)
from d_quotient_classical.compensator import (
    verify_complex_scale_u1_connection_preflight as verifier,
)


class ComplexScaleU1ConnectionPreflightTest(unittest.TestCase):
    def test_exact_producer(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_replay(self) -> None:
        verifier.verify()

    def test_import_hash_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORTS)
        mutated["level3b"]["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORTS", mutated):
            with self.assertRaisesRegex(AssertionError, "hash drifted"):
                producer.build()

    def test_reducibility_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["gauge_rank_and_reducibility"]["strata"]["Delta_zero"][
            "candidate_scale_contracts_dressed_trace"
        ] = True
        with self.assertRaisesRegex(AssertionError, "rank/reducibility"):
            producer.validate_payload(payload)

    def test_ward_removal_rejected(self) -> None:
        payload = producer.build()
        payload["constant_scale_Ward_system"]["exact_Ward_ideal_generators"].remove(
            "Delta*kappa_theta"
        )
        with self.assertRaisesRegex(AssertionError, "Ward"):
            producer.validate_payload(payload)

    def test_Gauss_clock_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["stationary_systems"]["frozen_Berger_clock_lift"][
            "decisive_relation"
        ] = "Z_theta>0"
        with self.assertRaisesRegex(AssertionError, "Berger/Gauss"):
            producer.validate_payload(payload)

    def test_selected_action_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["terminal_verdict"]["selected_action"] = True
        with self.assertRaisesRegex(AssertionError, "promotion"):
            producer.validate_payload(payload)

    def test_causal_or_quantum_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["terminal_verdict"]["causal_completion_activated"] = True
        payload["claim_flags"]["HADAMARD_OR_QUANTUM"] = True
        with self.assertRaisesRegex(AssertionError, "promotion"):
            producer.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
