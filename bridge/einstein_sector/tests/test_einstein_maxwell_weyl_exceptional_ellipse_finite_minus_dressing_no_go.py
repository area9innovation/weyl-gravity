from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class FiniteMinusNoGoTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.v=json.loads((ROOT/'bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json').read_text())
 def test_finite_coverage(self):self.assertTrue(self.v['classification']['arbitrary_finite_minus_superpositions_covered']);self.assertTrue(self.v['classification']['both_parities_and_all_m_covered'])
 def test_no_three_wave_collision(self):self.assertTrue(self.v['classification']['three_minus_shell_resonances_excluded_analytically']);self.assertIn('w(a+b-1)',self.v['dispersion_lemma']['integer_bracket'])
 def test_classes(self):self.assertEqual(self.v['correction_classes']['BOUNDED_OR_FINITE_QUASIPERIODIC']['status'],'OBSTRUCTED');self.assertEqual(self.v['correction_classes']['SMOOTH_EXPONENTIAL_POLYNOMIAL']['status'],'CERTIFIED')
 def test_fail_closed(self):self.assertFalse(self.v['classification']['additional_nonminus_carriers_classified']);self.assertFalse(self.v['classification']['infinite_completion_classified']);self.assertFalse(self.v['classification']['causal_or_quantum_claim'])
if __name__=='__main__':unittest.main()
