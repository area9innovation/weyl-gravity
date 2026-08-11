#!/usr/bin/env python3
"""Verify the five-link BT separable C*-state audit."""
from __future__ import annotations
import ast,hashlib,json
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_bt_separable_state_chain import check
RESULT=ROOT/'foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json';SCHEMA=ROOT/'foundations/schema/foundational-bt-separable-state-chain-zf-v1.schema.json';REPORT=ROOT/'foundations/reports/bt-separable-cstar-state-chain.md';CHECKER=ROOT/'foundations/check_bt_separable_state_chain.py';LEDGER=ROOT/'foundations/literature-ledger.json'
SOURCES=[ROOT/'reverse_physics/certificates/REVERSE_PHYSICS_BT_CROSS_KREIN_TRACE_LIMIT_V1.json',ROOT/'reverse_physics/certificates/REVERSE_PHYSICS_BT_SEMIFINITE_RELATIVE_BORN_WEIGHT_V1.json',ROOT/'reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json',ROOT/'reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json']
def load(p:Path)->Any:return json.loads(p.read_text())
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p:Path)->set[str]:
 t=ast.parse(p.read_text());o=set()
 for n in ast.walk(t):
  if isinstance(n,ast.Import):o.update(a.name.split('.')[0] for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module and n.module!='__future__':o.add(n.module.split('.')[0])
 return o
def acyclic(nodes,edges):
 o={n:[] for n in nodes};d={n:0 for n in nodes}
 for e in edges:
  a,b=e.get('from'),e.get('to')
  if a not in nodes or b not in nodes:return False
  o[a].append(b);d[b]+=1
 q=[n for n in nodes if d[n]==0];seen=0
 while q:
  n=q.pop();seen+=1
  for b in o[n]:
   d[b]-=1
   if d[b]==0:q.append(b)
 return seen==len(nodes)
def verify(*,result=None,sources=None,ledger=None,report=None):
 r=load(RESULT) if result is None else result;s=[load(p) for p in SOURCES] if sources is None else sources;l=load(LEDGER) if ledger is None else ledger;t=REPORT.read_text() if report is None else report
 load(SCHEMA);e=[];c=['artifacts parse']
 if r.get('result_id')!='FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1' or r.get('lifecycle')!='SEPARATED':e.append('identity/lifecycle drift')
 if r.get('dependency_tags')!=['LOCAL-ALGEBRAIC','REDUCED-MODE'] or r.get('programme_context',{}).get('opportunity_realized')!='OP-SEPARABLE-CSTAR-STATE-CHAIN':e.append('tag/opportunity drift')
 c.append('identity and opportunity')
 objs={x.get('id'):x for x in r.get('object_separation',[])}
 if set(objs)!={'FINITE-RANK-ALGEBRA','SEPARABLE-DETECTOR-ALGEBRA','FULL-ORBIT-ALGEBRA','RESOLUTION-CCR-ALGEBRA'}:e.append('object typing drift')
 if objs.get('FULL-ORBIT-ALGEBRA',{}).get('separability')!='NOT_NORM_SEPARABLE' or objs.get('RESOLUTION-CCR-ALGEBRA',{}).get('relation_to_A')!='DISTINCT_ALGEBRA_NOT_IDENTIFIED':e.append('algebra conflation')
 chain=r.get('five_link_chain',[])
 if [x.get('link') for x in chain]!=[1,2,3,4,5] or [x.get('name') for x in chain]!=['ALGEBRA_CONSTRUCTION','POSITIVE_FUNCTIONAL_EXISTENCE','GNS_REPRESENTATION','PHYSICAL_STATE_SELECTION','DYNAMICS_AND_LOCAL_NORMALITY']:e.append('five-link chain drift')
 if any(chain[i].get('foundational_base')!='ZF' for i in range(3)) or any(chain[i].get('relation')!='NOT_IMPLIED_BY_PREVIOUS_LINK' for i in (3,4)):e.append('logical implication boundary drift')
 c.append('four objects and five links separated')
 ce,summary=check(r);e.extend('checker: '+x for x in ce)
 if summary.get('digest')!=r.get('independent_checker',{}).get('expected_digest') or summary.get('factor')!=5:e.append('exact witness drift')
 if imports(CHECKER)!=set(r.get('independent_checker',{}).get('permitted_runtime_modules',[])):e.append('checker imports drift')
 c.append('independent exact state/GNS controls')
 prov=r.get('provenance',{}).get('inputs',[])
 if len(prov)!=4:e.append('source ledger length')
 for item in prov:
  p=ROOT/item.get('path','')
  if not p.is_file() or sha(p)!=item.get('sha256'):e.append('source hash '+item.get('path',''))
 cross,semi,coherent,six=s
 if cross.get('disposition',{}).get('normal_trace_class_thermodynamic_limit')!='OBSTRUCTED':e.append('normal-limit obstruction drift')
 if semi.get('disposition',{}).get('canonical_semifinite_orbit_trace')!='CONSTRUCTED' or semi.get('disposition',{}).get('thermodynamic_normal_state')!='NOT_CONSTRUCTED':e.append('semifinite source drift')
 if coherent.get('disposition',{}).get('rank_two_physical_GNS_factor')!='CONSTRUCTED':e.append('GNS source drift')
 if six.get('disposition',{}).get('coherent_Poisson_dynamics')!='DISAGREES_BY_FACTOR_FIVE_AT_LEADING_ORDERED_DOUBLE_LOG':e.append('six-point source drift')
 c.append('four source certificates and hashes')
 lit=r.get('zf_literature_dependency',{});entry=next((x for x in l.get('entries',[]) if x.get('id')=='blackadar-farah-2026'),None)
 if sha(LEDGER)!=lit.get('local_ledger_sha256') or not entry or entry.get('artifact',{}).get('sha256')!=lit.get('pinned_pdf_sha256'):e.append('literature pin drift')
 if not {'Lemma 2.2.4','Theorem 3.0.5','Theorem 4.0.1'}<=set(lit.get('theorems_used',[])):e.append('theorem pins missing')
 c.append('ZF literature pins')
 dag=r.get('proof_dependency_dag',{});ids=[x.get('id') for x in dag.get('nodes',[])]
 if len(ids)!=len(set(ids)) or not acyclic(set(ids),dag.get('edges',[])):e.append('DAG invalid')
 flags=r.get('claim_flags',{})
 for f in ('separable_detector_algebra_constructed','explicit_zf_states_constructed','explicit_corner_gns_constructed'):
  if flags.get(f) is not True:e.append('positive flag '+f)
 for f in ('semifinite_weight_is_normalized_state','physical_thermodynamic_state_selected','coherent_state_dynamically_selected','full_orbit_algebra_separable','lorentzian_claim'):
  if flags.get(f) is not False:e.append('boundary flag '+f)
 c.append('DAG and fail-closed flags')
 for token in ('FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1','ALGEBRA_CONSTRUCTION','POSITIVE_FUNCTIONAL_EXISTENCE','GNS_REPRESENTATION','PHYSICAL_STATE_SELECTION','DYNAMICS_AND_LOCAL_NORMALITY','Countable Choice','semifinite weight','factor five','LORENTZIAN-CAUSAL'):
  if token not in t:e.append('report missing '+token)
 c.append('report mirrors chain')
 return e,c
def main():
 e,c=verify();print('FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1: '+('PASS' if not e else 'FAIL'))
 for x in (c if not e else e):print('  - '+x)
 return bool(e)
if __name__=='__main__':sys.exit(main())
