from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PATH = ROOT / "berger_all_weight_cartan_import_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_all_weight_cartan_import_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
IMPORTER = sys.modules[CERT.build_import.__module__]


class BergerAllWeightCartanImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = IMPORTER._git_json(IMPORTER.CERTIFICATE_RELATIVE)
        cls.schema = IMPORTER._git_json(IMPORTER.SCHEMA_RELATIVE)
        cls.q2 = IMPORTER._git_json(IMPORTER.Q2_CERTIFICATE_RELATIVE)

    def test_checked_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(CERT.OUTPUT_PATH.read_text()), CERT.build_certificate())

    def test_nonzero_source_has_nonzero_exact_primitive(self) -> None:
        result = CERT.build_certificate()
        verdict = result["cartan_verdict"]
        self.assertTrue(verdict["source_nonzero_for_generic_nonzero_weights"])
        self.assertTrue(verdict["primitive_nonzero"])
        self.assertEqual(verdict["binary_verdict"], "ADMISSIBLE_EXACT_PRIMITIVE")
        self.assertEqual(verdict["primitive_operator_D_weight"], 0)
        self.assertIsNone(verdict["obstruction_witness"])
        self.assertTrue(all(result["exact_import_checks"].values()))

    def test_physical_and_reduced_mode_boundaries(self) -> None:
        result = CERT.build_certificate()
        self.assertFalse(result["physical_interpretation"]["introduces_negative_physical_direction"])
        self.assertEqual(
            result["physical_interpretation"]["einstein_extra_weyl_coupling"]["status"],
            "NOT_APPLICABLE_AT_NON_EINSTEIN_HOMOGENEOUS_BERGER_BASE_POINT",
        )
        flags = result["claim_flags"]
        self.assertTrue(flags["NONZERO_WEIGHT_D_CARTAN_TESTED"])
        self.assertFalse(flags["FULL_4D_SUPPORT_LOCAL_Q2"])
        self.assertFalse(flags["COMPLETE_54_ROW_ARITY_TWO_D_CARTAN"])
        self.assertFalse(flags["ND2_PHYSICAL_EXECUTION_AUTHORIZED"])

    def test_mutations_fail_closed(self) -> None:
        forged = deepcopy(self.payload)
        forged["flags"]["FULL_4D_SUPPORT_LOCAL_Q2"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            IMPORTER.validate_classical_payload(forged, self.schema, self.q2)

        forged = deepcopy(self.payload)
        forged["arity_two_Cartan_homotopy"]["mixed_sparse_entries"][0][
            "coefficient_equation_weight"
        ] = "0"
        with self.assertRaisesRegex(ValueError, "mixed primitive coefficient"):
            IMPORTER.validate_classical_payload(forged, self.schema, self.q2)

        forged = deepcopy(self.payload)
        forged["coefficients"]["H_inverse"][0][0] = "0"
        with self.assertRaisesRegex(ValueError, "Hessian inverse"):
            IMPORTER.validate_classical_payload(forged, self.schema, self.q2)

        forged_schema = deepcopy(self.schema)
        forged_schema["additionalProperties"] = True
        with self.assertRaisesRegex(ValueError, "schema identity"):
            IMPORTER.validate_classical_payload(self.payload, forged_schema, self.q2)


if __name__ == "__main__":
    unittest.main()
