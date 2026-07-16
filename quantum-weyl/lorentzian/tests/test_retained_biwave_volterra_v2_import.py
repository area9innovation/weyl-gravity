from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.retained_biwave_volterra_v2_import import validate_import
from lorentzian.retained_biwave_volterra_v2_import_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class RetainedBiwaveVolterraV2ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (ROOT / "schema/berger-retained-biwave-volterra-v2-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_all_eight_historical_defects_are_closed(self) -> None:
        self.assertEqual(len(self.certificate["repair_closure"]), 8)
        self.assertTrue(all(self.certificate["source_import"]["proof_checks"].values()))
        self.assertTrue(all(self.certificate["source_import"]["provenance_checks"].values()))

    def test_metric_green_and_D_compatibility_are_imported(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["BERGER_RETAINED_METRIC_GREEN_OPERATORS_IMPORTED"])
        self.assertTrue(flags["BERGER_RETAINED_BIWAVE_D_EQUIVARIANT"])
        self.assertTrue(flags["BERGER_RETAINED_BIWAVE_FORMAL_ADJOINT_BUNDLE_READY"])

    def test_downstream_claims_remain_open(self) -> None:
        for flag in (
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
            "BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2",
            "BERGER_CAUSAL_D_CARTAN_V2",
            "BERGER_HADAMARD_DATA",
            "QUANTUM_CLAIM",
        ):
            self.assertFalse(self.certificate["claim_flags"][flag])

    def test_source_import_mutation_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["source_import"]["commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source import receipt"):
            validate_import(mutant)

    def test_downstream_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2"] = True
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            validate_import(mutant)


if __name__ == "__main__":
    unittest.main()
