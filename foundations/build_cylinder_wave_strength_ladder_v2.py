#!/usr/bin/env python3
"""Promote the coded-energy rung after the polygonal RCA_0 certificate."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];F=ROOT/"foundations"
V1=F/"results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json";WAVE=F/"results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json";OUTPUT=F/"results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json";REPORT=F/"reports/cylinder-wave-strength-ladder-v2.md"
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(r):
    payload={k:r[k] for k in ("ladder","typed_relation_graph","claim_flags","does_not_establish")};return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def build()->dict[str,Any]:
    old=load(V1);r=dict(old);r.update({"schema_version":"foundational-cylinder-wave-strength-ladder-v2","result_id":"FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2","lifecycle":"L2_UPPER_BOUND_CERTIFIED","repository_base_commit":"a0c5fab221459d0938a8d66a91bf7386ab2b9fba","answer":"The finite Laurent and named-tail rungs remain exact. The L2 target is now closed for one explicit second-order-arithmetic representation: mean-zero rational polygonal chiral pairs, completed by fast Cauchy names with prescribed rates. RCA_0 suffices to extend exact rational translations to a unique real-time isometric energy evolution. This does not close L3: a coded localized test class and weak spacetime equation remain to be formalized, and causal Green support remains separate."})
    ladder=[dict(x) for x in old["ladder"]]
    ladder[2]={"level":"L2_CODED_ENERGY_CARRIER","object":"Fast-Cauchy completion of mean-zero rational polygonal chiral pairs","status":"CERTIFIED","sufficient_base":"RCA_0 for the declared representation","source":"FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1","adds":["coded Cauchy completion with prescribed rate","exact rational translation group","finite-code time moduli","primitive-recursive diagonal for named real times"],"establishes":["completed energy state","energy-conserving real-time solution name","Cauchy existence and uniqueness in the declared carrier"],"does_not_establish":["necessity or reversal","representation invariance","localized weak equation","causal support"]}
    ladder[3]=dict(ladder[3]);ladder[3]["open"]=["coded localized test class","coefficient-to-distribution comparison","weakest base"];ladder[3]["source_boundary"]="L2 supplies a completed evolution name, but the present certificate does not formalize test-function integration."
    r["ladder"]=ladder
    graph=json.loads(json.dumps(old["typed_relation_graph"]));
    for node in graph["nodes"]:
        if node["id"]=="M-CODED-HILBERT":node["statement"]="A fast-Cauchy completed chiral energy state and its isometric evolution exist in the declared RCA_0 coding."
    for edge in graph["edges"]:
        if edge["from"]=="M-TAIL-MODULUS" and edge["to"]=="M-CODED-HILBERT":edge.update({"relation":"SUFFICIENT","evidence":["FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1"],"meaning":"A prescribed fast Cauchy rate and finite-code time moduli support the explicit diagonal extension in RCA_0."})
        if edge["from"]=="M-CODED-HILBERT" and edge["to"]=="M-COEFFICIENT-WEAK":edge["evidence"]=["FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1"]
    r["typed_relation_graph"]=graph
    r["provenance"]={"inputs":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in (V1,WAVE)]}
    r["claim_flags"]={**old["claim_flags"],"arbitrary_energy_completion_formalized_in_rca0":True,"declared_representation_rca0_upper_bound":True,"coefficient_weak_solution_formalized":False,"weakest_base_proved":False,"choice_strength_proved":False,"spacetime_distribution_constructed":False,"causal_green_operator_constructed":False,"new_lorentzian_claim":False}
    r["does_not_establish"]=["that RCA_0 is necessary or the weakest base","a WKL_0, ACA_0, or Choice reversal","an upper bound for representations lacking prescribed Cauchy rates","representation invariance","a coefficient-weak or localized spacetime-distribution theorem","finite propagation or causal support from Fourier or polygonal evolution","a normally-hyperbolic Green theorem","the full biwave or metric-BV propagator","renormalized Lorentzian products or a QME theorem","a new LORENTZIAN-CAUSAL result"]
    r["next_gate"]="Formalize L3 against a fixed coded test class. Only then compare it with localized spacetime distributions; support propagation and Green maps remain a separate L5 problem."
    r["human_report"]="foundations/reports/cylinder-wave-strength-ladder-v2.md"
    r["independent_checker"]={"path":"foundations/check_cylinder_wave_strength_ladder_v2.py","checks":["v1 rung preservation outside L2/L3","L2 source closure","typed graph promotion","input pins","boundary flags","canonical digest"],"expected_digest":""};r["independent_checker"]["expected_digest"]=digest(r);return r
def render(r):
    lines=["# Cylinder-wave strength ladder v2","",f"**Result:** `{r['result_id']}`","","## Outcome","",r["answer"],"","## Six levels","","| Level | Status | Object | Base or boundary |","|---|---|---|---|"]
    for x in r["ladder"]:lines.append(f"| `{x['level']}` | `{x['status']}` | {x['object']} | {x.get('sufficient_base',x.get('boundary',x.get('separation','Open')))} |")
    lines += ["","## L2 promotion","","The promotion is representation-specific. A point of the completed carrier already includes a fast Cauchy rate. The proof applies exact translations to dense rational polygonal codes and uses their computed time moduli to form a diagonal name. It invokes neither compactness nor basis selection.","","The next implication, L2 → L3, remains open because an energy-state name is not automatically a coded spacetime distribution or a localized weak solution.","","## Reproduction","","```text","python3 foundations/build_cylinder_wave_strength_ladder_v2.py --check","python3 foundations/check_cylinder_wave_strength_ladder_v2.py","python3 foundations/verify_cylinder_wave_strength_ladder_v2.py","```","","## Boundaries",""]
    lines += ["- This does not establish "+x+"." for x in r["does_not_establish"]];return "\n".join(lines)+"\n"
def generated():r=build();return (json.dumps(r,indent=2,ensure_ascii=False)+"\n").encode(),render(r).encode()
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();vals=generated();outs=((OUTPUT,vals[0]),(REPORT,vals[1]));stale=[str(p.relative_to(ROOT)) for p,v in outs if not p.is_file() or p.read_bytes()!=v]
    if a.check:
        if stale:print("FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2: stale: "+", ".join(stale));return 1
        print("FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2: generated artifacts current");return 0
    for p,v in outs:p.write_bytes(v)
    print("FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2: wrote result and report");return 0
if __name__=="__main__":raise SystemExit(main())
