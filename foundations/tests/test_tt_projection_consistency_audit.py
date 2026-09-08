from copy import deepcopy
import json
import unittest
import sympy as s
from foundations.verify_tt_projection_consistency_audit import RESULT, verify, product, X


class ProjectionConsistencyTests(unittest.TestCase):
    def test_independent_audit(self):
        verify()

    def test_mutated_evidence_and_promotions_rejected(self):
        value = json.loads(RESULT.read_text())
        for kind in ('square', 'trace', 'candidate', 'promotion', 'hash'):
            bad = deepcopy(value)
            if kind == 'square': bad['metric_from_dual_identity_Q_squared'][0][-1] = '0'
            if kind == 'trace': bad['primal_NA_minus_BC'][0][-1] = '0'
            if kind == 'candidate': bad['candidate_missing_metric_attachment'][0][-1] = '0'
            if kind == 'promotion': bad['claims']['full_consistent_repair_established'] = True
            if kind == 'hash': bad['inputs'][0]['sha256'] = '0'*64
            with self.subTest(kind=kind), self.assertRaises(ValueError): verify(bad)

    def test_unproved_derivative_products_rejected(self):
        a = s.SparseMatrix(386, 386, {(10, 2): X[0]})
        b = s.SparseMatrix(386, 386, {(2, 313): X[1]})
        with self.assertRaisesRegex(ValueError, 'unsafe derivative'):
            product(a, b, [10], [313])


if __name__ == '__main__': unittest.main()
