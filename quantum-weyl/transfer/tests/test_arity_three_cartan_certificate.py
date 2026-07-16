from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
QUANTUM_ROOT = TRANSFER_ROOT.parent
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
if str(QUANTUM_ROOT) not in sys.path:
    sys.path.insert(0, str(QUANTUM_ROOT))
from local_bv.schema_validation import validate_instance

MODULE_PATH = TRANSFER_ROOT / "arity_three_cartan_certificate.py"
SPEC = importlib.util.spec_from_file_location("arity_three_cartan_certificate_test_module", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)


class ArityThreeCartanCertificateTests(unittest.TestCase):
    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())
        schema = json.loads(
            (TRANSFER_ROOT / "schema/arity-three-cartan-engine-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(validate_instance(checked, schema))

    def test_direct_exchange_and_obstruction_branches_are_live(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["direct_q3_fixture"]["classification"], "EXACT_CORRECTION")
        self.assertTrue(certificate["direct_q3_fixture"]["correction_identity"])
        self.assertTrue(certificate["exchange_fixture"]["exchange_nonzero"])
        self.assertEqual(
            certificate["obstruction_fixture"]["classification"],
            "NONTRIVIAL_OBSTRUCTION",
        )

    def test_lower_physical_chain_is_current_and_q3_remains_gated(self) -> None:
        certificate = CERTIFICATE.build_certificate()
        self.assertEqual(certificate["setting_verdict"], "INPUT_GATE_BLOCKED")
        gate = certificate["input_gate"]
        self.assertEqual(
            gate["support_local_classical_bv_q2"],
            "IMPORTED_AND_INDEPENDENTLY_REPLAYED_54_ROWS",
        )
        self.assertEqual(
            gate["physical_iota_D2"],
            "CERTIFIED_CAUSAL_CYCLIC_TWO_SIDED_54_ROWS",
        )
        self.assertTrue(
            gate["support_local_classical_bv_q3"].startswith("NOT_AVAILABLE")
        )
        self.assertFalse(gate["physical_arity_three_execution_authorized"])
        self.assertTrue(
            any("conformal-gravity q3" in claim for claim in certificate["not_established"])
        )

    def test_mutated_q2_prerequisite_is_rejected(self) -> None:
        inputs = CERTIFICATE._load_current_inputs()
        mutant = deepcopy(inputs)
        mutant["support_local_q2_replay"]["claim_flags"][
            "SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED"
        ] = False
        with self.assertRaisesRegex(ValueError, "support-local q2"):
            CERTIFICATE._validate_current_inputs(mutant)

    def test_mutated_causal_iota_D2_prerequisite_is_rejected(self) -> None:
        inputs = CERTIFICATE._load_current_inputs()
        mutant = deepcopy(inputs)
        mutant["causal_chain_v2"]["coverage"]["checks"]["causal_D_Cartan"][
            "arity_two_cyclic_primitive"
        ] = False
        with self.assertRaisesRegex(ValueError, "causal arity-two"):
            CERTIFICATE._validate_current_inputs(mutant)


if __name__ == "__main__":
    unittest.main()
