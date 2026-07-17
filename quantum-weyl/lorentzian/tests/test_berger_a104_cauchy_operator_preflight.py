from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_a104_cauchy_operator_preflight import validate
from lorentzian.berger_a104_cauchy_operator_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_a104_cauchy_operator_preflight import verify


class BergerA104CauchyOperatorPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.artifacts = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-a104-cauchy-operator-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_two_exact_A40_operators_cover_metric_A80(self) -> None:
        ledgers = self.certificate["metric_Cauchy_operators"]
        self.assertEqual(set(ledgers), {"metric", "metric_antifield"})
        for ledger in ledgers.values():
            self.assertEqual(ledger["first_order_Cauchy_rank"], 40)
            self.assertEqual(ledger["temporal_leading_rank"], 20)
            self.assertTrue(all(ledger["checks"].values()))
        self.assertEqual(
            self.certificate["partial_A104_assembly"][
                "certified_Cauchy_components"
            ],
            80,
        )

    def test_all_exact_operator_artifacts_are_emitted(self) -> None:
        self.assertEqual(len(self.artifacts), 10)
        self.assertEqual(
            {len(payload["shape"]) for payload in self.artifacts.values()}, {2}
        )

    def test_row_ledger_is_complete_but_pairing_is_open(self) -> None:
        ledger = self.certificate["Cauchy_row_ledger"]
        self.assertEqual(len(ledger["rows"]), 104)
        self.assertEqual(ledger["degree_ranks"], [12, 40, 40, 12])
        self.assertTrue(all(ledger["checks"].values()))
        self.assertEqual(
            ledger["pairing_partner_status"],
            "NOT_DERIVED_REQUIRES_CAUCHY_LAGRANGE_FORM",
        )

    def test_missing_endpoint_carrier_is_exactly_named(self) -> None:
        missing = self.certificate["minimal_missing_endpoint_carrier"]
        self.assertEqual(len(missing["required_factor_record_ids"]), 4)
        self.assertIn("do not reconstruct", missing["forbidden_fallback"])
        self.assertEqual(
            self.certificate["partial_A104_assembly"]["missing_Cauchy_components"],
            24,
        )

    def test_BRST_pairing_and_analytic_claims_fail_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_FULL_A104_CAUCHY_OPERATOR"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)
        mutant = deepcopy(self.certificate)
        mutant["analytic_gate"]["closed_generator_theorem_authorized"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
