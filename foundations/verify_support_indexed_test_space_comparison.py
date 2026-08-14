#!/usr/bin/env python3
"""Fail-closed verifier for the support-indexed test-space comparison."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from foundations.build_support_indexed_test_space_comparison import generated
from foundations.check_support_indexed_test_space_comparison import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1.json"
REPORT = ROOT / "foundations/reports/support-indexed-test-space-comparison-v1.md"
SCHEMA = ROOT / "foundations/schema/foundational-support-indexed-test-space-comparison-v1.schema.json"
CHECKER = ROOT / "foundations/check_support_indexed_test_space_comparison.py"

def imports(path: Path) -> set[str]:
    tree=ast.parse(path.read_text()); found:set[str]=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module and node.module!="__future__": found.add(node.module.split(".")[0])
    return found

def verify(*,result:dict|None=None,report:str|None=None)->tuple[list[str],list[str]]:
    value=json.loads(RESULT.read_text()) if result is None else result; text=REPORT.read_text() if report is None else report
    errors=["schema "+e.message for e in Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)]
    checker_errors,_=check(value); errors += ["checker "+e for e in checker_errors]
    result_bytes,report_bytes=generated()
    if (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode()!=result_bytes: errors.append("deterministic result drift")
    if text.encode()!=report_bytes: errors.append("deterministic report drift")
    if imports(CHECKER)!={"fractions","hashlib","json","pathlib","typing"}: errors.append("checker import boundary")
    lowered=CHECKER.read_text().lower()
    for token in ("float(","numpy","sympy","random","requests","urlopen"):
        if token in lowered: errors.append("checker forbidden token "+token)
    for token in ("Support-indexed", "plain language", "not established", "excluded", "does not establish"):
        if token not in text: errors.append("report token "+token)
    return errors,["Draft 2020-12 schema","independent exact checker","deterministic artifacts","six name roundtrips","15 stage inclusions","LF/H2 boundary"]

def main()->int:
    errors,checks=verify(); print("FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1: "+("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors: print("  - "+item)
    return bool(errors)

if __name__=="__main__": raise SystemExit(main())
