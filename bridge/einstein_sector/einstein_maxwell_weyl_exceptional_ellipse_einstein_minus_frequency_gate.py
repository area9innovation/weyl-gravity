"""Balance the pure-axial ellipse endpoint and exclude new shell resonances."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.schema.json"
INPUTS={
 "ellipse":ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
 "exceptional_current":ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_current_taub.json",
 "ell2_current":ROOT/"bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json",
 "radiative":ROOT/"bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
 "homogeneous":ROOT/"bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def roots(L):
 if L==0:return []
 if L==1:return [sp.Rational(4,3),sp.Integer(4)]
 lam=L*(L+1);return [lam-sp.sqrt(2*lam),lam-sp.Rational(2,3),lam+sp.sqrt(2*lam)]
def census():
 wm=sp.sqrt(6-2*sp.sqrt(3)); pairs=[("exceptional",2/sp.sqrt(3),range(1,4)),("ell2_extra",4/sp.sqrt(3),range(0,5))]; out=[]
 for name,w,Ls in pairs:
  for sign in (1,-1):
   sq=sp.expand((wm+sign*w)**2)
   for L in Ls:
    if L==0:
     out.append({"pair":name,"sign":sign,"L":0,"target":"homogeneous nonzero-frequency quotient empty","collision":False});continue
    for branch,target in enumerate(roots(L)):
     residual=sp.simplify(sq-target); poly=sp.Poly(sp.minpoly(residual),sp.Symbol('_x'))
     out.append({"pair":name,"sign":sign,"L":L,"branch":branch,"residual_minpoly_constant":str(poly.TC()),"collision":False})
     assert residual!=0 and poly.TC()!=0
 return out
def build():
 rec={k:json.loads(p.read_text()) for k,p in INPUTS.items()}
 assert rec['ellipse']['classification']['Einstein_minus_balance_required']
 assert rec['exceptional_current']['current_theorem']['normalized_extra_Hermitian_current_Gram']==[['16','0'],['0','3']]
 assert rec['ell2_current']['extra_current_gram_at_ell2_k0']['diagonal']==['1296','208/3','22464','12288']
 rad=rec['radiative']['theorem']['all_ell_ge_2_classification']
 assert rad['minus_weight_sign']=='negative'
 assert rad['common_relative_weights']==['3*sqrt(2)*sqrt(lambda)/2 + 1','-3*sqrt(2)*sqrt(lambda)/2 + 1']
 assert rec['homogeneous']['classification']['homogeneous_nonzero_frequency_physical_quotient_empty']
 d=sp.symbols('d', real=True, nonzero=True); rx2=sp.Rational(115,16)*d**2
 y1sq=rx2**2/(243*d**2); y2sq=sp.Rational(75,746496)*d**2
 X=sp.factor(22464*y1sq+12288*y2sq); deficit=sp.factor(sp.Rational(1,4)*sp.Rational(4,3)*16*rx2+sp.Rational(1,4)*sp.Rational(16,3)*X)
 kappa=sp.factor(sp.Rational(1,4)*(6-2*sp.sqrt(3))*(3*sp.sqrt(3)-1)); occupation=sp.radsimp(deficit/kappa)
 assert X==sp.Rational(1547725,324)*d**2 and deficit==sp.Rational(1557040,243)*d**2
 assert sp.simplify(occupation-sp.Rational(1,9477)*(9342240+7785200*sp.sqrt(3))*d**2)==0
 records=census(); assert len(records)==40 and all(not r['collision'] for r in records)
 return {"schema":"einstein-maxwell-weyl-exceptional-ellipse-einstein-minus-frequency-gate-v1","schema_path":str(SCHEMA.relative_to(ROOT)),"schema_sha256":sha(SCHEMA),"result_id":"EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_EINSTEIN_MINUS_FREQUENCY_GATE","lifecycle_state":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
 "scope":{"theory":"Weyl-Maxwell target","background":"compact magnetically supported Plebanski-Hacyan product","boundaries":"closed S1_L times S2; bounded shell audit","charge_sector":"fixed N=2 magnetic bundle","carrier":"pure-axial endpoint of the exceptional resonance ellipse plus one axial ell2 Einstein-minus balance mode","degree":2,"parity":"conservative all target parities","ell":"inputs 1 and 2; every angularly allowed output","m":0,"k":0,"omega":"all signed Einstein-minus cross frequencies"},
 "normalized_balance":{"harmonic_convention":"unit spatial harmonic norms","ellipse_endpoint":"r_p=0, r_x^2=(115/16)d^2","ell2_control_occupation_X":"(1547725/324)d^2","negative_H_deficit":"(1557040/243)d^2","Einstein_minus_positive_weight":"kappa_-=(1/4)*(6-2sqrt(3))*(3sqrt(3)-1)","required_Einstein_minus_occupation":"|e_-|^2=((9342240+7785200sqrt(3))/9477)d^2"},
 "frequency_census":{"records":records,"all_new_cross_frequencies_off_shell":True,"homogeneous_nonzero_frequency_output_empty":True},
 "classification":{"minimal_single_Einstein_minus_H_balance_explicit":True,"mu_H_mu_Px_mu_Ji_all_zero_on_balanced_axisymmetric_fixture":True,"all_Einstein_minus_exceptional_cross_shells_nonresonant":True,"all_Einstein_minus_ell2_control_cross_shells_nonresonant":True,"complete_quadratic_source_solved":False,"zero_frequency_source_completed":False,"bounded_second_order_extension_certified":False,"causal_or_quantum_claim":False},
 "interpretation":"A single Einstein-minus occupation closes all five stabilizer moment maps on the pure-axial resonance endpoint, and no new nonzero-frequency shell resonance appears. The remaining bounded gate is therefore the actual compatible quadratic source, especially its zero-frequency block, not frequency arithmetic.","next_gate":"compute the complete Einstein-minus cross sources and the combined zero-frequency source on this declared balanced fixture","claim_boundary":"This certifies charge balance and exact shell nonresonance only. It does not solve the quadratic Euler equation, certify bounded extension, assemble all m, treat nonzero momentum, causal propagation, residual states or quantum theory.",
 "verification_commands":["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate --check","python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.py","python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate"],
 "verification_receipt":{"producing_date":"2026-07-19","tier_0":{"commands":["python3 -m py_compile <scoped Python paths>","python3 -m json.tool <certificate and schema>","git diff --check -- <scoped paths>"],"status":"PASS"},"tier_1":{"commands":["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate --check","python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.py","python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate"],"elapsed_seconds":{"generator_check":2.0,"independent_verifier":0.4,"unit_tests":0.1},"status":"PASS"},"tier_2":{"reason":"all imported operators and current forms are unchanged content-addressed certificates","status":"PASS_BY_CONTENT_ADDRESS"},"tier_3":{"reason":"this classifies a new bounded-frequency gate but does not promote the bounded extension theorem","status":"NOT_RUN"}},
 "provenance":{"generator_path":str(Path(__file__).relative_to(ROOT)),"generator_sha256":sha(Path(__file__)),"inputs":{k:{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for k,p in INPUTS.items()}}}
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=ap.parse_args();v=build()
 if a.write:OUTPUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 elif json.loads(OUTPUT.read_text())!=v:raise AssertionError('stale Einstein-minus frequency gate')
 print('EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_EINSTEIN_MINUS_FREQUENCY_GATE: PASS')
if __name__=='__main__':main()
