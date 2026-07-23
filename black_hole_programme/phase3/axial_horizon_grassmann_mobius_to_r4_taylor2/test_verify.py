from pathlib import Path
import unittest

from . import verify


class Taylor2VerifierTests(unittest.TestCase):
    def test_frozen_receipt_verifies(self):
        self.assertEqual(verify.verify(), [])

    def test_pass_mutation_is_rejected(self):
        text = verify.LOG.read_text() + "PASS q=0\n"
        self.assertIn("refused run contains PASS", verify.verify_log(text))

    def test_gate_mutation_is_rejected(self):
        text = verify.LOG.read_text().replace(
            "REFUSE amplitude-rank q=0 shell=2",
            "REFUSE amplitude-rank q=0 shell=3",
        )
        self.assertIn(
            "missing unique shell-2 amplitude-rank refusal",
            verify.verify_log(text),
        )

    def test_non_q0_mutation_is_rejected(self):
        text = verify.LOG.read_text().replace("BEGIN q=0", "BEGIN q=1", 1)
        self.assertIn("missing q0 begin", verify.verify_log(text))


if __name__ == "__main__":
    unittest.main()
