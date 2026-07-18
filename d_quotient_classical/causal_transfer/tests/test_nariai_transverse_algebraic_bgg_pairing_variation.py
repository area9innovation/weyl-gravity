from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_algebraic_bgg_pairing_variation import build


class TransverseAlgebraicBGGPairingVariationTest(unittest.TestCase):
    def test_exact_checks(self) -> None:
        self.assertTrue(all(build()["exact_checks"].values()))

    def test_fail_closed(self) -> None:
        flags = build()["flags"]
        self.assertFalse(flags["TRANSVERSE_CONNECTION_PBW_VARIATION"])
        self.assertFalse(flags["TRANSVERSE_MIDDLE_SCHUR_VARIATION"])
        self.assertFalse(flags["TRANSVERSE_CAUSAL_TRANSFER"])


if __name__ == "__main__":
    unittest.main()
