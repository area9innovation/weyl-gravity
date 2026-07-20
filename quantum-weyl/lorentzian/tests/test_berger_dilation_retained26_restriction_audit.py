from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_dilation_retained26_restriction_audit import (
    canonical_summand_replay,
    graph_restriction_contract,
    validate,
)
from lorentzian.berger_dilation_retained26_restriction_audit_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_dilation_retained26_restriction_audit import verify


class BergerDilationRetained26RestrictionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-dilation-retained26-restriction-audit-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_canonical_summands_are_isotropic(self) -> None:
        replay = canonical_summand_replay()
        self.assertTrue(replay["all_pass"])
        self.assertEqual(
            replay["first_summand"]["pairing_rank_in_block_replay"], 0
        )
        self.assertEqual(
            replay["second_summand"]["pairing_rank_in_block_replay"], 0
        )

    def test_empty_graph_contract_fails_closed(self) -> None:
        contract = graph_restriction_contract()
        self.assertFalse(contract["raw_metric_covariance_ready"])
        self.assertFalse(contract["retained_26_covariance_ready"])

    def test_complete_contract_fixture_is_ready(self) -> None:
        contract = graph_restriction_contract(
            support_local_intertwiner_supplied=True,
            intertwining_verified=True,
            graph_pairing_nondegenerate=True,
            covariance_pullback_verified=True,
            ghost_covariance_supplied=True,
        )
        self.assertTrue(contract["retained_26_covariance_ready"])

    def test_ghost_rows_are_load_bearing(self) -> None:
        contract = graph_restriction_contract(
            support_local_intertwiner_supplied=True,
            intertwining_verified=True,
            graph_pairing_nondegenerate=True,
            covariance_pullback_verified=True,
            ghost_covariance_supplied=False,
        )
        self.assertTrue(contract["raw_metric_covariance_ready"])
        self.assertFalse(contract["retained_26_covariance_ready"])

    def test_54_row_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
