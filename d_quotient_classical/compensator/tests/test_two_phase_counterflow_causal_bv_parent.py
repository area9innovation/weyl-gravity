from __future__ import annotations

import copy
import unittest
from unittest import mock

from d_quotient_classical.compensator import two_phase_counterflow_causal_bv_parent as producer
from d_quotient_classical.compensator import verify_two_phase_counterflow_causal_bv_parent as verifier
from d_quotient_classical.atlas import generate_two_phase_counterflow_causal_bv_atlas_fragment as atlas


class TwoPhaseCounterflowCausalBVParentTest(unittest.TestCase):
    def test_producer_deterministic(self) -> None:
        self.assertEqual(producer.build(), producer.build())

    def test_independent_replay(self) -> None:
        verifier.verify()

    def test_import_drift_rejected(self) -> None:
        mutated = copy.deepcopy(producer.IMPORTS)
        row = list(mutated["green_54"])
        row[1] = "0" * 64
        mutated["green_54"] = tuple(row)
        with mock.patch.object(producer, "IMPORTS", mutated):
            with self.assertRaisesRegex(AssertionError, "import drifted"):
                producer.build()

    def test_rank_mutation_rejected(self) -> None:
        certificate, payload, receiver = producer.build()
        payload["complete_parent"]["complete_component_rank"] = 69
        payload["content_sha256"] = producer._digest({k: v for k, v in payload.items() if k != "content_sha256"})
        with self.assertRaisesRegex(AssertionError, "carrier rank"):
            producer.validate(certificate, payload, receiver)

    def test_nilpotency_mutation_rejected(self) -> None:
        certificate, payload, receiver = producer.build()
        payload["u1_minimal_nonminimal_extension"]["Q_squared_zero"] = False
        payload["content_sha256"] = producer._digest({k: v for k, v in payload.items() if k != "content_sha256"})
        with self.assertRaisesRegex(AssertionError, "contraction"):
            producer.validate(certificate, payload, receiver)

    def test_coulomb_and_downstream_promotions_rejected(self) -> None:
        for key in ("COULOMB_INVERSE", "UNRESTRICTED_D_GAUGE", "HADAMARD", "NONLINEAR_Q2", "QME_OR_QUANTUM"):
            certificate, payload, receiver = producer.build()
            certificate["claim_flags"][key] = True
            with self.assertRaisesRegex(AssertionError, "claim boundary"):
                producer.validate(certificate, payload, receiver)

    def test_receiver_mutation_rejected(self) -> None:
        certificate, payload, receiver = producer.build()
        receiver["receivers"].pop("Quantum")
        receiver["content_sha256"] = producer._digest({k: v for k, v in receiver.items() if k != "content_sha256"})
        with self.assertRaisesRegex(AssertionError, "receiver content"):
            producer.validate(certificate, payload, receiver)

    def test_fixed_charge_and_unrestricted_D_are_distinct(self) -> None:
        certificate, _, _ = producer.build()
        self.assertIn("not gauge", certificate["Cartan_ledger"]["D"]["charge"])
        self.assertIn("fixed-Q_rel", certificate["terminal_verdict"]["activation_scope"])

    def test_atlas_fail_closed(self) -> None:
        first = atlas.build()
        self.assertEqual(first, atlas.build())
        self.assertEqual(len(first["entries"]), 4)
        for row in first["entries"]:
            self.assertEqual(row["descriptions"]["quantum"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
