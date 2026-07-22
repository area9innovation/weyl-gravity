from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / "black_hole_programme/phase2/general_l_polar_completion"
PRODUCER = HERE / "produce.py"
VERIFIER = HERE / "verify.py"
CERT = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


class PolarCanonicalFrontierTest(unittest.TestCase):
    def test_regeneration_and_independent_verifier(self):
        subprocess.run(["python3", str(PRODUCER), "--check"], cwd=ROOT, check=True)
        subprocess.run(["python3", str(VERIFIER)], cwd=ROOT, check=True)

    def test_schema_covers_assembly_and_each_branch(self):
        schema = json.loads(SCHEMA.read_text())
        jsonschema.validate(json.loads(CERT.read_text()), schema)
        for path in sorted((HERE / "branch_artifacts").glob("*.json")):
            jsonschema.validate(json.loads(path.read_text()), schema)

    def test_log_and_current_promotions_fail_closed(self):
        data = json.loads(CERT.read_text())
        self.assertIn(
            "complete resonant log-degree and carrier-splitting classification",
            data["unavailable_theorem_fields"],
        )
        self.assertIn("branch-specialized EE/EX/XX leading table", data["unavailable_theorem_fields"])
        self.assertEqual(data["resonant_log_discrepancy"]["status"], "NONEXTENDIBLE_SHALLOW_SOURCE_ARTIFACT")

    def test_branch_schema_rejects_complete_log_promotion(self):
        schema = json.loads(SCHEMA.read_text())
        branch = json.loads((HERE / "branch_artifacts/oscillatory-1.json").read_text())
        mutated = copy.deepcopy(branch)
        mutated["complete_log_classification"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(mutated, schema)


if __name__ == "__main__":
    unittest.main()
