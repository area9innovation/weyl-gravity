from __future__ import annotations

import json
import unittest

from bridge.phase2.dyonic_flat_family_preflight.generate import (
    OUTPUT,
    build_certificate,
    check_outputs,
)
from bridge.phase2.dyonic_flat_family_preflight.verify import (
    IndependentPreflightVerificationError,
    mutated,
    verify,
    verify_payload,
)


class DyonicFlatFamilyPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_reproduction_and_independent_verification(self) -> None:
        self.assertEqual(self.payload, build_certificate())
        check_outputs()
        verify()

    def test_rejects_false_fixed_coupling_promotion(self) -> None:
        bad = mutated(self.payload, ("classification", "fixed_coupling_open_family"), True)
        with self.assertRaises(Exception):
            verify_payload(bad)

    def test_rejects_false_global_H_lift(self) -> None:
        bad = mutated(
            self.payload,
            ("connection_and_symmetry", "stabilizer_lifts", "H"),
            "GLOBAL_CONNECTION_LIFT_EXISTS",
        )
        with self.assertRaises(Exception):
            verify_payload(bad)

    def test_rejects_inherited_parity_split(self) -> None:
        bad = mutated(self.payload, ("classification", "generic_axial_polar_block_split_authorized"), True)
        with self.assertRaises(IndependentPreflightVerificationError):
            verify_payload(bad)

    def test_rejects_duality_fixed_chern_promotion(self) -> None:
        bad = mutated(
            self.payload,
            ("connection_and_symmetry", "parity_duality", "preserves_fixed_chern_tangent_for_tau_nonzero"),
            True,
        )
        with self.assertRaises(Exception):
            verify_payload(bad)

    def test_rejects_family_formula_mutation(self) -> None:
        bad = mutated(self.payload, ("exact_family", "k_2"), "8*q_min**2/(N**2*kappa*(tau**2+1))")
        with self.assertRaises(IndependentPreflightVerificationError):
            verify_payload(bad)


if __name__ == "__main__":
    unittest.main()

