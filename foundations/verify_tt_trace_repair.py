#!/usr/bin/env python3
"""Independent matrix verification of the trace repair and left-null obstruction."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundations.verify_tt_projection_consistency_audit import ROOT, X, s, matrix, product, require

RESULT = ROOT/'foundations/results/TT_TRACE_REPAIR_V1.json'


def verify(v=None):
    v=json.loads(RESULT.read_text()) if v is None else v
    for item in v['inputs']:
        require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'input drift')
    g,sh,ba=[json.loads((ROOT/i['path']).read_text()) for i in v['inputs'][:3]]
    qt=g['graph_q1_serialization']['tables']; ft=sh['canonical_transform']['forward']['tables']
    one=lambda ts,name:matrix([t for t in ts if t['table_id']==name])
    q=matrix(qt); n=one(qt,'CONE_X_EQ_TO_X_ID'); a=one(ft,'A_PRIMAL'); b=one(ft,'B_PRIMAL'); c=one(qt,'ENDPOINT_E_TO_I')
    block=lambda name:[r['index'] for r in ba['component_basis']['rows'] if r['block']==name]
    def correction(rows):
        entries={}
        for powers,i,j,val in rows: entries[i,j]=entries.get((i,j),0)+s.Rational(val)*s.prod(x**p for x,p in zip(X,powers))
        return s.SparseMatrix(386,386,entries)
    l=correction(v['B_derivative_correction'])
    require(len(v['B_derivative_correction'])==4 and all(j==29 for i,j in l.todok()),'Weyl correction scope')
    primal=product(n,a,block('CONE_X_ID'),block('ENDPOINT_E'))-product(b+l,c,block('CONE_X_ID'),block('ENDPOINT_E'))
    require(all(s.expand(x)==0 for x in primal),'corrected primal identity')
    delta=correction(v['Q_candidate_changes']); candidate=q+delta
    maps=g['graph_sdr_component_maps']
    inc=matrix([maps['i_end_graph']])+correction(v['inclusion_changes'])
    proj=matrix([maps['p_end_graph']])+correction(v['projection_changes'])
    h=matrix([maps['H_alg_graph']]); allrows=list(range(386))
    require(v['inclusion_changes']==v['B_derivative_correction'],'inclusion correction')
    require(len(v['projection_changes'])==8,'projection correction scope')
    pi=product(proj,inc,list(range(30)),list(range(30)))-s.eye(30)
    homotopy=product(candidate,h,allrows,allrows)+product(h,candidate,allrows,allrows)-s.eye(386)+product(inc,proj,allrows,allrows)
    hi=product(h,inc,allrows,list(range(30))); ph=product(proj,h,list(range(30)),allrows)
    for residual in (pi,homotopy,hi,ph):
        require(all(s.expand(x)==0 for x in residual.todok().values()),'candidate contraction')
    require(v['candidate_contraction_defect_counts']=={'projection_inclusion':0,'QH_plus_HQ_equals_identity_minus_ip':0,'H_inclusion':0,'projection_H':0},'contraction counts')
    require(len(v['Q_candidate_changes'])==12,'candidate count')
    for name,target,source in [('metric','ENDPOINT_M','CONE_Y_ID_SHARP'),('trace','CONE_Y_ID','ENDPOINT_E')]:
        square=product(candidate,candidate,block(target),block(source))
        require(all(s.expand(x)==0 for x in square),'candidate square '+name)
    witness=v['constant_A_repair_obstruction']
    require(witness['left_rows']==[[[1,0,0,0],144],[[0,1,0,0],138],[[0,0,1,0],139],[[0,0,0,1],140]],'null witness rows')
    require(witness['source']==15,'null witness source')
    d=product(n,a,block('CONE_X_ID'),[15])-product(b,c,block('CONE_X_ID'),[15])
    for j in block('CONE_X_EQ'):
        require(sum(s.Poly(n[i,j],*X).coeff_monomial(tuple(m)) for m,i in witness['left_rows'])==0,'left null')
    contracted=-sum(s.Poly(d[block('CONE_X_ID').index(i),0],*X).coeff_monomial(tuple(m)) for m,i in witness['left_rows'])
    require(str(contracted)==witness['contracted_rhs']=='-1/2','constant A obstruction')
    require(v['candidate_square_defect_counts']=={'metric':0,'trace':0},'counts')
    require(v['dependency_tags']==['LOCAL-ALGEBRAIC'],'tags')
    require(v['claims']=={'primal_NA_equals_corrected_BC':True,'selected_44_square_coefficients_repaired':True,
        'constant_A_only_repair_possible':False,'candidate_contraction_identities_checked':True,'candidate_is_full_repaired_complex':False,
        'candidate_applied_to_authoritative_export':False,'full_transfer_accepted':False},'claim boundary')
    return v


if __name__=='__main__':
    verify();print('PASS: independent trace repair and exact obstruction to constant-A-only repair; full transfer OPEN')
