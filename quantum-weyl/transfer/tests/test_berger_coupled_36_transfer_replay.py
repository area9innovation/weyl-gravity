from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from transfer.berger_coupled_36_transfer_replay import _q10_string, build_payload, replay
from transfer.berger_coupled_36_transfer_replay_certificate import HERE, OUTPUT, build_certificate
from transfer.verify_berger_coupled_36_transfer_replay import _rejects_overclaim, verify


class BergerCoupled36TransferReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replay = replay()
        cls.payload = build_payload()

    def test_transfer_formula_and_arity_two_replay(self) -> None:
        self.assertEqual(self.replay.transferred_terms, 1522)
        self.assertEqual(self.replay.transferred_nonzero_rows, 23)
        self.assertEqual(self.payload["independent_replay"]["transfer_formula_all_1522_coefficients"], "VERIFIED")
        self.assertEqual(self.payload["independent_replay"]["full_q1_q2_arity_two_identity"], "VERIFIED")
        self.assertEqual(self.payload["independent_replay"]["retained_q1_q2_arity_two_identity"], "VERIFIED")

    def test_cyclicity_obstruction_is_exact_and_fail_closed(self) -> None:
        obstruction = self.payload["cyclicity_obstruction"]
        self.assertEqual(obstruction["full_64_defect_coefficient_count"], 1234)
        self.assertEqual(obstruction["retained_36_defect_coefficient_count"], 953)
        self.assertEqual(obstruction["retained_36_first_normalized_witness"][:5], [0, 26, 35, [], [1]])
        self.assertFalse(self.payload["claim_flags"]["RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED"])
        self.assertTrue(self.payload["claim_flags"]["EXACT_CYCLICITY_OBSTRUCTION_WITNESS"])

    def test_overclaim_and_float_mutations_are_rejected(self) -> None:
        mutant = deepcopy(self.payload)
        mutant["claim_flags"]["RETAINED_BV_CYCLICITY_INDEPENDENTLY_REPLAYED"] = True
        with self.assertRaises(ValueError):
            _rejects_overclaim(mutant)
        with self.assertRaises(ValueError):
            _q10_string("0.5")

    def test_certificate_reproduces_and_schema_is_strict(self) -> None:
        certificate = build_certificate()
        schema = json.loads((HERE / "schema/berger-coupled-36-transfer-replay-v1.schema.json").read_text())
        self.assertEqual(json.loads(OUTPUT.read_text()), certificate)
        self.assertFalse(validate_instance(certificate, schema))

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build_certificate())


if __name__ == "__main__":
    unittest.main()
