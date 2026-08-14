#!/usr/bin/env python3
"""Independent preservation checker for foundations cube v14."""
from __future__ import annotations
from collections import Counter
import hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json";V13=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V13.json"
TRANSLATOR=ROOT/"foundations/results/FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1.json";TEST_SPACE=ROOT/"foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json";GREEN=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
TID="FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1";LID="FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1";GID="FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1"
EXPECTED={
 "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|KINEMATICS_OBSERVABLES":("LOCAL_RESULT","LOCAL_RESULT",{TID:"DIRECT_LOCAL",LID:"DIRECT_LOCAL"}),
 "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS":("LOCAL_RESULT","LOCAL_RESULT",{LID:"SUPPORTING",GID:"DIRECT_LOCAL"}),
 "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN":("PIECES_ONLY","LOCAL_RESULT",{LID:"SUPPORTING",GID:"DIRECT_LOCAL"}),
 "WEAK_ARITHMETIC|SMOOTH_DISTRIBUTIONAL|RECONSTRUCTION_LIMITS":("PIECES_ONLY","LOCAL_RESULT",{TID:"DIRECT_LOCAL",LID:"DIRECT_LOCAL",GID:"SUPPORTING"})}
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text())
def key(c:dict[str,Any])->str:return "|".join(c[n] for n in ("foundation","carrier","obligation"))
def digest(cells:list[dict[str,Any]],interfaces:list[dict[str,Any]],carrier_interfaces:list[dict[str,Any]])->str:
    proj={"cells":[(key(c),c["status"],c["evidence"],c["evidence_roles"],c["migration_status"],c.get("vertical_slice_revision")) for c in cells],"interfaces":interfaces,"carrier_interfaces":carrier_interfaces};return hashlib.sha256(json.dumps(proj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def check(value:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    result=load(RESULT) if value is None else value;old=load(V13);errors:list[str]=[];current,prior=({key(c):c for c in d.get("cells",[])} for d in (result,old))
    if len(current)!=576 or set(current)!=set(prior):errors.append("exact preserved 576-cell surface")
    changed=status_changes=0
    for coordinate,old_cell in prior.items():
        cell=current.get(coordinate)
        if cell is None:continue
        if coordinate not in EXPECTED:
            if cell!=old_cell:errors.append("undeclared v13 cell drift "+coordinate);break
            continue
        changed+=1;previous,new,evidence=EXPECTED[coordinate];status_changes+=previous!=new
        revision={"previous_status":previous,"new_status":new,"evidence":evidence}
        if old_cell.get("status")!=previous or cell.get("status")!=new or cell.get("vertical_slice_revision")!=revision:errors.append("declared vertical revision "+coordinate)
        for item,role in evidence.items():
            if item not in cell.get("evidence",[]) or cell.get("evidence_roles",{}).get(item)!=role:errors.append("typed vertical evidence "+coordinate)
        copy=json.loads(json.dumps(cell));copy["status"]=old_cell["status"];copy["summary"]=old_cell["summary"];copy["boundary"]=old_cell["boundary"];copy.pop("vertical_slice_revision",None)
        for item in evidence:copy["evidence"].remove(item);copy["evidence_roles"].pop(item)
        if copy!=old_cell:errors.append("unscoped field drift "+coordinate)
    if changed!=4 or status_changes!=2:errors.append("exact four augmentations and two status changes")
    if any(sorted(c.get("evidence",[]))!=sorted(c.get("evidence_roles",{})) for c in current.values()):errors.append("evidence-role closure")
    expected_counts={"LITERATURE_RESULT":90,"LOCAL_RESULT":127,"NOT_MAPPED":0,"PIECES_ONLY":160,"PRIORITY_GAP":30,"REVIEWED_GAP":169};counter=Counter(c.get("status") for c in current.values());counts={n:counter.get(n,0) for n in expected_counts}
    if counts!=expected_counts or result.get("dimensions",{}).get("status_counts")!=dict(sorted(expected_counts.items())):errors.append("status counts")
    if result.get("certified_interfaces")!=old.get("certified_interfaces") or result.get("certified_carrier_interfaces")!=old.get("certified_carrier_interfaces"):errors.append("interface preservation")
    translator,test_space,green=map(load,(TRANSLATOR,TEST_SPACE,GREEN))
    if translator["claim_flags"]["full_lf_topology_identified"] or test_space["claim_flags"]["full_lf_locally_convex_topology_identified"] or not green["claim_flags"]["strict_causal_support_proved"] or green["claim_flags"]["weyl_bv_propagator_constructed"]:errors.append("source certificate boundaries")
    calculated=digest(result.get("cells",[]),result.get("certified_interfaces",[]),result.get("certified_carrier_interfaces",[]))
    if calculated!=result.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    return errors,{"digest":calculated,"cells":len(current),"evidence_augmented_cells":changed,"status_changes":status_changes,"status_counts":counts}
def main()->int:
    errors,summary=check();print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True));return bool(errors)
if __name__=="__main__":raise SystemExit(main())
