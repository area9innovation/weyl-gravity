import copy,json,os,unittest
from reverse_physics.verify_bt_fully_rearranged_lambda9_parity_selection import CERT_REL,ROOT,verify
class Q9Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  with open(os.path.join(ROOT,CERT_REL),encoding="utf-8") as f:c.x=json.load(f)
 def reject(c,p,v):
  x=copy.deepcopy(c.x);o=x
  for k in p[:-1]:o=o[k]
  o[p[-1]]=v;c.assertFalse(all(verify(x).values()))
 def test_baseline(c):c.assertTrue(all(verify(copy.deepcopy(c.x)).values()))
 def test_identity(c):c.reject(["certificate"],"X")
 def test_source(c):c.reject(["provenance","source_commit"],"0"*40)
 def test_hash(c):c.reject(["provenance","inputs",4,"sha256"],"0"*64)
 def test_K(c):c.reject(["finite_dual_metric_witness","Krein_metric",0,1],"0")
 def test_H(c):c.reject(["finite_dual_metric_witness","Hilbert_metric",0,0],"0")
 def test_P(c):c.reject(["finite_dual_metric_witness","Fock_parity",0,0],"1")
 def test_y4(c):c.reject(["finite_dual_metric_witness","y4",0],"0")
 def test_y5(c):c.reject(["finite_dual_metric_witness","y5",2],"0")
 def test_public(c):c.reject(["finite_dual_metric_witness","public_cross"],"1")
 def test_hilbert(c):c.reject(["finite_dual_metric_witness","Hilbert_cross"],"1")
 def test_mutation(c):c.reject(["finite_dual_metric_witness","parity_breaking_cross"],"0")
 def test_witness(c):c.reject(["finite_dual_metric_witness","status"],"ASSUMED")
 def test_series(c):c.reject(["fully_rearranged_output_selection","output_series"],"Y=y")
 def test_y5ledger(c):c.reject(["fully_rearranged_output_selection","complete_next_output"],"T5 only")
 def test_publicrecord(c):c.reject(["fully_rearranged_output_selection","public_cross"],"nonzero")
 def test_hilbertrecord(c):c.reject(["fully_rearranged_output_selection","Hilbert_cross"],"nonzero")
 def test_probability(c):c.reject(["fully_rearranged_output_selection","probability_series"],"O(lambda9)")
 def test_status(c):c.reject(["fully_rearranged_output_selection","status"],"GENERAL")
 def test_q8(c):c.reject(["disposition","leading_q8_common_Born"],"OPEN")
 def test_q9(c):c.reject(["disposition","probability_order_lambda9"],"NONZERO")
 def test_q10(c):c.reject(["disposition","q10_coefficient"],"COMPUTED")
 def test_eq19(c):c.reject(["disposition","general_Eq19"],"PROVED")
 def test_gravity(c):c.reject(["disposition","gravity_or_metric_BV_BRST_transfer"],"CONSTRUCTED")
 def test_causal(c):c.reject(["disposition","Lorentzian_causal_claim"],"ESTABLISHED")
 def test_boundaries(c):c.reject(["does_not_establish"],[])
 def test_missing(c):c.reject(["missing_object_ledger"],[])
 def test_next(c):c.reject(["next_gate"],"done")
 def test_report(c):c.reject(["report"],"none")
if __name__=="__main__":unittest.main()
