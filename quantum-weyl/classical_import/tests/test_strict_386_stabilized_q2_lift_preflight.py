#!/usr/bin/env python3
"""Mutation tests for the strict 386-row stabilized-q2 preflight."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


builder = module(HERE / "build_strict_386_stabilized_q2_lift_preflight.py", "test_q2_preflight_builder")
checker = module(HERE / "check_strict_386_stabilized_q2_lift_preflight.py", "test_q2_preflight_checker")
verifier = module(HERE / "verify_strict_386_stabilized_q2_lift_preflight.py", "test_q2_preflight_verifier")


class Strict386StabilizedQ2LiftPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(RESULT.read_text())

    def test_repository_result(self) -> None:
        self.assertEqual(checker.check(self.value), [])
        self.assertEqual(verifier.main(), 0)

    def test_generated_current(self) -> None:
        self.assertEqual(RESULT.read_bytes(), builder.generated()[0])

    def test_component_channel_removal_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_transport_dag"]["expanded_component_channel_ledger"].pop()
        value["graph_transport_dag"]["expanded_ordered_component_channels"] = 139
        self.assertTrue(checker.check(value))

    def test_block_triple_relabel_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_transport_dag"]["block_triple_ledger"][0]["output_block"] = "AUX_ETA"
        self.assertTrue(checker.check(value))

    def test_support_envelope_overclaim_fails(self) -> None:
        value = deepcopy(self.value)
        value["graph_transport_dag"]["support_envelope_warning"] = "Every coefficient is nonzero."
        self.assertTrue(checker.check(value))

    def test_D_q2_defect_fails(self) -> None:
        value = deepcopy(self.value)
        value["identity_transport"]["D_q2_derivation"]["derivation_defects"] = 1
        self.assertTrue(checker.check(value))

    def test_authoritative_import_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["theory_identity_boundary"]["authoritative_full_nonlinear_386_row_export_present"] = True
        value["theory_identity_boundary"]["candidate_equals_authoritative_classical_theory"] = "ESTABLISHED"
        value["claim_flags"]["STRICT_386_AUTHORITATIVE_FULL_Q2_IMPORTED"] = True
        self.assertTrue(checker.check(value))

    def test_common_snapshot_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["candidate_snapshot"]["receiver_status"] = "ACCEPTED"
        value["candidate_snapshot"]["accepted_gate_a_object_hashes"] = 1
        value["claim_flags"]["STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT_ACCEPTED"] = True
        self.assertTrue(checker.check(value))

    def test_gate_and_quantum_promotion_fails(self) -> None:
        value = deepcopy(self.value)
        value["gate_disposition"]["classical_import_gate_a_status"] = "PASS"
        value["claim_flags"]["CLASSICAL_IMPORT_GATE_PASSED"] = True
        value["claim_flags"]["HADAMARD_STATE_CONSTRUCTED"] = True
        value["claim_flags"]["QME_RESTORED"] = True
        self.assertTrue(checker.check(value))

    def test_source_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.assertTrue(checker.check(value))

    def test_candidate_hash_mutation_fails(self) -> None:
        value = deepcopy(self.value)
        value["split_candidate"]["sha256"] = "f" * 64
        self.assertTrue(checker.check(value))


if __name__ == "__main__":
    unittest.main()
