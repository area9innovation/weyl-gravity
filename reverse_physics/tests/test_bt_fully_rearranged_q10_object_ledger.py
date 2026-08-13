import copy,json,os,unittest
from reverse_physics.verify_bt_fully_rearranged_q10_object_ledger import CERT_REL,ROOT,verify
class T(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  with open(os.path.join(ROOT,CERT_REL),encoding='utf-8') as f:c.x=json.load(f)
 def r(c,p,v):
  x=copy.deepcopy(c.x);o=x
  for k in p[:-1]:o=o[k]
  o[p[-1]]=v;c.assertFalse(all(verify(x).values()))
 def test_00(c):c.assertTrue(all(verify(c.x).values()))
 def test_id(c):c.r(['certificate'],'X')
 def test_lifecycle(c):c.r(['lifecycle_state'],'COEFFICIENT_COMPUTED')
 def test_hash(c):c.r(['provenance','inputs',2,'sha256'],'0'*64)
 def test_q10(c):c.r(['exact_probability_decomposition','q10'],'unknown')
 def test_row(c):c.r(['connected_order6_graphs','rows',0,'L'],0)
 def test_graph_status(c):c.r(['connected_order6_graphs','status'],'TREE')
 def test_support(c):c.r(['support_disposition','status'],'COMPLETE')
 def test_vacuum(c):c.r(['support_disposition','vacuum_components'],'zero')
 def test_blocks(c):c.r(['required_blocks'],[])
 def test_kappa(c):c.r(['required_blocks',4,'status'],'COMPUTED')
 def test_q8(c):c.r(['disposition','q8'],'OPEN')
 def test_q9(c):c.r(['disposition','q9'],'UNKNOWN')
 def test_q10status(c):c.r(['disposition','q10'],'COEFFICIENT_COMPUTED')
 def test_born(c):c.r(['disposition','common_Born_q10'],'PROVED')
 def test_eq19(c):c.r(['disposition','general_Eq19'],'PROVED')
 def test_causal(c):c.r(['disposition','Lorentzian_causal_claim'],'ESTABLISHED')
 def test_boundaries(c):c.r(['does_not_establish'],[])
 def test_next(c):c.r(['next_gate'],'done')
 def test_report(c):c.r(['report'],'none')
if __name__=='__main__':unittest.main()
