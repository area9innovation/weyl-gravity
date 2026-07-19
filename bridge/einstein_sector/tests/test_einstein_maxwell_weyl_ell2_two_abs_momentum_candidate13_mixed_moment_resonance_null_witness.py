import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json"


class Candidate13MixedMomentResonanceNullWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_scope_keeps_mixed_carrier_explicit(self) -> None:
        carrier = self.value["scope"]["carrier"]
        self.assertIn("p-primary", carrier)
        self.assertIn("q-minus", carrier)
        self.assertEqual(self.value["scope"]["m"], 0)

    def test_nonzero_five_moment_null_witness(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["nonzero_real_mixed_witness_certified"])
        self.assertTrue(flags["all_five_stabilizer_moment_maps_zero"])

    def test_candidate13_cross_fibre_resonance_vanishes(self) -> None:
        self.assertEqual(self.value["occupation_witness"]["p_primary_n_minus2"], "0")
        self.assertTrue(self.value["classification"]["candidate_13_cross_fibre_resonance_functionals_zero"])

    def test_extension_stays_fail_closed(self) -> None:
        flags = self.value["classification"]
        verdict = self.value["second_order_verdict"]
        self.assertFalse(flags["same_fibre_resonance_functionals_classified"])
        self.assertFalse(flags["bounded_or_smooth_second_order_extension_certified"])
        self.assertEqual(verdict["bounded_or_finite_quasiperiodic"], "OPEN")
        self.assertEqual(verdict["smooth_secular"], "OPEN")
        self.assertEqual(verdict["causal_retarded"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
