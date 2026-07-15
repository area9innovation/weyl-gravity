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
PATH = ROOT / "berger_reduced_mode_cartan_certificate.py"
SPEC = importlib.util.spec_from_file_location("berger_reduced_mode_cartan_certificate_test", PATH)
assert SPEC is not None and SPEC.loader is not None
CERT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CERT
SPEC.loader.exec_module(CERT)
ADAPTER = sys.modules[CERT.build_verdict.__module__]


class BergerReducedModeCartanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.receipt = ADAPTER.build_verdict().import_receipt
        cls.schema = json.loads((ROOT / "schema/berger-first-arity-two-cartan-verdict-v1.schema.json").read_text())

    def test_checked_certificate_reproduces_and_validates(self) -> None:
        built = CERT.build_certificate()
        self.assertEqual(json.loads(CERT.OUTPUT.read_text()), built)
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_real_nonzero_block_reaches_exact_solver(self) -> None:
        result = ADAPTER.build_verdict()
        self.assertEqual(result.import_receipt["imported_block"]["q2_nonzero_canonical_count"], 18)
        self.assertEqual(result.engine_classification.status, "ZERO_SOURCE")
        self.assertTrue(result.primitive.is_zero())
        self.assertTrue(all(result.data.checks().values()))

    def test_binary_verdict_and_physical_boundary(self) -> None:
        result = CERT.build_certificate()
        equation = result["cartan_equation"]
        self.assertEqual(equation["binary_verdict"], "ADMISSIBLE_EXACT_PRIMITIVE")
        self.assertEqual(equation["primitive"]["operator"], "iota_D^(2)=0")
        self.assertEqual(equation["primitive"]["D_weight"], 0)
        self.assertIsNone(equation["obstruction_witness"])
        physical = result["physical_interpretation"]
        self.assertFalse(physical["introduces_negative_physical_direction"])
        self.assertEqual(physical["degree_zero_cohomology_dimension"], 0)
        self.assertEqual(
            physical["einstein_extra_weyl_coupling"]["status"],
            "NOT_APPLICABLE_AT_NON_EINSTEIN_BERGER_BASE_POINT",
        )

    def test_reduced_mode_flags_fail_closed(self) -> None:
        flags = CERT.build_certificate()["claim_flags"]
        self.assertTrue(flags["BERGER_REDUCED_MODE_ARITY_TWO_CARTAN_EXISTS"])
        for name in (
            "BERGER_SUPPORT_LOCAL_ARITY_TWO_CARTAN_EXISTS",
            "NONZERO_WEIGHT_D_OBSTRUCTION_TESTED",
            "EINSTEIN_EXTRA_WEYL_BRANCH_COUPLING_CLASSIFIED",
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
            "ND2_FULL_PHYSICAL_EXECUTION_AUTHORIZED",
            "QME_RESTORED",
            "LORENTZIAN_CERTIFIED",
        ):
            self.assertFalse(flags[name])

    def test_input_mutations_are_rejected_before_verdict(self) -> None:
        forged = deepcopy(self.receipt)
        forged["dependency_tags"] = ["LOCAL-ALGEBRAIC"]
        with self.assertRaisesRegex(ValueError, "identity drifted"):
            ADAPTER.validate_import_receipt(forged)

        forged = deepcopy(self.receipt)
        forged["imported_block"]["input_D_weights"][0] = 1
        with self.assertRaisesRegex(ValueError, "imported block drifted"):
            ADAPTER.validate_import_receipt(forged)

        forged = deepcopy(self.receipt)
        forged["imported_block"]["q2_nonzero_canonical_count"] = 0
        with self.assertRaisesRegex(ValueError, "imported block drifted"):
            ADAPTER.validate_import_receipt(forged)

        forged = deepcopy(self.receipt)
        forged["nd2_classification"]["status"] = "NONTRIVIAL_OBSTRUCTION"
        with self.assertRaisesRegex(ValueError, "Cartan source drifted"):
            ADAPTER.validate_import_receipt(forged)

        forged = deepcopy(self.receipt)
        forged["authorization"]["physical_ND2_execution"] = True
        with self.assertRaisesRegex(ValueError, "authorization boundary"):
            ADAPTER.validate_import_receipt(forged)


if __name__ == "__main__":
    unittest.main()
