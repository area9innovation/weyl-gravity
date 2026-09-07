"""Adversarial controls on exact witnesses, with digests resealed after mutation."""
from __future__ import annotations

import ast
import copy
from fractions import Fraction as Q
import json
import unittest

from foundations.verify_coded_wave_modulus_reversal import RESULT, ROOT, digest, verify


def seal(value):
    value['content_sha256'] = digest({k: v for k, v in value.items() if k != 'content_sha256'})
    return value


class WaveModulusReversalTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(RESULT.read_text())

    def rejected(self, edit, reason):
        value = copy.deepcopy(self.value)
        edit(value)
        errors = verify(seal(value))
        self.assertTrue(any(reason in e for e in errors), errors)
        self.assertNotIn('content digest', errors)

    def test_repository_receipt(self):
        self.assertEqual(verify(self.value), [])

    def test_gain_is_not_assumed(self):
        self.rejected(lambda x: x['profile'].__setitem__('gain_at_zero', [1, 2]), 'detector gain')

    def test_metric_normalization(self):
        self.rejected(lambda x: x['profile'].__setitem__('metric_scaling_squared', [2, 1]), 'metric scaling')

    def test_response_coefficient(self):
        self.rejected(lambda x: x['profile']['response_pieces'][1]['coefficients'].__setitem__(2, [-4, 1]), 'polynomial identity')

    def test_detector_preserved(self):
        self.rejected(lambda x: x['detector']['test_values'].__setitem__(1, [2, 1]), 'same imported detector')

    def test_diagonal_budget(self):
        self.rejected(lambda x: x['upper_bound'].__setitem__('dyadic_mesh_index_shift', 2), 'error budget')

    def test_tail_bound(self):
        self.rejected(lambda x: x['encoding'].__setitem__('tail_after_e_over_weight_e', [1, 4]), 'tail identity')

    def test_output_index_shift(self):
        self.rejected(lambda x: x['encoding'].__setitem__('output_evaluation_index_shift', 1), 'index shift')

    def test_duplicate_discovery_not_counted_twice(self):
        def edit(x):
            row = x['fixtures'][0]['stages'][3]  # prefix 4,1,4
            q = Q(*row['amplitude'])+Q(1, 4**5)
            row['amplitude'] = [q.numerator, q.denominator]
        self.rejected(edit, 'duplicate removal')

    def test_delayed_discovery_cannot_be_declared_absent(self):
        def edit(x):
            row = x['fixtures'][1]['range_witnesses'][0]  # 0 arrives only at index 4
            row['in_range'] = False
            row['absence_witness'] = {'stage': 1, 'precision': 6, 'limit_approximant': [0, 1], 'upper_remainder': [0, 1]}
        self.rejected(edit, 'false absence witness')

    def test_finite_prefix_is_not_the_limit(self):
        self.rejected(lambda x: x['fixtures'][1].__setitem__('limit', x['fixtures'][1]['stages'][1]['amplitude']), 'not a finite prefix')

    def test_strict_absence_margin(self):
        def edit(x):
            row = next(r for r in x['fixtures'][0]['range_witnesses'] if not r['in_range'])
            row['absence_witness']['upper_remainder'] = [1, 1]
        self.rejected(edit, 'strict Sigma1 absence witness')

    def test_blind_evaluation_control(self):
        self.rejected(lambda x: x['blind_control'].__setitem__('gain_at_zero', [1, 4]), 'blind evaluation control')

    def test_noncanonical_rationals_rejected(self):
        self.rejected(lambda x: x['profile'].__setitem__('mean', [0, 2]), 'noncanonical rational')

    def test_kernel_promotion_rejected(self):
        self.rejected(lambda x: x['claim_flags'].__setitem__('infinite_proof_kernel_checked', True), 'schema')

    def test_premise_change_rejected(self):
        self.rejected(lambda x: x['theorem'].__setitem__('input_rate_supplied', True), 'schema')

    def test_quantifier_strengthening_rejected(self):
        self.rejected(lambda x: x['theorem'].__setitem__('higher_type_choice_functional_asserted', True), 'schema')

    def test_causal_promotion_rejected(self):
        self.rejected(lambda x: x['claim_flags'].__setitem__('new_lorentzian_claim', True), 'schema')

    def test_proof_report_drift(self):
        self.assertTrue(any('asset hash' in e for e in verify(self.value, report='Changed proof.')))

    def test_missing_logical_obligation(self):
        self.rejected(lambda x: x['infinite_proof_obligations'].__setitem__(2, x['infinite_proof_obligations'][0]), 'obligation ledger')

    def test_missing_delayed_fixture(self):
        self.rejected(lambda x: x['fixtures'].__setitem__(1, x['fixtures'][0]), 'fixture coverage')

    def test_checker_independence(self):
        path = ROOT/'foundations/verify_coded_wave_modulus_reversal.py'
        tree = ast.parse(path.read_text())
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.add(node.module)
        self.assertEqual(modules, {'__future__', 'argparse', 'fractions', 'hashlib', 'json', 'pathlib', 'jsonschema'})
        self.assertFalse(any(isinstance(n, ast.Constant) and isinstance(n.value, float) for n in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main()
