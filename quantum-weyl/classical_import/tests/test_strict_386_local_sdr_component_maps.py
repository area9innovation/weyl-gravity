#!/usr/bin/env python3
"""Mutation tests for the strict 386-row local SDR component maps."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_local_sdr_component_maps.py", "test_local_sdr_builder")
checker = module(HERE / "check_strict_386_local_sdr_component_maps.py", "test_local_sdr_checker")
verifier = module(HERE / "verify_strict_386_local_sdr_component_maps.py", "test_local_sdr_verifier")


class Strict386LocalSdrComponentMapsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_h_coefficient_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["component_maps"]["H_alg"]["entries"][0]["coefficient"] = "2"
        self.assertTrue(checker.check(value))

    def test_homotopy_promotion_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["exact_replay"]["qH_plus_Hq_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_shear_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["coordinate_transport_boundary"]["T_A_B_canonical_shear_serialized"] = True
        value["claim_flags"]["STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED"] = True
        self.assertTrue(checker.check(value))

    def test_gate_and_quantum_promotions_fail(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["gate_disposition"]["one_common_gate_a_snapshot_accepted"] = True
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value))

    def test_snapshot_binding_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["local_sdr_snapshot"]["unary_snapshot_sha256"] = "0" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
