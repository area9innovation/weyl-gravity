from __future__ import annotations
import copy,unittest
from foundations.check_hardy_continuity_kn import check
from foundations.verify_hardy_continuity_kn import LEDGER,REPORT,RESULT,load,verify
class HardyContinuityKNTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=load(RESULT);cls.l=load(LEDGER);cls.t=REPORT.read_text()
 def v(self,**k):return verify(result=k.get('result',copy.deepcopy(self.r)),ledger=k.get('ledger',copy.deepcopy(self.l)),report=k.get('report',self.t))[0]
 def test_pass(self):self.assertEqual(self.v(),[])
 def test_digest(self):
  x=copy.deepcopy(self.r);x['independent_checker']['expected_digest']='0'*64;self.assertTrue(self.v(result=x))
 def test_regression_domain(self):
  x=copy.deepcopy(self.r);x['independent_checker']['regression_N']=[2];self.assertTrue(check(x)[0])
 def test_minimality(self):
  x=copy.deepcopy(self.r);x['mathematical_encoding']['minimality']='PROVED';self.assertTrue(self.v(result=x))
 def test_reversal(self):
  x=copy.deepcopy(self.r);x['claim_flags']['physical_axiom_implies_rca0_or_wkl0']=True;self.assertTrue(self.v(result=x))
 def test_full_reconstruction(self):
  x=copy.deepcopy(self.r);x['claim_flags']['full_hardy_reconstruction_audited']=True;self.assertTrue(self.v(result=x))
 def test_modulus_boundary(self):
  x=copy.deepcopy(self.r);x['dependency_classification'][3]['status']='NOT_USED';self.assertTrue(self.v(result=x))
 def test_compact_group(self):
  x=copy.deepcopy(self.r);x['dependency_classification'][5]['status']='USED_BY_DISPLAYED_PROOF';self.assertTrue(self.v(result=x))
 def test_literature(self):
  l=copy.deepcopy(self.l);next(x for x in l['entries'] if x['id']=='hardy-2001')['artifact']['sha256']='f'*64;self.assertTrue(self.v(ledger=l))
 def test_lorentzian(self):
  x=copy.deepcopy(self.r);x['dependency_tags']=['LORENTZIAN-CAUSAL'];self.assertTrue(self.v(result=x))
 def test_report(self):self.assertTrue(self.v(report=self.t.replace('REPRESENTATION_SENSITIVE','SENSITIVE')))
if __name__=='__main__':unittest.main()
