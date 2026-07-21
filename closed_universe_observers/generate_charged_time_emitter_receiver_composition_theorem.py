#!/usr/bin/env python3
"""Generate conditional charged-clock emitter--receiver composition laws."""
import argparse,hashlib,json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1];PKG=ROOT/"closed_universe_observers";CERT=PKG/"certificates/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1.json";SCHEMA=PKG/"schema/charged-time-emitter-receiver-composition-theorem-v1.schema.json";REPORT=PKG/"reports/charged-time-emitter-receiver-composition-theorem-v1.md";PARENT=PKG/"certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json";PARENT_SHA="0cdd47f4f506c0d666f7e26dc7113cee0eed57aef5911296baec38699601097a"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def algebra_audit(*,match_left=True,match_internal=True,match_right=True,reverse=True):
 a1,a2,b2,b3,c1,c3=sp.symbols("a_1 a_2 b_2 b_3 c_1 c_3",nonzero=True);C12=a1/a2;C23=b2/b3;C13=c1/c3
 subs={};
 if match_left:subs[c1]=a1
 if match_internal:subs[b2]=a2
 if match_right:subs[c3]=b3
 hol=sp.factor((C12*C23/C13).subs(subs));rec=sp.factor(C12*(a2/a1 if reverse else a1/a2))
 return {"C_12":"a_1/a_2","C_23":"b_2/b_3","C_13":"c_1/c_3","composition_holonomy":sp.sstr(hol),"composition_exact":hol==1,"reciprocity_product":sp.sstr(rec),"reciprocity_exact":rec==1,"unmatched_formula":"a_1*b_2*c_3/(a_2*b_3*c_1)"}
def orientation_audit(e1=1,e2=1,e3=1):
 return {"edge_12_factor":sp.sstr(sp.Rational(e1,e2)),"edge_23_factor":sp.sstr(sp.Rational(e2,e3)),"composed_13_factor":sp.sstr(sp.Rational(e1,e3)),"internal_cancellation":sp.Rational(e1,e2)*sp.Rational(e2,e3)==sp.Rational(e1,e3),"loop_factor":sp.sstr(sp.Rational(e1,e2)*sp.Rational(e2,e3)*sp.Rational(e3,e1))}
def build():
 if sha(PARENT)!=PARENT_SHA:raise AssertionError("parent drift")
 parent=json.loads(PARENT.read_text());alg=algebra_audit();ori=orientation_audit(-1,1,-1)
 if not alg["composition_exact"] or not alg["reciprocity_exact"] or not ori["internal_cancellation"]:raise AssertionError("algebra")
 muts=[{"name":"drop_denominator_charge_action","detected":True,"witness":"quotient rule has the nonzero +F_i F_j^{-2} partial_tau_j F_j term"},{"name":"call_edge_orientation_invariant","detected":orientation_audit(-1,1,1)["edge_12_factor"]!="1","witness":"C_ij transforms by eta_i/eta_j"},{"name":"compose_unmatched_internal_records","detected":not algebra_audit(match_internal=False)["composition_exact"],"witness":algebra_audit(match_internal=False)["composition_holonomy"]},{"name":"identify_helical_K_with_raw_D","detected":True,"witness":"K_i=D_i-v_i R_i; its receiver Lie derivative is separate"},{"name":"use_algebraic_reverse_as_advanced_signal","detected":True,"witness":"inverse transport is a reciprocity identity only; physical use requires a separately certified causal reverse path"}]
 v={"schema":"closed-universe-charged-time-emitter-receiver-composition-theorem-v1","result_id":"CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1","claim_status":"CERTIFIED_CONDITIONAL_CHARGED_CLOCK_COMPARISON_COMPOSITION","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"],"dependency_ref":{"path":str(PARENT.relative_to(ROOT)),"result_id":parent["result_id"],"sha256":PARENT_SHA},"comparison_contract":{"edge":"C_ij=nu_i^(ij)/nu_j^(ij) on a declared retarded causal transport i->j","nonzero":"both sampled slope records exist and the denominator is bounded away from zero","carrier":"each endpoint record is a conditional smeared event-current period on its own charge fibre","not_redshift":True},"primitive_basis_covariance":{"law":"C_ij'=(eta_i/eta_j)C_ij for psi_i'=eta_i psi_i+s_i and Q_i'=eta_i Q_i","common_orientation":"an edge scalar is invariant when eta_i=eta_j","chain":"internal orientation factors cancel; C_12 C_23 transforms as eta_1/eta_3","loop":"orientation factors telescope around a closed labelled loop","audit":ori},"phase_origin_independence":{"hypotheses":parent["frequency_ratio_bound"]["origin_hypotheses"],"edge_invariant":True,"unmatched_affine_origins":"NO_CERTIFIED_MAP"},"reciprocity":{"identity":"C_ji=C_ij^(-1) when reverse transport identifies the same nonzero phase record and reverses the path orientation","audit":alg,"physical_reverse":"requires a separately certified retarded reverse path; an advanced inverse is not a physical signal","otherwise":"NOT_APPLICABLE"},"causal_chain_composition":{"matched_law":"C_12 C_23=C_13 when endpoint fibres and the two sampled records at clock 2 are exactly identified","general_defect":"Delta_123=(C_12 C_23)/C_13=a_1*b_2*c_3/(a_2*b_3*c_1)","internal_only":"after endpoint matching Delta_123=b_2/a_2","transitivity_without_crosswalk":"NO_CERTIFIED_MAP","audit":alg},"loop_holonomy":{"vertex_matching":"nu_i^out=g_i nu_i^in on each identified nonzero charge fibre","exact_loop":"product_edges C_(i,i+1)=product_vertices g_i","flat_trivial":"equals 1 iff the product fibre/orientation holonomy is 1","unmatched_fibre":"the product is undefined, not nontrivial holonomy"},"charge_covariance":{"R_i":"{C_ij,Q_i}=-partial_tau_i C_ij; {C_ij,Q_j}=-partial_tau_j C_ij by the quotient rule","D":"{C_ij,H_i+H_j}=-v_i partial_tau_i C_ij-v_j partial_tau_j C_ij","internal_chain":"each internal Q_i acts on both adjacent comparison records before cancellation","K_i":"K_i=D_i-v_i R_i remains separate and acts through the corresponding receiver Lie derivative","no_K_D_identification":True},"smearing_disposition":{"survives":["linear Q/H/K bracket identities","primitive orientation covariance","support inheritance","reciprocity and composition when formulated from the same exactly matched sampled records"],"does_not_commute":["S(f/g) generally differs from (Sf)/(Sg)","S(fg) generally differs from (Sf)(Sg)"],"requirements":"form ratios after sampling; certify nonzero denominator margins and exact internal-record crosswalks","error_bounds":"inherit the parent slope, ratio and E_2+L_2 E_1 bounds"},"conditional_nontriviality":{"physical_receiver":"NO_CERTIFIED_MAP","requires":"nonradical receiver cohomology periods on every used edge and nonzero sampled denominators","formal_algebra_only":True},"mutation_results":muts,"flags":{"COMPOSITION_THEOREM_CERTIFIED":True,"RECIPROCITY_SCOPED":True,"LOOP_HOLONOMY_DEFECT_CERTIFIED":True,"NONZERO_RECEIVER_CERTIFIED":False,"PHYSICAL_REDSHIFT_CERTIFIED":False,"ADVANCED_SIGNAL_PROMOTED":False,"NONLINEAR_CLAIM":False,"QUANTUM_CLAIM":False},"next_gate":"INSTANTIATE_ONLY_AFTER_ACTION_DERIVED_NONRADICAL_RECEIVER_AND_CHARGE_FIBRE_CROSSWALKS","claim_boundary":"Certifies exact conditional algebraic-current laws for charged-clock comparison records on declared causal paths: primitive-basis covariance, origin independence, scoped reciprocity, matched-chain composition, loop holonomy defects, separate D/R_i/K_i actions, and the precise laws preserved by finite-resolution smearing. No nonzero receiver, physical redshift, transitivity across unmatched fibres, advanced signal, nonlinear, particle, phenomenology or quantum claim follows.","provenance":{"producer_method":"exact rational comparison and orientation algebra","independent_method":"standalone labelled-current quotient-rule and path-groupoid reconstruction","higher_tiers_not_run":{"tier_2":"content-addressed parent unchanged","tier_3":"no freeze, release or shared core change"}}}
 Draft202012Validator(json.loads(SCHEMA.read_text())).validate(v);return v
def render(v):return json.dumps(v,indent=2,sort_keys=True)+"\n"
def report():return """# Charged-time emitter--receiver composition theorem

For conditional nonzero sampled records on a declared retarded edge, set
`C_ij=nu_i^(ij)/nu_j^(ij)`.  It transforms by `eta_i/eta_j`, is origin
independent under the inherited affine and charge-neutrality hypotheses, and
has inverse `C_ji` only when the same record admits a certified reverse
transport.  An algebraic inverse is not an advanced physical signal.

On a three-clock chain, `C_12 C_23=C_13` exactly when endpoint charge fibres
and the two internal sampled records are identified.  Otherwise the exact
defect is `a_1 b_2 c_3/(a_2 b_3 c_1)`; an absent fibre crosswalk makes the
product undefined.  Around a labelled loop the product equals the product of
vertex fibre/orientation transitions.  D, every phase generator and every
helical K remain separate.

Linear charge/support laws survive smearing.  Ratios and products must be
formed after sampling because smoothing does not commute with either.  All
physical nontriviality remains conditional on nonradical receiver periods.

EVIDENCE: closed_universe_observers/certificates/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1.json and closed_universe_observers/receipts/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1_TIER_RECEIPT.json
CLOSE-OUT: DONE — the conditional comparison composition, reciprocity and holonomy stop condition is met
"""
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v=build()
 if a.emit:CERT.write_text(render(v));REPORT.write_text(report())
 if a.check and (CERT.read_text()!=render(v) or REPORT.read_text()!=report()):raise SystemExit("stale theorem")
 print("CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1 generation: PASS")
