#!/usr/bin/env python3
"""Verifier for the energy-2 PRA sufficiency and avoidance certificate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_free_bv_energy2_primitive import check


RESULT_PATH = ROOT / "foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json"
SCHEMA_PATH = ROOT / "foundations/schema/foundational-free-bv-energy2-pra-sdr-v1.schema.json"
REPORT_PATH = ROOT / "foundations/reports/free-bv-energy2-pra-sdr.md"
CHECKER_PATH = ROOT / "foundations/check_free_bv_energy2_primitive.py"
SOURCE_CERTIFICATE_PATH = ROOT / "bridge/certificates/free_bv_complex.json"
SOURCE_LEDGER_PATH = ROOT / "symbolic/conformal-paper-verification.sha256"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_HASH = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__":
            modules.add(node.module.split(".")[0])
    return modules


def dag_is_acyclic(nodes: set[str], edges: list[dict[str, Any]]) -> bool:
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for edge in edges:
        source, target = edge.get("from"), edge.get("to")
        if source not in nodes or target not in nodes:
            return False
        outgoing[source].append(target)
        indegree[target] += 1
    ready = [node for node, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited == len(nodes)


def verify(
    *,
    result: dict[str, Any] | None = None,
    source_certificate: dict[str, Any] | None = None,
    report_text: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []
    if result is None:
        result = load_json(RESULT_PATH)
    if source_certificate is None:
        source_certificate = load_json(SOURCE_CERTIFICATE_PATH)
    if report_text is None:
        report_text = REPORT_PATH.read_text(encoding="utf-8")
    load_json(SCHEMA_PATH)
    checks.append("schema, result, source certificate, and report parse")

    if result.get("result_id") != "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1":
        errors.append("result id mismatch")
    if result.get("result_kind") != "FOUNDATIONAL_DEPENDENCY_CERTIFICATE":
        errors.append("result kind mismatch")
    if result.get("lifecycle") != "SUFFICIENCY_PROVED":
        errors.append("lifecycle is not the bounded SUFFICIENCY_PROVED state")
    if result.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("dependency tag must be LOCAL-ALGEBRAIC only")
    if not GIT_HASH.fullmatch(result.get("repository_base_commit", "")):
        errors.append("repository base commit is not a full hash")
    context = result.get("programme_context", {})
    if context.get("coverage_matrix") != "FOUNDATIONAL_COVERAGE_MATRIX_V0":
        errors.append("coverage-matrix predecessor mismatch")
    expected_opportunities = {
        "OP-EXACT-BV-WEAK-BASELINE",
        "OP-SEPARATION-WITNESS-CROSSWALK",
    }
    if set(context.get("opportunities_realized", [])) != expected_opportunities:
        errors.append("realized opportunity links mismatch")
    if context.get("disposition") != "FIRST_BOUNDED_CASE_COMPLETED":
        errors.append("programme disposition mismatch")
    checks.append("identity, bounded lifecycle, tag, base provenance, and programme links")

    foundational = result.get("foundational_classification", {})
    if foundational.get("base_theory") != "PRA":
        errors.append("named weak base is not PRA")
    if foundational.get("relation") != "SUFFICIENT_OVER_BASE":
        errors.append("sufficiency relation drifted")
    if foundational.get("status") != "PROVED_FOR_FIXED_WITNESS":
        errors.append("sufficiency scope drifted")
    if foundational.get("minimality_status") != "NOT_CLAIMED":
        errors.append("minimality was promoted")
    if foundational.get("necessity_status") != "NOT_PROVED":
        errors.append("necessity was promoted")
    if foundational.get("formal_proof_assistant_encoding") != "NOT_SUPPLIED":
        errors.append("formal proof assistant status drifted")
    checks.append("PRA sufficiency is separated from minimality and necessity")

    avoidance = result.get("avoidance_classification", {})
    if avoidance.get("relation") != "AVOIDED_BY_REFORMULATION":
        errors.append("avoidance relation drifted")
    if avoidance.get("status") != "PROVED_FOR_DISPLAYED_CERTIFICATE":
        errors.append("avoidance scope drifted")
    avoided = set(avoidance.get("apparent_dependencies_avoided", []))
    for required in ("Hahn-Banach theorem", "Zorn lemma", "rank or nullspace computation"):
        if required not in avoided:
            errors.append(f"missing avoidance control: {required}")
    if not avoidance.get("precise_boundary"):
        errors.append("avoidance result lacks a precise boundary")
    checks.append("explicit-SDR avoidance relation and controls")

    primitive_errors, summary = check(result)
    errors.extend(f"primitive checker: {error}" for error in primitive_errors)
    expected_digest = result.get("independent_checker", {}).get("expected_matrix_digest")
    if summary.get("matrix_digest") != expected_digest or not SHA256.fullmatch(str(expected_digest)):
        errors.append("expanded matrix digest mismatch")
    if summary.get("cohomology_rank_from_explicit_sdr") != 10:
        errors.append("primitive checker did not retain ten physical coordinates")
    if not all(summary.get("identity_checks", {}).values()):
        errors.append("not every SDR identity passed")
    checks.append("dependency-minimal sparse integer checker and matrix digest")

    permitted = set(result.get("independent_checker", {}).get("permitted_runtime_modules", []))
    actual_imports = imported_modules(CHECKER_PATH)
    if actual_imports != permitted:
        errors.append(f"checker imports {sorted(actual_imports)} but permits {sorted(permitted)}")
    checker_source = CHECKER_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ("import sympy", "import numpy", ".rank(", ".nullspace(", "float("):
        if forbidden in checker_source:
            errors.append(f"primitive checker contains forbidden operation token: {forbidden}")
    checks.append("checker independence and forbidden-operation guard")

    module = result.get("module", {})
    source_level = next(
        (level for level in source_certificate.get("levels", []) if level.get("energy") == 2),
        None,
    )
    if source_level is None:
        errors.append("source certificate has no energy-2 level")
    else:
        if source_level.get("full_dimension") != module.get("full_dimension"):
            errors.append("source and foundational full dimensions differ")
        if source_level.get("cohomology_dimension") != module.get("reduced_dimension"):
            errors.append("source and foundational reduced dimensions differ")
        source_fields = [(field.get("name"), field.get("dimension")) for field in source_level.get("fields", [])]
        result_fields = [(field.get("name"), field.get("dimension")) for field in module.get("field_slices", [])]
        if source_fields != result_fields:
            errors.append("source and foundational field layouts differ")
    checks.append("compact witness agrees with published energy-2 metadata")

    for item in result.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        expected = item.get("sha256")
        if not path.is_file():
            errors.append(f"missing provenance input: {item.get('path')}")
        elif not SHA256.fullmatch(str(expected)) or sha256(path) != expected:
            errors.append(f"provenance hash mismatch: {item.get('path')}")
    checks.append("all upstream content hashes")

    source_ledger = SOURCE_LEDGER_PATH.read_text(encoding="utf-8")
    required_ledger_lines = (
        "015d829312c2d4337d6dc4a2212e4ab81a5ec699a1e8c79c76c3fe5128ce4bde  bridge/certificates/free_bv_complex.json",
        "482a6998ce35fb0ef56ce574cba107c51e00505243722930a78bd2949b4b20e8  symbolic/verify_conformal_free_bv_complex.py",
    )
    for line in required_ledger_lines:
        if line not in source_ledger:
            errors.append(f"source content ledger missing line: {line}")
    checks.append("pre-existing source verification ledger agrees")

    dag = result.get("proof_dependency_dag", {})
    node_ids = [node.get("id") for node in dag.get("nodes", [])]
    if len(node_ids) != len(set(node_ids)) or not node_ids:
        errors.append("DAG node ids are missing or duplicated")
    if not dag_is_acyclic(set(node_ids), dag.get("edges", [])):
        errors.append("proof dependency graph is cyclic or has dangling edges")
    required_kinds = {
        "DECLARED_DATA",
        "PRIMITIVE_RECURSIVE_CHECK",
        "INTEGER_MATRIX_IDENTITY",
        "COHOMOLOGY_CONSEQUENCE",
        "SCALAR_EXTENSION",
        "AVOIDANCE_CONSEQUENCE",
    }
    if not required_kinds <= {node.get("kind") for node in dag.get("nodes", [])}:
        errors.append("proof DAG omits a required dependency kind")
    checks.append("acyclic proof-dependency DAG and consequence separation")

    flags = result.get("claim_flags", {})
    required_true = {
        "fixed_energy2_integer_sdr_verified",
        "pra_sufficiency_for_fixed_checker",
        "hahn_banach_avoided_for_displayed_certificate",
    }
    required_false = {
        "weakest_base_proved",
        "necessity_or_reversal_proved",
        "all_energy_bv_classified",
        "classical_import_freeze",
        "choice_free_infinite_completion",
        "constructive_weyl_qft",
        "lorentzian_claim",
    }
    for flag in required_true:
        if flags.get(flag) is not True:
            errors.append(f"bounded result flag is not true: {flag}")
    for flag in required_false:
        if flags.get(flag) is not False:
            errors.append(f"claim flag must fail closed: {flag}")
    if len(result.get("does_not_establish", [])) < 6:
        errors.append("global claim boundary is too small")
    checks.append("bounded positive flags and fail-closed promotions")

    for token in (
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1",
        "SUFFICIENT_OVER_BASE",
        "AVOIDED_BY_REFORMULATION",
        "Primitive Recursive Arithmetic",
        "Hahn--Banach",
        "q^2=0",
        "jp=1-qh-hq",
        "LOCAL-ALGEBRAIC",
        "not the weakest",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report_text:
            errors.append(f"report missing required token: {token}")
    checks.append("human report mirrors theorem, relations, and boundaries")

    return errors, checks


def main() -> int:
    errors, checks = verify()
    if errors:
        print("FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1: PASS ({len(checks)}/{len(checks)} checks)")
    for item in checks:
        print(f"  - {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
