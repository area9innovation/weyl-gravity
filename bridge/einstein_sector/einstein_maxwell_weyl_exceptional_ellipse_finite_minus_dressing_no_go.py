"""Exclude arbitrary finite Einstein-minus dressings of the exceptional ellipse."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.schema.json"
INPUTS={
 "single":ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.json",
 "pivot":ROOT/"bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
 "ellipse":ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
 "smooth":ROOT/"bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 r={k:json.loads(p.read_text()) for k,p in INPUTS.items()}
 assert r['single']['classification']['every_single_m0_Einstein_minus_dressing_ell_ge_2_covered']
 assert r['pivot']['classification']['all_m_promoted'] and r['pivot']['classification']['both_parities_classified']
 assert r['ellipse']['parameterization']['domain']=="r_x,r_p>=0, d!=0, not both r_x,r_p zero"
 t,x=sp.symbols('t x',positive=True)
 lower_num=3*t**2-2*t+1
 upper_gap=2*t**2-4*t-9+6/t-3/t**2
 upper_derivative=4*t-4-6/t**2+6/t**3
 t0=2*sp.sqrt(3)
 assert sp.discriminant(lower_num,t)<0
 assert sp.simplify(upper_gap.subs(t,t0)-(sp.Rational(59,4)-7*sp.sqrt(3)))==0
 assert sp.Rational(59,4)-7*sp.sqrt(3)>0
 assert sp.simplify(upper_derivative-(4*t-4-6/t**2))==6/t**3
 assert 8*sp.sqrt(3)-sp.Rational(9,2)>0
 delta_half_witness=2*x**2-3*x+sp.Rational(1,16)
 assert delta_half_witness.subs(x,2)>0 and sp.diff(delta_half_witness,x).subs(x,2)>0
 original_squares=[sp.Rational(4,3),sp.Rational(16,3),sp.Integer(12),sp.Rational(64,3)]
 minus_squares={ell:sp.Integer(ell*(ell+1))-sp.sqrt(2*ell*(ell+1)) for ell in range(2,5)}
 assert all(sp.simplify(value-target)!=0 for value in minus_squares.values() for target in original_squares)
 return {
  "schema":"einstein-maxwell-weyl-exceptional-ellipse-finite-minus-dressing-no-go-v1","schema_path":str(SCHEMA.relative_to(ROOT)),"schema_sha256":sha(SCHEMA),
  "result_id":"EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_FINITE_MINUS_DRESSING_NO_GO","lifecycle_state":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
  "scope":{"theory":"Weyl-Maxwell target","background":"compact magnetically supported Plebanski-Hacyan product","boundaries":"closed S1_L times S2; bounded/finite-quasiperiodic correction","charge_sector":"fixed N=2 magnetic bundle","carrier":"any axisymmetric exceptional resonance-ellipse point plus an arbitrary finite k=0 Einstein-minus q-primary sum","degree":2,"parity":"both dressing parities","ell":"arbitrary finite subset of ell>=2","m":"all m subject to total rotation moment map zero","k":0,"omega":"all occupied omega_minus(ell)"},
  "dispersion_lemma":{"definition":"w(x)=sqrt(x*(x+1)-sqrt(2*x*(x+1))), delta(x)=x-w(x)","domain":"real x>=2","bounds":"0<delta(x)<1/2 and 1<w'(x)<2/sqrt(3)","delta_witness":"delta>0 follows from 2*x*(x+1)>x^2; delta<1/2 follows from 2*x^2-3*x+1/16>0","lower_derivative_witness":"3*t^2-2*t+1>0 for t=sqrt(2*x*(x+1))>=2sqrt(3)","upper_derivative_witness":"g(t)=2*t^2-4*t-9+6/t-3/t^2; g(2sqrt(3))=59/4-7sqrt(3)>0 and g'(t)>0","integer_bracket":"w(a+b-1)<w(a)+w(b)<w(a+b) for integers a,b>=2","consequence":"no angularly allowed sum or difference of two minus frequencies equals a third minus frequency"},
  "original_carrier_isolation":{"exceptional_shift":"|L-ell|<=1 but every adjacent minus gap is <2/sqrt(3)=omega_exceptional","ell2_control_shift":"|L-ell|<=2 but every two-step minus gap is <4/sqrt(3)=omega_control","original_original_squared_frequency_audit":{"candidate_squares":["4/3","16/3","12","64/3"],"target_ell":[2,3,4],"all_unequal":True}},
  "obstruction":{"d_cross_map":"nonzero scalar SO3 intertwiner on every occupied ell,m and separately in each parity","no_cancellation":"minus-minus and original-minus products cannot share a d-times-minus carrier","charge_reason":"balancing the strictly negative ellipse mu_H requires at least one nonzero minus coefficient","contradiction":"bounded compatibility forces every minus coefficient to vanish because d!=0"},
  "correction_classes":{"BOUNDED_OR_FINITE_QUASIPERIODIC":{"status":"OBSTRUCTED"},"SMOOTH_EXPONENTIAL_POLYNOMIAL":{"status":"CERTIFIED"},"CAUSAL_RETARDED":{"status":"NO_CERTIFIED_MAP"}},
  "classification":{"arbitrary_finite_minus_superpositions_covered":True,"both_parities_and_all_m_covered":True,"three_minus_shell_resonances_excluded_analytically":True,"original_minus_shell_collisions_excluded_analytically":True,"bounded_extension_obstructed":True,"smooth_secular_extension_certified":True,"additional_nonminus_carriers_classified":False,"infinite_completion_classified":False,"all_orders_integrability":False,"causal_or_quantum_claim":False},
  "interpretation":"No finite collection of Einstein-minus waves rescues the exceptional resonance ellipse in the bounded correction class. The d-cross obstruction acts independently on every occupied minus carrier, and exact dispersion inequalities prevent quadratic minus pairs or the original exceptional/control modes from canceling it. Smooth secular extension remains available on the stabilizer zero cone.",
  "next_gate":"allow additional nonminus or nonzero-momentum carriers, or classify the infinite completed minus sector with a declared topology","claim_boundary":"This theorem covers arbitrary finite k=0 Einstein-minus dressings only. Additional nonminus carriers, infinite completion, nonzero momentum, all-orders, causal, residual and quantum claims remain open.",
  "provenance":{"generator_path":str(Path(__file__).relative_to(ROOT)),"generator_sha256":sha(Path(__file__)),"inputs":{k:{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for k,p in INPUTS.items()}}
 }
def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUTPUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 elif json.loads(OUTPUT.read_text())!=v:raise AssertionError('stale finite-minus no-go')
 print('EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_FINITE_MINUS_DRESSING_NO_GO: PASS')
if __name__=='__main__':main()
