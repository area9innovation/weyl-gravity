from __future__ import annotations

from copy import deepcopy
import json
import unittest

from covariant_completion.final_transport.proof_ledger import (
    DAG_PATH,
    ProofLedgerError,
    build_ledger,
    outputs_are_current,
)


class ProofLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dag = json.loads(DAG_PATH.read_text(encoding="utf-8"))

    def test_generated_outputs_match_live_evidence(self) -> None:
        self.assertTrue(outputs_are_current(build_ledger(self.dag)))

    def test_missing_evidence_fails_closed(self) -> None:
        broken = deepcopy(self.dag)
        broken["claims"]["scalar_wave_witness_no_go"]["evidence"] = [
            "does_not_exist.json"
        ]
        with self.assertRaises(ProofLedgerError):
            build_ledger(broken)

    def test_false_requirement_fails_closed(self) -> None:
        broken = deepcopy(self.dag)
        broken["claims"]["causal_green_homotopy"]["status"] = False
        with self.assertRaises(ProofLedgerError):
            build_ledger(broken)

    def test_dependency_drift_fails_closed(self) -> None:
        broken = deepcopy(self.dag)
        broken["claims"]["final_covariant_H4"]["requires"].pop()
        with self.assertRaises(ProofLedgerError):
            build_ledger(broken)


if __name__ == "__main__":
    unittest.main()
