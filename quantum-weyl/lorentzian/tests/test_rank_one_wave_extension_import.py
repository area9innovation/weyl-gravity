from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian import rank_one_wave_extension_import as IMPORT
from lorentzian.rank_one_wave_extension_import_certificate import OUTPUT, ROOT, build_certificate


class RankOneWaveExtensionImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads((ROOT / "schema/berger-rank-one-wave-extension-import-v1.schema.json").read_text())
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_exact_extension_without_green_promotion(self) -> None:
        self.assertTrue(all(self.certificate["independent_exact_checks"].values()))
        self.assertTrue(self.certificate["claim_flags"]["BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION"])
        self.assertFalse(self.certificate["claim_flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"])
        self.assertEqual(self.certificate["next_gate"], "BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS")

    def test_mutated_lifecycle_and_artifact_fail_closed(self) -> None:
        source = deepcopy(IMPORT._git_json(IMPORT.CERTIFICATE))
        schema = IMPORT._git_json(IMPORT.SCHEMA)
        raw = json.loads(IMPORT.RAW_IMPORT.read_text())
        source["flags"]["BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS"] = True
        with self.assertRaisesRegex(ValueError, "schema validation|lifecycle"):
            IMPORT.validate_import(source, schema, raw)
        source = IMPORT._git_json(IMPORT.CERTIFICATE)
        source["prolongation"]["artifacts"]["prolonged_L13"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact hash"):
            IMPORT.validate_import(source, schema, raw)


if __name__ == "__main__":
    unittest.main()
