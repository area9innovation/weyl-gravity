from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import flat_tt_bach


class FlatTTBachTests(unittest.TestCase):
    def test_canonical_certificate_is_current(self) -> None:
        flat_tt_bach.verify_certificate()

    def test_exact_operator_and_helicities(self) -> None:
        result = flat_tt_bach.build_certificate()
        self.assertEqual(result["operator_identity"], "B_1(h_TT)=-(1/4) Box^2 h_TT")
        self.assertEqual(result["curvature_identities"]["linearized_scalar"], "0")
        self.assertTrue(result["helicity_commutator_zero"])
        self.assertEqual(len(result["nonzero_bach_components"]), 4)

    def test_false_normalization_is_rejected(self) -> None:
        payload = flat_tt_bach.build_certificate()
        payload["operator_identity"] = "B_1(h_TT)=Box^2 h_TT"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(flat_tt_bach.FlatTTBachError):
                flat_tt_bach.verify_certificate(path)


if __name__ == "__main__":
    unittest.main()
