from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_full_dilation_hadamard_krein_covariance_transport import (
    transport_replay,
    validate,
)
from lorentzian.berger_full_dilation_hadamard_krein_covariance_transport_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_full_dilation_hadamard_krein_covariance_transport import (
    verify,
)


class BergerFullDilationHadamardKreinCovarianceTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-full-dilation-hadamard-krein-covariance-transport-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_two_leg_transport_preserves_exact_ccr(self) -> None:
        replay = transport_replay()
        self.assertTrue(replay["all_pass"])
        self.assertIn("=i E_full", replay["composite"]["CCR_calculation"])

    def test_quotient_inverse_is_load_bearing(self) -> None:
        replay = transport_replay(quotient_inverses=False)
        self.assertFalse(replay["all_pass"])
        self.assertFalse(
            replay["checks"]["full_transport_preserves_exact_CCR"]
        )

    def test_cone_action_is_load_bearing(self) -> None:
        replay = transport_replay(cone_action=False)
        self.assertFalse(replay["checks"]["full_transport_is_Hadamard"])

    def test_common_transport_is_load_bearing_for_ccr(self) -> None:
        replay = transport_replay(
            same_map_for_covariance_and_pauli_jordan=False
        )
        self.assertFalse(
            replay["checks"]["full_transport_preserves_exact_CCR"]
        )

    def test_positive_state_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"][
            "BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"
        ] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_graded_bv_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_54_ROW_BRST_HADAMARD"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
