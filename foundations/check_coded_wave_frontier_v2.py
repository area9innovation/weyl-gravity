#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/"foundations/results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json";LEDGER=ROOT/"foundations/literature-coded-wave-frontier-v2.json";CUBE=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json"
def load(p):return json.loads(p.read_text())
def digest(r):return hashlib.sha256(json.dumps({k:r[k] for k in ("framework_distinctions","cell_actions","evidence_overlays","bounded_search")},sort_keys=True,separators=(",",":")).encode()).hexdigest()
def check(result:dict[str,Any]|None=None,ledger:dict[str,Any]|None=None):
    r=load(RESULT) if result is None else result;l=load(LEDGER) if ledger is None else ledger;cube=load(CUBE);errors=[]
    sources={x.get("id"):x for x in l.get("entries",[])};expected={"simpson-1984-ode","pischke-2025-semigroups","weihrauch-zhong-2007-cauchy","zhong-1999-sobolev","zhong-weihrauch-2003-distributions","weihrauch-zhong-2006-fundamental","bridges-wang-1998-dirichlet"}
    if set(sources)!=expected:errors.append("seven-source closure")
    if sources.get("pischke-2025-semigroups",{}).get("artifact",{}).get("status")!="CONTENT_PINNED" or sources.get("pischke-2025-semigroups",{}).get("artifact",{}).get("sha256")!="df22f1d13d554d99c41a0da840078f0614680171b77338aa2507601a33856877":errors.append("content pin")
    if any(not x.get("boundary") or not x.get("supported_statements") for x in sources.values()):errors.append("source boundary closure")
    frameworks={x.get("framework") for x in r.get("framework_distinctions",[])}
    if frameworks!={"REVERSE_MATHEMATICS","PROOF_MINING","COMPUTABLE_TTE","BISHOP_CONSTRUCTIVE","ZF_WITHOUT_COUNTABLE_CHOICE"}:errors.append("framework distinction closure")
    by={"|".join(x[k] for k in ("foundation","carrier","obligation")):x for x in cube["cells"]};actions=r.get("cell_actions",[]);overlays=r.get("evidence_overlays",[])
    if len(actions)!=2 or len({x.get("coordinate") for x in actions})!=2:errors.append("two status actions")
    if len(overlays)!=5 or len({x.get("coordinate") for x in overlays})!=5:errors.append("five overlays")
    for x in actions:
        if by.get(x.get("coordinate"),{}).get("status")!=x.get("old") or x.get("new")!="LOCAL_RESULT":errors.append("action "+str(x.get("coordinate")))
    for x in overlays:
        if x.get("coordinate") not in by:errors.append("overlay "+str(x.get("coordinate")))
    known=expected|{"FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1","FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2","FOUNDATIONAL_CODED_WAVE_FRONTIER_V2","blackadar-farah-karagila-2026"}
    used={e for section in (r.get("framework_distinctions",[]),actions,overlays) for x in section for e in x.get("evidence",[])}
    if not used<=known:errors.append("evidence closure")
    calculated=digest(r)
    if calculated!=r.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":calculated,"sources":len(sources),"frameworks":len(frameworks),"cell_actions":len(actions),"evidence_overlays":len(overlays)}
def main():
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
