from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "build_strict_residual_zero_mode_payload.py"
CHECKER = HERE / "check_strict_residual_zero_mode_payload.py"
RESULT = HERE / "certificates/STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.json"
REPORT = HERE / "REPORT_STRICT_RESIDUAL_ZERO_MODE_PAYLOAD_V1.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = load(SOURCE, "strict_residual_zero_mode_source")
checker = load(CHECKER, "strict_residual_zero_mode_checker")


def repin(value: dict) -> None:
    structure = value["so42_structure_constants"]
    body = {key: structure[key] for key in (
        "convention", "generator_order", "generator_compact_degrees",
        "entries", "tensor_shape",
    )}
    structure["sha256"] = checker.digest(body)
    value["residual_differential_q_res_0"]["nonlinear_CE_structure_sha256"] = structure["sha256"]
    q_res = value["residual_differential_q_res_0"]
    q_body = {key: q_res[key] for key in (
        "carrier_order", "degree_zero_unary_matrix", "meaning", "nonlinear_CE_structure_sha256",
    )}
    q_res["sha256"] = checker.digest(q_body)
    value["canonical_hashes"]["structure_constants_sha256"] = structure["sha256"]
    value["canonical_hashes"]["q_res_0_sha256"] = q_res["sha256"]
    value["residual_snapshot"]["canonical_hashes"] = value["canonical_hashes"]
    snapshot = value["residual_snapshot"]
    snapshot_body = {key: snapshot[key] for key in ("theory", "background", "canonical_hashes", "input_sha256")}
    snapshot["sha256"] = checker.digest(snapshot_body)
    value["independent_checker"]["expected_digest"] = checker.digest({
        "zero_mode_basis": value["zero_mode_basis"],
        "so42_structure_constants": structure,
        "residual_representation": value["residual_representation"],
        "residual_differential_q_res_0": q_res,
        "residual_snapshot": snapshot,
        "claim_flags": value["claim_flags"],
    })


class StrictResidualZeroModePayloadTests(unittest.TestCase):
    def test_generated_current(self):
        certificate, report = producer.generated()
        self.assertEqual(RESULT.read_bytes(), certificate)
        self.assertEqual(REPORT.read_bytes(), report)

    def test_repository_payload_replays(self):
        value = json.loads(RESULT.read_text())
        self.assertEqual(checker.check(value), [])
        self.assertEqual(value["scope"]["primal_dimension"], 15)
        self.assertEqual(len(value["residual_representation"]["matrices"]), 15)

    def test_structure_mutation_fails_after_full_repin(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["so42_structure_constants"]["entries"][0][3] = "2"
        repin(value)
        self.assertTrue(checker.check(value))

    def test_primal_basis_mutation_fails(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["zero_mode_basis"]["matrices"]["primal_basis_Z"]["entries"][0][2] = "2"
        self.assertTrue(checker.check(value))

    def test_false_gate_promotion_fails(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        self.assertTrue(checker.check(value))

    def test_provenance_drift_fails(self):
        value = copy.deepcopy(json.loads(RESULT.read_text()))
        value["residual_snapshot"]["input_sha256"]["bridge/zero_modes/ckv_projector.py"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
