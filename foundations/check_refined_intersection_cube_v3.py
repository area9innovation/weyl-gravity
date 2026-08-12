#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter
import hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json"
V2 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V2.json"
ATLAS = ROOT / "foundations/results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json"
def load(p): return json.loads(p.read_text())
def coord(x): return "|".join(x[k] for k in ("foundation", "carrier", "obligation"))
def digest(cells):
    payload=[(coord(x),x["status"],x["evidence"],x["migration_status"],x.get("research_revision")) for x in cells]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def check(result: dict[str, Any] | None=None):
    result=load(RESULT) if result is None else result; v2=load(V2); atlas=load(ATLAS); errors=[]
    cells=result.get("cells",[]); by={coord(x):x for x in cells}; old={coord(x):x for x in v2["cells"]}
    if len(cells)!=452 or set(by)!=set(old): errors.append("v2 coordinate preservation")
    actions={x["coordinate"]:x for x in atlas["cell_actions"]}; overlays={x["coordinate"]:x for x in atlas["evidence_overlays"]}
    for key, cell in by.items():
        source=old[key]
        for field in ("migration_status","migration_evidence","migration_rationale","migration_relation","parent_obligation"):
            if cell.get(field)!=source.get(field): errors.append("migration preservation "+key); break
        if key in actions:
            a=actions[key]
            if cell.get("status")!=a["new"] or not set(a["evidence"])<=set(cell.get("evidence",[])) or cell.get("research_revision",{}).get("kind")!="STATUS_CHANGE": errors.append("action "+key)
        elif key in overlays:
            o=overlays[key]
            if cell.get("status")!=source["status"] or not set(o["evidence"])<=set(cell.get("evidence",[])) or cell.get("research_revision",{}).get("kind")!="EVIDENCE_OVERLAY": errors.append("overlay "+key)
        elif cell!=source: errors.append("unaffected preservation "+key)
    # Role and status are written by different passes; agreement is checked, not assumed.
    DIRECT_STATUS={"DIRECT_LOCAL":"LOCAL_RESULT","DIRECT_LITERATURE":"LITERATURE_RESULT"}
    for key, cell in by.items():
        roles=cell.get("evidence_roles") or {}
        if sorted(roles)!=sorted(cell.get("evidence") or []): errors.append("evidence-role closure "+key); break
        present=[r for r in ("DIRECT_LOCAL","DIRECT_LITERATURE") if r in roles.values()]
        if present and cell.get("status")!=DIRECT_STATUS[present[0]]: errors.append("role/status agreement "+key); break
    counts=Counter(x.get("status") for x in cells); expected={"LITERATURE_RESULT":93,"LOCAL_RESULT":86,"NOT_MAPPED":81,"PIECES_ONLY":162,"PRIORITY_GAP":30}
    if dict(sorted(counts.items()))!=expected or result.get("dimensions",{}).get("status_counts")!=expected: errors.append("status counts")
    d=result.get("dimensions",{})
    if d.get("coverage_classified_cells")!=371 or d.get("reviewed_no_transfer_unmapped_cells")!=81 or d.get("research_status_changes")!=9 or d.get("research_evidence_overlays")!=5: errors.append("research dimensions")
    calculated=digest(cells)
    if calculated!=result.get("independent_checker",{}).get("expected_digest"): errors.append("canonical digest")
    return errors,{"digest":calculated,"cells":len(cells),"coverage_classified":d.get("coverage_classified_cells"),"status_changes":d.get("research_status_changes"),"evidence_overlays":d.get("research_evidence_overlays"),"reviewed_no_transfer_unmapped":d.get("reviewed_no_transfer_unmapped_cells")}


def main():
    errors,summary=check(); print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True)); return bool(errors)
if __name__=="__main__": raise SystemExit(main())
