from copy import deepcopy
import json
import unittest
import sympy as s
from foundations.verify_tt_observable_extension import ROOT, RESULT, verify, replay_reference


class ExtensionTests(unittest.TestCase):
    def test_reconciled_reference(self):
        replay_reference()

    def test_sparse_factorization(self):
        verify()

    def test_mutation_controls(self):
        v = json.loads(RESULT.read_text())
        for mutation in ('coefficient', 'gamma', 'promotion', 'witness'):
            bad = deepcopy(v)
            if mutation == 'coefficient': bad['metric_projection']['entries'][0][2] = '2'
            if mutation == 'gamma': bad['gauge_factorization']['zero_order_ghost_changes'][0][2] = '1/4'
            if mutation == 'promotion': bad['claims']['full_strict_physical_positivity_decided'] = True
            if mutation == 'witness': bad['advertised_projection_chain_witness'][-1] = '0'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): verify(bad)

    def test_independent_dense_principal_witness(self):
        path = ROOT / 'quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json'
        g = json.loads(path.read_text()); p = s.zeros(30, 386); r = s.zeros(386)
        for c in g['graph_sdr_component_maps']['p_end_graph']['coefficients']:
            if c['multiindex'] == [0, 0, 0, 0]:
                for i, j, a in c['entries']: p[i,j] += s.Rational(a)
        for table in g['graph_q1_serialization']['tables']:
            for c in table['coefficients']:
                if c['multiindex'] == [0, 1, 0, 0]:
                    for i, j, a in c['entries']: r[i,j] += s.Rational(a)
        self.assertEqual((p[10,:]*r[:,233])[0], -s.Rational(1,4))
        self.assertEqual((r[10,:5]*p[:5,233])[0], s.Rational(1,4))


if __name__ == '__main__': unittest.main()
