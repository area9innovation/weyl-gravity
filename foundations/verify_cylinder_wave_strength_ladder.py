#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from foundations.check_cylinder_wave_strength_ladder import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-cylinder-wave-strength-ladder-v1.schema.json"
REPORT = ROOT / "foundations/reports/cylinder-wave-strength-ladder.md"
CHECKER = ROOT / "foundations/check_cylinder_wave_strength_ladder.py"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            found.add(node.module.split(".")[0])
    return found


def verify(*, result=None, report=None) -> tuple[list[str], list[str]]:
    r = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    checks: list[str] = []
    schema = load(SCHEMA)
    errors.extend("schema " + error.message for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(r))
    checks.append("Draft 2020-12 schema")
    checker_errors, summary = check(r)
    errors.extend("checker " + error for error in checker_errors)
    if summary.get("digest") != r.get("independent_checker", {}).get("expected_digest"):
        errors.append("checker digest")
    if imports(CHECKER) != {"fractions", "hashlib", "json", "typing"}:
        errors.append("checker import boundary")
    lowered = CHECKER.read_text().lower()
    for forbidden in ("float(", "complex(", "numpy", "sympy", "cmath", "math", "random", "requests", "urlopen"):
        if forbidden in lowered:
            errors.append("checker forbidden token " + forbidden)
    checks.append("independent exact arithmetic rail")
    for pin in r.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    checks.append("content-pinned local inputs")
    graph = r.get("typed_relation_graph", {})
    node_ids = {node.get("id") for node in graph.get("nodes", [])}
    vocab = set(graph.get("relation_vocabulary", []))
    for edge in graph.get("edges", []):
        if edge.get("from") not in node_ids or edge.get("to") not in node_ids or edge.get("relation") not in vocab:
            errors.append("relation graph closure")
    if len(node_ids) != 12 or len(graph.get("edges", [])) != 10:
        errors.append("relation graph dimensions")
    checks.append("typed physics-to-mathematics graph")
    literature = {item.get("id"): item for item in r.get("literature_dependencies", [])}
    if set(literature) != {"weihrauch-zhong-2002", "pour-el-richards-1981"}:
        errors.append("literature identities")
    if any(item.get("artifact_status") != "METADATA_ONLY" for item in literature.values()):
        errors.append("literature pin boundary")
    local_ledger = ROOT / literature["pour-el-richards-1981"].get("local_ledger", "")
    if not local_ledger.is_file() or sha(local_ledger) != literature["pour-el-richards-1981"].get("local_ledger_sha256"):
        errors.append("Pour-El ledger pin")
    checks.append("fail-closed literature provenance")
    flags = r.get("claim_flags", {})
    for key in ("finite_cylinder_wave_exact", "explicit_tail_modulus_exact", "finite_spectral_locality_obstruction_exact", "typed_physics_to_mathematics_graph_constructed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("arbitrary_energy_completion_formalized_in_rca0", "weakest_base_proved", "choice_strength_proved", "spacetime_distribution_constructed", "causal_green_operator_constructed", "new_lorentzian_claim"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("claim boundaries")
    for token in ("six levels", "L0", "L5", "N(k)=2^k", "D_N(pi)", "representation dependence", "RCA_0", "WKL_0", "ACA_0", "METADATA_ONLY", "no new `LORENTZIAN-CAUSAL`", "coefficient-weak solution"):
        if token not in text:
            errors.append("report token " + token)
    checks.append("human-readable ladder and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
