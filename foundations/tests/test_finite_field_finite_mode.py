from __future__ import annotations
import copy,unittest
from foundations.check_finite_field_finite_mode import check
from foundations.verify_finite_field_finite_mode import LEDGER,REPORT,RESULT,load,verify
class FiniteFieldFiniteModeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=load(RESULT);cls.l=load(LEDGER);cls.t=REPORT.read_text()
 def v(self,**k):return verify(result=k.get('result',copy.deepcopy(self.r)),ledger=k.get('ledger',copy.deepcopy(self.l)),report=k.get('report',self.t))[0]
 def test_pass(self):self.assertEqual(self.v(),[])
 def test_non_prime_power(self):
  x=copy.deepcopy(self.r);x['independent_checker']['prime_powers'][0]=6;self.assertTrue(check(x)[0])
 def test_digest(self):
  x=copy.deepcopy(self.r);x['independent_checker']['expected_digest']='0'*64;self.assertTrue(self.v(result=x))
 def test_type_collapse(self):
  x=copy.deepcopy(self.r);x['typed_objects'][1]['id']='FINITE-FIELD-PHASE-SPACE';self.assertTrue(self.v(result=x))
 def test_pair_loss(self):
  x=copy.deepcopy(self.r);x['pairwise_non_equivalence'].pop();self.assertTrue(self.v(result=x))
 def test_bridge_promotion(self):
  x=copy.deepcopy(self.r);x['claim_flags']['continuum_bridge_constructed']=True;self.assertTrue(self.v(result=x))
 def test_finitism_conflation(self):
  x=copy.deepcopy(self.r);x['claim_flags']['mode_cutoff_implies_finitism']=True;self.assertTrue(self.v(result=x))
 def test_source(self):
  l=copy.deepcopy(self.l);next(x for x in l['entries'] if x['id']=='gibbons-hoffman-wootters-2004')['artifact']['sha256']='f'*64;self.assertTrue(self.v(ledger=l))
 def test_local_hash(self):
  x=copy.deepcopy(self.r);x['provenance']['inputs'][0]['sha256']='f'*64;self.assertTrue(self.v(result=x))
 def test_lorentzian(self):
  x=copy.deepcopy(self.r);x['dependency_tags']=['LORENTZIAN-CAUSAL'];self.assertTrue(self.v(result=x))
 def test_report(self):self.assertTrue(self.v(report=self.t.replace('NOT_EQUIVALENT_BY_TYPE','EQUIVALENT')))
if __name__=='__main__':unittest.main()
