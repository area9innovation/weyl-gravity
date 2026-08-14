#!/usr/bin/env python3
"""Fail-closed verifier for the scalar Minkowski Green choice audit."""
from __future__ import annotations
import ast,json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from foundations.build_scalar_minkowski_green_choice_audit import generated
from foundations.check_scalar_minkowski_green_choice_audit import check
RESULT=ROOT/"foundations/results/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1.json"
REPORT=ROOT/"foundations/reports/scalar-minkowski-green-choice-audit-v1.md"
SCHEMA=ROOT/"foundations/schema/foundational-scalar-minkowski-green-choice-audit-v1.schema.json"
CHECKER=ROOT/"foundations/check_scalar_minkowski_green_choice_audit.py"
def imports(path:Path)->set[str]:
    tree=ast.parse(path.read_text());found:set[str]=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module and node.module!="__future__":found.add(node.module.split(".")[0])
    return found
def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    value=json.loads(RESULT.read_text()) if result is None else result;text=REPORT.read_text() if report is None else report
    errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)];checker_errors,_=check(value);errors += ["checker "+e for e in checker_errors]
    result_bytes,report_bytes=generated()
    if (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode()!=result_bytes:errors.append("deterministic result drift")
    if text.encode()!=report_bytes:errors.append("deterministic report drift")
    if imports(CHECKER)!={"fractions","hashlib","json","pathlib","typing"}:errors.append("checker import boundary")
    lowered=CHECKER.read_text().lower()
    for token in ("float(","numpy","sympy","random","requests","urlopen"):
        if token in lowered:errors.append("checker forbidden token "+token)
    if value.get("dependency_tags")!=["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"]:errors.append("dependency-tag scope")
    for token in ("Scalar 1+1", "first cell", "Choice ledger", "Scope firewall", "does not establish"):
        if token not in text:errors.append("report token "+token)
    return errors,["Draft 2020-12 schema","independent rational checker","deterministic artifacts","exact P G and G P identities","exact causal support and duality","LORENTZIAN-CAUSAL scalar firewall"]
def main()->int:
    errors,checks=verify();print("FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1: "+("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:print("  - "+item)
    return bool(errors)
if __name__=="__main__":raise SystemExit(main())
