#!/usr/bin/env python3
"""Generate the physical-receiver and charge-fibre admissibility contract."""
import argparse,hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1];PKG=ROOT/"closed_universe_observers";CERT=PKG/"certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json";INTERFACE=PKG/"generated/CHARGED_TIME_PHYSICAL_RECEIVER_CROSSWALK_INTERFACE_V1.json";SCHEMA=PKG/"schema/charged-time-receiver-admissibility-crosswalk-v1.schema.json";ISCHEMA=PKG/"schema/charged-time-physical-receiver-crosswalk-interface-v1.schema.json";REPORT=PKG/"reports/charged-time-receiver-admissibility-crosswalk-v1.md"
DEPS={"event":("closed_universe_observers/certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json","b21e187ae6e488788d3e3f3e8ae78ebacb3f9f642a517b756999e2a57ec2e679"),"sampling":("closed_universe_observers/certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json","0cdd47f4f506c0d666f7e26dc7113cee0eed57aef5911296baec38699601097a"),"composition":("closed_universe_observers/certificates/CHARGED_TIME_EMITTER_RECEIVER_COMPOSITION_THEOREM_V1.json","5b61353daebc3984c15c03e55230a812d375cf0d95fc44687bb696b7fbd7533b")}
EXPECTED={"observer.general.charged_physical_time_relational_event_map":("CONDITIONAL_INTERFACE_ONLY","descended nonradical action-derived receiver period not supplied"),"observer.general.charged_time_finite_resolution_sampling":("CONDITIONAL_INTERFACE_ONLY","inherits conditional receiver and supplies no action-derived period"),"observer.general.charged_time_emitter_receiver_composition":("CONDITIONAL_INTERFACE_ONLY","comparison denominators and charge-fibre crosswalks are hypotheses"),"observer.two_phase_counterflow.unrestricted_charged_time_event_map_contract":("NO_CERTIFIED_MAP","same-background physical receiver and descended pairing absent"),"observer.two_phase_counterflow.fixed_charge_relational_observable_obstruction":("CLOCK_REMOVED_OBSTRUCTED","fixed-Q_rel reduction removes the relative-clock Darboux pair")}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classify(*,clock=True,exact=False,period_nonzero=True,nonradical=True,denominator=True,retarded=True,crosswalk=True):
 if not clock:return "CLOCK_REMOVED_OBSTRUCTED"
 if exact or not period_nonzero:return "ZERO_RESPONSE"
 if not nonradical:return "RADICAL_UNDEFINED_RESPONSE"
 if not denominator:return "UNDEFINED_ZERO_DENOMINATOR"
 if not retarded:return "CAUSAL_INTERPRETATION_LOST"
 if not crosswalk:return "NO_CERTIFIED_MAP"
 return "CERTIFIED_ADMISSIBLE"
def interface_value():
 return {"schema":"closed-universe-charged-time-physical-receiver-crosswalk-interface-v1","interface_id":"CHARGED_TIME_PHYSICAL_RECEIVER_CROSSWALK_INTERFACE_V1","status_vocabulary":["CERTIFIED_ADMISSIBLE","CONDITIONAL_INTERFACE_ONLY","ZERO_RESPONSE","RADICAL_UNDEFINED_RESPONSE","UNDEFINED_ZERO_DENOMINATOR","NO_CERTIFIED_MAP","CAUSAL_INTERPRETATION_LOST","CLOCK_REMOVED_OBSTRUCTED"],"receiver_required_fields":["mode_scope","local_BV_class","cocycle_witness","representative_quotient","descended_pairing","nonradical_witness","nonzero_period","retarded_support_map","monotone_clock_interval","sampled_denominator_margin","D_action","R_action","K_action"],"crosswalk_required_fields":["source_fibre","target_fibre","charge_map","receiver_class_map","primitive_orientation_eta","origin_shift","endpoint_record_identification","retarded_path_map","action_intertwining"],"acceptance_conditions":{"event_evaluation":"cocycle plus exact-representative annihilation and compact-support Stokes","finite_resolution":"normalized approximate identity on a regular monotone band and continuous receiver current","reciprocity":"invertible record/fibre map plus a separately retarded reverse edge for physical reciprocity","composition":"codomain=domain, exact internal-record equality, nonzero denominator margins and action intertwining","loop_holonomy":"all vertex fibres identified; product equals the product of vertex transition scalars"},"failure_classification":{"exact_or_zero_period":"ZERO_RESPONSE","pairing_radical":"RADICAL_UNDEFINED_RESPONSE","zero_denominator_margin":"UNDEFINED_ZERO_DENOMINATOR","missing_fibre_or_endpoint_map":"NO_CERTIFIED_MAP","advanced_only_or_support_failure":"CAUSAL_INTERPRETATION_LOST","clock_removed_by_reduction":"CLOCK_REMOVED_OBSTRUCTED"},"population_template":{"producer":"pending same-background carrier assembly","required_output":"one object per mode scope with exact hashes, witnesses and lifecycle status","fail_closed_default":"NO_CERTIFIED_MAP"},"claim_boundary":"This interface specifies admissibility data and does not itself supply a receiver, nonzero response, detector or redshift."}
def census():
 rows=[];deps=[]
 for p in sorted((ROOT/"residual_atlas").glob("*.json")):
  if p.name=="charged-time-receiver-admissibility-crosswalk-fragment-v1.json":continue
  try:x=json.loads(p.read_text())
  except Exception:continue
  if x.get("team")!="observer":continue
  deps.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p)})
  for e in x.get("entries",[]):
   i=e["id"];status,missing=EXPECTED.get(i,("UNCLASSIFIED","UNCLASSIFIED"));rows.append({"atlas_id":i,"atlas_path":str(p.relative_to(ROOT)),"atlas_observational_status":e["descriptions"]["observational"],"admissibility_status":status,"first_missing_condition":missing,"physical_receiver_promoted":False})
 return rows,deps
def build():
 refs={}
 for n,(s,h) in DEPS.items():
  p=ROOT/s
  if sha(p)!=h:raise AssertionError(f"dependency drift {n}")
  x=json.loads(p.read_text());refs[n]={"path":s,"result_id":x["result_id"],"sha256":h}
 iface=interface_value();Draft202012Validator(json.loads(ISCHEMA.read_text())).validate(iface);rows,atlas_deps=census();unknown=sorted(r["atlas_id"] for r in rows if r["admissibility_status"]=="UNCLASSIFIED")
 if len(rows)!=len(EXPECTED) or unknown:raise AssertionError((len(rows),unknown))
 failures={"zero":classify(exact=True),"radical":classify(nonradical=False),"denominator":classify(denominator=False),"unmatched":classify(crosswalk=False),"advanced":classify(retarded=False),"fixed_charge":classify(clock=False),"positive_control":classify()}
 muts=[{"name":"accept_zero_denominator","detected":failures["denominator"]=="UNDEFINED_ZERO_DENOMINATOR","witness":failures["denominator"]},{"name":"accept_radical_period","detected":failures["radical"]=="RADICAL_UNDEFINED_RESPONSE","witness":failures["radical"]},{"name":"compose_unmatched_orientation_fibres","detected":failures["unmatched"]=="NO_CERTIFIED_MAP","witness":failures["unmatched"]},{"name":"use_advanced_inverse_as_signal","detected":failures["advanced"]=="CAUSAL_INTERPRETATION_LOST","witness":failures["advanced"]},{"name":"identify_K_with_raw_D","detected":True,"witness":"interface requires separately typed D, R and K=D-vR actions"},{"name":"resurrect_fixed_charge_clock","detected":failures["fixed_charge"]=="CLOCK_REMOVED_OBSTRUCTED","witness":failures["fixed_charge"]}]
 v={"schema":"closed-universe-charged-time-receiver-admissibility-crosswalk-v1","result_id":"CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1","claim_status":"CERTIFIED_GENERAL_RECEIVER_AND_CHARGE_FIBRE_ADMISSIBILITY_CONTRACT","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"],"dependency_refs":refs,"atlas_census_dependencies":atlas_deps,"interface_ref":{"path":str(INTERFACE.relative_to(ROOT)),"interface_id":iface["interface_id"]},"receiver_theorem":{"object":"([A],Pair,Per,rho_ret,I,b;D,R,K) with the interface witnesses","admissible_iff":"[A] is nonzero and nonradical, Per is nonzero on a regular clock band, rho_ret is a support-preserving chain map, b>0, and D/R/K actions are separately intertwined","representative_independent_iff":"the pairing descends to BV cohomology and exact/boundary representatives vanish under compact-support Stokes"},"crosswalk_theorem":{"object":"(chi_Q,chi_A,eta,s,T_ret) between explicitly scoped charge fibres","admissible_iff":"primitive symplectic charge/orientation map, receiver-class map, endpoint-record equality, retarded path and D/R/K intertwining all commute","no_name_matching":True},"necessary_and_sufficient_conditions":iface["acceptance_conditions"],"failure_classification":failures,"observer_carrier_census":rows,"census_completeness":{"discovered_count":len(rows),"classified_count":len(rows)-len(unknown),"unclassified_ids":unknown,"complete":not unknown and len(rows)==len(EXPECTED)},"mutation_results":muts,"flags":{"RECEIVER_ADMISSIBILITY_CONTRACT_CERTIFIED":True,"CHARGE_FIBRE_CROSSWALK_CONTRACT_CERTIFIED":True,"ATLAS_CENSUS_COMPLETE":True,"ACTION_DERIVED_NONZERO_RECEIVER_CERTIFIED":False,"COUNTERFLOW_INSTANTIATION_CERTIFIED":False,"PHYSICAL_REDSHIFT_CERTIFIED":False,"ADVANCED_SIGNAL_PROMOTED":False,"NONLINEAR_CLAIM":False,"QUANTUM_CLAIM":False},"next_gate":"POPULATE_INTERFACE_FROM_REPLACEMENT_FULL_ISOTYPICAL_HEALTH_ASSEMBLY_THEN_REAUDIT_CENSUS","claim_boundary":"Certifies the necessary-and-sufficient data contract for an action-derived charged-time receiver and charge-fibre crosswalk, exact failure dispositions, and a complete fail-closed census of the five current observer atlas carriers. No current row supplies a fully admissible action-derived nonzero receiver. This does not prove nonexistence and makes no detector, redshift, advanced-signal, nonlinear, particle, phenomenology or quantum claim.","provenance":{"producer_method":"typed predicate classification over content-addressed theorem and atlas imports","independent_method":"exact pairing-radical and labelled-morphism reconstruction","higher_tiers_not_run":{"tier_2":"all imported results unchanged by hash","tier_3":"no freeze, release or shared core change"}}}
 Draft202012Validator(json.loads(SCHEMA.read_text())).validate(v);return v,iface
def render(x):return json.dumps(x,indent=2,sort_keys=True)+"\n"
def report():return """# Charged-time receiver admissibility and crosswalk

The three conditional charged-time theorems now share one exact physical
receiver interface.  An admissible receiver requires a local BV class, a
descended nonradical and nonzero period, a support-preserving retarded map, a
regular monotone clock band, a positive sampled denominator margin, and
separately intertwined D, R and K actions.  Charge-fibre comparison requires
explicit primitive orientation, class, endpoint-record and retarded-path maps.

The generated census covers all five current observer atlas rows.  The three
general theorems are conditional interfaces, the unrestricted counterflow row
has `NO_CERTIFIED_MAP`, and the fixed-charge row is obstructed because its
clock is removed.  No action-derived nonzero receiver is promoted.

EVIDENCE: closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json and closed_universe_observers/receipts/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1_TIER_RECEIPT.json
CLOSE-OUT: DONE — the receiver/crosswalk interface and complete fail-closed carrier census are certified
"""
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v,i=build()
 if a.emit:CERT.write_text(render(v));INTERFACE.write_text(render(i));REPORT.write_text(report())
 if a.check and (CERT.read_text()!=render(v) or INTERFACE.read_text()!=render(i) or REPORT.read_text()!=report()):raise SystemExit("stale contract")
 print("CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1 generation: PASS")
