#!/usr/bin/env python3
"""Fail-closed verifier for foundations cube v14."""
from __future__ import annotations
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.check_refined_intersection_cube_v14 import check
from foundations.refine_intersection_cube_v14 import generated
RESULT=ROOT/"foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V14.json";REPORT=ROOT/"foundations/reports/refined-intersection-cube-v14.md";SCHEMA=ROOT/"foundations/schema/foundational-intersection-cube-v14.schema.json"
def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    value=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report
    errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)];checker_errors,_=check(value);errors += ["checker "+e for e in checker_errors];rb,mb=generated()
    if (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode()!=rb:errors.append("deterministic result drift")
    if text.encode()!=mb:errors.append("deterministic report drift")
    flags=value.get("claim_flags",{})
    for key in ("v13_surface_preserved","all_576_coordinates_assessed","fixed_support_translator_imported","support_indexed_comparison_imported","scalar_green_audit_imported","represented_name_equivalence_established","scalar_causal_green_established","new_lorentzian_claim"):
        if flags.get(key) is not True:errors.append("positive flag "+key)
    for key in ("full_lf_test_topology_established","arbitrary_distributional_uniqueness_established","variable_coefficient_green_established","weyl_bv_green_established","hadamard_or_quantum_causal_construction_established","empirical_agreement_assessed","complete_physical_theory_established"):
        if flags.get(key) is not False:errors.append("boundary flag "+key)
    for token in ("576", "Reconstruction/limits", "causal", "scalar", "does not establish"):
        if token not in text:errors.append("report token "+token)
    return errors,["Draft 2020-12 schema","independent preservation audit","four-cell evidence scope","two local promotions","scalar LORENTZIAN-CAUSAL firewall","deterministic artifacts"]
def main()->int:
    errors,checks=verify();print("FOUNDATIONAL_INTERSECTION_CUBE_V14: "+("PASS" if not errors else "FAIL"));[print("  - "+x) for x in (checks if not errors else errors)];return bool(errors)
if __name__=="__main__":raise SystemExit(main())
