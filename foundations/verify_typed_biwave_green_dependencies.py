#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_typed_biwave_green_dependencies import check
RESULT=ROOT/'foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json';SCHEMA=ROOT/'foundations/schema/foundational-typed-biwave-green-dependency-audit-v1.schema.json';REPORT=ROOT/'foundations/reports/typed-biwave-green-foundational-dependencies.md';CLASSICAL=ROOT/'d_quotient_classical/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json';QUANTUM=ROOT/'quantum-weyl/lorentzian/certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT.json'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(*,result=None,classical=None,quantum=None,report=None):
 r=load(RESULT) if result is None else result;c=load(CLASSICAL) if classical is None else classical;q=load(QUANTUM) if quantum is None else quantum;t=REPORT.read_text() if report is None else report;load(SCHEMA);e=[];checks=['artifacts parse']
 if r.get('result_id')!='FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1' or r.get('lifecycle')!='SEPARATED' or r.get('dependency_tags')!=['LOCAL-ALGEBRAIC','LORENTZIAN-CAUSAL']:e.append('identity')
 if r.get('programme_context',{}).get('opportunity_realized')!='OP-GREEN-OPERATOR-FOUNDATIONS':e.append('opportunity')
 layers={x.get('id'):x for x in r.get('dependency_layers',[])}
 expected={'GEOMETRY','FACTOR-GREEN','SOBOLEV-COMPLETION','ENERGY-ESTIMATE','EXACT-RESOLVENT-ALGEBRA','VOLTERRA-CONVERGENCE','UNIQUENESS','CAUSAL-SUPPORT','ADJOINT-DUALITY'}
 if set(layers)!=expected or layers.get('EXACT-RESOLVENT-ALGEBRA',{}).get('status')!='FINITE_EXACT':e.append('layers')
 if any(layers.get(x,{}).get('foundational_strength')!='NOT_CLASSIFIED' for x in ('GEOMETRY','FACTOR-GREEN','ENERGY-ESTIMATE','UNIQUENESS','CAUSAL-SUPPORT','ADJOINT-DUALITY')):e.append('analytic overclaim')
 checks.append('nine-layer dependency cut')
 ce,s=check(r);e.extend('checker '+x for x in ce)
 if s.get('digest')!=r.get('independent_checker',{}).get('expected_digest') or not s.get('noncommuting'):e.append('checker')
 checks.append('exact independent algebra')
 if c.get('claim_status')!='CERTIFIED_CONDITIONAL_ANALYTIC_THEOREM' or not c.get('theorem',{}).get('biwave_green_hyperbolic'):e.append('classical source')
 if q.get('result_id')!='TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORT' or not q.get('claim_flags',{}).get('TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_IMPORTED'):e.append('quantum import')
 for x in r.get('provenance',{}).get('inputs',[]):
  p=ROOT/x.get('path','')
  if not p.is_file() or sha(p)!=x.get('sha256'):e.append('hash '+x.get('path',''))
 checks.append('source claims and hashes')
 f=r.get('claim_flags',{})
 for k in ('dependency_cut_complete_for_source_theorem','finite_resolvent_algebra_replayed','conditional_lorentzian_theorem_imported'):
  if f.get(k) is not True:e.append('positive '+k)
 for k in ('weakest_base_proved','choice_free_pde_theorem_proved','full_bv_propagator_constructed','hadamard_state_constructed','renormalized_products_constructed','lorentzian_qme_proved'):
  if f.get(k) is not False:e.append('boundary '+k)
 checks.append('fail-closed flags')
 for token in ('FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1','LOCAL-ALGEBRAIC','LORENTZIAN-CAUSAL','normally-hyperbolic','Sobolev','energy estimate','factorial Volterra','Choice strength','finite checker','full off-shell metric BV propagator'):
  if token not in t:e.append('report '+token)
 checks.append('report')
 return e,checks
def main():
 e,c=verify();print('FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1: '+('PASS' if not e else 'FAIL'))
 for x in (c if not e else e):print('  - '+x)
 return bool(e)
if __name__=='__main__':sys.exit(main())
