from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import (
    closed_s3_gauged_clock_gauss_structure_theorem as producer,
)
from d_quotient_classical.compensator import (
    verify_closed_s3_gauged_clock_gauss_structure_theorem as verifier,
)


class ClosedS3GaugedClockGaussStructureTheoremTest(unittest.TestCase):
    def test_exact_producer(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_replay(self) -> None:
        verifier.verify()

    def test_import_mutation_rejected(self) -> None:
        mutated = list(copy.deepcopy(producer.IMPORTS))
        mutated[1]["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORTS", tuple(mutated)):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_nonzero_total_charge_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["claim_flags"][
            "NONZERO_TOTAL_GAUGE_CHARGE_ON_CLOSED_SOURCE_FREE_S3"
        ] = True
        with self.assertRaisesRegex(AssertionError, "claim boundary"):
            producer.validate_payload(payload)

    def test_individual_momenta_no_go_rejected(self) -> None:
        payload = producer.build()
        payload["terminal_verdict"]["individual_phase_momenta_forced_zero"] = True
        with self.assertRaisesRegex(AssertionError, "terminal"):
            producer.validate_payload(payload)

    def test_relative_clock_source_requirement_rejected(self) -> None:
        payload = producer.build()
        payload["terminal_verdict"][
            "boundary_or_external_source_needed_for_relative_clock"
        ] = True
        with self.assertRaisesRegex(AssertionError, "terminal"):
            producer.validate_payload(payload)

    def test_counterflow_witness_mutation_rejected(self) -> None:
        payload = producer.build()
        fixture = next(
            item
            for item in payload["exact_fixtures"]
            if item["fixture_id"] == "two_equal_charges_counterflow_clock"
        )
        fixture["phase_momentum_p_equals_N_Pi"] = ["1", "1"]
        with self.assertRaisesRegex(AssertionError, "counterflow"):
            producer.validate_payload(payload)

    def test_reduced_sign_mutation_rejected(self) -> None:
        payload = producer.build()
        fixture = next(
            item
            for item in payload["exact_fixtures"]
            if item["fixture_id"] == "two_equal_charges_counterflow_clock"
        )
        fixture["reduced_metric_Grel_equals_Ainv"] = [["-6/5"]]
        with self.assertRaisesRegex(AssertionError, "positive reduced"):
            producer.validate_payload(payload)

    def test_sigma_projector_mutation_rejected(self) -> None:
        payload = producer.build()
        payload["exact_sigma_model_projector_fixture"][
            "horizontal_projector_P_G"
        ][0][0] = "0"
        with self.assertRaisesRegex(AssertionError, "projector"):
            producer.validate_payload(payload)

    def test_causal_promotion_rejected(self) -> None:
        payload = producer.build()
        payload["claim_flags"]["FULL_BV_OR_CAUSAL_PARENT"] = True
        with self.assertRaisesRegex(AssertionError, "claim boundary"):
            producer.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
