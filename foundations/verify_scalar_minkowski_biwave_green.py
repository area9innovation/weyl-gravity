#!/usr/bin/env python3
"""Fail-closed verifier for the flat scalar biwave certificate."""
from __future__ import annotations
import ast,json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.build_scalar_minkowski_biwave_green import generated
from foundations.check_scalar_minkowski_biwave_green import check
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1.json"
REPORT=ROOT/"foundations/reports/scalar-minkowski-biwave-green-v1.md"
SCHEMA=ROOT/"foundations/schema/foundational-scalar-minkowski-biwave-green-v1.schema.json"
CHECKER=ROOT/"foundations/check_scalar_minkowski_biwave_green.py"
def imports(path:Path)->set[str]:
    tree=ast.parse(path.read_text());found=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):found.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module and node.module!='__future__':found.add(node.module.split('.')[0])
    return found
def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    v=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report
    errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(v)]
    ce,_=check(v);errors += ["checker "+x for x in ce]
    rb,mb=generated()
    if (json.dumps(v,indent=2,ensure_ascii=False)+"\n").encode()!=rb:errors.append("deterministic result drift")
    if text.encode()!=mb:errors.append("deterministic report drift")
    if imports(CHECKER)!={"fractions","hashlib","json","pathlib","typing"}:errors.append("checker import boundary")
    for token in ("float(","numpy","sympy","random","requests","urlopen"):
        if token in CHECKER.read_text().lower():errors.append("checker forbidden token "+token)
    for token in ("Flat scalar biwave","Four-data interpretation","Scope firewall","does not establish"):
        if token not in text:errors.append("report token "+token)
    return errors,["Draft 2020-12 schema","independent rational checker","deterministic artifacts","two-sided exact Green identities","causal support and adjoint duality","finite-horizon energy boundary","scalar-to-BV firewall"]
def main()->int:
    e,c=verify();print("FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1: "+("PASS" if not e else "FAIL"));[print("  - "+x) for x in (c if not e else e)];return bool(e)
if __name__=="__main__":raise SystemExit(main())
