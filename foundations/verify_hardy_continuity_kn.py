#!/usr/bin/env python3
from __future__ import annotations
import ast,hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_hardy_continuity_kn import check
RESULT=ROOT/'foundations/results/FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1.json';SCHEMA=ROOT/'foundations/schema/foundational-hardy-continuity-kn-audit-v1.schema.json';REPORT=ROOT/'foundations/reports/hardy-continuity-kn-foundational-audit.md';LEDGER=ROOT/'foundations/literature-ledger.json';CHECKER=ROOT/'foundations/check_hardy_continuity_kn.py'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):
 o=set();t=ast.parse(p.read_text())
 for n in ast.walk(t):
  if isinstance(n,ast.Import):o.update(a.name.split('.')[0] for a in n.names)
  elif isinstance(n,ast.ImportFrom) and n.module and n.module!='__future__':o.add(n.module.split('.')[0])
 return o
def verify(*,result=None,ledger=None,report=None):
 r=load(RESULT) if result is None else result;l=load(LEDGER) if ledger is None else ledger;t=REPORT.read_text() if report is None else report;load(SCHEMA);e=[];c=['artifacts parse']
 if r.get('result_id')!='FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1' or r.get('lifecycle')!='SEPARATED' or r.get('dependency_tags')!=['LOCAL-ALGEBRAIC']:e.append('identity boundary')
 if r.get('programme_context',{}).get('opportunity_realized')!='OP-OPERATIONAL-RECONSTRUCTION-STRENGTH':e.append('opportunity')
 c.append('identity/opportunity')
 enc=r.get('mathematical_encoding',{})
 if enc.get('base_upper_bound')!='RCA_0' or enc.get('minimality')!='NOT_CLAIMED':e.append('base/minimality')
 rel=r.get('relation',{})
 if rel.get('primary')!='SUFFICIENT_OVER_BASE' or rel.get('secondary')!='REPRESENTATION_SENSITIVE' or rel.get('avoidance')!='AVOIDED_BY_REFORMULATION':e.append('relations')
 dep={x.get('item'):x for x in r.get('dependency_classification',[])}
 for key in ('extreme-value theorem','compact Lie-group representation','Hilbert-space spectral theorem'):
  if dep.get(key,{}).get('status')!='NOT_USED_BY_SELECTED_STEP':e.append('later dependency promoted')
 if dep.get('uniform-modulus extraction from pointwise continuity on [0,1]',{}).get('status')!='USED_ONLY_IF_MODULUS_NOT_SUPPLIED':e.append('representation boundary')
 c.append('representation-sensitive dependency table')
 ce,s=check(r);e.extend('checker '+x for x in ce)
 if s.get('digest')!=r.get('independent_checker',{}).get('expected_digest') or s.get('cases')!=42:e.append('checker witness')
 if imports(CHECKER)!=set(r.get('independent_checker',{}).get('permitted_runtime_modules',[])):e.append('checker imports')
 c.append('independent finite checker')
 lit=r.get('literature_dependency',{});entry=next((x for x in l.get('entries',[]) if x.get('id')=='hardy-2001'),None)
 if sha(LEDGER)!=lit.get('local_ledger_sha256') or not entry or entry.get('artifact',{}).get('sha256')!=lit.get('pinned_pdf_sha256'):e.append('literature pin')
 c.append('Hardy artifact pin')
 flags=r.get('claim_flags',{})
 for f in ('hardy_kn_step_audited','rca0_sufficient_for_explicit_modulus_route'):
  if flags.get(f) is not True:e.append('positive '+f)
 for f in ('physical_axiom_implies_rca0_or_wkl0','weakest_base_proved','full_hardy_reconstruction_audited','empirical_superiority_established','lorentzian_claim'):
  if flags.get(f) is not False:e.append('boundary '+f)
 c.append('fail-closed flags')
 for token in ('FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1','Axiom 5','RCA_0','SUFFICIENT_OVER_BASE','REPRESENTATION_SENSITIVE','AVOIDED_BY_REFORMULATION','uniform modulus','pointwise continuity','compact Lie group','does not imply','LORENTZIAN-CAUSAL'):
  if token not in t:e.append('report '+token)
 c.append('report mirrors audit')
 return e,c
def main():
 e,c=verify();print('FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1: '+('PASS' if not e else 'FAIL'))
 for x in (c if not e else e):print('  - '+x)
 return bool(e)
if __name__=='__main__':sys.exit(main())
