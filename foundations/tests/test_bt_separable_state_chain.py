from __future__ import annotations
import copy,unittest
from foundations.check_bt_separable_state_chain import check
from foundations.verify_bt_separable_state_chain import LEDGER,REPORT,RESULT,SOURCES,load,verify
class BTSeparableStateChainTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=load(RESULT);cls.s=[load(p) for p in SOURCES];cls.l=load(LEDGER);cls.t=REPORT.read_text()
 def v(cls,**k):return verify(result=k.get('result',copy.deepcopy(cls.r)),sources=k.get('sources',copy.deepcopy(cls.s)),ledger=k.get('ledger',copy.deepcopy(cls.l)),report=k.get('report',cls.t))[0]
 def test_pass(self):self.assertEqual(self.v(),[])
 def test_digest(self):
  x=copy.deepcopy(self.r);x['independent_checker']['expected_digest']='0'*64;self.assertTrue(self.v(result=x))
 def test_five_link(self):
  x=copy.deepcopy(self.r);x['five_link_chain'][3]['relation']='IMPLIED';self.assertTrue(self.v(result=x))
 def test_algebra_conflation(self):
  x=copy.deepcopy(self.r);x['object_separation'][2]['separability']='SEPARABLE';self.assertTrue(self.v(result=x))
 def test_semifinite_as_state(self):
  x=copy.deepcopy(self.r);x['claim_flags']['semifinite_weight_is_normalized_state']=True;self.assertTrue(self.v(result=x))
 def test_physical_selection(self):
  x=copy.deepcopy(self.r);x['claim_flags']['physical_thermodynamic_state_selected']=True;self.assertTrue(self.v(result=x))
 def test_source_obstruction(self):
  s=copy.deepcopy(self.s);s[0]['disposition']['normal_trace_class_thermodynamic_limit']='PASS';self.assertTrue(self.v(sources=s))
 def test_source_six_point(self):
  s=copy.deepcopy(self.s);s[3]['disposition']['coherent_Poisson_dynamics']='SELECTED';self.assertTrue(self.v(sources=s))
 def test_hash(self):
  x=copy.deepcopy(self.r);x['provenance']['inputs'][0]['sha256']='f'*64;self.assertTrue(self.v(result=x))
 def test_dag(self):
  x=copy.deepcopy(self.r);x['proof_dependency_dag']['edges'].append({'from':'B','to':'M'});self.assertTrue(self.v(result=x))
 def test_lorentzian(self):
  x=copy.deepcopy(self.r);x['dependency_tags']=['LORENTZIAN-CAUSAL'];self.assertTrue(self.v(result=x))
 def test_report(self):self.assertTrue(self.v(report=self.t.replace('factor five','factor-five')))
if __name__=='__main__':unittest.main()
