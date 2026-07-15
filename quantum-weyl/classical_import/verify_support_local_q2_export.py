#!/usr/bin/env python3
"""Fail-closed preflight for a support-local classical BV q1/q2 export.

The preflight validates a portable local-polydifferential payload.  It does
not infer missing Taylor coefficients or treat finite-mode matrices as a
support-local substitute.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REQUIRED_ROLES = {
    "metric": {"ghost_number": 0, "antifield_number": 0, "Grassmann_parity": 0},
    "diffeomorphism_ghost": {
        "ghost_number": 1,
        "antifield_number": 0,
        "Grassmann_parity": 1,
    },
    "weyl_ghost": {"ghost_number": 1, "antifield_number": 0, "Grassmann_parity": 1},
    "metric_antifield": {
        "ghost_number": -1,
        "antifield_number": 1,
        "Grassmann_parity": 1,
    },
    "diffeomorphism_ghost_antifield": {
        "ghost_number": -2,
        "antifield_number": 2,
        "Grassmann_parity": 0,
    },
    "weyl_ghost_antifield": {
        "ghost_number": -2,
        "antifield_number": 2,
        "Grassmann_parity": 0,
    },
}
REQUIRED_PROOF_CHECKS = {
    "q1_squared_zero",
    "q1_q2_arity_two_nilpotency",
    "q2_koszul_symmetry",
    "q2_row_completeness",
    "D_q1_commutator_zero",
    "D_q2_derivation",
    "BV_cyclicity_q2",
}
TOP_LEVEL_FIELDS = {
    "schema",
    "classical_commit",
    "dependency_tags",
    "convention",
    "expression_schema_version",
    "support_category",
    "generators",
    "q1",
    "q2",
    "D_action",
    "proof_checks",
    "canonical_hashes",
}
GENERATOR_FIELDS = {
    "symbol",
    "role",
    "sector",
    "tensor_type",
    "ghost_number",
    "antifield_number",
    "form_degree",
    "Grassmann_parity",
    "mass_dimension",
    "Weyl_weight",
    "canonical_index_symmetry",
}
OPERATOR_FIELDS = {
    "arity",
    "degree",
    "factorial_convention",
    "components",
    "row_completeness",
}
COMPONENT_FIELDS = {
    "component_id",
    "output",
    "inputs",
    "max_jet_orders",
    "expression",
}
HASH_KEYS = {
    "support_metadata_hash",
    "generator_dictionary_hash",
    "q1_hash",
    "q2_hash",
    "D_action_hash",
    "proof_checks_hash",
}


class SupportLocalQ2ExportError(RuntimeError):
    """Raised when a purported support-local q2 export is incomplete."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SupportLocalQ2ExportError(f"cannot load support-local q2 export: {exc}") from exc
    if not isinstance(value, dict):
        raise SupportLocalQ2ExportError("support-local q2 export must be a JSON object")
    return value


def _exact_payload(value: object, path: str = "$") -> None:
    if isinstance(value, float):
        raise SupportLocalQ2ExportError(f"floating-point value forbidden at {path}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise SupportLocalQ2ExportError(f"non-string object key at {path}")
            _exact_payload(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _exact_payload(child, f"{path}[{index}]")


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_exact_number(value: object) -> bool:
    return _is_int(value) or (
        isinstance(value, dict)
        and set(value) == {"numerator", "denominator"}
        and _is_int(value["numerator"])
        and _is_int(value["denominator"])
        and value["denominator"] != 0
    )


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _verify_pinned_artifact(
    repository_root: Path,
    classical_commit: str,
    relative: str,
    expected_sha256: str,
) -> None:
    root = repository_root.resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise SupportLocalQ2ExportError(f"unsafe proof path: {relative}")
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
        working_data = path.read_bytes()
    except (ValueError, OSError) as exc:
        raise SupportLocalQ2ExportError(f"cannot read proof artifact {relative}: {exc}") from exc
    if hashlib.sha256(working_data).hexdigest() != expected_sha256:
        raise SupportLocalQ2ExportError(f"working-tree proof hash mismatch: {relative}")

    prefix = subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if prefix.returncode != 0:
        raise SupportLocalQ2ExportError("repository_root is not inside a Git worktree")
    git_relative = prefix.stdout.strip() + relative
    committed = subprocess.run(
        ["git", "show", f"{classical_commit}:{git_relative}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if committed.returncode != 0:
        raise SupportLocalQ2ExportError(
            f"proof artifact is absent at classical_commit: {relative}"
        )
    if hashlib.sha256(committed.stdout).hexdigest() != expected_sha256:
        raise SupportLocalQ2ExportError(f"classical-commit proof hash mismatch: {relative}")


def _validate_generators(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    generators = payload.get("generators")
    if not isinstance(generators, list) or len(generators) < len(REQUIRED_ROLES):
        raise SupportLocalQ2ExportError("the six minimal field/ghost/antifield roles are required")
    by_symbol: dict[str, dict[str, Any]] = {}
    by_role: dict[str, dict[str, Any]] = {}
    for generator in generators:
        if not isinstance(generator, dict) or set(generator) != GENERATOR_FIELDS:
            raise SupportLocalQ2ExportError("each generator must carry the exact required field set")
        symbol = generator["symbol"]
        if not isinstance(symbol, str) or not symbol or symbol in by_symbol:
            raise SupportLocalQ2ExportError("generator symbols must be nonempty and unique")
        by_symbol[symbol] = generator
        role = generator["role"]
        if role not in {*REQUIRED_ROLES, "other_field", "other_ghost", "other_antifield"}:
            raise SupportLocalQ2ExportError(f"{symbol}: unknown generator role")
        if role in REQUIRED_ROLES:
            if role in by_role:
                raise SupportLocalQ2ExportError(f"duplicate required role: {role}")
            by_role[role] = generator
        if generator["sector"] not in {"minimal", "nonminimal", "auxiliary"}:
            raise SupportLocalQ2ExportError(f"{symbol}: invalid sector")
        for field in ("ghost_number", "antifield_number", "form_degree"):
            if not _is_int(generator[field]):
                raise SupportLocalQ2ExportError(f"{symbol}: {field} must be an integer")
        if generator["antifield_number"] < 0 or not 0 <= generator["form_degree"] <= 4:
            raise SupportLocalQ2ExportError(f"{symbol}: invalid antifield or form degree")
        if generator["Grassmann_parity"] not in {0, 1}:
            raise SupportLocalQ2ExportError(f"{symbol}: invalid Grassmann parity")
        for field in ("mass_dimension", "Weyl_weight"):
            if not _is_exact_number(generator[field]):
                raise SupportLocalQ2ExportError(f"{symbol}: {field} must be exact")
        for field in ("tensor_type", "canonical_index_symmetry"):
            if not isinstance(generator[field], dict) or not generator[field]:
                raise SupportLocalQ2ExportError(f"{symbol}: {field} must be a nonempty object")

    missing = set(REQUIRED_ROLES) - set(by_role)
    if missing:
        raise SupportLocalQ2ExportError(f"missing minimal roles: {sorted(missing)}")
    for role, expected in REQUIRED_ROLES.items():
        generator = by_role[role]
        if generator["sector"] != "minimal":
            raise SupportLocalQ2ExportError(f"{role} must be in the minimal sector")
        for field, value in expected.items():
            if generator[field] != value:
                raise SupportLocalQ2ExportError(f"{role}: expected {field}={value}")
    return by_symbol


def _validate_operator(
    name: str,
    operator: object,
    *,
    arity: int,
    degree: int,
    generators: dict[str, dict[str, Any]],
) -> int:
    if not isinstance(operator, dict) or set(operator) != OPERATOR_FIELDS:
        raise SupportLocalQ2ExportError(f"{name} has the wrong field set")
    if operator["arity"] != arity or operator["degree"] != degree:
        raise SupportLocalQ2ExportError(f"{name} has the wrong arity or degree")
    if operator["factorial_convention"] != "suspended-graded-symmetric-factorial-v1":
        raise SupportLocalQ2ExportError(f"{name} has the wrong Taylor convention")
    components = operator["components"]
    rows = operator["row_completeness"]
    if not isinstance(components, list) or not isinstance(rows, list):
        raise SupportLocalQ2ExportError(f"{name} components and row ledger must be lists")
    if name == "q2" and not components:
        raise SupportLocalQ2ExportError("q2 must contain at least one local component")

    component_ids: set[str] = set()
    component_outputs: dict[str, str] = {}
    for component in components:
        if not isinstance(component, dict) or set(component) != COMPONENT_FIELDS:
            raise SupportLocalQ2ExportError(f"{name} component has the wrong field set")
        component_id = component["component_id"]
        if not isinstance(component_id, str) or not component_id or component_id in component_ids:
            raise SupportLocalQ2ExportError(f"{name} component ids must be nonempty and unique")
        component_ids.add(component_id)
        output = component["output"]
        inputs = component["inputs"]
        jets = component["max_jet_orders"]
        if output not in generators or not isinstance(inputs, list) or len(inputs) != arity:
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: unknown output or wrong inputs")
        if any(symbol not in generators for symbol in inputs):
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: unknown input symbol")
        if not isinstance(jets, list) or len(jets) != arity or any(
            not _is_int(order) or order < 0 for order in jets
        ):
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: invalid jet orders")
        if not isinstance(component["expression"], dict) or not component["expression"]:
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: expression is missing")
        output_parity = generators[output]["Grassmann_parity"]
        input_parity = sum(generators[symbol]["Grassmann_parity"] for symbol in inputs)
        output_degree = generators[output]["ghost_number"]
        input_degree = sum(generators[symbol]["ghost_number"] for symbol in inputs)
        if output_degree - input_degree != degree:
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: cohomological degree violation")
        if (output_parity - input_parity - degree) % 2:
            raise SupportLocalQ2ExportError(f"{name}/{component_id}: parity degree violation")
        component_outputs[component_id] = output

    row_outputs: set[str] = set()
    referenced: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"output", "status", "component_ids"}:
            raise SupportLocalQ2ExportError(f"{name} row ledger is malformed")
        output = row["output"]
        if output not in generators or output in row_outputs:
            raise SupportLocalQ2ExportError(f"{name} row outputs must be known and unique")
        row_outputs.add(output)
        if row["status"] != "COMPLETE":
            raise SupportLocalQ2ExportError(f"{name}/{output}: row is not COMPLETE")
        ids = row["component_ids"]
        if not isinstance(ids, list) or len(ids) != len(set(ids)):
            raise SupportLocalQ2ExportError(f"{name}/{output}: component ids are malformed")
        for component_id in ids:
            if component_id not in component_outputs or component_outputs[component_id] != output:
                raise SupportLocalQ2ExportError(f"{name}/{output}: component reference mismatch")
            if component_id in referenced:
                raise SupportLocalQ2ExportError(f"{name}: component referenced more than once")
            referenced.add(component_id)
    if row_outputs != set(generators):
        raise SupportLocalQ2ExportError(f"{name} row ledger does not cover every generator")
    if referenced != component_ids:
        raise SupportLocalQ2ExportError(f"{name} row ledger omits components")
    return len(components)


def validate_export(
    payload: dict[str, Any],
    *,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    """Validate exactness, locality metadata, complete rows, proofs, and hashes."""

    _exact_payload(payload)
    if set(payload) != TOP_LEVEL_FIELDS:
        raise SupportLocalQ2ExportError("support-local q2 export has the wrong top-level field set")
    if payload.get("schema") != "quantum-weyl-support-local-q2-export-v1":
        raise SupportLocalQ2ExportError("unsupported support-local q2 export schema")
    commit = payload.get("classical_commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise SupportLocalQ2ExportError("classical_commit must be a full lowercase Git id")
    if payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        raise SupportLocalQ2ExportError("support-local q2 export must be LOCAL-ALGEBRAIC only")
    if payload.get("convention") != "suspended-graded-symmetric-factorial-v1":
        raise SupportLocalQ2ExportError("unsupported Taylor convention")
    if not isinstance(payload.get("expression_schema_version"), str) or not payload[
        "expression_schema_version"
    ]:
        raise SupportLocalQ2ExportError("expression_schema_version is required")

    support = payload.get("support_category")
    support_fields = {
        "spacetime_dimension",
        "background_id",
        "boundary_conditions",
        "locality",
        "test_function_space",
        "integration_by_parts_quotient",
        "maximum_jet_order",
    }
    if not isinstance(support, dict) or set(support) != support_fields:
        raise SupportLocalQ2ExportError("support_category has the wrong field set")
    if support["spacetime_dimension"] != 4:
        raise SupportLocalQ2ExportError("support-local conformal gravity export must be four-dimensional")
    if support["locality"] != "SUPPORT_LOCAL_POLYDIFFERENTIAL":
        raise SupportLocalQ2ExportError("finite-mode or endpoint data are not support-local q2")
    for field in ("background_id", "boundary_conditions", "test_function_space"):
        if not isinstance(support[field], str) or not support[field]:
            raise SupportLocalQ2ExportError(f"support_category.{field} is required")
    if not isinstance(support["integration_by_parts_quotient"], bool):
        raise SupportLocalQ2ExportError("integration_by_parts_quotient must be boolean")
    if not _is_int(support["maximum_jet_order"]) or support["maximum_jet_order"] < 0:
        raise SupportLocalQ2ExportError("maximum_jet_order must be a nonnegative integer")

    generators = _validate_generators(payload)
    counts = {
        "q1": _validate_operator("q1", payload["q1"], arity=1, degree=1, generators=generators),
        "q2": _validate_operator("q2", payload["q2"], arity=2, degree=1, generators=generators),
        "D_action": _validate_operator(
            "D_action", payload["D_action"], arity=1, degree=0, generators=generators
        ),
    }

    checks = payload.get("proof_checks")
    if not isinstance(checks, list):
        raise SupportLocalQ2ExportError("proof_checks must be a list")
    check_ids = [check.get("check_id") for check in checks if isinstance(check, dict)]
    if len(check_ids) != len(checks) or set(check_ids) != REQUIRED_PROOF_CHECKS:
        raise SupportLocalQ2ExportError("proof check inventory is incomplete or duplicated")
    for check in checks:
        if set(check) != {"check_id", "status", "proof_artifact"} or check["status"] != "VERIFIED":
            raise SupportLocalQ2ExportError(f"{check.get('check_id')}: proof check is not VERIFIED")
        proof = check["proof_artifact"]
        if not isinstance(proof, dict) or set(proof) != {"path", "sha256"}:
            raise SupportLocalQ2ExportError(f"{check['check_id']}: malformed proof artifact")
        path = proof["path"]
        digest = proof["sha256"]
        if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise SupportLocalQ2ExportError(f"{check['check_id']}: unsafe proof path")
        if not isinstance(digest, str) or len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise SupportLocalQ2ExportError(f"{check['check_id']}: malformed proof digest")
        if repository_root is not None:
            _verify_pinned_artifact(repository_root, commit, path, digest)

    hashes = payload.get("canonical_hashes")
    if not isinstance(hashes, dict) or set(hashes) != HASH_KEYS:
        raise SupportLocalQ2ExportError("canonical_hashes has the wrong key set")
    expected_hashes = {
        "support_metadata_hash": _digest(
            {
                "convention": payload["convention"],
                "expression_schema_version": payload["expression_schema_version"],
                "support_category": payload["support_category"],
            }
        ),
        "generator_dictionary_hash": _digest(payload["generators"]),
        "q1_hash": _digest(payload["q1"]),
        "q2_hash": _digest(payload["q2"]),
        "D_action_hash": _digest(payload["D_action"]),
        "proof_checks_hash": _digest(payload["proof_checks"]),
    }
    if hashes != expected_hashes:
        raise SupportLocalQ2ExportError("canonical support-local q2 hashes do not reproduce")

    return {
        "status": "PREFLIGHT_VERIFIED",
        "classical_commit": commit,
        "support_category": support,
        "generator_count": len(generators),
        "component_counts": counts,
        "proof_checks": sorted(REQUIRED_PROOF_CHECKS),
        "proof_artifact_integrity_status": (
            "VERIFIED" if repository_root is not None else "NOT_CHECKED"
        ),
        "canonical_hashes": hashes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    parser.add_argument("--repository-root", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate_export(_load(args.export), repository_root=args.repository_root)
    except SupportLocalQ2ExportError as exc:
        print(f"SUPPORT_LOCAL_Q2_EXPORT_FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
