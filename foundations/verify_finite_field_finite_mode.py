#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_finite_field_finite_mode import check
RESULT=ROOT/'foundations/results/FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1.json';SCHEMA=ROOT/'foundations/schema/foundational-finite-field-finite-mode-non-equivalence-v1.schema.json';REPORT=ROOT/'foundations/reports/finite-field-versus-finite-mode.md';LEDGER=ROOT/'foundations/literature-supplement-known-attempts-v1.json'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(*,result=None,ledger=None,report=None):
 r=load(RESULT) if result is None else result;l=load(LEDGER) if ledger is None else ledger;t=REPORT.read_text() if report is None else report;load(SCHEMA);e=[];c=['artifacts parse']
 if r.get('result_id')!='FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1' or r.get('lifecycle')!='SEPARATED' or r.get('dependency_tags')!=['LOCAL-ALGEBRAIC','REDUCED-MODE']:e.append('identity')
 if r.get('programme_context',{}).get('opportunity_realized')!='OP-FINITE-FIELD-WEYL-BRIDGE':e.append('opportunity')
 ids={x.get('id') for x in r.get('typed_objects',[])}
 if ids!={'FINITE-FIELD-PHASE-SPACE','FINITE-MODE-CUTOFF','FINITE-DIMENSIONAL-COMPLEX-HILBERT','FOUNDATIONAL-FINITISM'}:e.append('types')
 if len(r.get('pairwise_non_equivalence',[]))!=6 or r.get('relations',{}).get('between_four_objects')!='NOT_EQUIVALENT_BY_TYPE':e.append('non-equivalence')
 c.append('four types and six witnesses')
 ce,s=check(r);e.extend('checker '+x for x in ce)
 if s.get('digest')!=r.get('independent_checker',{}).get('expected_digest') or s.get('mode_cutoff_12')!=3740:e.append('checker')
 c.append('exact finite counts')
 lit=r.get('literature_dependency',{});entry=next((x for x in l.get('entries',[]) if x.get('id')=='gibbons-hoffman-wootters-2004'),None)
 if sha(LEDGER)!=lit.get('local_ledger_sha256') or not entry or entry.get('artifact',{}).get('sha256')!=lit.get('pinned_pdf_sha256'):e.append('literature')
 for x in r.get('provenance',{}).get('inputs',[]):
  p=ROOT/x.get('path','')
  if not p.is_file() or sha(p)!=x.get('sha256'):e.append('provenance')
 c.append('literature/local pins')
 f=r.get('claim_flags',{})
 for k in ('four_objects_typed','pairwise_non_equivalence_witnessed'):
  if f.get(k) is not True:e.append('positive '+k)
 for k in ('continuum_bridge_constructed','finite_field_replaces_complex_quantum_scalars','mode_cutoff_implies_finitism','finitism_empirically_selected','lorentzian_claim'):
  if f.get(k) is not False:e.append('boundary '+k)
 c.append('fail-closed flags')
 for token in ('FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1','NOT_EQUIVALENT_BY_TYPE','F_q^2','C^q','3,740','actual infinity','regulator','LORENTZIAN-CAUSAL'):
  if token not in t:e.append('report '+token)
 c.append('report')
 return e,c
def main():
 e,c=verify();print('FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1: '+('PASS' if not e else 'FAIL'))
 for x in (c if not e else e):print('  - '+x)
 return bool(e)
if __name__=='__main__':sys.exit(main())
