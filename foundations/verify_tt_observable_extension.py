#!/usr/bin/env python3
"""Independent exact sparse-matrix checks and reconciled upstream replay."""
import hashlib
import importlib.util
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'foundations/results/TT_OBSERVABLE_EXTENSION_V1.json'


def require(value, message):
    if not value: raise ValueError(message)


def multiply(a, b):
    out = defaultdict(F)
    by_row = defaultdict(list)
    for (i, j), v in b.items(): by_row[i].append((j, v))
    for (i, k), v in a.items():
        for j, w in by_row[k]: out[i, j] += v*w
    return {k: v for k, v in out.items() if v}


def verify(value=None):
    v = json.loads(RESULT.read_text()) if value is None else value
    for record in v['inputs']:
        require(hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'], 'input hash')
    graph = json.loads((ROOT / v['inputs'][0]['path']).read_text())
    basis = json.loads((ROOT / v['inputs'][1]['path']).read_text())['component_basis']['rows']
    degree = {r['index']: r['degree'] for r in basis}
    maps = graph['graph_sdr_component_maps']
    def block(name, selected):
        out = {}
        for c in maps[name]['coefficients']:
            for i, j, raw in c['entries']:
                if selected(i, j):
                    require(not any(c['multiindex']), 'expected zero-order block')
                    out[i, j] = F(raw)
        return out
    p0 = block('p_end_graph', lambda i, j: 5 <= i < 15)
    pg = block('p_end_graph', lambda i, j: i < 5)
    # p0 also sees complement columns; include their inclusion rows when present.
    i0 = block('i_end_graph', lambda i, j: 5 <= j < 15 and i in {k[1] for k in p0})
    require(multiply(p0, i0) == {(i, i): F(1) for i in range(5, 15)}, 'metric retract')
    expected = [[i, j, str(a)] for (i, j), a in sorted(p0.items())]
    require(sorted(v['metric_projection']['entries']) == expected, 'exported metric projection')
    require(len(expected) == 25 and v['metric_projection']['order'] == 0, 'metric lift census')
    # All q coefficients are read from serialized global indices. Since p0 and
    # pg are parallel order-zero maps, no covariant derivative commutation occurs.
    q = defaultdict(lambda: defaultdict(F))
    for table in graph['graph_q1_serialization']['tables']:
        for c in table['coefficients']:
            for i, j, a in c['entries']:
                if degree[i] == 0 and degree[j] == -1:
                    q[tuple(c['multiindex'])][i, j] += F(a)
    zero = (0, 0, 0, 0)
    endpoint_q = {index: {(i, j): a for (i, j), a in r.items()
                          if 5 <= i < 15 and j < 5 and a} for index, r in q.items()}
    gamma0 = dict(pg)
    for pair in ((0, 238), (1, 232), (2, 233), (3, 234)):
        gamma0[pair] = -F(1, 4)
    gamma = {zero: gamma0}
    for axis, source in enumerate((238, 232, 233, 234)):
        index = tuple(int(a == axis) for a in range(4))
        gamma[index] = {(4, source): F(1, 16)}
    rhs = defaultdict(lambda: defaultdict(F))
    for a, r in endpoint_q.items():
        for b, g in gamma.items():
            product = multiply(r, g)
            require(not (any(a) and any(b) and product), 'noncommuting derivatives needed')
            for key, value in product.items():
                rhs[tuple(x+y for x, y in zip(a, b))][key] += value
    defects = []
    for index in set(q) | set(rhs):
        left = multiply(p0, q.get(index, {}))
        right = {k: a for k, a in rhs.get(index, {}).items() if a}
        require(left == right, 'p0 R386 = Rmetric Gamma')
        old_right = multiply(endpoint_q.get(index, {}), pg)
        for key in sorted(left.keys() | old_right.keys()):
            delta = left.get(key, F()) - old_right.get(key, F())
            if delta:
                defects.append([list(index), *key, str(delta)])
    require(len(defects) == 28, 'advertised projection defect count')
    witness = [[0, 1, 0, 0], 10, 233, '-1/2']
    require(witness in defects and v['advertised_projection_chain_witness'] == witness, 'principal witness')
    require(v['gauge_factorization'] == {
        'zero_order_ghost_changes': [[0, 238, '-1/4'], [1, 232, '-1/4'], [2, 233, '-1/4'], [3, 234, '-1/4']],
        'Weyl_derivative_coefficients': [[axis, source, '1/16'] for axis, source in enumerate((238, 232, 233, 234))],
        'identity': 'p0 R386 = Rmetric Gamma', 'advertised_pghost_identity_defects': 28,
    }, 'factorization export')
    old = json.loads((ROOT / v['inputs'][2]['path']).read_text())
    new_path = ROOT / v['reconciliation']['new_reference']
    new = json.loads(new_path.read_text())
    record = old['dependencies']['causal_pairing_transport']
    record['sha256'] = hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest()
    require(old == new, 'reconciliation changed scientific content')
    require(v['claims'] == {
        'order_zero_compact_source_lift': True, 'coefficientwise_gauge_factorization': True,
        'advertised_projection_gauge_chain_identity': False,
        'conditional_positivity_transport_argument': True, 'full_strict_physical_positivity_decided': False,
        'all_energy_TT_commutator_normalization_identified': False, 'quantum_lifecycle_promoted': False}, 'claim boundary')
    return v


def replay_reference():
    path = ROOT / 'quantum-weyl/lorentzian/verify_vacuum_cylinder_reduced_bridge4_hadamard.py'
    spec = importlib.util.spec_from_file_location('tt_reference_independent', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.OUTPUT = ROOT / 'foundations/inputs/tt-reduced-reference-reconciled-v1.json'
    result = module.verify(); module.mutation_guards(result)


if __name__ == '__main__':
    verify(); replay_reference()
    print('PASS: 25-entry order-zero metric lift, exact repaired gauge factorization, 28 advertised-chain defects, metric retract, reconciled reduced reference; full positivity remains OPEN')
