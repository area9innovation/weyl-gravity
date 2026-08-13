#!/usr/bin/env python3
import hashlib,json,os
import sympy as sp
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT_REL="reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1.json";INPUTS=["planning/work-items/reverse-physics-bateman-fully-rearranged-q10-object-ledger.json","planning/events/reverse-physics-bateman-fully-rearranged-q10-object-ledger-DONE-8f4f6cf1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json"]
def load(p):
 try:
  with open(os.path.join(ROOT,p),encoding="utf-8") as f:return json.load(f)
 except:return {}
def sha(p):
 h=hashlib.sha256()
 try:
  with open(os.path.join(ROOT,p),"rb") as f:
   for b in iter(lambda:f.read(65536),b""):h.update(b)
 except:return ""
 return h.hexdigest()
def verify(c):
 q={};q["identity"]=c.get("certificate")=="REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_OBJECT_LEDGER_V1";q["schema"]=c.get("schema")=="reverse_physics/schema/reverse-physics-bt-fully-rearranged-q10-object-ledger-v1.schema.json";q["version"]=c.get("schema_version")==1;q["lifecycle"]=c.get("lifecycle_state")=="CLASSIFIED";q["tags"]=c.get("dependency_tags")==["LOCAL-ALGEBRAIC","REDUCED-MODE"]
 p=c.get("provenance",{});ins=p.get("inputs",[]);q["source"]=p.get("source_commit")=="8f4f6cf116fce8efe8f23942ebb9efd6c8cfccb6";q["paths"]=[x.get("path") for x in ins]==INPUTS;q["hashes"]=len(ins)==6 and all(x.get("sha256")==sha(y) for x,y in zip(ins,INPUTS));q["producer"]=p.get("generated_by")=="reverse_physics/bt_fully_rearranged_q10_object_ledger.py";q["verifier"]=p.get("independent_verifier")=="reverse_physics/verify_bt_fully_rearranged_q10_object_ledger.py";pred=list(map(load,INPUTS[2:]));q["predecessors"]=all(x.get("checks",{}).get("ok") for x in pred)
 l=sp.symbols('l');a4,a5,a6=sp.symbols('a4 a5 a6',real=True);poly=sp.expand((l**4*a4+l**5*a5+l**6*a6)**2);q["q10"]=sp.Poly(poly,l).coeff_monomial(l**10)==a5**2+2*a4*a6 and c.get("exact_probability_decomposition",{}).get("q10")=="<y5,y5>+2*Re<y4,y6>"
 rows=c.get("connected_order6_graphs",{}).get("rows",[]);expected={(0,3,3,1),(2,2,4,1),(4,1,5,1),(6,0,6,1)};q["rows"]={(r.get('V3'),r.get('V4'),r.get('I'),r.get('L')) for r in rows}==expected;q["identity_rows"]=all(r.get('d_lambda')==r.get('E')+2*r.get('L')-2 for r in rows);q["graph_status"]=c.get("connected_order6_graphs",{}).get("status")=="FOUR_ONE_LOOP_VERTEX_COUNT_CLASSES_EXHAUSTIVE";s=c.get("support_disposition",{});q["support"]=s.get("status")=="EXTERNAL_DISCONNECTED_ZERO_VACUUM_NORMALIZATION_OPEN" and "not decided" in s.get("vacuum_components","")
 blocks=c.get("required_blocks",[]);q["blocks"]=len(blocks)==5 and sum(x.get("status")=="MISSING" for x in blocks)==4 and sum(x.get("status")=="CLASSIFIED_NOT_COMPUTED" for x in blocks)==1;q["kappa_missing"]=any(x.get("object")=="total ghost-kappa audit" and x.get("status")=="MISSING" for x in blocks)
 d=c.get("disposition",{});q["q8q9q10"]=(d.get("q8"),d.get("q9"),d.get("q10"))==("COMMON_BORN_COEFFICIENT_COMPUTED","EXACTLY_ZERO","CLASSIFIED_NOT_COMPUTED");q["not_promoted"]=d.get("common_Born_q10")=="NOT_ESTABLISHED" and d.get("general_Eq19")=="NOT_PROVED" and d.get("Lorentzian_causal_claim")=="NOT_ESTABLISHED";q["boundaries"]=len(c.get("does_not_establish",[]))==11;q["next"]=all(x in c.get("next_gate","") for x in ("V4^3","fewest vertices","counterterm"));q["report"]=c.get("report")=="reverse_physics/reports/bt-fully-rearranged-q10-object-ledger.md";return q
def main():
 q=verify(load(CERT_REL));bad=[k for k,v in q.items() if not v];print(f"{len(q)-len(bad)}/{len(q)} checks passed");print("RESULT: PASS" if not bad else "failures: "+", ".join(bad));return bool(bad)
if __name__=="__main__":raise SystemExit(main())
