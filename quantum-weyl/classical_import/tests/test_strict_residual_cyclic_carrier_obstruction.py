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
SOURCE = HERE / "build_strict_residual_cyclic_carrier_obstruction.py"
CHECKER = HERE / "check_strict_residual_cyclic_carrier_obstruction.py"
RESULT = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.md"
SCHEMA = HERE / "schema/strict-residual-cyclic-carrier-obstruction-v1.schema.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_residual_cyclic_carrier_obstruction_source")
checker = load(CHECKER, "strict_residual_cyclic_carrier_obstruction_checker")


class StrictResidualCyclicCarrierObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current_schema_and_independent_replay(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_rank_zero_obstruction_is_exact(self):
        replay = self.value["obstruction_replay"]
        self.assertEqual(replay["m3r_inclusion_degree_counts"], {"0": 470})
        self.assertEqual(replay["m3r_inclusion_sector_counts"], {"metric_tf": 470})
        self.assertEqual(replay["endpoint_metric_metric_pairing_nonzeros"], 0)
        self.assertEqual(replay["pulled_back_odd_pairing_rank"], 0)
        self.assertEqual(replay["nondegeneracy_rank_defect"], 470)

    def test_cotangent_preflight_is_full_rank(self):
        preflight = self.value["cotangent_preflight"]
        self.assertEqual(preflight["total_dimension"], 940)
        self.assertEqual(preflight["constructive_exact_rank"], 940)
        self.assertEqual(len(preflight["pair_dictionary"]), 470)
        self.assertEqual(
            {item["dual_index"] for item in preflight["pair_dictionary"]},
            set(range(470, 940)),
        )

    def test_even_form_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["OLDER_EVEN_COHOMOLOGY_FORM_IS_BV_ANTIBRACKET"] = True
        self.assertTrue(checker.check(value))

    def test_rank_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["obstruction_replay"]["pulled_back_odd_pairing_rank"] = 470
        self.assertTrue(checker.check(value))

    def test_cotangent_transport_promotion_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["FINITE_940_PAIRING_IDENTIFIED_WITH_ACTION_BV_PAIRING"] = True
        self.assertTrue(checker.check(value))

    def test_quantum_promotions_fail(self):
        for flag in (
            "M3RC_DUAL_COMPARISON_MAPS_CONSTRUCTED",
            "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
            "CLASSICAL_IMPORT_GATE_PASSED",
            "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
            "QME_RESTORED",
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        ):
            with self.subTest(flag=flag):
                value = copy.deepcopy(self.value)
                value["claim_flags"][flag] = True
                self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
