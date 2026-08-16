from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
CHECKER = HERE / "check_strict_centered_cohomology_payload.py"
RESULT = HERE / "certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"
SCHEMA = HERE / "schema/strict-centered-cohomology-payload-v1.schema.json"
REPORT = HERE / "REPORT_STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checker = load(CHECKER, "strict_centered_cohomology_checker")


def repin_representatives(value: dict) -> None:
    representatives = value["normalized_H4_representatives"]
    vector = representatives["W_plus_squared_times_v_minus"]
    vector_body = {key: vector[key] for key in ("dimension", "coefficient_field", "encoding", "radicand", "entries")}
    vector["sha256"] = checker.digest(vector_body)
    rep_body = {key: representatives[key] for key in (
        "carrier", "ghost_vacuum", "two_particle_C4_global_offset", "construction",
        "W_plus_squared_times_v_minus", "W_minus_squared_times_v_minus",
        "two_particle_pairing", "two_particle_parity", "normalized_gram",
        "parity_action_in_chiral_basis", "interpretation",
    )}
    representatives["sha256"] = checker.digest(rep_body)
    value["canonical_hashes"]["representatives_sha256"] = representatives["sha256"]
    snapshot = value["centered_snapshot"]
    snapshot["canonical_hashes"] = value["canonical_hashes"]
    snapshot_body = {key: snapshot[key] for key in ("theory", "background", "canonical_hashes", "input_sha256")}
    snapshot["sha256"] = checker.digest(snapshot_body)
    value["independent_checker"]["expected_digest"] = checker.digest({
        "ordered_centered_cochain_basis": value["ordered_centered_cochain_basis"],
        "coefficient_modules": value["coefficient_modules"],
        "centered_differential_summary": value["centered_differential_summary"],
        "normalized_H4_representatives": representatives,
        "centered_snapshot": snapshot,
        "claim_flags": value["claim_flags"],
    })


class StrictCenteredCohomologyPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_repository_payload_replays(self):
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])
        self.assertEqual(self.value["scope"]["centered_cochain_dimensions_C3_C4_C5"], [727, 3084, 8532])
        self.assertEqual(self.value["centered_differential_summary"]["aggregate_ranks_d3_d4"], [636, 2446])

    def test_schema_and_report(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertIn("not one-particle states", REPORT.read_text(encoding="utf-8"))

    def test_representative_mutation_fails_after_repin(self):
        value = copy.deepcopy(self.value)
        value["normalized_H4_representatives"]["W_plus_squared_times_v_minus"]["entries"][0][1] = "1"
        repin_representatives(value)
        self.assertTrue(checker.check(value))

    def test_basis_order_mutation_fails(self):
        value = copy.deepcopy(self.value)
        entries = value["ordered_centered_cochain_basis"]["degrees"]["3"]["entries"]
        entries[0], entries[1] = entries[1], entries[0]
        self.assertTrue(checker.check(value, algebra=False))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value, algebra=False))

    def test_provenance_drift_fails(self):
        value = copy.deepcopy(self.value)
        value["centered_snapshot"]["input_sha256"]["bridge/transfer/integration.py"] = "0" * 64
        self.assertTrue(checker.check(value, algebra=False))


if __name__ == "__main__":
    unittest.main()
