from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from bridge.einstein_sector import compensated_minimal_bv_operator_export as exporter
from bridge.einstein_sector import verify_compensated_minimal_bv_operator_export as independent


class CompensatedMinimalBVOperatorExportTests(unittest.TestCase):
    def test_canonical_export_is_current(self) -> None:
        exporter.verify_export()

    def test_independent_consumer_rechecks_actual_operators(self) -> None:
        payload, matrices, _ = independent.load_verified_export()
        self.assertEqual(payload["result_id"], "COMPENSATED_MINIMAL_BV_CANONICAL_OPERATOR_EXPORT")
        self.assertEqual(matrices["q"].shape, (32, 32))
        self.assertEqual(matrices["reduced_pairing"].rank(), 28)

    def test_consumer_does_not_import_constructor_or_exporter(self) -> None:
        source = Path(independent.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import compensated_quadratic_minimal_bv", source)
        self.assertNotIn("import compensated_minimal_bv_operator_export", source)

    def test_sparse_entry_tampering_is_rejected(self) -> None:
        payload = json.loads(exporter.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        payload["matrices"]["q"]["entries"][0][2] = "2"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(independent.IndependentOperatorVerificationError):
                independent.load_verified_export(path)


if __name__ == "__main__":
    unittest.main()
