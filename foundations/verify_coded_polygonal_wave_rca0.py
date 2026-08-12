#!/usr/bin/env python3
from __future__ import annotations
import ast,hashlib,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.build_coded_polygonal_wave_rca0 import generated
from foundations.check_coded_polygonal_wave_rca0 import check
RESULT=ROOT/"foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json";REPORT=ROOT/"foundations/reports/coded-polygonal-wave-rca0.md";SCHEMA=ROOT/"foundations/schema/foundational-coded-polygonal-wave-rca0-v1.schema.json";CHECKER=ROOT/"foundations/check_coded_polygonal_wave_rca0.py"
def imports(path):
    tree=ast.parse(path.read_text());found=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):found.update(a.name.split('.')[0] for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module and n.module!='__future__':found.add(n.module.split('.')[0])
    return found
def verify(*,result=None,report=None):
    r=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report;errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(r)]
    ce,summary=check(r);errors += ["checker "+e for e in ce];er,ep=generated()
    if (json.dumps(r,indent=2,ensure_ascii=False)+"\n").encode()!=er:errors.append("deterministic result drift")
    if text.encode()!=ep:errors.append("deterministic report drift")
    if imports(CHECKER)!={"fractions","hashlib","json","pathlib","typing"}:errors.append("checker import boundary")
    lowered=CHECKER.read_text().lower()
    for token in ("float(","numpy","sympy","cmath","random","requests","urlopen"):
        if token in lowered:errors.append("checker forbidden token "+token)
    source=r.get("literature_context",[{}])[0]
    if source.get("artifact",{}).get("sha256")!="72579f36f47d21861a878568ee5d5199609a00e197e2d25e422011d387349638":errors.append("literature content pin")
    flags=r.get("claim_flags",{})
    for key in ("rca0_upper_bound_for_declared_representation","completed_energy_state_constructed","real_time_solution_name_constructed","energy_conservation_proved","cauchy_uniqueness_in_declared_carrier"):
        if flags.get(key) is not True:errors.append("positive flag "+key)
    for key in ("weakest_base_proved","reverse_lower_bound_proved","representation_invariance_proved","spacetime_distribution_constructed","causal_green_operator_constructed","choice_free_zf_theorem_proved","new_lorentzian_claim"):
        if flags.get(key) is not False:errors.append("boundary flag "+key)
    for token in ("RCA₀","fast Cauchy rate","no modulus is extracted","unique continuous isometric extension","does not establish"):
        if token not in text:errors.append("report token "+token)
    return errors,["schema","independent exact rail","deterministic artifacts","checker isolation","content pin","claim boundaries"]
def main():
    e,c=verify();print("FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1: "+("PASS" if not e else "FAIL"));[print("  - "+x) for x in (c if not e else e)];return bool(e)
if __name__=="__main__":raise SystemExit(main())
