#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from typing import Any

EXPECTED={1:"OP-EXACT-BV-WEAK-BASELINE",2:"OP-KREIN-EXPLICIT-J-AUDIT",3:"OP-SEPARATION-WITNESS-CROSSWALK",4:"OP-SEPARABLE-CSTAR-STATE-CHAIN",5:"OP-SPECTRAL-FRAGMENT-AUDIT",6:"OP-OPERATIONAL-RECONSTRUCTION-STRENGTH",7:"OP-GREEN-OPERATOR-FOUNDATIONS",8:"OP-FINITE-FIELD-WEYL-BRIDGE",9:"OP-TOPOS-WEYL-BV"}

def canonical_digest(result:dict[str,Any])->str:
    payload=[(x.get("rank"),x.get("opportunity_id"),x.get("first_artifact_status"),x.get("scientific_status"),x.get("artifact",{}).get("result_id"),x.get("artifact",{}).get("sha256")) for x in result.get("entries",[])]
    return hashlib.sha256(json.dumps(payload,separators=(",",":")).encode()).hexdigest()

def check(result:dict[str,Any])->tuple[list[str],dict[str,Any]]:
    errors=[];entries=result.get("entries",[])
    mapping={x.get("rank"):x.get("opportunity_id") for x in entries}
    if len(entries)!=9 or mapping!=EXPECTED or len({x.get("opportunity_id") for x in entries})!=9:errors.append("rank/opportunity bijection")
    if any(x.get("first_artifact_status")!="COMPLETE" for x in entries):errors.append("incomplete first artifact")
    if any(not x.get("evidence") or not x.get("deeper_gate") for x in entries):errors.append("missing evidence/deeper gate")
    by_artifact={}
    for x in entries:by_artifact.setdefault(x.get("artifact",{}).get("result_id"),[]).append(x.get("rank"))
    shared=sorted(sorted(v) for v in by_artifact.values() if len(v)>1)
    if shared!=[[1,3]]:errors.append("unexpected shared artifact")
    agg=result.get("aggregate",{})
    if agg.get("ranked_opportunity_count")!=9 or agg.get("complete_first_artifact_count")!=9 or agg.get("distinct_artifact_count")!=8 or agg.get("deeper_programmes_open")!=9 or agg.get("closure")!="ALL_RANKED_FIRST_ARTIFACTS_COMPLETE":errors.append("aggregate")
    digest=canonical_digest(result)
    if digest!=result.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":digest,"entries":len(entries),"distinct_artifacts":len(by_artifact),"shared":shared}

def main()->int:
    import pathlib
    path=pathlib.Path(__file__).resolve().parent/"results/FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1.json"
    errors,summary=check(json.loads(path.read_text()))
    print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True))
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
