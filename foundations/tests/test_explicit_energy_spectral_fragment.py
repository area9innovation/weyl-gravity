from __future__ import annotations
import copy
import unittest
from foundations.check_explicit_energy_spectral_fragment import check
from foundations.verify_explicit_energy_spectral_fragment import BLOCKS,DOMAINS,REPORT,RESULT,load,verify

class ExplicitEnergySpectralFragmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=load(RESULT);cls.domains=load(DOMAINS);cls.blocks=load(BLOCKS);cls.report=REPORT.read_text()
    def run_mutation(self,**kw):
        e,_=verify(result=kw.get('result',copy.deepcopy(self.result)),domains=kw.get('domains',copy.deepcopy(self.domains)),blocks=kw.get('blocks',copy.deepcopy(self.blocks)),report=kw.get('report',self.report));return e
    def test_repository_passes(self):self.assertEqual(self.run_mutation(),[])
    def test_fock_count_mutation(self):
        x=copy.deepcopy(self.result);x['fock_proof']['matter_fixed_energy_dimensions']['12']+=1;self.assertTrue(check(x)[0])
    def test_digest_mutation(self):
        x=copy.deepcopy(self.result);x['independent_checker']['expected_digest']='0'*64;self.assertTrue(self.run_mutation(result=x))
    def test_abstract_spectral_promotion(self):
        x=copy.deepcopy(self.result);x['fragment_classification'][-1]['relation']='USED_BY_DISPLAYED_PROOF';self.assertTrue(self.run_mutation(result=x))
    def test_base_conflation(self):
        x=copy.deepcopy(self.result);x['fragment_classification'][0]['base_theory']='ZF';self.assertTrue(self.run_mutation(result=x))
    def test_source_domain_drift(self):
        x=copy.deepcopy(self.domains);x['D_hilbert_self_adjoint']=False;self.assertTrue(self.run_mutation(domains=x))
    def test_source_fock_drift(self):
        x=copy.deepcopy(self.blocks);x['all_total_degree_blocks_finite']=False;self.assertTrue(self.run_mutation(blocks=x))
    def test_provenance_drift(self):
        x=copy.deepcopy(self.result);x['provenance']['inputs'][0]['sha256']='f'*64;self.assertTrue(self.run_mutation(result=x))
    def test_weakest_base_promotion(self):
        x=copy.deepcopy(self.result);x['claim_flags']['weakest_base_proved']=True;self.assertTrue(self.run_mutation(result=x))
    def test_lorentzian_promotion(self):
        x=copy.deepcopy(self.result);x['dependency_tags']=['LORENTZIAN-CAUSAL'];self.assertTrue(self.run_mutation(result=x))
    def test_dag_cycle(self):
        x=copy.deepcopy(self.result);x['proof_dependency_dag']['edges'].append({'from':'B','to':'I'});self.assertTrue(self.run_mutation(result=x))
    def test_report_drift(self):self.assertTrue(self.run_mutation(report=self.report.replace('NOT_USED_BY_DISPLAYED_PROOF','USED')))

if __name__=='__main__':unittest.main()
