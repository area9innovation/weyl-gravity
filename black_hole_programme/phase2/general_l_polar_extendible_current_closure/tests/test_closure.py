import json, unittest
from pathlib import Path
from ..module_audit import master_infinity_audit, polynomial_master_ricci_residual, shallow_log_audit
class TestClosure(unittest.TestCase):
    def test_master(self): self.assertEqual(master_infinity_audit()['zero_generalized_nullities'],[1,2,3])
    def test_polynomial_not_ricci_zero(self): self.assertIn('Lambda**2',polynomial_master_ricci_residual()['remaining_vv_residual'])
    def test_shallow(self): self.assertTrue(shallow_log_audit()['nowhere_zero'])
    def test_current_filtration(self):
        path=Path(__file__).parents[1]/'current_artifacts/oscillatory-matrix-filtration.json'
        data=json.loads(path.read_text())
        self.assertEqual(data['leading_p0']['generic_rank_away_from_detK_walls'],3)
        self.assertEqual(data['leading_p0']['generic_radical_dimension_away_from_detK_walls'],1)
        self.assertTrue(data['leading_p0']['schur_numerator_identically_zero'])
        self.assertTrue(data['subleading_p_minus_1']['induced_form_on_leading_radical_identically_zero'])
        self.assertFalse(data['first_finite_p_minus_2']['identically_zero'])
    def test_wall_and_lift(self):
        root=Path(__file__).parents[1]/'current_artifacts'
        wall=json.loads((root/'canonical-pivot-wall-certificate.json').read_text())
        basis=json.loads((root/'basis-lift-congruence.json').read_text())
        self.assertEqual(wall['disposition'],'EMPTY_CANONICAL_PIVOT_WALL_ON_PHYSICAL_DOMAIN')
        self.assertEqual(wall['finite_line']['generic_disposition'],'NONRADICAL_AWAY_FROM_Q21_ZERO_LOCUS')
        self.assertTrue(basis['exact_probe']['einstein_cross_covector_unchanged'])
if __name__=='__main__': unittest.main()
