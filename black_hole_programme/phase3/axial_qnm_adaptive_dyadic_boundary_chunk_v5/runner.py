#!/usr/bin/env python3
"""Reuse v4 parent 103 and evaluate only its two children."""
import hashlib, json, time
from pathlib import Path
from ..axial_qnm_adaptive_dyadic_boundary_chunk_v3 import continuation as core
from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as base

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
RAW=HERE/"adaptive-raw-run.json"; AGG=HERE/"adaptive-aggregate-run.json"
CERT=HERE/"certificate.json"; REPORT=HERE/"report.md"
P=ROOT/"black_hole_programme/phase3/axial_qnm_adaptive_dyadic_boundary_chunk_v4"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def main():
    start=time.monotonic()
    core.START=103; core.STOP=104
    core.PREDECESSOR_CERT=P/"certificate.json"
    core.PREDECESSOR_RAW=P/"adaptive-raw-run.json"
    core.PREDECESSOR_AGGREGATE=P/"adaptive-aggregate-run.json"
    raw=core.compute_raw(); RAW.write_text(json.dumps(raw,indent=2,sort_keys=True)+"\n")
    base.PREDECESSOR_CERT=P/"certificate.json"
    base.PREDECESSOR_RUN=P/"adaptive-aggregate-run.json"
    agg=base.build_aggregate(raw); AGG.write_text(json.dumps(agg,indent=2,sort_keys=True)+"\n")
    flags={k:False for k in ["full_contour_nonzero_certified","argument_principle_certified","root_count_certified","QNM_location_certified","Smith_selector_certified","defective_fibre_or_EP2_certified"]}
    flags.update({"children_206_207_nonzero_certified":len(raw["accepted_segments"])==2,"threshold_lowered":False})
    cert={"schema":"phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v5","status":"CHILD_ONLY_REPAIR_FAIL_CLOSED","lifecycle":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"claim_flags":flags,"result":{"elapsed_seconds":time.monotonic()-start,"coverage_stop":agg["summary"]["coverage_stop"],"next_gap":agg["next_honest_boundary_gap"],"children":[{"segment":f"{e['panel']}/{e['panel_count']}","row_sha256":e["row_sha256"],"delta_lower":e["row"]["physical_mismatch"]["modulus_lower"]} for e in raw["accepted_segments"]]},"imports":{"v4_raw":{"path":rel(P/"adaptive-raw-run.json"),"sha256":sha(P/"adaptive-raw-run.json")},"v4_aggregate":{"path":rel(P/"adaptive-aggregate-run.json"),"sha256":sha(P/"adaptive-aggregate-run.json")}},"runs":{"raw":{"path":rel(RAW),"sha256":sha(RAW)},"aggregate":{"path":rel(AGG),"sha256":sha(AGG)}},"does_not_establish":["full contour","root count","QNM location","Smith selector","EP2","H4","T_plus","time-domain stability"]}
    CERT.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
    REPORT.write_text(f"# Child-only repair v5\n\nCoverage `{cert['result']['coverage_stop']}`; next gap `{cert['result']['next_gap']['start']}`. Root/QNM/Smith/EP2 gates remain false.\n")
    print(CERT)
if __name__=="__main__": main()
