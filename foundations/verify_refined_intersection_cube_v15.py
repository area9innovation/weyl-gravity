#!/usr/bin/env python3
"""Fail-closed verifier for foundations cube v15."""
from __future__ import annotations
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_refined_intersection_cube_v15 import check
from foundations.refine_intersection_cube_v15 import generated
RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V15.json";REPORT=ROOT/"foundations/reports/refined-intersection-cube-v15.md";SCHEMA=ROOT/"foundations/schema/foundational-intersection-cube-v15.schema.json"
def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    v=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report;e=["schema "+x.message for x in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(v)];ce,_=check(v);e += ["checker "+x for x in ce];rb,mb=generated()
    if (json.dumps(v,indent=2,ensure_ascii=False)+"\n").encode()!=rb:e.append("result drift")
    if text.encode()!=mb:e.append("report drift")
    flags=v.get("claim_flags",{})
    for x in ("v14_surface_preserved","all_576_coordinates_assessed","scalar_biwave_imported","weyl_bv_dependency_delta_imported","scalar_biwave_green_established","weyl_bv_gap_classified","new_lorentzian_claim"):
        if flags.get(x) is not True:e.append("positive flag "+x)
    for x in ("weyl_bv_green_established","classical_import_gate_passed","hadamard_or_quantum_causal_construction_established","complete_physical_theory_established"):
        if flags.get(x) is not False:e.append("boundary flag "+x)
    return e,["Draft 2020-12 schema","independent v14 preservation audit","three-cell evidence scope","zero status changes","scalar-to-Weyl firewall","deterministic artifacts"]
def main()->int:
    e,c=verify();print("FOUNDATIONAL_INTERSECTION_CUBE_V15: "+("PASS" if not e else "FAIL"));[print("  - "+x) for x in (c if not e else e)];return bool(e)
if __name__=="__main__":raise SystemExit(main())
