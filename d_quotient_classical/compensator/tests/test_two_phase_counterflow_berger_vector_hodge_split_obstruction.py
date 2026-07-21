import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_PAYLOAD_V1.json"


class VectorHodgeSplitObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads(CERT.read_text())
        cls.payload = json.loads(PAYLOAD.read_text())

    def test_formal_adjoint(self):
        endpoint = self.payload["endpoint"]
        self.assertTrue(endpoint["formal_self_adjoint"])
        self.assertEqual(endpoint["formal_adjoint_defects"], [])
        self.assertEqual(endpoint["PBW_term_count"], 18)

    def test_two_way_rank_pattern(self):
        for row in self.cert["finite_rank_ledger"]:
            expected = row["two_j"] + 1 if row["two_j"] % 2 else row["two_j"]
            self.assertEqual(row["expected_cross_rank"], expected)
            self.assertEqual(row["exact_to_coexact_rank"], expected)
            self.assertEqual(row["coexact_to_exact_rank"], expected)

    def test_round_negative_control(self):
        for row in self.payload["round_mutation_audits"]:
            self.assertEqual(row["exact_to_coexact_rank"], 0)
            self.assertEqual(row["coexact_to_exact_rank"], 0)

    def test_fail_closed_terminal(self):
        terminal = self.cert["terminal_verdict"]
        self.assertFalse(terminal["requested_longitudinal_coexact_split_closed"])
        self.assertFalse(terminal["downstream_exceptional_export_activated"])
        self.assertTrue(terminal["q70_parent_preserved"])

    def test_no_oracle_fields(self):
        self.assertEqual(self.payload["oracle_fields_consumed"], [])
        for item in self.cert["imports"].values():
            self.assertEqual(item["oracle_fields_consumed"], [])


if __name__ == "__main__":
    unittest.main()
