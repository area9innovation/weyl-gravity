#!/usr/bin/env python3
"""Verifier for the bounded low-hanging foundations-cell closure audit."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.check_low_hanging_cell_closure import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1.json"
SCHEMA = ROOT / "foundations/schema/foundational-low-hanging-cell-closure-audit-v1.schema.json"
REPORT = ROOT / "foundations/reports/low-hanging-cell-closure-audit.md"
CUBE = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
CHECKER = ROOT / "foundations/check_low_hanging_cell_closure.py"
MODE = ROOT / "foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json"
H04 = ROOT / "quantum-weyl/local_bv/cohomology/H04_GAUGE_FIXED_BV_RESULT.json"
H14 = ROOT / "quantum-weyl/local_bv/cohomology/H14_GAUGE_FIXED_BV_RESULT.json"
CONTRACTION = ROOT / "quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json"
IMPORT_GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_CERTIFICATE.json"
COMPATIBILITY = ROOT / "quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
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


def verify(
    *,
    result: dict[str, Any] | None = None,
    report: str | None = None,
    cube: dict[str, Any] | None = None,
    mode: dict[str, Any] | None = None,
    h04: dict[str, Any] | None = None,
    h14: dict[str, Any] | None = None,
    contraction: dict[str, Any] | None = None,
    import_gate: dict[str, Any] | None = None,
    compatibility: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    result = load(RESULT) if result is None else result
    report = REPORT.read_text() if report is None else report
    cube = load(CUBE) if cube is None else cube
    mode = load(MODE) if mode is None else mode
    h04 = load(H04) if h04 is None else h04
    h14 = load(H14) if h14 is None else h14
    contraction = load(CONTRACTION) if contraction is None else contraction
    import_gate = load(IMPORT_GATE) if import_gate is None else import_gate
    compatibility = load(COMPATIBILITY) if compatibility is None else compatibility
    errors: list[str] = []
    checks: list[str] = []

    schema = load(SCHEMA)
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(result)
    except Exception as exc:
        errors.append("schema " + str(exc).splitlines()[0])
    checks.append("Draft 2020-12 schema")

    if (
        result.get("result_id") != "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
        or result.get("lifecycle") != "SEPARATED"
        or result.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
    ):
        errors.append("identity/lifecycle/dependency tags")
    checks.append("scope-audit identity and dependency boundary")

    for pin in result.get("provenance", {}).get("inputs", []):
        path = ROOT / pin.get("path", "")
        if not path.is_file() or sha256(path) != pin.get("sha256"):
            errors.append("provenance " + str(pin.get("path")))
    checks.append("six content-pinned source artifacts")

    for source, ghost, representatives in (
        (h04, 0, ["CT_C2", "CT_E4", "CT_C_DUAL_C"]),
        (h14, 1, ["ANOM_OMEGA_C2", "ANOM_OMEGA_E4", "ANOM_OMEGA_C_DUAL_C"]),
    ):
        if (
            source.get("result_state") != "GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE"
            or source.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
            or source.get("regularity_scope") != "REGULAR_BACH_LOCUS"
            or source.get("ghost_number") != ghost
            or source.get("form_degree") != 4
            or source.get("claim_flags", {}).get("COHOMOLOGY_COMPLETE") is not True
            or [item.get("representative_id") for item in source.get("classes", [])] != representatives
        ):
            errors.append("local cohomology source H" + str(ghost) + "4")
    flags = contraction.get("claim_flags", {})
    if (
        contraction.get("result_state") != "FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN"
        or flags.get("FULL_BV_G2_COMPLETE") is not True
        or flags.get("H04_GAUGE_FIXED_BV_COMPLETE") is not True
        or flags.get("H14_GAUGE_FIXED_BV_COMPLETE") is not True
        or flags.get("QME_RESTORED") is not False
        or flags.get("LORENTZIAN_QUANTUM_THEORY") is not False
    ):
        errors.append("local-BV contraction source/boundary")
    checks.append("completed H04/H14 and gauge-fixing contraction on regular Bach locus")

    if (
        import_gate.get("gate_a_status") != "FAIL_CLOSED"
        or import_gate.get("publishable_quantum_results_allowed") is not False
        or not import_gate.get("blocked_or_failed_freeze_checks")
    ):
        errors.append("classical import gate was not preserved fail-closed")
    if compatibility.get("compatibility", {}).get("status") != "CONTENT_HASH_COMPATIBLE":
        errors.append("local/analytic snapshot compatibility")
    checks.append("local result separated from failed broader classical freeze gate")

    if mode.get("result_id") != "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1":
        errors.append("mode dynamics source identity")
    finite = dict(mode.get("finite_exact_witness", {}))
    finite.pop("energy_representative_multiplicity", None)
    finite.pop("fixed_energy_matrix_units", None)
    finite.pop("nontrivial_degree_matrix_units", None)
    finite.pop("nontrivial_example", None)
    expected_finite = dict(result.get("finite_dynamics_evidence", {}))
    expected_finite.pop("source_result", None)
    expected_finite.pop("axis_separation", None)
    if finite != expected_finite:
        errors.append("finite dynamics source witness")
    checks.append("finite exact dynamics inherited from certified mode group")

    checker_errors, summary = check(result)
    errors.extend("checker " + item for item in checker_errors)
    if imports(CHECKER) != {"hashlib", "json", "pathlib", "typing"}:
        errors.append("checker import boundary")
    lowered = CHECKER.read_text().lower()
    for forbidden in ("numpy", "sympy", "float(", "random", "urlopen", "requests"):
        if forbidden in lowered:
            errors.append("checker forbidden token " + forbidden)
    if summary.get("assessed_open_after") != 22:
        errors.append("checker summary")
    checks.append("independent exact structural rail")

    cube_cells = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation")): item
        for item in cube.get("cells", [])
    }
    for promotion in result.get("promotions", []):
        coordinate = tuple(promotion.get(key) for key in ("foundation", "carrier", "obligation"))
        cell = cube_cells.get(coordinate, {})
        if cell.get("status") != "LOCAL_RESULT" or result.get("result_id") not in cell.get("evidence", []):
            errors.append("promotion not applied " + "/".join(str(value) for value in coordinate))
    declared_remaining = {
        (item.get("foundation"), item.get("carrier"), item.get("obligation"), item.get("status"))
        for item in result.get("remaining_assessed_open_cells", [])
    }
    actual_remaining = {
        (cell.get("foundation"), cell.get("carrier"), cell.get("obligation"), cell.get("status"))
        for cell in cube.get("cells", [])
        if cell.get("status") in {"PIECES_ONLY", "PRIORITY_GAP"}
    }
    if declared_remaining != actual_remaining:
        errors.append("remaining open-cell ledger is not exhaustive")
    checks.append("three applied promotions and exhaustive post-promotion open ledger")

    claim_flags = result.get("claim_flags", {})
    for key in (
        "three_existing_result_closures_identified",
        "local_bv_cohomology_imported_with_scope",
        "local_counterterm_anomaly_classes_imported_with_scope",
        "finite_cutoff_dynamics_imported_with_scope",
        "remaining_assessed_open_cells_exhaustively_triaged",
    ):
        if claim_flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "classical_freeze_gate_passed", "qme_restored", "lorentzian_certified",
        "all_216_cells_assessed", "remaining_cells_impossible",
    ):
        if claim_flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("bounded closure and fail-closed flags")

    for token in (
        "Three corrections, not three new theories",
        "regular Bach locus",
        "freeze gate remains failed",
        "continuum comparison belongs to reconstruction",
        "22 assessed open cells remain",
        "157 not-mapped cells",
        "LOCAL-ALGEBRAIC",
        "LORENTZIAN-CAUSAL",
    ):
        if token not in report:
            errors.append("report token " + token)
    checks.append("human report decisions and boundaries")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
