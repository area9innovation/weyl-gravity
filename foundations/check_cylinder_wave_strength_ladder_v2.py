#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/"foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json";V1=ROOT/"foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
def load(p):return json.loads(p.read_text())
def digest(r):return hashlib.sha256(json.dumps({k:r[k] for k in ("ladder","typed_relation_graph","claim_flags","does_not_establish")},sort_keys=True,separators=(",",":")).encode()).hexdigest()
def check(result:dict[str,Any]|None=None):
    r=load(RESULT) if result is None else result;old=load(V1);errors=[];ladder=r.get("ladder",[])
    if len(ladder)!=6 or [x.get("level") for x in ladder]!=[x.get("level") for x in old["ladder"]]:errors.append("six-rung closure")
    for i in (0,1,4,5):
        if ladder[i]!=old["ladder"][i]:errors.append("v1 rung preservation "+str(i))
    if ladder[2].get("status")!="CERTIFIED" or ladder[2].get("sufficient_base")!="RCA_0 for the declared representation" or ladder[2].get("source")!="FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1":errors.append("L2 promotion")
    graph=r.get("typed_relation_graph",{});nodes={x.get("id") for x in graph.get("nodes",[])};edges=graph.get("edges",[])
    if len(nodes)!=12 or len(edges)!=10:errors.append("graph dimensions")
    promoted=[x for x in edges if x.get("from")=="M-TAIL-MODULUS" and x.get("to")=="M-CODED-HILBERT"]
    if len(promoted)!=1 or promoted[0].get("relation")!="SUFFICIENT" or promoted[0].get("evidence")!=["FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1"]:errors.append("typed graph promotion")
    flags=r.get("claim_flags",{})
    if flags.get("declared_representation_rca0_upper_bound") is not True or flags.get("coefficient_weak_solution_formalized") is not False or flags.get("causal_green_operator_constructed") is not False:errors.append("boundary flags")
    calculated=digest(r)
    if calculated!=r.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":calculated,"levels":len(ladder),"graph_edges":len(edges),"certified_levels":sum(x.get("status")=="CERTIFIED" for x in ladder)}
def main():
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
