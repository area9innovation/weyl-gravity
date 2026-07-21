from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import (
    closed_s3_relative_phase_nonhomogeneous_hodge_preflight as producer,
)
from d_quotient_classical.compensator import (
    verify_closed_s3_relative_phase_nonhomogeneous_hodge_preflight as verifier,
)


class ClosedS3RelativePhaseNonhomogeneousHodgeTest(unittest.TestCase):
    def test_producer_is_deterministic(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_exact_replay(self) -> None:
        verifier.verify()

    def test_import_hash_mutation_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORT)
        mutated["sha256"] = "0" * 64
        with mock.patch.object(producer, "IMPORT", mutated):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_homogeneous_oracle_consumption_rejected(self) -> None:
        certificate, payload = producer.build()
        payload["import_ref"]["oracle_fields_consumed"] = ["terminal_verdict"]
        with self.assertRaisesRegex(AssertionError, "oracle"):
            producer.validate_payload(payload)

    def test_payload_matrix_mutation_rejected(self) -> None:
        _, payload = producer.build()
        payload["fixtures"][0]["relative_metric_Grel"] = [["-6/5"]]
        with self.assertRaisesRegex(AssertionError, "content hash"):
            producer.validate_payload(payload)

    def test_claim_promotion_rejected(self) -> None:
        certificate, payload = producer.build()
        certificate["claim_flags"]["FULL_BV_CAUSAL_PARENT"] = True
        with self.assertRaisesRegex(AssertionError, "claim boundary"):
            producer.validate_certificate(certificate, payload)

    def test_rank_deficient_fixture_splits_massless_connection(self) -> None:
        _, payload = producer.build()
        row = next(
            item
            for item in payload["fixtures"]
            if item["fixture_id"].startswith("rank_deficient")
        )
        self.assertEqual(row["rank_Q"], 1)
        self.assertEqual(row["matter_kernel_gauge_dimension"], 1)
        self.assertEqual(row["relative_dimension"], 2)
        self.assertEqual(row["longitudinal_frequency_squared_operator"], [["11"]])

    def test_full_rank_fixture_has_no_relative_phase(self) -> None:
        _, payload = producer.build()
        row = next(
            item
            for item in payload["fixtures"]
            if item["fixture_id"].startswith("full_phase_rank")
        )
        self.assertEqual(row["relative_dimension"], 0)
        self.assertEqual(row["relative_metric_Grel"], [])

    def test_all_ell_and_zero_mode_flags(self) -> None:
        certificate, _ = producer.build()
        self.assertTrue(certificate["terminal_verdict"]["all_ell_symbolic"])
        self.assertTrue(
            certificate["terminal_verdict"]["homogeneous_ell_zero_reproduced"]
        )
        self.assertFalse(
            certificate["terminal_verdict"]["full_causal_parent_activated"]
        )


if __name__ == "__main__":
    unittest.main()
