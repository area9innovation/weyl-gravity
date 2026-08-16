from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_residual_sdr_type_audit.py"
CHECKER = HERE / "check_strict_residual_sdr_type_audit.py"
RESULT = HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_residual_sdr_type_audit_source")
checker = load(CHECKER, "strict_residual_sdr_type_audit_checker")


class StrictResidualSdrTypeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_independent_replay(self):
        self.assertEqual(checker.check(copy.deepcopy(self.value)), [])

    def test_dimension_collision_cannot_promote_identity(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["GRAPH_ENDPOINT_30_IS_FINITE_RESIDUAL_30"] = True
        self.assertTrue(checker.check(value))

    def test_mode_projector_cannot_promote_locality(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["DFINITE_RESIDUAL_PROJECTOR_SUPPORT_LOCAL"] = True
        self.assertTrue(checker.check(value))

    def test_fixture_mutation_fails(self):
        value = copy.deepcopy(self.value)
        value["support_locality_obstruction"]["finite_exact_fixture"]["harmonic_projector"][0][0] = "1"
        self.assertTrue(checker.check(value))

    def test_unsplit_m3_fails(self):
        value = copy.deepcopy(self.value)
        value["claim_flags"]["M3_TYPED_SPLIT_REQUIRED"] = False
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
