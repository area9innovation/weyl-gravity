from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import sys
import unittest


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_rational_fixture_q2_d_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_rational_fixture_q2_d_import_certificate_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)


class BergerRationalFixtureQ2DImportTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_nd2_exact_identities_pass(self) -> None:
        payload = CERTIFICATE.build_certificate()
        self.assertTrue(all(payload["nd2_checks"].values()))
        self.assertEqual(payload["nd2_classification"]["status"], "ZERO_SOURCE")
        self.assertEqual(payload["imported_block"]["coefficient_domain"], "Q")

    def test_validated_input_exposes_exact_zero_primitive(self) -> None:
        importer = sys.modules[CERTIFICATE.build_import.__module__]
        data = importer.assemble_cartan_data()
        classification = data.classify()
        primitive = data.complex.solve_boundary(
            classification.source.scaled(-1, name="minus_A_D_2")
        )
        self.assertEqual(classification.status, "ZERO_SOURCE")
        self.assertIsNotNone(primitive)
        self.assertTrue(primitive.is_zero())

    def test_scope_remains_reduced_mode(self) -> None:
        authorization = CERTIFICATE.build_certificate()["authorization"]
        self.assertTrue(authorization["reduced_mode_solver_input"])
        self.assertFalse(authorization["full_support_local_q2"])
        self.assertFalse(authorization["nonzero_weight_D_equivariance"])
        self.assertFalse(authorization["physical_ND2_execution"])

    def test_classical_source_is_pinned(self) -> None:
        source = CERTIFICATE.build_certificate()["classical_source"]
        self.assertEqual(source["commit"], "74311edb2fb907060e86f740977439f4db8b0ed5")
        self.assertTrue(all(len(artifact["sha256"]) == 64 for artifact in source["artifacts"].values()))


if __name__ == "__main__":
    unittest.main()
