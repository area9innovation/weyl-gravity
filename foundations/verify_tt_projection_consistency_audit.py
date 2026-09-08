#!/usr/bin/env python3
"""Independent SymPy polynomial-matrix rail for selected, composition-safe blocks."""
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT/'foundations/results/TT_PROJECTION_CONSISTENCY_AUDIT_V1.json'
X = s.symbols('d0:4')


def require(condition, message):
    if not condition: raise ValueError(message)


def matrix(tables):
    entries = {}
    for table in tables:
        for c in table['coefficients']:
            monomial = s.prod(x**n for x, n in zip(X, c['multiindex']))
            for i, j, v in c['entries']:
                entries[i, j] = entries.get((i, j), 0)+s.Rational(v)*monomial
    return s.SparseMatrix(386, 386, entries)


def product(left, right, targets, sources):
    # Check individual paths BEFORE polynomial multiplication: this prevents
    # a commuting-symbol cancellation from concealing unproved PBW products.
    l = left.extract(targets, range(386)); r = right.extract(range(386), sources)
    l_nonconstant = {j for (i, j), v in l.todok().items() if v.free_symbols}
    r_nonconstant = {i for (i, j), v in r.todok().items() if v.free_symbols}
    require(not (l_nonconstant & r_nonconstant), 'unsafe derivative composition')
    return l*r


def records(m, targets, sources):
    out = []
    for (i, j), value in m.todok().items():
        for powers, coefficient in s.Poly(s.expand(value), *X).terms():
            if coefficient: out.append([list(powers), targets[i], sources[j], str(coefficient)])
    return sorted(out)


def verify(value=None):
    v = json.loads(RESULT.read_text()) if value is None else value
    for item in v['inputs']:
        require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'hash drift')
    graph, shear, basis = [json.loads((ROOT/i['path']).read_text()) for i in v['inputs'][:3]]
    block = lambda name: [r['index'] for r in basis['component_basis']['rows'] if r['block'] == name]
    metric = block('ENDPOINT_M'); ydual = block('CONE_Y_ID_SHARP')
    equations = block('ENDPOINT_E'); identities = block('CONE_Y_ID')
    allrows = list(range(386)); qt = graph['graph_q1_serialization']['tables']
    q = matrix(qt); p = matrix([graph['graph_sdr_component_maps']['p_end_graph']])
    endpoint = matrix([t for t in qt if t['table_id'] == 'ENDPOINT_G_TO_M'])
    defect = product(p, q, metric, allrows)-product(endpoint, p, metric, allrows)
    require(records(defect, metric, allrows) == v['projection_defect'], 'projection coefficients')
    require(len(v['projection_defect']) == 28, 'projection count')
    for rows, columns, field, count in (
        (metric, ydual, 'metric_from_dual_identity_Q_squared', 28),
        (identities, equations, 'identity_from_equation_Q_squared', 16)):
        actual = records(product(q, q, rows, columns), rows, columns)
        require(actual == v[field] and len(actual) == count, field)
    ft = shear['canonical_transform']['forward']['tables']
    one = lambda tables, name: matrix([t for t in tables if t['table_id'] == name])
    n = one(qt, 'CONE_X_EQ_TO_X_ID'); a = one(ft, 'A_PRIMAL')
    b = one(ft, 'B_PRIMAL'); c = one(qt, 'ENDPOINT_E_TO_I')
    xid = block('CONE_X_ID')
    primal = product(n, a, xid, equations)-product(b, c, xid, equations)
    require(records(primal, xid, equations) == v['primal_NA_minus_BC'], 'primal trace mismatch')
    require(len(v['primal_NA_minus_BC']) == 16, 'primal count')
    correction = s.SparseMatrix(386, 386, {})
    for powers, i, j, coefficient in v['candidate_missing_metric_attachment']:
        correction[i, j] += s.Rational(coefficient)*s.prod(x**n for x, n in zip(X, powers))
    require(records(correction.extract(metric, allrows), metric, allrows) == records(-defect, metric, allrows), 'candidate correction')
    require(len(correction.todok()) == len(correction.extract(metric, allrows).todok()), 'candidate outside scope')
    repaired = q+correction
    gauge = product(p, repaired, metric, allrows)-product(endpoint, p, metric, allrows)
    flip = q-2*one(qt, 'GRAPH_Y_ID_SHARP_TO_ENDPOINT_G')
    checks = {
        'metric_dual_identity_square_defects': len(records(product(repaired, repaired, metric, ydual), metric, ydual)),
        'metric_projection_chain_defects': len(records(gauge, metric, allrows)),
        'identity_equation_square_defects': len(records(product(repaired, repaired, identities, equations), identities, equations)),
        'B_attachment_sign_flip_only_square_defects': len(records(product(flip, flip, metric, ydual), metric, ydual)),
        'applied_to_authoritative_export': False}
    require(checks == v['candidate_checks'] == {
        'metric_dual_identity_square_defects': 0, 'metric_projection_chain_defects': 0,
        'identity_equation_square_defects': 16, 'B_attachment_sign_flip_only_square_defects': 16,
        'applied_to_authoritative_export': False}, 'candidate scope')
    require(v['dependency_tags'] == ['LOCAL-ALGEBRAIC'], 'dependency boundary')
    require(v['claims'] == {
        'serialized_graph_differential_nilpotent': False, 'projection_only_repair_sufficient': False,
        'missing_metric_attachment_repairs_selected_28_defects': True,
        'full_consistent_repair_established': False,
        'current_export_accepted_for_full_Green_Hadamard_transfer': False,
        'abstract_classical_BRST_theory_refuted': False, 'full_TT_commutator_identified': False,
        'quantum_lifecycle_promoted': False}, 'claim boundary')
    # Two tiny independently readable path witnesses, not only inventory agreement.
    require(q[10, 2] == X[1] and q[2, 313] == -s.Rational(1, 4), 'first sign path')
    require(q[10, 332] == s.Rational(1, 4) and q[332, 313] == -X[1], 'second sign path')
    require(q[218, 210] == X[1]/3 and q[210, 15] == s.Rational(3, 8), 'trace path')
    return v


if __name__ == '__main__':
    verify()
    print('PASS: independent polynomial rail; Q squared witnesses -d1/2 and d1/8; full transfer FAIL_CLOSED')
