#!/usr/bin/env python3
"""Apply the coded-wave RCA_0 frontier to cube v3 without rewriting history."""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];F=ROOT/"foundations";V3=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V3.json";FRONTIER=F/"results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json";OUTPUT=F/"results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json";REPORT=F/"reports/refined-intersection-cube-v4.md"
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coord(x):return "|".join(x[k] for k in ("foundation","carrier","obligation"))
def digest(cells):return hashlib.sha256(json.dumps([(coord(x),x["status"],x["evidence"],x["migration_status"],x.get("coded_wave_revision")) for x in cells],sort_keys=True,separators=(",",":")).encode()).hexdigest()
def build()->dict[str,Any]:
    old=load(V3);frontier=load(FRONTIER);actions={x["coordinate"]:x for x in frontier["cell_actions"]};overlays={x["coordinate"]:x for x in frontier["evidence_overlays"]};cells=[]
    for source in old["cells"]:
        cell=dict(source);key=coord(cell);a=actions.pop(key,None);o=overlays.pop(key,None)
        if a:
            if cell["status"]!=a["old"]:raise ValueError("old status mismatch "+key)
            cell["status"]=a["new"];cell["evidence"]=list(dict.fromkeys([*cell["evidence"],*a["evidence"]]));cell["summary"]=a["basis"];cell["boundary"]="The local RCA_0 upper bound is restricted to the declared fast-Cauchy polygonal energy representation; it is neither a reversal nor a spacetime causal theorem."
        if o:
            cell["evidence"]=list(dict.fromkeys([*cell["evidence"],*o["evidence"]]));cell["summary"] += " Frontier evidence: "+o["basis"]
        if a or o:
            cell["coded_wave_revision"]={"frontier":frontier["result_id"],"status_change":bool(a),"evidence_overlay":bool(o),"previous_status":source["status"]}
            # Frontier records carry no per-obligation directness review of their own.
            cell["evidence_roles"]={**{e:"UNREVIEWED" for e in cell["evidence"]},**cell["evidence_roles"]}
        cells.append(cell)
    if actions or overlays:raise ValueError("unused frontier coordinates")
    counts=Counter(x["status"] for x in cells);migrations=Counter(x["migration_status"] for x in cells)
    r={"schema_version":"foundational-intersection-cube-v4","result_id":"FOUNDATIONAL_INTERSECTION_CUBE_V4","result_kind":"CODED_UPPER_BOUND_REFINED_NAVIGATION_CUBE","lifecycle":"L2_UPPER_BOUND_CERTIFIED","created":"2026-08-12","repository_base_commit":"a0c5fab221459d0938a8d66a91bf7386ab2b9fba","dependency_tags":old["dependency_tags"],"purpose":"Apply the certified coded polygonal-wave RCA_0 upper bound and independent literature overlays while preserving every v3 coordinate and migration field.","compatibility":{"v0_unchanged":True,"v1_unchanged":True,"v2_unchanged":True,"v3_unchanged":True,"coordinates_preserved_from_v3":True,"migration_fields_preserved_from_v3":True,"coded_wave_frontier":frontier["result_id"]},"axes":old["axes"],"cell_statuses":old["cell_statuses"],"migration_statuses":old["migration_statuses"],"evidence_role_vocabulary":old["evidence_role_vocabulary"],"evidence_role_rule":old["evidence_role_rule"],"dimensions":{"axis_sizes":[6,6,16],"cartesian_total":576,"emitted_cells":452,"coverage_classified_cells":452-counts["NOT_MAPPED"],"migration_reviewed_cells":452,"migration_pending_cells":0,"reviewed_no_transfer_cells":migrations["REVIEWED_NO_TRANSFER"],"reviewed_no_transfer_unmapped_cells":sum(x["migration_status"]=="REVIEWED_NO_TRANSFER" and x["status"]=="NOT_MAPPED" for x in cells),"coded_wave_status_changes":len(frontier["cell_actions"]),"coded_wave_evidence_overlays":len(frontier["evidence_overlays"]),"status_counts":dict(sorted(counts.items())),"migration_status_counts":dict(sorted(migrations.items())),"evidence_role_counts":dict(sorted(Counter(role for x in cells for role in x["evidence_roles"].values()).items())),"dual_direct_cells":sum({"DIRECT_LOCAL","DIRECT_LITERATURE"}<=set(x["evidence_roles"].values()) for x in cells)},"cells":cells,"provenance":{"inputs":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in (V3,FRONTIER)]},"independent_checker":{"path":"foundations/check_refined_intersection_cube_v4.py","checks":["v3 coordinate and migration preservation","two status changes","five overlays","status counts","canonical digest"],"expected_digest":digest(cells)},"claim_flags":{"v3_preserved":True,"coded_wave_actions_applied":True,"all_emitted_migrations_reviewed":True,"weakest_base_proved":False,"reverse_lower_bound_proved":False,"all_576_cells_assessed":False,"literature_complete":False,"new_lorentzian_claim":False},"does_not_establish":["literature completeness","that RCA_0 is necessary or weakest","a WKL_0 or ACA_0 reversal","representation invariance","a spacetime-distribution theorem","causal Green support","coverage for 81 still-unmapped emitted coordinates","coherence of 124 synthetic coordinates","a new Lorentzian Weyl result"],"human_report":"foundations/reports/refined-intersection-cube-v4.md"};return r
def render(r):
    d=r["dimensions"];lines=["# Coded-upper-bound foundations cube v4","",f"**Result:** `{r['result_id']}`","","## Outcome","",f"Two weak-arithmetic Hilbert/operator cells move from `PIECES_ONLY` to `LOCAL_RESULT`: a represented isometric one-parameter group and represented Cauchy well-posedness. Five cells receive literature or local evidence overlays. The number of classified cells remains **{d['coverage_classified_cells']}**, while the mix becomes **{d['status_counts']['LOCAL_RESULT']} local results** and **{d['status_counts']['PIECES_ONLY']} pieces-only cells**.","","All v3 coordinates and migration decisions remain unchanged. The promotion says `RCA_0` is sufficient for one named representation; it says nothing about necessity or other representations.","","## Status counts","","| Status | Cells |","|---|---:|"]+[f"| `{k}` | {v} |" for k,v in d["status_counts"].items()]+["","## Reproduction","","```text","python3 foundations/refine_intersection_cube_v4.py --check","python3 foundations/check_refined_intersection_cube_v4.py","python3 foundations/verify_refined_intersection_cube_v4.py","```","","## Boundaries",""]+["- This does not establish "+x+"." for x in r["does_not_establish"]];return "\n".join(lines)+"\n"
def generated():r=build();return (json.dumps(r,indent=2,ensure_ascii=False)+"\n").encode(),render(r).encode()
def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();vals=generated();outs=((OUTPUT,vals[0]),(REPORT,vals[1]));stale=[str(p.relative_to(ROOT)) for p,v in outs if not p.is_file() or p.read_bytes()!=v]
    if a.check:
        if stale:print("FOUNDATIONAL_INTERSECTION_CUBE_V4: stale: "+", ".join(stale));return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V4: generated artifacts current");return 0
    for p,v in outs:p.write_bytes(v)
    print("FOUNDATIONAL_INTERSECTION_CUBE_V4: wrote result and report");return 0
if __name__=="__main__":raise SystemExit(main())
