#!/usr/bin/env python3
"""Independently verify fully rearranged BT q9 parity selection."""
from __future__ import annotations
import hashlib,json,os
from fractions import Fraction
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT_REL="reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1.json";SOURCE="acb87dd1ff3986be900ebdbf1c0f13086c654964"
INPUTS=["planning/work-items/reverse-physics-bateman-fully-rearranged-lambda9-parity-selection.json","planning/events/reverse-physics-bateman-fully-rearranged-lambda9-parity-selection-DONE-acb87dd1.json","reverse_physics/data/bateman_turok_hamiltonian_source_v1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json"]
def load(p):
 try:
  with open(os.path.join(ROOT,p),encoding="utf-8") as f:return json.load(f)
 except (OSError,ValueError):return {}
def sha(p):
 h=hashlib.sha256()
 try:
  with open(os.path.join(ROOT,p),"rb") as f:
   for b in iter(lambda:f.read(65536),b""):h.update(b)
 except OSError:return ""
 return h.hexdigest()
def mat(v):
 try:return [[Fraction(x) for x in r] for r in v]
 except:return []
def mv(a,v):return [sum((a[i][j]*v[j] for j in range(len(v))),Fraction()) for i in range(len(a))]
def dot(v,a,w):return sum((v[i]*a[i][j]*w[j] for i in range(len(v)) for j in range(len(w))),Fraction())
def verify(c):
 q={};q["identity"]=c.get("certificate")=="REVERSE_PHYSICS_BT_FULLY_REARRANGED_LAMBDA9_PARITY_SELECTION_V1";q["schema"]=c.get("schema")=="reverse_physics/schema/reverse-physics-bt-fully-rearranged-lambda9-parity-selection-v1.schema.json";q["version"]=c.get("schema_version")==1;q["tags"]=c.get("dependency_tags")==["LOCAL-ALGEBRAIC","REDUCED-MODE"];q["lifecycle"]=c.get("lifecycle_state")=="COEFFICIENT_COMPUTED"
 p=c.get("provenance",{});ins=p.get("inputs",[]);q["source"]=p.get("source_commit")==SOURCE;q["paths"]=[x.get("path") for x in ins]==INPUTS;q["hashes"]=len(ins)==6 and all(x.get("sha256")==sha(y) for x,y in zip(ins,INPUTS));q["producer"]=p.get("generated_by")=="reverse_physics/bt_fully_rearranged_lambda9_parity_selection.py";q["verifier"]=p.get("independent_verifier")=="reverse_physics/verify_bt_fully_rearranged_lambda9_parity_selection.py"
 physical,parity,source=map(load,INPUTS[3:6]);q["predecessors"]=all(x.get("checks",{}).get("ok") for x in (physical,parity,source));q["covariance"]=parity.get("exact_covariance",{}).get("probability")=="q(lambda)=q(-lambda)";q["distinct"]=parity.get("exact_covariance",{}).get("distinction")=="Pi_F is not BT ghost parity kappa and is not the SO+(1,1) charge";q["source_odd"]="Upsilon^3" in source.get("positive_packet_frame",{}).get("declared_source","")
 w=c.get("finite_dual_metric_witness",{});K,H,P=map(lambda k:mat(w.get(k,[])),("Krein_metric","Hilbert_metric","Fock_parity"));y4=[Fraction(x) for x in w.get("y4",[])];y5=[Fraction(x) for x in w.get("y5",[])];q["dims"]=all(len(x)==4 and all(len(r)==4 for r in x) for x in (K,H,P)) and len(y4)==len(y5)==4;q["odd_even"]=mv(P,y4)==[-x for x in y4] and mv(P,y5)==y5;q["public_cross"]=2*dot(y4,K,y5)==0 and w.get("public_cross")=="0";q["Hilbert_cross"]=2*dot(y4,H,y5)==0 and w.get("Hilbert_cross")=="0";broken=[r[:] for r in K];broken[0][2]=broken[2][0]=1;q["mutation"]=2*dot(y4,broken,y5)==20 and w.get("parity_breaking_cross")=="20";q["witness_status"]=w.get("status")=="ODD_EVEN_OUTPUTS_ARE_ORTHOGONAL_IN_BOTH_BORN_FORMS"
 q["metrics_exact"]=K==[[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]] and H==[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] and P==[[-1,0,0,0],[0,-1,0,0],[0,0,1,0],[0,0,0,1]]
 s=c.get("fully_rearranged_output_selection",{});q["series"]=s.get("output_series")=="Y=lambda^4*y4+lambda^5*y5+O(lambda^6)";q["complete_y5"]=all(x in s.get("complete_next_output","") for x in ("T5 psi0","T4 psi1","detector correction"));q["public_record"]=s.get("public_cross")=="q9_public=2*Re<y4,y5>_K=0";q["Hilbert_record"]=s.get("Hilbert_cross")=="q9_Hilbert=2*Re<y4,y5>_H=0";q["probability_series"]=all(x in s.get("probability_series","") for x in ("0*lambda^9","lambda^10*q10","every odd coefficient zero"));q["status"]=s.get("status")=="COMPLETE_FULLY_REARRANGED_PROBABILITY_ORDER_LAMBDA9_COEFFICIENT_ZERO"
 d=c.get("disposition",{});q["q8"]=d.get("leading_q8_common_Born")=="COEFFICIENT_COMPUTED";q["q9"]=d.get("probability_order_lambda9")=="EXACTLY_ZERO_IN_BOTH_BORN_FORMS";q["q10_open"]=d.get("first_unresolved_probability_order")=="LAMBDA10" and d.get("q10_coefficient")=="NOT_COMPUTED";q["Eq19_open"]=d.get("general_Eq19")=="NOT_PROVED";q["gravity_open"]=d.get("gravity_or_metric_BV_BRST_transfer")=="NOT_CONSTRUCTED";q["causal_open"]=d.get("Lorentzian_causal_claim")=="NOT_ESTABLISHED";q["boundaries"]=len(c.get("does_not_establish",[]))==10;q["missing"]=len(c.get("missing_object_ledger",[]))==4;q["next"]=all(x in c.get("next_gate","") for x in ("||y5||^2","y4,y6","ghost-kappa"));q["report"]=c.get("report")=="reverse_physics/reports/bt-fully-rearranged-lambda9-parity-selection.md";return q
def main():
 q=verify(load(CERT_REL));bad=[k for k,v in q.items() if not v];print(f"{len(q)-len(bad)}/{len(q)} checks passed");print("failures: "+", ".join(bad) if bad else "RESULT: PASS");return bool(bad)
if __name__=="__main__":raise SystemExit(main())
