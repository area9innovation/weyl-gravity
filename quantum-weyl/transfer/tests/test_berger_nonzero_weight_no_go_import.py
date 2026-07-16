from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "berger_nonzero_weight_no_go_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_nonzero_weight_no_go_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORTER = sys.modules[CERT.build_import.__module__]


class BergerNonzeroWeightNoGoImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORTER._git_json(IMPORTER.CERTIFICATE_RELATIVE)
        cls.schema = IMPORTER._git_json(IMPORTER.SCHEMA_RELATIVE)

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT_PATH.read_text()), CERT.build_certificate())

    def test_exact_no_go_and_scope(self) -> None:
        result = CERT.build_certificate()
        self.assertTrue(all(result["exact_import_checks"].values()))
        self.assertTrue(result["claim_flags"]["FINITE_NONZERO_WEIGHT_ROUTE_DECIDED"])
        self.assertFalse(result["cartan_disposition"]["cartan_equation_reached"])
        self.assertIsNone(result["cartan_disposition"]["cartan_obstruction_witness"])
        self.assertEqual(
            result["imported_theorem"]["normalized_dual_leakage_witness"],
            ["80/27", "0", "0"],
        )

    def test_mutations_fail_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["flags"]["NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            IMPORTER.validate_classical_payload(forged, self.schema)

        forged = deepcopy(self.payload)
        forged["first_failed_block"]["normalized_dual_witness"][0] = "1"
        with self.assertRaisesRegex(ValueError, "leakage witness"):
            IMPORTER.validate_classical_payload(forged, self.schema)

        forged = deepcopy(self.payload)
        forged["complex_anisotropy_certificate"]["multipliers_by_target"][1][0] = "0"
        with self.assertRaisesRegex(ValueError, "ideal-membership"):
            IMPORTER.validate_classical_payload(forged, self.schema)

        forged_schema = deepcopy(self.schema)
        forged_schema["additionalProperties"] = True
        with self.assertRaisesRegex(ValueError, "schema identity"):
            IMPORTER.validate_classical_payload(self.payload, forged_schema)


if __name__ == "__main__":
    unittest.main()
