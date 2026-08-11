#!/usr/bin/env python3
"""Verify the explicit energy spectral-fragment certificate."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from foundations.check_explicit_energy_spectral_fragment import check

RESULT=ROOT/"foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json"
SCHEMA=ROOT/"foundations/schema/foundational-explicit-energy-spectral-fragment-zf-v1.schema.json"
REPORT=ROOT/"foundations/reports/explicit-energy-spectral-fragment-audit.md"
CHECKER=ROOT/"foundations/check_explicit_energy_spectral_fragment.py"
DOMAINS=ROOT/"analytic_completion/certificates/generator_domains.json"
BLOCKS=ROOT/"analytic_completion/certificates/finite_total_degree_blocks.json"
SHA=re.compile(r"^[0-9a-f]{64}$")

def load(path:Path)->Any: return json.loads(path.read_text())
def digest(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def imports(path:Path)->set[str]:
    tree=ast.parse(path.read_text()); out=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): out.update(a.name.split('.')[0] for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module and n.module!='__future__': out.add(n.module.split('.')[0])
    return out
def acyclic(nodes:set[str],edges:list[dict[str,Any]])->bool:
    out={n:[] for n in nodes}; degree={n:0 for n in nodes}
    for e in edges:
        a,b=e.get('from'),e.get('to')
        if a not in nodes or b not in nodes:return False
        out[a].append(b);degree[b]+=1
    ready=[n for n in nodes if degree[n]==0]; seen=0
    while ready:
        n=ready.pop();seen+=1
        for b in out[n]:
            degree[b]-=1
            if degree[b]==0:ready.append(b)
    return seen==len(nodes)

def verify(*,result=None,domains=None,blocks=None,report=None)->tuple[list[str],list[str]]:
    result=load(RESULT) if result is None else result; domains=load(DOMAINS) if domains is None else domains
    blocks=load(BLOCKS) if blocks is None else blocks; report=REPORT.read_text() if report is None else report
    load(SCHEMA); errors=[]; checks=["all artifacts parse"]
    if result.get('result_id')!='FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1':errors.append('id drift')
    if result.get('lifecycle')!='SUFFICIENCY_PROVED' or result.get('dependency_tags')!=['LOCAL-ALGEBRAIC','REDUCED-MODE']:errors.append('lifecycle or tags drift')
    ctx=result.get('programme_context',{})
    if ctx.get('opportunity_realized')!='OP-SPECTRAL-FRAGMENT-AUDIT' or ctx.get('phase')!='B_COMPLETE':errors.append('opportunity link drift')
    checks.append('identity and phase-B link')
    fragments={x.get('id'):x for x in result.get('fragment_classification',[])}
    if set(fragments)!={'FINITE-CUTOFF','MAXIMAL-DIAGONAL','COORDINATE-PVM','CONTINUOUS-FUNCTIONAL-CALCULUS','COMPACT-RESOLVENT','FOCK-ENERGY','COMPACT-SELF-ADJOINT-DECOMPOSITION','GENERAL-PVM-SPECTRAL-THEOREM'}:errors.append('fragment inventory drift')
    for key in ('COMPACT-SELF-ADJOINT-DECOMPOSITION','GENERAL-PVM-SPECTRAL-THEOREM'):
        if fragments.get(key,{}).get('relation')!='NOT_USED_BY_DISPLAYED_PROOF':errors.append(f'abstract theorem promoted: {key}')
    if fragments.get('MAXIMAL-DIAGONAL',{}).get('base_theory')!='ZF' or fragments.get('FINITE-CUTOFF',{}).get('base_theory')!='PRA':errors.append('base separation drift')
    avoid=result.get('avoidance_classification',{})
    if avoid.get('relation')!='AVOIDED_BY_REFORMULATION' or avoid.get('status')!='PROVED_FOR_EXPLICIT_ENERGY_OPERATOR':errors.append('avoidance drift')
    checks.append('eight spectral fragments and avoidance boundary')
    ce,summary=check(result);errors.extend('checker: '+e for e in ce)
    if summary.get('digest')!=result.get('independent_checker',{}).get('expected_digest') or summary.get('coordinates')!=3740:errors.append('checker digest/count drift')
    checks.append('exact coordinate and occupation checker')
    permitted=set(result.get('independent_checker',{}).get('permitted_runtime_modules',[]))
    if imports(CHECKER)!=permitted:errors.append('checker import boundary drift')
    source=CHECKER.read_text().lower()
    if any(t in source for t in ('import sympy','import numpy','float(','eig(','network')):errors.append('checker forbidden token')
    checks.append('checker independence')
    cp=result.get('coordinate_proof',{})
    if domains.get('D_domain')!='sum_n n^2 ||u_n||^2 finite' or not domains.get('D_hilbert_self_adjoint') or not domains.get('D_krein_self_adjoint'):errors.append('source D claim drift')
    if cp.get('domain')!='Dom(D)={x in l2(I): sum_i energy(i)^2 |x_i|^2 is finite}':errors.append('foundational D domain drift')
    expected={str(k):v for k,v in list(result.get('fock_proof',{}).get('matter_fixed_energy_dimensions',{}).items())[:5]}
    for k,v in {'0':1,'1':0,'2':10,'3':40,'4':137}.items():
        if result.get('fock_proof',{}).get('matter_fixed_energy_dimensions',{}).get(k)!=v:errors.append('low Fock count drift')
    if blocks.get('matter_energy_operator')!='self-adjoint dGamma(D) on its spectral domain' or not blocks.get('all_total_degree_blocks_finite'):errors.append('source Fock claim drift')
    checks.append('source domain and Fock claims agree')
    for item in result.get('provenance',{}).get('inputs',[]):
        p=ROOT/item.get('path',''); h=item.get('sha256')
        if not p.is_file() or not SHA.fullmatch(str(h)) or digest(p)!=h:errors.append('provenance mismatch: '+item.get('path',''))
    checks.append('content-pinned inputs')
    dag=result.get('proof_dependency_dag',{}); ids=[n.get('id') for n in dag.get('nodes',[])]
    if len(ids)!=len(set(ids)) or not acyclic(set(ids),dag.get('edges',[])):errors.append('DAG invalid')
    checks.append('acyclic proof DAG')
    flags=result.get('claim_flags',{})
    for f in ('explicit_energy_self_adjointness_route_classified','fock_fixed_energy_finiteness_route_classified'):
        if flags.get(f) is not True:errors.append('positive flag drift: '+f)
    for f in ('abstract_spectral_theorem_used','weakest_base_proved','euclidean_spectral_measures_classified','determinant_or_trace_constructed','lorentzian_claim'):
        if flags.get(f) is not False:errors.append('boundary flag drift: '+f)
    checks.append('fail-closed flags')
    for token in ('FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1','USED_BY_DISPLAYED_PROOF','NOT_USED_BY_DISPLAYED_PROOF','AVOIDED_BY_REFORMULATION','Primitive Recursive Arithmetic','Countable Choice','dGamma(D)','not the weakest','LORENTZIAN-CAUSAL'):
        if token not in report:errors.append('report missing '+token)
    checks.append('report boundary')
    return errors,checks

def main()->int:
    e,c=verify(); print('FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1: '+('PASS' if not e else 'FAIL'))
    for x in (c if not e else e):print('  - '+x)
    return bool(e)
if __name__=='__main__':sys.exit(main())
