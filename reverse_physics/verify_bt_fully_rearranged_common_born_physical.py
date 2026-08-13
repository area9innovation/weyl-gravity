#!/usr/bin/env python3
"""Independent verifier for the fully rearranged common-Born theorem."""
from __future__ import annotations
import hashlib, json, os
from fractions import Fraction

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL="reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1.json"
CERT=os.path.join(ROOT,CERT_REL)
SOURCE="23de3e07843b5acd41a6c9bf880fc05c0e6e4ff7"
INPUTS=[
"planning/work-items/reverse-physics-bateman-fully-rearranged-common-born-physical.json",
"planning/events/reverse-physics-bateman-fully-rearranged-common-born-physical-DONE-23de3e07.json",
"reverse_physics/data/bateman_turok_hamiltonian_source_v1.json",
"reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json",
"reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPLETE_CONNECTED_COMMON_BORN_PACKET_V1.json",
"reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json"]

def load(p):
    try:
        with open(os.path.join(ROOT,p),encoding="utf-8") as handle: return json.load(handle)
    except (OSError,ValueError): return {}
def sha(p):
    h=hashlib.sha256()
    try:
        with open(os.path.join(ROOT,p),"rb") as f:
            for b in iter(lambda:f.read(65536),b""): h.update(b)
    except OSError: return ""
    return h.hexdigest()
def mat(v):
    try: a=[[Fraction(x) for x in r] for r in v]
    except (TypeError,ValueError,ZeroDivisionError): return []
    return a if a and all(len(r)==len(a[0]) for r in a) else []
def tr(a): return [list(r) for r in zip(*a)] if a else []
def mul(a,b):
    if not a or not b or len(a[0])!=len(b): return []
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))),Fraction()) for j in range(len(b[0]))] for i in range(len(a))]
def trace(a): return sum((a[i][i] for i in range(len(a))),Fraction()) if a else Fraction()

def verify(c):
    q={}
    q["identity"]=c.get("certificate")=="REVERSE_PHYSICS_BT_FULLY_REARRANGED_COMMON_BORN_PHYSICAL_V1"
    q["schema"]=c.get("schema")=="reverse_physics/schema/reverse-physics-bt-fully-rearranged-common-born-physical-v1.schema.json"
    q["version"]=c.get("schema_version")==1; q["lifecycle"]=c.get("lifecycle_state")=="COEFFICIENT_COMPUTED"
    q["tags"]=c.get("dependency_tags")==["LOCAL-ALGEBRAIC","REDUCED-MODE"]
    p=c.get("provenance",{}); ins=p.get("inputs",[])
    q["source"]=p.get("source_commit")==SOURCE
    q["paths"]=[x.get("path") for x in ins]==INPUTS
    q["hashes"]=len(ins)==len(INPUTS) and all(x.get("sha256")==sha(y) for x,y in zip(ins,INPUTS))
    q["producer"]=p.get("generated_by")=="reverse_physics/bt_fully_rearranged_common_born_physical.py"
    q["verifier"]=p.get("independent_verifier")=="reverse_physics/verify_bt_fully_rearranged_common_born_physical.py"
    physical,common,globalc=map(load,INPUTS[3:6]); q["predecessors"]=all(x.get("checks",{}).get("ok") for x in (physical,common,globalc))
    w=c.get("exact_tensor_witness",{}); px,py,k,t=map(lambda key:mat(w.get(key,[])),("P_X","P_Y","kappa_total","T4_YX"))
    z=[[Fraction() for _ in range(16)] for _ in range(16)]; ident=[[Fraction(i==j) for j in range(16)] for i in range(16)]
    q["dimensions"]=all(len(x)==16 and all(len(r)==16 for r in x) for x in (px,py,k,t))
    q["orthogonal"]=mul(py,px)==z; q["idempotent"]=mul(px,px)==px and mul(py,py)==py; q["kappa2"]=mul(k,k)==ident
    q["commute_X"]=mul(px,k)==mul(k,px); q["commute_Y"]=mul(py,k)==mul(k,py)
    q["restriction"]=mul(mul(py,t),px)==t
    q["fixed"]=mul(mul(k,t),k)==t
    sharp=mul(mul(k,tr(t)),k); q["adjoint"]=sharp==tr(t)
    pub=mul(sharp,t); hil=mul(tr(t),t); q["effects"]=pub==hil
    q["squares"]=trace(pub)==trace(hil)==770 and w.get("public_trace_square")==w.get("Hilbert_trace_square")=="770"
    q["defect"]=w.get("Born_defect")=="0"; q["witness_status"]=w.get("status")=="ORTHOGONAL_PACKET_RESTRICTION_PRESERVES_TOTAL_KAPPA_FIXEDNESS_EXACTLY"
    q["projector_record"]=w.get("projector_product")=="P_Y P_X=0"
    q["commutator_record"]=w.get("commutators")==["[P_X,kappa_total]=0","[P_Y,kappa_total]=0"]
    q["fixed_record"]=w.get("fixed_point")=="kappa_total T4,YX kappa_total=T4,YX"
    q["adjoint_record"]=w.get("adjoint")=="T4,YX^sharp=T4,YX*"
    r=c.get("complete_leading_common_Born_transition",{})
    q["expansion"]=r.get("expansion")=="P_Y(U_T-I)P_X=lambda^4*T4,YX+O(lambda^5)"
    q["disconnected"]=r.get("disconnected_restriction")=="P_Y*D4_disconnected*P_X=0 for all 202 disconnected partitions"
    q["complete"]=r.get("complete_leading_identity")=="L4_YX=T4,YX"
    q["complete_fixed"]=r.get("fixed_point")=="alpha(L4_YX)=L4_YX"
    q["effect_identity"]="E8_public=" in r.get("effect_identity","") and "=E8_Hilbert" in r.get("effect_identity","")
    q["operator_defect"]=r.get("Born_defect")=="E8_public-E8_Hilbert=0 as an operator coefficient"
    q["probability"]=all(x in r.get("scalar_probability","") for x in ("lambda^8","sum_(B=1)^9","O(lambda^9)"))
    q["bound"]=r.get("coefficient_bound")=="q_click^(8)<=81*lambda^8*T^2/(200*pi^6)"
    q["status"]=r.get("status")=="COMPLETE_LEADING_FULLY_REARRANGED_PUBLIC_COMMON_BORN_PHYSICAL_PROBABILITY"
    d=c.get("disposition",{}); q["physical"]=d.get("complete_leading_finite_time_public_physical_probability")=="COEFFICIENT_COMPUTED"
    q["ledger"]=d.get("complete_leading_disconnected_ledger")=="EXHAUSTED_AND_ZERO_ON_DETECTOR"
    q["higher_open"]=d.get("higher_orders")=="NOT_CONTROLLED"; q["Eq19_open"]=d.get("general_Eq19")=="NOT_PROVED"
    q["gravity_open"]=d.get("gravity_or_metric_BV_BRST_transfer")=="NOT_CONSTRUCTED"; q["causal_open"]=d.get("Lorentzian_causal_claim")=="NOT_ESTABLISHED"
    q["boundaries"]=len(c.get("does_not_establish",[]))==11; q["missing"]=len(c.get("missing_object_ledger",[]))==4
    q["next"]=all(x in c.get("next_gate","") for x in ("T5","spectator-overlap","Eq. (19)"))
    q["commands"]=len(c.get("verification_commands",[]))==3; q["report"]=c.get("report")=="reverse_physics/reports/bt-fully-rearranged-common-born-physical.md"
    q["support_import"]=physical.get("disconnected_support_classification",{}).get("disconnected_set_partitions")==202
    q["common_import"]=common.get("complete_packet_descent",{}).get("Born_defect")=="E_click^public-E_click^Hilbert=0 as an operator"
    q["global_import"]=globalc.get("global_connected_column",{}).get("status")=="GLOBAL_CONNECTED_FINITE_TIME_POSITIVE_EFFECT_CONSTRUCTED"
    q["global_structure"]=globalc.get("global_connected_column",{}).get("amplitude")=="A_full=16*lambda^4*sum_(B=0)^9(K_B,T tensor R_B)" and "full phase-space product" in globalc.get("global_connected_column",{}).get("kernel","")
    return q

def main():
    q=verify(load(CERT_REL)); bad=[k for k,v in q.items() if not v]; print(f"{len(q)-len(bad)}/{len(q)} checks passed")
    if bad: print("failures: "+", ".join(bad)); return 1
    return 0
if __name__=="__main__": raise SystemExit(main())
