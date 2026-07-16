from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_causal_chain_v2_import import validate_import
from lorentzian.berger_causal_chain_v2_import_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class BergerCausalChainV2ImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (ROOT / "schema/berger-causal-chain-v2-import-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_complete_causal_coverage(self) -> None:
        coverage = self.certificate["coverage"]
        self.assertEqual(coverage["retained_rows"], 26)
        self.assertEqual(coverage["complete_rows"], 54)
        self.assertEqual(coverage["D_Cartan_arities"], [1, 2])
        self.assertTrue(
            all(all(group.values()) for group in coverage["checks"].values())
        )

    def test_imported_claims_and_open_gates(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"])
        self.assertTrue(flags["BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2_IMPORTED"])
        self.assertTrue(flags["BERGER_CAUSAL_D_CARTAN_V2_IMPORTED"])
        self.assertFalse(flags["BERGER_ARITY_THREE_D_CARTAN"])
        self.assertFalse(flags["BERGER_HADAMARD_DATA"])
        self.assertFalse(flags["QUANTUM_CLAIM"])

    def test_downstream_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_HADAMARD_DATA"] = True
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            validate_import(mutant)

    def test_check_deletion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        del mutant["coverage"]["checks"]["causal_D_Cartan"]
        with self.assertRaisesRegex(ValueError, "check dropped"):
            validate_import(mutant)


if __name__ == "__main__":
    unittest.main()
