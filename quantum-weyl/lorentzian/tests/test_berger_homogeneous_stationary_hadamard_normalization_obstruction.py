from __future__ import annotations

from copy import deepcopy
import json
import unittest

from lorentzian.berger_homogeneous_stationary_hadamard_normalization_obstruction import (
    evaluate,
    validate,
)
from lorentzian.berger_homogeneous_stationary_hadamard_normalization_obstruction_certificate import (
    OUTPUT,
    build,
)
from lorentzian.verify_berger_homogeneous_stationary_hadamard_normalization_obstruction import (
    verify,
)


class BergerHomogeneousStationaryObstructionTests(unittest.TestCase):
    def test_exact_checks(self) -> None:
        self.assertTrue(all(evaluate()["exact_checks"].values()))

    def test_two_positive_root_brackets(self) -> None:
        intervals = evaluate()["homogeneous_spectral_data"][
            "positive_root_intervals"
        ]
        self.assertEqual(len(intervals), 2)

    def test_scope_keeps_nonstationary_route_open(self) -> None:
        flags = evaluate()["claim_flags"]
        self.assertFalse(flags["NONSTATIONARY_HADAMARD_REPRESENTATIVE_RULED_OUT"])
        self.assertFalse(flags["PHYSICAL_BRST_QUOTIENT_INSTABILITY_CERTIFIED"])

    def test_certificate_reproduces(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text()), build())

    def test_nonstationary_overpromotion_rejected(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["NONSTATIONARY_HADAMARD_REPRESENTATIVE_RULED_OUT"] = True
        with self.assertRaisesRegex(ValueError, "over-promoted"):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), build())


if __name__ == "__main__":
    unittest.main()
