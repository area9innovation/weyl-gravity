from __future__ import annotations
import json,unittest
from bridge.einstein_sector.einstein_maxwell_polar_exceptional_complex import DEFAULT_OUTPUT,SCHEMA_PATH,build_certificate
from bridge.einstein_sector.verify_einstein_maxwell_polar_exceptional_complex import verify_certificate
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=build_certificate()
 def test_schema(self):self.assertEqual(set(self.p),set(json.loads(SCHEMA_PATH.read_text())["required"]))
 def test_ell0_nonzero(self):self.assertIn("no local",self.p["ell0_complex"]["nonzero_Fourier_quotient"])
 def test_ell0_global(self):self.assertEqual(len(self.p["ell0_complex"]["global_moduli"]),3)
 def test_fixed_bundle(self):self.assertIn("Chern class",self.p["ell0_complex"]["absent_fixed_bundle_variable"])
 def test_ell1_gauge(self):self.assertEqual(self.p["ell1_complex"]["gauge_invariant_master"],"Psi=U-K/2")
 def test_ell1_physical(self):self.assertEqual(self.p["ell1_complex"]["physical_dispersion"],"omega^2=k_n^2+4")
 def test_zero_branch(self):self.assertIn("exactly",self.p["ell1_complex"]["removed_zero_branch"])
 def test_scope(self):self.assertFalse(self.p["classification"]["covariant_symplectic_matching"])
 def test_committed(self):self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()),self.p);verify_certificate()
if __name__=="__main__":unittest.main()
