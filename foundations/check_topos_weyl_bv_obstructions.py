#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from typing import Any

EXPECTED_GLOSSARY={"LOGIC","SET_OBJECT","SPECTRUM","QUANTUM_ALGEBRA","SPACETIME","FIELD","BV_ALGEBRA","DIFFERENTIAL_OPERATOR","TEST_DISTRIBUTION","GREEN_CAUSAL","KREIN_COMPLETION","STATE_PROBABILITY","BRST_COHOMOLOGY","RENORMALIZATION_QME","PROVENANCE"}
ALLOWED_GLOSSARY_STATUS={"STANDARD_TRANSLATION","LITERATURE_BRIDGE","CANDIDATE_TRANSLATION","CANDIDATE_INTERNALIZATION","OPEN_BRIDGE","EXTERNAL_ONLY"}

def canonical_digest(result:dict[str,Any])->str:
    payload={
        "glossary":sorted((x["id"],x["status"]) for x in result.get("glossary",[])),
        "obstructions":sorted((x["id"],x["status"],sorted(x.get("requires",[]))) for x in result.get("obstructions",[])),
        "candidate":result.get("lowest_risk_candidate",{}).get("obstruction_id"),
        "sources":sorted(x.get("source_id") for x in result.get("source_dependencies",[])),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def check(result:dict[str,Any])->tuple[list[str],dict[str,Any]]:
    errors=[]
    glossary=result.get("glossary",[]);gids=[x.get("id") for x in glossary]
    if set(gids)!=EXPECTED_GLOSSARY or len(gids)!=len(set(gids)):errors.append("glossary identifiers")
    if any(x.get("status") not in ALLOWED_GLOSSARY_STATUS or not x.get("warning") for x in glossary):errors.append("glossary status/warning")
    obs=result.get("obstructions",[]);ids=[x.get("id") for x in obs];idset=set(ids)
    if len(obs)!=12 or len(ids)!=len(idset):errors.append("obstruction identifiers")
    for x in obs:
        if not set(x.get("requires",[]))<=idset or x.get("id") in x.get("requires",[]):errors.append("prerequisite closure")
        if x.get("status") not in {"UNSELECTED","CANDIDATE","OPEN"} or not x.get("deliverable"):errors.append("obstruction status/deliverable")
    graph={x.get("id"):set(x.get("requires",[])) for x in obs};done=set()
    while True:
        ready={k for k,v in graph.items() if k not in done and v<=done}
        if not ready:break
        done|=ready
    if done!=idset:errors.append("prerequisite cycle")
    candidate=result.get("lowest_risk_candidate",{})
    if candidate.get("obstruction_id")!="O3-FINITE-BV-ALGEBRA" or candidate.get("constructed_internally") is not False:errors.append("lowest-risk boundary")
    if [x.get("status") for x in obs].count("CANDIDATE")!=1:errors.append("unique candidate")
    digest=canonical_digest(result)
    if digest!=result.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":digest,"glossary_count":len(glossary),"obstruction_count":len(obs),"topological_nodes":len(done)}

def main()->int:
    import pathlib,sys
    path=pathlib.Path(__file__).resolve().parent/"results/FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0.json"
    result=json.loads(path.read_text());errors,summary=check(result)
    print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True))
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
