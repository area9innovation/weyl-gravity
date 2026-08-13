import copy, json, os, unittest
from reverse_physics.verify_bt_fully_rearranged_common_born_physical import CERT_REL, ROOT, verify

class FullyRearrangedCommonBornTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT,CERT_REL),encoding="utf-8") as handle: cls.c=json.load(handle)
    def reject(self,path,value):
        row=copy.deepcopy(self.c); cur=row
        for key in path[:-1]: cur=cur[key]
        cur[path[-1]]=value; self.assertFalse(all(verify(row).values()))
    def test_baseline(self):
        q=verify(copy.deepcopy(self.c)); self.assertTrue(all(q.values()),[k for k,v in q.items() if not v])
    def test_identity(self): self.reject(["certificate"],"X")
    def test_schema(self): self.reject(["schema"],"x")
    def test_version(self): self.reject(["schema_version"],2)
    def test_lifecycle(self): self.reject(["lifecycle_state"],"LORENTZIAN_CERTIFIED")
    def test_tags(self): self.reject(["dependency_tags"],["LORENTZIAN-CAUSAL"])
    def test_source(self): self.reject(["provenance","source_commit"],"0"*40)
    def test_hash(self): self.reject(["provenance","inputs",3,"sha256"],"0"*64)
    def test_px(self): self.reject(["exact_tensor_witness","P_X",0,0],"0")
    def test_py(self): self.reject(["exact_tensor_witness","P_Y",8,8],"0")
    def test_kappa(self): self.reject(["exact_tensor_witness","kappa_total",0,7],"0")
    def test_transition(self): self.reject(["exact_tensor_witness","T4_YX",8,0],"99")
    def test_projector_product(self): self.reject(["exact_tensor_witness","projector_product"],"nonzero")
    def test_commutator(self): self.reject(["exact_tensor_witness","commutators"],[])
    def test_fixed(self): self.reject(["exact_tensor_witness","fixed_point"],"false")
    def test_adjoint(self): self.reject(["exact_tensor_witness","adjoint"],"different")
    def test_public_square(self): self.reject(["exact_tensor_witness","public_trace_square"],"769")
    def test_hilbert_square(self): self.reject(["exact_tensor_witness","Hilbert_trace_square"],"771")
    def test_defect(self): self.reject(["exact_tensor_witness","Born_defect"],"1")
    def test_witness_status(self): self.reject(["exact_tensor_witness","status"],"ASSUMED")
    def test_expansion(self): self.reject(["complete_leading_common_Born_transition","expansion"],"all orders")
    def test_disconnected(self): self.reject(["complete_leading_common_Born_transition","disconnected_restriction"],"unknown")
    def test_complete(self): self.reject(["complete_leading_common_Born_transition","complete_leading_identity"],"connected only")
    def test_complete_fixed(self): self.reject(["complete_leading_common_Born_transition","fixed_point"],"odd")
    def test_effect(self): self.reject(["complete_leading_common_Born_transition","effect_identity"],"different")
    def test_operator_defect(self): self.reject(["complete_leading_common_Born_transition","Born_defect"],"nonzero")
    def test_probability(self): self.reject(["complete_leading_common_Born_transition","scalar_probability"],"selected")
    def test_bound(self): self.reject(["complete_leading_common_Born_transition","coefficient_bound"],"unbounded")
    def test_status(self): self.reject(["complete_leading_common_Born_transition","status"],"GENERAL_EQ19")
    def test_physical(self): self.reject(["disposition","complete_leading_finite_time_public_physical_probability"],"NOT_COMPUTED")
    def test_ledger(self): self.reject(["disposition","complete_leading_disconnected_ledger"],"OPEN")
    def test_higher_promotion(self): self.reject(["disposition","higher_orders"],"CONTROLLED")
    def test_eq19_promotion(self): self.reject(["disposition","general_Eq19"],"PROVED")
    def test_gravity_promotion(self): self.reject(["disposition","gravity_or_metric_BV_BRST_transfer"],"CONSTRUCTED")
    def test_causal_promotion(self): self.reject(["disposition","Lorentzian_causal_claim"],"ESTABLISHED")
    def test_boundaries(self): self.reject(["does_not_establish"],[])
    def test_missing(self): self.reject(["missing_object_ledger"],[])
    def test_next(self): self.reject(["next_gate"],"done")
    def test_commands(self): self.reject(["verification_commands"],[])
    def test_report(self): self.reject(["report"],"none")

if __name__=="__main__": unittest.main()
