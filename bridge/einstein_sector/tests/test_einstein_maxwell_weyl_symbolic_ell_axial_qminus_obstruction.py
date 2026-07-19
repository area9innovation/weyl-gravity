from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symbolic_ell_axial_qminus_obstruction.json"


class SymbolicEllAxialQminusObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_exact_norm_factorization_is_positive_on_domain(self) -> None:
        ell = sp.symbols("ell", integer=True, positive=True)
        expected = 2 * (ell - 1) ** 3 * (ell + 2) * (
            81 * ell**4 + 54 * ell**3 + 42 * ell - 1
        )
        stored = sp.sympify(
            self.payload["nonvanishing_proof"]["norm_factorization"],
            locals={"ell": ell},
        )
        self.assertEqual(sp.factor(stored - expected), 0)
        self.assertGreater(expected.subs(ell, 2), 0)

    def test_lifecycle_split_is_fail_closed(self) -> None:
        correction = self.payload["correction_classes"]
        self.assertEqual(correction["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OBSTRUCTED")
        self.assertEqual(correction["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(correction["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        classification = self.payload["classification"]
        self.assertFalse(classification["polar_or_mixed_input_coefficient_computed"])
        self.assertFalse(classification["fixed_circumference_or_multiple_abs_momentum_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])

    def test_frozen_ell2_value_is_recovered(self) -> None:
        expected = -sp.Rational(1152, 203) * (-265 + 149 * sp.sqrt(3))
        stored = sp.sympify(
            self.payload["symbolic_adjoint_pairing"]["direct_exact_samples"]["2"]
        )
        self.assertEqual(sp.factor(stored - expected), 0)

    def test_all_direct_slow_rail_samples_are_positive(self) -> None:
        samples = self.payload["symbolic_adjoint_pairing"]["direct_exact_samples"]
        self.assertEqual(set(samples), {"2", "3", "4", "5", "6"})
        for value in samples.values():
            self.assertGreater(sp.N(sp.sympify(value), 30), 0)


if __name__ == "__main__":
    unittest.main()
