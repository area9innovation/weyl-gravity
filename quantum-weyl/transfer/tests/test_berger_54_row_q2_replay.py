from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

import sympy as sp


TRANSFER_ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, TRANSFER_ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


REPLAY = _load("berger_54_row_q2_replay", "berger_54_row_q2_replay.py")
CERTIFICATE = _load(
    "berger_54_row_q2_replay_certificate_test",
    "berger_54_row_q2_replay_certificate.py",
)
SCHEMA_PATH = TRANSFER_ROOT / "schema/berger-54-row-q2-replay-engine-v1.schema.json"


class Berger54RowQ2ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = REPLAY.build_replay_engine_payload()

    def test_noncommutative_pbw_reduction(self) -> None:
        self.assertEqual(
            REPLAY.pbw_word((2, 1)),
            (((1, 2), sp.S.One), ((3,), -REPLAY.U)),
        )

    def test_nonzero_fixture_replays_all_three_identities(self) -> None:
        fixture = self.payload["implementation_fixture"]
        self.assertTrue(fixture["all_identities_pass"])
        self.assertEqual(
            {name: result["nonzero_coefficient_count"] for name, result in fixture["results"].items()},
            {
                "q1_q2_arity_two_nilpotency": 0,
                "D_q2_derivation": 0,
                "BV_cyclicity_q2": 0,
            },
        )

    def test_valid_degree_output_mutation_is_localized(self) -> None:
        mutation = self.payload["mutation_sensitivity"]["output_row_mutation"]
        self.assertTrue(mutation["q1_q2_detected"])
        self.assertTrue(mutation["cyclicity_detected"])
        q1_sample = mutation["localized_results"]["q1_q2_arity_two_nilpotency"]["localized_sample"]
        cyclic_sample = mutation["localized_results"]["BV_cyclicity_q2"]["localized_sample"]
        self.assertEqual(q1_sample[0]["output"], 49)
        self.assertEqual((cyclic_sample[0]["first"], cyclic_sample[0]["second"], cyclic_sample[0]["third"]), (5, 5, 6))

    def test_D_axis_mutation_is_localized(self) -> None:
        mutation = self.payload["mutation_sensitivity"]["D_axis_mutation"]
        self.assertTrue(mutation["D_derivation_detected"])
        result = mutation["localized_result"]
        self.assertEqual(result["status"], "FAIL")
        self.assertGreater(result["nonzero_coefficient_count"], 0)
        self.assertEqual(result["localized_sample"][0]["output"], 27)

    def test_schema_and_checked_certificate_reproduce(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(certificate))
        for field in ("schema", "result_id", "result_state", "lifecycle_layer", "setting_id"):
            self.assertEqual(schema["properties"][field]["const"], certificate[field])
        self.assertEqual(json.loads(CERTIFICATE.OUTPUT.read_text()), certificate)

    def test_claim_boundary_remains_fail_closed(self) -> None:
        self.assertEqual(
            set(self.payload["prerequisite_binding"]["operator_hashes"]),
            {"q1_sha256", "D54_sha256", "iota_sha256", "pi_sha256", "S_sha256", "pairing_sha256"},
        )
        self.assertEqual(self.payload["input_gate"]["status"], "INPUT_BLOCKED")
        self.assertFalse(self.payload["claim_flags"]["CLASSICAL_SUPPORT_LOCAL_Q2_IMPORTED"])
        self.assertFalse(self.payload["claim_flags"]["SCIENTIFIC_ARITY_TWO_IDENTITIES_REPLAYED"])
        self.assertFalse(self.payload["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
