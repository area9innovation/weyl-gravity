from copy import deepcopy
import json
import unittest
from foundations.verify_tt_trace_repair import ROOT, RESULT, verify
from foundations.check_current_strict386_transfer import GRAPH, BASIS, check


class TraceRepairTests(unittest.TestCase):
    def test_independent_repair(self): verify()

    def test_mutations(self):
        original=json.loads(RESULT.read_text())
        for kind in ('B','ghost','projection','obstruction','promotion'):
            v=deepcopy(original)
            if kind=='B':v['B_derivative_correction'][0][-1]='0'
            if kind=='ghost':v['Q_candidate_changes'][0][-1]='0'
            if kind=='projection':v['projection_changes'][0][-1]='0'
            if kind=='obstruction':v['constant_A_repair_obstruction']['contracted_rhs']='0'
            if kind=='promotion':v['claims']['full_transfer_accepted']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):verify(v)

    def test_current_gate_rejects_published_export(self):
        result=check(json.loads(GRAPH.read_text()),json.loads(BASIS.read_text()))
        self.assertEqual(result['status'],'FAIL_CLOSED')
        self.assertEqual(result['defect_counts'],{'metric':28,'trace':16})
        self.assertFalse(result['full_transfer_accepted'])

    def test_partial_repair_does_not_pass_full_gate(self):
        graph=json.loads(GRAPH.read_text());v=json.loads(RESULT.read_text())
        # Add the experimental changes to an existing table. This is a test
        # fixture only, not a valid replacement serialization/hash package.
        for m,i,j,a in v['Q_candidate_changes']:
            graph['graph_q1_serialization']['tables'][0]['coefficients'].append({'multiindex':m,'entries':[[i,j,a]]})
        result=check(graph,json.loads(BASIS.read_text()))
        self.assertTrue(result['selected_nilpotency_prerequisites_pass'])
        self.assertFalse(result['full_transfer_accepted'])

    def test_incomplete_inventory_rejected(self):
        graph=json.loads(GRAPH.read_text());graph['graph_q1_serialization']['tables'].pop()
        with self.assertRaises(ValueError):check(graph,json.loads(BASIS.read_text()))


if __name__=='__main__':unittest.main()
