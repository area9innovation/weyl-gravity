#!/usr/bin/env python3
"""Independent preservation checker for foundations cube v15."""
from __future__ import annotations
from collections import Counter
import hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json";V14=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json"
BID="FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1";DID="FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1"
EXPECTED={"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS":{BID:"DIRECT_LOCAL"},"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN":{BID:"DIRECT_LOCAL",DID:"SUPPORTING"},"WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|GAUGE_BV_COHOMOLOGY":{DID:"SUPPORTING"}}
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def key(c:dict[str,Any])->str:return "|".join(c[x] for x in ("foundation","carrier","obligation"))
def digest(cells:list[dict[str,Any]],i:list[dict[str,Any]],ci:list[dict[str,Any]])->str:
    return hashlib.sha256(json.dumps({"cells":[(key(c),c["status"],c["evidence"],c["evidence_roles"],c["migration_status"],c.get("biwave_delta_revision")) for c in cells],"interfaces":i,"carrier_interfaces":ci},sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def check(v:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    v=load(RESULT) if v is None else v;old=load(V14);e=[];current,prior=({key(c):c for c in x["cells"]} for x in (v,old));changed=0
    if len(current)!=576 or set(current)!=set(prior):e.append("surface")
    for coordinate,oc in prior.items():
        c=current.get(coordinate)
        if coordinate not in EXPECTED:
            if c!=oc:e.append("undeclared drift "+coordinate);break
            continue
        changed+=1;ev=EXPECTED[coordinate];revision={"previous_status":oc["status"],"new_status":oc["status"],"evidence":ev}
        if c["status"]!=oc["status"] or c.get("biwave_delta_revision")!=revision:e.append("revision "+coordinate)
        for item,role in ev.items():
            if item not in c["evidence"] or c["evidence_roles"].get(item)!=role:e.append("evidence "+coordinate)
        copy=json.loads(json.dumps(c));copy["summary"]=oc["summary"];copy["boundary"]=oc["boundary"];copy.pop("biwave_delta_revision",None)
        for item in ev:copy["evidence"].remove(item);copy["evidence_roles"].pop(item)
        if copy!=oc:e.append("unscoped drift "+coordinate)
    if changed!=3:e.append("changed count")
    counts=Counter(c["status"] for c in current.values())
    for status in ("LOCAL_RESULT","LITERATURE_RESULT","PIECES_ONLY","PRIORITY_GAP","REVIEWED_GAP","NOT_MAPPED"):counts.setdefault(status,0)
    if dict(sorted(counts.items()))!=v.get("dimensions",{}).get("status_counts") or dict(sorted(counts.items()))!=old.get("dimensions",{}).get("status_counts"):e.append("status counts")
    if any(sorted(c["evidence"])!=sorted(c["evidence_roles"]) for c in current.values()):e.append("role closure")
    if v["certified_interfaces"]!=old["certified_interfaces"] or v["certified_carrier_interfaces"]!=old["certified_carrier_interfaces"]:e.append("interfaces")
    d=digest(v["cells"],v["certified_interfaces"],v["certified_carrier_interfaces"])
    if d!=v["independent_checker"]["expected_digest"]:e.append("digest")
    return e,{"digest":d,"cells":len(current),"evidence_augmented_cells":changed,"status_changes":0,"status_counts":dict(sorted(counts.items()))}
def main()->int:
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
