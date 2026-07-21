import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERIFIER = ROOT / "bridge/einstein_sector/verify_paper13_third_order_kuranishi_disposition.py"


class Paper13ThirdOrderDispositionTest(unittest.TestCase):
    def test_fail_closed_disposition_verifier(self):
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("PAPER13_THIRD_ORDER_KURANISHI_DISPOSITION: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
