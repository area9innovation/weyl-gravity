from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_free_dilation_krein_ccr_covariance import (
    sign_negative_control,
    symmetrization_replay,
    validate,
)
from lorentzian.berger_free_dilation_krein_ccr_covariance_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_free_dilation_krein_ccr_covariance import verify


class BergerFreeDilationKreinCCRCovarianceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (
                HERE
                / "schema/berger-free-dilation-krein-ccr-covariance-v1.schema.json"
            ).read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_transpose_average_gives_exact_project_ccr(self) -> None:
        replay = symmetrization_replay()
        self.assertTrue(replay["all_pass"])
        self.assertIn("=i E_project", replay["CCR_calculation"])

    def test_reality_is_required(self) -> None:
        self.assertFalse(
            symmetrization_replay(real_symmetric_operator=False)["all_pass"]
        )

    def test_transpose_symmetrization_is_required(self) -> None:
        self.assertFalse(symmetrization_replay(symmetrize=False)["all_pass"])

    def test_source_sign_without_map_is_rejected(self) -> None:
        bad = sign_negative_control()
        self.assertFalse(bad["matches_project_CCR"])
        self.assertEqual(bad["antisymmetric_part"], "-i E_project")

    def test_positive_state_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_FREE_DILATION_POSITIVE_HADAMARD_STATE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
