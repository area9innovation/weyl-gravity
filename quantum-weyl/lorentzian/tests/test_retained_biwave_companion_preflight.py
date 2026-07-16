from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.retained_biwave_companion_preflight import validate_preflight_result
from lorentzian.retained_biwave_companion_preflight_certificate import (
    OUTPUT,
    ROOT,
    build_certificate,
)


class RetainedBiwaveCompanionPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_certificate_reproduces_and_validates(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                ROOT
                / "schema/berger-retained-biwave-companion-preflight-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_retained_projection_and_companion_are_exact(self) -> None:
        self.assertTrue(all(self.certificate["exact_checks"].values()))
        self.assertEqual(
            self.certificate["retained_endpoint"]["metric_identity"],
            "P26_metric=A10=Box_2^2+V_2",
        )
        self.assertEqual(
            self.certificate["companion_system"]["principal_determinant"],
            "q^20",
        )
        self.assertFalse(
            self.certificate["companion_system"]["extra_characteristic_cone"]
        )

    def test_green_and_quantum_promotions_fail_closed(self) -> None:
        for flag in (
            "BERGER_RETAINED_BIWAVE_CAUSAL_RESOLVENT",
            "BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.certificate)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "lifecycle"):
                validate_preflight_result(mutant)

    def test_unproved_volterra_policy_cannot_be_promoted(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["causal_policy"][
            "volterra_convergence_and_global_support_proof"
        ] = "PROVED"
        with self.assertRaisesRegex(ValueError, "causal policy"):
            validate_preflight_result(mutant)


if __name__ == "__main__":
    unittest.main()
