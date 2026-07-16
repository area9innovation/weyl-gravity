from __future__ import annotations

from copy import deepcopy
import json
import unittest

from local_bv.schema_validation import validate_instance
from lorentzian.berger_companion_pauli_jordan_characteristic_preflight import (
    orientation_sector_replay,
    validate,
)
from lorentzian.berger_companion_pauli_jordan_characteristic_preflight_certificate import (
    HERE,
    OUTPUT,
    build_certificate,
)
from lorentzian.verify_berger_companion_pauli_jordan_characteristic_preflight import verify


class BergerCompanionPauliJordanCharacteristicPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = build_certificate()

    def test_reproduces_and_validates_strict_schema(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), self.certificate)
        schema = json.loads(
            (HERE / "schema/berger-companion-pauli-jordan-characteristic-preflight-v1.schema.json").read_text()
        )
        self.assertFalse(validate_instance(self.certificate, schema))

    def test_kernel_and_bisolution_are_certified(self) -> None:
        self.assertIn(
            "Schwartz kernels",
            self.certificate["kernel_continuity_derivation"]["conclusion"],
        )
        self.assertEqual(
            self.certificate["bisolution_derivation"]["status"],
            "TWO_SIDED_BISOLUTION_CERTIFIED",
        )

    def test_factorwise_null_bound_is_certified(self) -> None:
        elliptic = self.certificate["elliptic_regularization"]
        self.assertEqual(
            elliptic["certified_inclusion"],
            "WF(E_C) subset (N_plus union N_minus) x (N_plus union N_minus)",
        )

    def test_only_same_orientation_sectors_remain(self) -> None:
        replay = orientation_sector_replay()
        self.assertEqual(
            replay["unresolved_same_orientation_sectors"],
            ["N+ x N+", "N- x N-"],
        )
        self.assertTrue(all(replay["checks"].values()))

    def test_orientation_promotion_fails_closed(self) -> None:
        mutant = deepcopy(self.certificate)
        mutant["claim_flags"]["BERGER_COMPANION_NULL_CONE_DECOMPOSABLE"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.certificate)


if __name__ == "__main__":
    unittest.main()
