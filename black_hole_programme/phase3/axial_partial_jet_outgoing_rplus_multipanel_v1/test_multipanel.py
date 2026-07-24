from __future__ import annotations
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

class MultipanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads((HERE / "certificate.json").read_text())

    def test_fail_closed_join(self):
        self.assertFalse(self.d["claim_flags"]["T_plus_recovered"])
        self.assertFalse(
            self.d["claim_flags"]["complementary_outgoing_columns_constructed"]
        )

    def test_transport_has_terminal_disposition(self):
        self.assertIn(
            self.d["status"],
            (
                "RPLUS_CORRELATED_FIRST_CHUNK_PASS",
                "RPLUS_CORRELATED_MULTIPANEL_SHORTFALL",
            ),
        )

if __name__ == "__main__":
    unittest.main()
