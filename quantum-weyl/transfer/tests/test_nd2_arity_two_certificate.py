from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = TRANSFER_ROOT / "nd2_arity_two_certificate.py"
SPEC = importlib.util.spec_from_file_location("nd2_arity_two_certificate", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)


class ND2ArityTwoCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_schema_receipt_is_present_and_pinned(self) -> None:
        schema_path = TRANSFER_ROOT / "schema" / "nd2-arity-two-cartan-engine-v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(
            schema["properties"]["result_id"]["const"],
            "ND2_ARITY_TWO_CARTAN_ENGINE",
        )
        self.assertEqual(
            CERTIFICATE.build_certificate()["provenance"]["schema"],
            "quantum-weyl/transfer/schema/nd2-arity-two-cartan-engine-v1.schema.json",
        )

    def test_exact_correction_and_obstruction_rails_are_both_live(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        exact = certificate["exact_correction_fixture"]
        self.assertEqual(exact["classification"], "EXACT_CORRECTION")
        self.assertTrue(exact["correction_identity"])
        self.assertTrue(all(exact["checks"].values()))
        self.assertEqual(
            certificate["obstruction_fixture"]["classification"],
            "NONTRIVIAL_OBSTRUCTION",
        )
        self.assertTrue(certificate["obstruction_fixture"]["dual_witness"])

    def test_mutation_and_admissibility_gates_fail_closed(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertTrue(certificate["mutation_fixture"]["nonzero_defect_detected"])
        self.assertEqual(
            certificate["mutation_fixture"]["solver_gate"],
            "REJECTED_BEFORE_CORRECTION_CLASSIFICATION",
        )
        admissibility = certificate["admissibility_fixture"]
        self.assertEqual(admissibility["ambient_classification"], "EXACT_CORRECTION")
        self.assertEqual(
            admissibility["admissible_classification"],
            "NONTRIVIAL_OBSTRUCTION",
        )

    def test_physical_claim_stays_behind_the_input_gate(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertEqual(certificate["setting_verdict"], "INPUT_GATE_BLOCKED")
        self.assertTrue(
            all(value.startswith("NOT_") for value in certificate["input_gate"].values())
        )
        self.assertTrue(
            any("conformal-gravity" in claim for claim in certificate["not_established"])
        )


if __name__ == "__main__":
    unittest.main()
