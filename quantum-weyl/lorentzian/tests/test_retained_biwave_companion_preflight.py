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

    def test_companion_is_a_two_sided_graph_sdr(self) -> None:
        expected = [
            "p_sol i_sol=I10",
            "p_src i_src=I10",
            "C20 i_sol=i_src A10",
            "p_src C20=A10 p_sol",
            "I20-i_sol p_sol=H C20",
            "I20-i_src p_src=C20 H",
            "H^2=0",
            "p_sol H=0",
            "H i_src=0",
        ]
        self.assertEqual(
            self.certificate["companion_system"][
                "two_sided_graph_sdr_identities"
            ],
            expected,
        )
        self.assertTrue(
            self.certificate["claim_flags"][
                "BERGER_RETAINED_BIWAVE_COMPANION_GRAPH_SDR"
            ]
        )

    def test_raw_extra_polarization_is_not_mislabeled_clock(self) -> None:
        interpretation = self.certificate["companion_system"][
            "raw_extra_cone_interpretation"
        ]
        self.assertEqual(
            interpretation["polarization"], "MIXED_RETAINED_METRIC_AND_CLOCK"
        )
        self.assertFalse(interpretation["pure_clock_mode"])
        self.assertFalse(interpretation["selector_projection_kills_polarization"])
        self.assertEqual(
            self.certificate["companion_system"]["principal_ranks"][
                "raw_extra_cone_fixture"
            ],
            20,
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

    def test_unproved_cyclic_pairing_cannot_be_promoted(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["causal_policy"]["companion_cyclic_pairing"] = "CONSTRUCTED"
        with self.assertRaisesRegex(ValueError, "causal policy"):
            validate_preflight_result(mutant)


if __name__ == "__main__":
    unittest.main()
