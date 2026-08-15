#!/usr/bin/env python3
"""Independent exact checker for the portable Bach-flat local q1 AST."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from local_q1_bach_flat import (
    DEGREES,
    PARITIES,
    SYMBOLS,
    LocalQ1Error,
    digest,
    exact_fixture_record,
    standard_backgrounds,
    validate_ast,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
TRUE_FLAGS = {
    "PORTABLE_LOCAL_Q1_AST_CERTIFIED",
    "Q1_SQUARED_ZERO_CERTIFIED",
    "BACH_FLAT_BACKGROUND_HYPOTHESIS_EXPLICIT",
}
FALSE_FLAGS = {
    "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED",
    "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED",
    "BV_CYCLICITY_Q1_REPLAYED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("result_state") != "PORTABLE_Q1_AND_Q1_SQUARED_CERTIFIED_ARITY_TWO_IDENTITY_OPEN":
        errors.append("result state drift")
    if value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("lifecycle or dependency boundary drift")
    if value.get("convention") != "suspended-graded-symmetric-factorial-v1":
        errors.append("suspension convention drift")
    scope = value.get("scope", {})
    if scope.get("background_equation") != "E_g(gbar)=0" or "Bach-flat" not in scope.get("background_class", ""):
        errors.append("Bach-flat hypothesis missing")
    if scope.get("maximum_input_jet_order") != 4 or scope.get("maximum_noether_fixture_metric_jet_order") != 5:
        errors.append("jet-order boundary drift")

    try:
        ast = validate_ast(value.get("local_q1_ast"))
    except LocalQ1Error as exc:
        errors.append(f"local q1 AST rejected: {exc}")
        ast = {}
    components = ast.get("components", []) if isinstance(ast, dict) else []
    if len(components) != 5 or ast.get("zero_output_rows") != ["c", "omega"]:
        errors.append("unary component coverage drift")

    generator_ledger = value.get("generator_ledger", [])
    expected_generators = [
        {
            "symbol": symbol,
            "local_tangent_degree": DEGREES[symbol],
            "Grassmann_parity": PARITIES[symbol],
            "q1_output_status": "ZERO" if symbol in {"c", "omega"} else "NONZERO",
        }
        for symbol in SYMBOLS
    ]
    if generator_ledger != expected_generators:
        errors.append("generator grading or q1 coverage ledger drift")

    square = value.get("square_zero_theorem", {})
    if square.get("status") != "CERTIFIED" or square.get("background_hypothesis") != "E_g(gbar)=0":
        errors.append("square-zero theorem status or hypothesis drift")
    expected_paths = [
        ("c", "h", "h_star"),
        ("omega", "h", "h_star"),
        ("h", "h_star", "c_star"),
        ("h", "h_star", "omega_star"),
        ("h_star", "c_star or omega_star", "zero"),
    ]
    if [
        (item.get("source"), item.get("intermediate"), item.get("target"))
        for item in square.get("compositions", [])
    ] != expected_paths or any(
        item.get("result") != "ZERO" for item in square.get("compositions", [])
    ):
        errors.append("square-zero composition ledger drift")
    if len(square.get("derivation", [])) != 4 or "away" not in square.get("derivation", ["", "", "", ""])[-1]:
        errors.append("off-shell boundary missing from square-zero derivation")

    records = square.get("exact_fixture_records", [])
    backgrounds = standard_backgrounds()
    if [item.get("background") for item in records] != [item[0] for item in backgrounds]:
        errors.append("exact fixture background inventory drift")
    else:
        for stored, (name, background, vector_seed, scalar_seed, metric_seed) in zip(records, backgrounds):
            replay = exact_fixture_record(
                name,
                background,
                vector_seed=vector_seed,
                scalar_seed=scalar_seed,
                metric_seed=metric_seed,
            )
            if stored != replay:
                errors.append(f"{name}: exact q1-square fixture drift")

    checks = {item.get("check_id"): item.get("status") for item in value.get("proof_checks", [])}
    if checks != {
        "q1_component_coverage": "VERIFIED",
        "q1_cohomological_degree_one": "VERIFIED",
        "q1_squared_zero": "VERIFIED_ON_DECLARED_BACH_FLAT_NATURAL_COMPLEX",
        "q1_q2_arity_two_nilpotency": "NOT_REPLAYED",
    }:
        errors.append("proof-check ledger drift or arity-two promotion")

    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not True for flag in TRUE_FLAGS) or any(
        flags.get(flag) is not False for flag in FALSE_FLAGS
    ):
        errors.append("claim flags drift or premature promotion")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")

    expected_hashes = {
        "generator_ledger_sha256": digest(generator_ledger),
        "local_q1_ast_sha256": digest(value.get("local_q1_ast")),
        "square_zero_theorem_sha256": digest(square),
        "proof_checks_sha256": digest(value.get("proof_checks")),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for group in value.get("provenance", {}).values():
        if not isinstance(group, list):
            errors.append("provenance group is not a list")
            continue
        for item in group:
            path = ROOT / item.get("path", "")
            if not path.is_file() or file_sha(path) != item.get("sha256"):
                errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_PORTABLE_LOCAL_Q1_AST_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - five portable unary components and Bach-flat q1^2 replayed exactly")
        print("  - q1q2, D, pairing, Gate A, causal, and QME claims remain false")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
