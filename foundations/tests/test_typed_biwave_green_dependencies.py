from __future__ import annotations
import copy,unittest
from foundations.check_typed_biwave_green_dependencies import check
from foundations.verify_typed_biwave_green_dependencies import CLASSICAL,QUANTUM,REPORT,RESULT,load,verify
class TypedBiwaveGreenDependencyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=load(RESULT);cls.c=load(CLASSICAL);cls.q=load(QUANTUM);cls.t=REPORT.read_text()
 def v(self,**k):return verify(result=k.get('result',copy.deepcopy(self.r)),classical=k.get('classical',copy.deepcopy(self.c)),quantum=k.get('quantum',copy.deepcopy(self.q)),report=k.get('report',self.t))[0]
 def test_pass(self):self.assertEqual(self.v(),[])
 def test_digest(self):
  x=copy.deepcopy(self.r);x['independent_checker']['expected_digest']='0'*64;self.assertTrue(self.v(result=x))
 def test_truncations(self):
  x=copy.deepcopy(self.r);x['independent_checker']['truncations']=[0];self.assertTrue(self.v(result=x))
 def test_layer_loss(self):
  x=copy.deepcopy(self.r);x['dependency_layers'].pop();self.assertTrue(self.v(result=x))
 def test_analytic_overclaim(self):
  x=copy.deepcopy(self.r);x['dependency_layers'][1]['foundational_strength']='PRA';self.assertTrue(self.v(result=x))
 def test_choice_promotion(self):
  x=copy.deepcopy(self.r);x['claim_flags']['choice_free_pde_theorem_proved']=True;self.assertTrue(self.v(result=x))
 def test_bv_promotion(self):
  x=copy.deepcopy(self.r);x['claim_flags']['full_bv_propagator_constructed']=True;self.assertTrue(self.v(result=x))
 def test_classical_source(self):
  x=copy.deepcopy(self.c);x['claim_status']='UNPROVED';self.assertTrue(self.v(classical=x))
 def test_quantum_import(self):
  x=copy.deepcopy(self.q);x['claim_flags']['TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED']=False;self.assertTrue(self.v(quantum=x))
 def test_hash(self):
  x=copy.deepcopy(self.r);x['provenance']['inputs'][0]['sha256']='f'*64;self.assertTrue(self.v(result=x))
 def test_tags(self):
  x=copy.deepcopy(self.r);x['dependency_tags']=['LOCAL-ALGEBRAIC'];self.assertTrue(self.v(result=x))
 def test_report(self):self.assertTrue(self.v(report=self.t.replace('Choice strength','choice status')))
if __name__=='__main__':unittest.main()
