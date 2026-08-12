#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json";V3=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json";FRONTIER=ROOT/"foundations/results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json"
def load(p):return json.loads(p.read_text())
def coord(x):return "|".join(x[k] for k in ("foundation","carrier","obligation"))
def digest(cells):return hashlib.sha256(json.dumps([(coord(x),x["status"],x["evidence"],x["migration_status"],x.get("coded_wave_revision")) for x in cells],sort_keys=True,separators=(",",":")).encode()).hexdigest()
def check(result:dict[str,Any]|None=None):
    r=load(RESULT) if result is None else result;old=load(V3);frontier=load(FRONTIER);errors=[];cells=r.get("cells",[]);by={coord(x):x for x in cells};prior={coord(x):x for x in old["cells"]};actions={x["coordinate"]:x for x in frontier["cell_actions"]};overlays={x["coordinate"]:x for x in frontier["evidence_overlays"]}
    if len(cells)!=452 or set(by)!=set(prior):errors.append("v3 coordinate preservation")
    for key,cell in by.items():
        source=prior[key]
        for f in ("migration_status","migration_evidence","migration_rationale","migration_relation","parent_obligation"):
            if cell.get(f)!=source.get(f):errors.append("migration preservation "+key);break
        if key in actions and cell.get("status")!=actions[key]["new"]:errors.append("action "+key)
        if key not in actions and cell.get("status")!=source.get("status"):errors.append("status preservation "+key)
        expected=set((actions.get(key) or {}).get("evidence",[])+(overlays.get(key) or {}).get("evidence",[]))
        if not expected<=set(cell.get("evidence",[])):errors.append("evidence "+key)
    counts=Counter(x.get("status") for x in cells);expected={"LITERATURE_RESULT":93,"LOCAL_RESULT":88,"NOT_MAPPED":81,"PIECES_ONLY":160,"PRIORITY_GAP":30}
    if dict(sorted(counts.items()))!=expected or r.get("dimensions",{}).get("status_counts")!=expected:errors.append("status counts")
    d=r.get("dimensions",{})
    if d.get("coverage_classified_cells")!=371 or d.get("coded_wave_status_changes")!=2 or d.get("coded_wave_evidence_overlays")!=5:errors.append("frontier dimensions")
    calculated=digest(cells)
    if calculated!=r.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":calculated,"cells":len(cells),"coverage_classified":d.get("coverage_classified_cells"),"status_changes":d.get("coded_wave_status_changes"),"evidence_overlays":d.get("coded_wave_evidence_overlays")}
def main():
    e,s=check();print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,**s},sort_keys=True));return bool(e)
if __name__=="__main__":raise SystemExit(main())
