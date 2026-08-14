#!/usr/bin/env python3
"""Fail-closed verifier for the scalar-biwave-to-Weyl-BV delta."""
from __future__ import annotations
import ast,json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.build_scalar_biwave_to_weyl_bv_delta import generated
from foundations.check_scalar_biwave_to_weyl_bv_delta import check
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1.json";REPORT=ROOT/"foundations/reports/scalar-biwave-to-weyl-bv-dependency-delta-v1.md";SCHEMA=ROOT/"foundations/schema/foundational-scalar-biwave-to-weyl-bv-dependency-delta-v1.schema.json";CHECKER=ROOT/"foundations/check_scalar_biwave_to_weyl_bv_delta.py"
def imports(p:Path)->set[str]:
    tree=ast.parse(p.read_text());found=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):found.update(x.name.split('.')[0] for x in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module and n.module!='__future__':found.add(n.module.split('.')[0])
    return found
def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    v=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report
    e=["schema "+x.message for x in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(v)];ce,_=check(v);e += ["checker "+x for x in ce]
    rb,mb=generated()
    if (json.dumps(v,indent=2,ensure_ascii=False)+"\n").encode()!=rb:e.append("deterministic result drift")
    if text.encode()!=mb:e.append("deterministic report drift")
    if imports(CHECKER)!={"hashlib","json","pathlib","typing"}:e.append("checker import boundary")
    for token in ("What transfers","two live positive routes","Why the gate is red","Scoped no-go results","does not establish"):
        if token not in text:e.append("report token "+token)
    return e,["Draft 2020-12 schema","independent status and provenance checker","deterministic artifacts","16-gate dependency closure","classical import fail-closed replay","quantum lifecycle firewall","scoped no-go firewall"]
def main()->int:
    e,c=verify();print("FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1: "+("PASS" if not e else "FAIL"));[print("  - "+x) for x in (c if not e else e)];return bool(e)
if __name__=="__main__":raise SystemExit(main())
