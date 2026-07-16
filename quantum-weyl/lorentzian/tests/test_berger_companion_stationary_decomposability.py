from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_companion_stationary_decomposability import (
    stationary_orientation_replay,
    validate,
)
from lorentzian.berger_companion_stationary_decomposability_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_companion_stationary_decomposability import verify


class BergerCompanionStationaryDecomposabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-companion-stationary-decomposability-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_stationarity_equivariance_uses_uniqueness(self) -> None:
        derivation = self.certificate["green_equivariance_derivation"]
        self.assertEqual(derivation["status"], "CERTIFIED")
        self.assertIn("unique", derivation["uniqueness_input"])

    def test_diagonal_generator_excludes_same_orientation(self) -> None:
        replay = stationary_orientation_replay()
        self.assertEqual(
            replay["stationarity_excluded_sectors"],
            ["N+ x N+", "N- x N-"],
        )
        self.assertTrue(all(replay["checks"].values()))

    def test_fewster_decomposability_is_certified(self) -> None:
        self.assertEqual(
            self.certificate["fewster_decomposability"]["status"],
            "N_PLUS_MINUS_DECOMPOSABLE",
        )
        self.assertTrue(
            self.certificate["claim_flags"][
                "BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"
            ]
        )

    def test_hadamard_state_remains_false(self) -> None:
        self.assertFalse(
            self.certificate["claim_flags"]["BERGER_COMPANION_HADAMARD_STATE"]
        )
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_COMPANION_HADAMARD_STATE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
