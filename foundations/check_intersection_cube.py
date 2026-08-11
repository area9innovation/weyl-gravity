#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from typing import Any

AXES=("FOUNDATION","CARRIER","OBLIGATION")
STATUSES={"LOCAL_RESULT","LITERATURE_RESULT","PIECES_ONLY","PRIORITY_GAP"}

def canonical_digest(result:dict[str,Any])->str:
    payload={
        "axes":[(a.get("id"),[(k.get("id"),k.get("label")) for k in a.get("keys",[])]) for a in result.get("axes",[])],
        "cells":sorted((x.get("foundation"),x.get("carrier"),x.get("obligation"),x.get("status"),tuple(x.get("evidence",[]))) for x in result.get("cells",[])),
        "faces":sorted(x.get("id") for x in result.get("missing_faces",[])),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def check(result:dict[str,Any])->tuple[list[str],dict[str,Any]]:
    errors=[];axes=result.get("axes",[])
    if [a.get("id") for a in axes]!=list(AXES):errors.append("axis order/identity")
    keys={a.get("id"):{k.get("id") for k in a.get("keys",[])} for a in axes}
    if any(len(a.get("keys",[]))!=6 or len(keys.get(a.get("id"),set()))!=6 for a in axes):errors.append("axis key count/uniqueness")
    if any(not a.get("question") or any(not k.get("label") or not k.get("meaning") for k in a.get("keys",[])) for a in axes):errors.append("axis explanations")
    cells=result.get("cells",[]);coordinates=[]
    for x in cells:
        coord=(x.get("foundation"),x.get("carrier"),x.get("obligation"));coordinates.append(coord)
        if coord[0] not in keys.get("FOUNDATION",set()) or coord[1] not in keys.get("CARRIER",set()) or coord[2] not in keys.get("OBLIGATION",set()):errors.append("cell coordinate closure")
        if x.get("status") not in STATUSES or not x.get("summary") or not x.get("boundary"):errors.append("cell status/explanation")
        if not isinstance(x.get("evidence"),list):errors.append("cell evidence type")
        elif any(not isinstance(item,str) or not item for item in x.get("evidence",[])):errors.append("cell evidence identifier")
    if len(coordinates)!=len(set(coordinates)):errors.append("duplicate coordinates")
    faces=result.get("missing_faces",[])
    if len(faces)!=5 or len({x.get("id") for x in faces})!=5:errors.append("missing faces")
    axis_field={"foundations":"FOUNDATION","carriers":"CARRIER","obligations":"OBLIGATION"}
    for face in faces:
        if not face.get("why"):errors.append("face explanation")
        for field,axis in axis_field.items():
            if not set(face.get("coordinates",{}).get(field,[]))<=keys.get(axis,set()):errors.append("face coordinate closure")
    digest=canonical_digest(result)
    if digest!=result.get("independent_checker",{}).get("expected_digest"):errors.append("canonical digest")
    counts={name:sum(x.get("status")==name for x in cells) for name in sorted(STATUSES)}
    return errors,{"digest":digest,"declared_cells":len(cells),"total_cells":216,"default_not_mapped":216-len(cells),"status_counts":counts}

def main()->int:
    import pathlib
    path=pathlib.Path(__file__).resolve().parent/"results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
    errors,summary=check(json.loads(path.read_text()))
    print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors,**summary},sort_keys=True))
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
