"""Digest-valid adversarial controls for the detector recovery benchmark."""
import ast
import copy
import json
import unittest
from fractions import Fraction as Q
from foundations.verify_wave_detector_recovery import ROOT, RESULT, digest, verify


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(RESULT.read_text())

    def reject(self, mutate, expected):
        v = copy.deepcopy(self.value)
        mutate(v)
        v['content_sha256'] = digest({k:x for k,x in v.items() if k != 'content_sha256'})
        errors = verify(v)
        self.assertNotIn('content digest', errors)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_repository(self):
        self.assertEqual(verify(), [])

    def test_kernel_sign(self):
        self.reject(lambda v: v['cases'][0]['kernel'][0]['coefficients'].__setitem__(1,[17,1]), 'kernel polynomial')

    def test_wrong_delay(self):
        self.reject(lambda v: v['cases'][0].__setitem__('delay',[1,8]), 'kernel polynomial')

    def test_projection(self):
        self.reject(lambda v: v['cases'][0]['kernel_cell_means'].__setitem__(0,[0,1]), 'cell projection')

    def test_unseen_energy(self):
        self.reject(lambda v: v['cases'][0].__setitem__('residual_norm_squared',[0,1]), 'norm identity')

    def test_exact_center(self):
        self.reject(lambda v: v['cases'][0]['exact_nonzero_data'].__setitem__('prediction_center',[0,1]), 'center/energy')

    def test_exact_extremizer(self):
        self.reject(lambda v: v['cases'][0]['exact_nonzero_data'].__setitem__('extremizer_residual_coefficient_squared',[1,1]), 'matching endpoint')

    def test_noise_feasibility(self):
        self.reject(lambda v: v['cases'][0]['zero_reading_noisy_data'][0].__setitem__('extremizer_projection_coefficient_squared',[1,1]), 'endpoint feasibility')

    def test_noise_branch(self):
        self.reject(lambda v: v['cases'][0]['zero_reading_noisy_data'][-1].__setitem__('branch','ACTIVE_NOISE_CONSTRAINT'), 'inactive constraint')

    def test_radius_response(self):
        self.reject(lambda v: v['cases'][0]['zero_reading_noisy_data'][1]['radius_sqrt_terms'].__setitem__(0,[0,1]), 'detector response')

    def test_accuracy_decision(self):
        self.reject(lambda v: v['cases'][0]['zero_reading_noisy_data'][1].__setitem__('tolerance_one_sixteenth_achievable',True), 'accuracy decision')

    def test_noise_contract(self):
        self.reject(lambda v: v['contract'].__setitem__('noise_type','Independent Gaussian noise'), 'observation contract')

    def test_new_theorem_claim(self):
        self.reject(lambda v: v['claim_flags'].__setitem__('new_general_recovery_theorem',True), 'claim boundary')

    def test_novelty(self):
        self.reject(lambda v: v.__setitem__('novelty_disposition','NEW_DISCOVERY'), 'novelty boundary')

    def test_causal_promotion(self):
        self.reject(lambda v: v['claim_flags'].__setitem__('new_lorentzian_claim',True), 'claim boundary')

    def test_missing_case(self):
        self.reject(lambda v: v['cases'].pop(), 'case inventory')

    def test_missing_calibration_boundary(self):
        self.reject(lambda v: v['missing_objects'].clear(), 'missing-object ledger')

    def test_literature_replay_not_claimed(self):
        self.reject(lambda v: v['literature'].__setitem__('pdf_local_replay', True), 'literature provenance boundary')

    def test_numerical_story_exactly(self):
        by_grid = {r['cells']:r for r in self.value['cases'] if r['delay']==[0,1]}
        self.assertEqual(Q(*by_grid[8]['residual_norm_squared']),Q(23,5760))
        self.assertEqual(Q(*by_grid[16]['residual_norm_squared']),Q(49,46080))
        self.assertFalse(by_grid[8]['zero_reading_noisy_data'][1]['tolerance_one_sixteenth_achievable'])
        self.assertTrue(by_grid[16]['zero_reading_noisy_data'][1]['tolerance_one_sixteenth_achievable'])

    def test_checker_isolation(self):
        tree=ast.parse((ROOT/'foundations/verify_wave_detector_recovery.py').read_text())
        imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): imports.update(a.name for a in node.names)
            if isinstance(node,ast.ImportFrom): imports.add(node.module)
        self.assertEqual(imports,{'fractions','hashlib','json','pathlib'})
        self.assertFalse(any(isinstance(n,ast.Constant) and isinstance(n.value,float) for n in ast.walk(tree)))


if __name__=='__main__':
    unittest.main()
