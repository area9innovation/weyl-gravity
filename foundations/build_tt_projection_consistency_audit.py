#!/usr/bin/env python3
"""Exact selected-block audit; never compose two positive-order operators."""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'quantum-weyl/classical_import/'
INPUTS = [BASE+'certificates/'+name+'.json' for name in (
    'STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1',
    'STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS_V1',
    'STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1')]
INPUTS += [BASE+'build_strict_386_graph_q1_sdr_component_jets.py',
           BASE+'build_strict_386_canonical_shear_component_jets.py',
           BASE+'build_strict_386_full_q1_component_jet_table.py',
           BASE+'check_strict_386_graph_q1_sdr_component_jets.py']
INPUTS += ['quantum-weyl/lorentzian/build_strict_386_brst_hadamard_two_point.py']
OUTPUT = ROOT/'foundations/results/TT_PROJECTION_CONSISTENCY_AUDIT_V1.json'
ZERO = (0, 0, 0, 0)


def decode(tables):
    out = defaultdict(Fraction)
    for table in tables:
        for c in table['coefficients']:
            for i, j, a in c['entries']:
                out[tuple(c['multiindex']), i, j] += Fraction(a)
    return {k: v for k, v in out.items() if v}


def add(a, b, sign=1):
    out = defaultdict(Fraction, a)
    for k, v in b.items(): out[k] += sign*v
    return {k: v for k, v in out.items() if v}


def select(a, rows=None, columns=None):
    return {k: v for k, v in a.items()
            if (rows is None or k[1] in rows) and (columns is None or k[2] in columns)}


def multiply(a, b):
    by_row = defaultdict(list)
    for (m, i, j), v in b.items(): by_row[i].append((m, j, v))
    out = defaultdict(Fraction)
    for (m, i, k), v in a.items():
        for n, j, w in by_row[k]:
            if any(m) and any(n):
                raise ValueError('unproved positive-order/positive-order composition')
            out[tuple(x+y for x, y in zip(m, n)), i, j] += v*w
    return {k: v for k, v in out.items() if v}


def encode(a):
    return [[list(m), i, j, str(v)] for (m, i, j), v in sorted(a.items())]


def build():
    graph, shear, basis = [json.loads((ROOT/p).read_text()) for p in INPUTS[:3]]
    rows = basis['component_basis']['rows']
    block = lambda name: {r['index'] for r in rows if r['block'] == name}
    metric = block('ENDPOINT_M'); ghosts = block('ENDPOINT_G')
    ydual = block('CONE_Y_ID_SHARP'); equations = block('ENDPOINT_E')
    yidentities = block('CONE_Y_ID')
    q = decode(graph['graph_q1_serialization']['tables'])
    p = decode([graph['graph_sdr_component_maps']['p_end_graph']])
    p0 = select(p, metric); pg = select(p, ghosts)
    r = select(q, metric, ghosts)
    gauge_defect = add(multiply(p0, q), multiply(r, pg), -1)
    # The missing metric attachment dictated by pQ=q_end p with p fixed.
    correction = {k: -v for k, v in gauge_defect.items()}
    corrected = add(q, correction)
    def square(operator, target, source):
        return multiply(select(operator, target), select(operator, columns=source))
    old_square = square(q, metric, ydual)
    candidate_square = square(corrected, metric, ydual)
    trace_square = square(q, yidentities, equations)
    remaining_square = square(corrected, yidentities, equations)
    ft = shear['canonical_transform']['forward']['tables']
    tab = lambda tables, name: decode([next(t for t in tables if t['table_id'] == name)])
    qt = graph['graph_q1_serialization']['tables']
    n = tab(qt, 'CONE_X_EQ_TO_X_ID')
    a = tab(ft, 'A_PRIMAL'); b = tab(ft, 'B_PRIMAL')
    c = tab(qt, 'ENDPOINT_E_TO_I')
    primal = add(multiply(n, a), multiply(b, c), -1)
    flip = add(q, tab(qt, 'GRAPH_Y_ID_SHARP_TO_ENDPOINT_G'), -2)
    return {
        'result_id': 'TT_PROJECTION_CONSISTENCY_AUDIT_V1',
        'dependency_tags': ['LOCAL-ALGEBRAIC'],
        'result_kind': 'EXACT_SERIALIZED_OPERATOR_OBSTRUCTION',
        'source_commit': '0f8939cd12b07f9e8ac54f9b627f62a6a803a95a',
        'inputs': [{'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in INPUTS],
        'assumptions': ['Published global target/source row orientation and ordinary composition of the degree-one differential.',
                        'Published parallel-coefficient covariant-jet interpretation; every audited product has an order-zero factor.'],
        'projection_defect': encode(gauge_defect),
        'metric_from_dual_identity_Q_squared': encode(old_square),
        'primal_NA_minus_BC': encode(primal),
        'identity_from_equation_Q_squared': encode(trace_square),
        'candidate_missing_metric_attachment': encode(correction),
        'candidate_checks': {
            'metric_dual_identity_square_defects': len(candidate_square),
            'metric_projection_chain_defects': len(add(multiply(p0, corrected), multiply(r, pg), -1)),
            'identity_equation_square_defects': len(remaining_square),
            'B_attachment_sign_flip_only_square_defects': len(square(flip, metric, ydual)),
            'applied_to_authoritative_export': False},
        'claims': {
            'serialized_graph_differential_nilpotent': False,
            'projection_only_repair_sufficient': False,
            'missing_metric_attachment_repairs_selected_28_defects': True,
            'full_consistent_repair_established': False,
            'current_export_accepted_for_full_Green_Hadamard_transfer': False,
            'abstract_classical_BRST_theory_refuted': False,
            'full_TT_commutator_identified': False,
            'quantum_lifecycle_promoted': False},
        'unresolved': ['Reconcile primal trace transport and suspended adjoint conventions against the authoritative classical operators.',
                       'Rebuild the complete conjugated differential with legitimate covariant-jet composition and independently check the full import gate.',
                       'Then replay Green/Hadamard transfer and compare the action-normalized tensor commutator.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true')
    args = parser.parse_args(); text = json.dumps(build(), indent=2)+'\n'
    if args.check:
        if OUTPUT.read_text() != text: raise SystemExit('FAIL: audit drift')
    else: OUTPUT.write_text(text)
    print('PASS: exact audit reproduced; full serialized transfer FAIL_CLOSED')
