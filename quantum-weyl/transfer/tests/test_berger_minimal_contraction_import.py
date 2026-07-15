from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


TRANSFER_ROOT = Path(__file__).resolve().parents[1]
if str(TRANSFER_ROOT) not in sys.path:
    sys.path.insert(0, str(TRANSFER_ROOT))
MODULE_PATH = TRANSFER_ROOT / "berger_minimal_contraction_import_certificate.py"
SPEC = importlib.util.spec_from_file_location(
    "berger_minimal_contraction_import_certificate_test", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
CERTIFICATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERTIFICATE
SPEC.loader.exec_module(CERTIFICATE)
IMPORT = sys.modules[CERTIFICATE.build_import.__module__]


class BergerMinimalContractionImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORT._git_json(IMPORT.CERTIFICATE_RELATIVE)
        cls.schema = IMPORT._git_json(IMPORT.SCHEMA_RELATIVE)
        cls.retained_q1 = IMPORT._git_json(IMPORT.Q1_RELATIVE)
        cls.retained_schema = IMPORT._git_json(IMPORT.Q1_SCHEMA_RELATIVE)
        cls.retained_layout = IMPORT._git_json(IMPORT.LAYOUT_RELATIVE)
        cls.clock_sdr = IMPORT._git_json(IMPORT.CLOCK_RELATIVE)

    def test_checked_in_certificate_reproduces(self) -> None:
        checked = json.loads(CERTIFICATE.OUTPUT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(checked, CERTIFICATE.build_certificate())

    def test_complete_minimal_contraction_closes_only_its_nd2_artifact(self) -> None:
        result = CERTIFICATE.build_certificate()
        self.assertTrue(result["coverage"]["complete_minimal_classical_contraction"])
        self.assertEqual(result["coverage"]["full_minimal_rows"], 34)
        self.assertEqual(result["coverage"]["retained_minimal_rows"], 26)
        self.assertTrue(result["nd2_gate"]["classical_contraction_artifact_satisfied"])
        self.assertEqual(result["nd2_gate"]["support_local_q1_q2_D"], "NOT_AVAILABLE")
        self.assertEqual(result["nd2_gate"]["D_equivariance"], "NOT_COMPUTED")
        self.assertFalse(result["nd2_gate"]["physical_execution_authorized"])

    def test_chain_cyclic_pairing_and_cohomology_checks_are_explicit(self) -> None:
        checks = CERTIFICATE.build_certificate()["independent_checks"]
        for name in (
            "classical_unary_q1_squared_zero",
            "full_classical_unary_q1_cyclic",
            "iota_cl_chain_map",
            "pi_cl_chain_map",
            "all_row_contraction_identity",
            "contraction_side_conditions",
            "homotopy_cyclic",
            "full_pairing_nondegenerate",
            "retained_pairing_nondegenerate",
            "projection_pairing_compatible",
            "retained_complex_cohomology_preserved_by_SDR",
        ):
            self.assertTrue(checks[name], name)

    def test_dependency_and_map_hash_drift_fail_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["dependency_refs"]["clock_sdr"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dependency hash drifted"):
            self._validate(forged)
        forged = deepcopy(self.payload)
        forged["contraction"]["S_cl"]["entries"][0][2][0][1] = "2"
        with self.assertRaisesRegex(ValueError, "record hash mismatch"):
            self._validate(forged)

    def test_schema_and_claim_promotion_fail_closed(self) -> None:
        forged_schema = deepcopy(self.schema)
        forged_schema["additionalProperties"] = True
        with self.assertRaisesRegex(ValueError, "schema identity or strictness"):
            IMPORT.validate_portable_contraction(
                self.payload,
                forged_schema,
                self.retained_q1,
                self.retained_schema,
                self.retained_layout,
                self.clock_sdr,
            )
        forged = deepcopy(self.payload)
        forged["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] = True
        with self.assertRaisesRegex(ValueError, "flags crossed"):
            self._validate(forged)

    def _validate(self, payload: dict[str, object]) -> dict[str, object]:
        return IMPORT.validate_portable_contraction(
            payload,
            self.schema,
            self.retained_q1,
            self.retained_schema,
            self.retained_layout,
            self.clock_sdr,
        )


if __name__ == "__main__":
    unittest.main()
