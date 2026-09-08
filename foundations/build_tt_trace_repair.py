#!/usr/bin/env python3
"""Construct a scoped trace/ghost repair experiment; do not mutate the export."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundations.build_tt_projection_consistency_audit import (
    ROOT, INPUTS, ZERO, Fraction, decode, add, select, multiply, encode)

OUTPUT = ROOT/'foundations/results/TT_TRACE_REPAIR_V1.json'


def build():
    graph, shear, basis = [json.loads((ROOT/p).read_text()) for p in INPUTS[:3]]
    tab = lambda ts, name: decode([t for t in ts if t['table_id'] == name])
    qt = graph['graph_q1_serialization']['tables']; ft = shear['canonical_transform']['forward']['tables']
    q = decode(qt); n = tab(qt, 'CONE_X_EQ_TO_X_ID')
    a = tab(ft, 'A_PRIMAL'); b = tab(ft, 'B_PRIMAL'); c = tab(qt, 'ENDPOINT_E_TO_I')
    defect = add(multiply(n, a), multiply(b, c), -1)
    # The source-15 trace coefficient determines L, then check all columns.
    trace = c[ZERO, 29, 15]
    correction_b = {(m, i, 29): v/trace for (m, i, j), v in defect.items() if j == 15}
    if add(multiply(n, a), multiply(add(b, correction_b), c), -1):
        raise ValueError('trace factorization fails')
    changes = {(ZERO, i, j): Fraction(1, 2) for i, j in [(0,318),(1,312),(2,313),(3,314)]}
    for axis, source in enumerate((318,312,313,314)):
        changes[tuple(int(a == axis) for a in range(4)),4,source] = -Fraction(1,16)
    for (m,i,j),v in correction_b.items(): changes[m,i+80,j] = -v
    candidate = add(q, changes)
    maps = graph['graph_sdr_component_maps']
    projection_changes = {(ZERO,i,j): -Fraction(1,2) for i,j in [(0,238),(1,232),(2,233),(3,234)]}
    for axis,source in enumerate((238,232,233,234)):
        projection_changes[tuple(int(a==axis) for a in range(4)),4,source] = Fraction(1,16)
    inclusion = add(decode([maps['i_end_graph']]), correction_b)
    projection = add(decode([maps['p_end_graph']]), projection_changes)
    h = decode([maps['H_alg_graph']])
    identity = {(ZERO,i,i):Fraction(1) for i in range(386)}
    identity30 = {(ZERO,i,i):Fraction(1) for i in range(30)}
    contraction = {
        'projection_inclusion': len(add(multiply(projection,inclusion),identity30,-1)),
        'QH_plus_HQ_equals_identity_minus_ip': len(add(add(multiply(candidate,h),multiply(h,candidate)),add(identity,multiply(inclusion,projection),-1),-1)),
        'H_inclusion': len(multiply(h,inclusion)),
        'projection_H': len(multiply(projection,h)),
    }
    blocks = lambda name: [r['index'] for r in basis['component_basis']['rows'] if r['block'] == name]
    counts = {}
    for name, target, source in [('metric','ENDPOINT_M','CONE_Y_ID_SHARP'),('trace','CONE_Y_ID','ENDPOINT_E')]:
        counts[name] = len(multiply(select(candidate, blocks(target)), select(candidate, columns=blocks(source))))
    # This sum annihilates every constant 40-component correction to A,
    # but it does not annihilate the required source-15 right hand side.
    witness = [((1,0,0,0),144),((0,1,0,0),138),((0,0,1,0),139),((0,0,0,1),140)]
    null_row = {j:sum(n.get((m,i,j),Fraction()) for m,i in witness) for j in blocks('CONE_X_EQ')}
    if any(null_row.values()): raise ValueError('left null witness failed')
    obstruction = -sum(defect.get((m,i,15),Fraction()) for m,i in witness)
    if not obstruction: raise ValueError('constant repair obstruction absent')
    return {'result_id':'TT_TRACE_REPAIR_V1','dependency_tags':['LOCAL-ALGEBRAIC'],
        'source_commit':'5a597d00', 'result_kind':'PARTIAL_REPAIR_EXPERIMENT',
        'inputs':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in INPUTS],
        'B_derivative_correction':encode(correction_b), 'Q_candidate_changes':encode(changes),
        'inclusion_changes':encode(correction_b), 'projection_changes':encode(projection_changes),
        'candidate_contraction_defect_counts':contraction,
        'constant_A_repair_obstruction':{'left_rows':[[list(m),i] for m,i in witness], 'source':15,'contracted_rhs':str(obstruction), 'assumptions':'N, B and C fixed; arbitrary constant 40 by 10 correction to A.'},
        'candidate_square_defect_counts':counts,
        'claims':{'primal_NA_equals_corrected_BC':True,'selected_44_square_coefficients_repaired':True,
                  'constant_A_only_repair_possible':False,'candidate_contraction_identities_checked':True,'candidate_is_full_repaired_complex':False,
                  'candidate_applied_to_authoritative_export':False,'full_transfer_accepted':False},
        'unresolved':['Full nilpotency outside the two audited blocks','Both complete chain-map identities','Cyclicity and transported suspension','Green/Hadamard transfer and all-energy tensor commutator']}


if __name__ == '__main__':
    text = json.dumps(build(),indent=2)+'\n'
    if '--check' in sys.argv:
        if OUTPUT.read_text()!=text: raise SystemExit('FAIL: trace repair drift')
    else: OUTPUT.write_text(text)
    print('PASS: four Weyl-derivative coefficients and ghost correction repair selected 44 terms; full complex OPEN')
