from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_weyl_generic_identity_cyclic_obstruction.json"


class GenericIdentityCyclicObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_both_parity_defects_are_nonradical(self) -> None:
        for row in self.value["cyclic_obstruction_theorem"]["parity_blocks"].values():
            self.assertEqual(row["determinant_D"], "-9*lambda/2")
            self.assertEqual(row["rank_for_physical_lambda"], 2)

    def test_obstruction_is_fixed_identity_only(self) -> None:
        flags = self.value["classification"]
        self.assertEqual(flags["fixed_identity_cyclic_pairing_compatibility"], "OBSTRUCTED")
        self.assertFalse(flags["corrected_nonidentity_or_chain_homotopy_cyclic_morphism_classified"])


if __name__ == "__main__":
    unittest.main()
