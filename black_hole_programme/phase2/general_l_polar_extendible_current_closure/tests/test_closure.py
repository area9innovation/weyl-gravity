import json, unittest
from pathlib import Path
from ..module_audit import master_infinity_audit, polynomial_master_ricci_residual, shallow_log_audit
class TestClosure(unittest.TestCase):
    def test_master(self): self.assertEqual(master_infinity_audit()['zero_generalized_nullities'],[1,2,3])
    def test_polynomial_not_ricci_zero(self): self.assertIn('Lambda**2',polynomial_master_ricci_residual()['remaining_vv_residual'])
    def test_shallow(self): self.assertTrue(shallow_log_audit()['nowhere_zero'])
if __name__=='__main__': unittest.main()

