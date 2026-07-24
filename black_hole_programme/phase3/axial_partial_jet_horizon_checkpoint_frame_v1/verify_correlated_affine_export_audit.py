#!/usr/bin/env python3
"""Independent verifier for the correlated-affine export audit."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "correlated-affine-export-audit-certificate.json"
SCHEMA = HERE / "correlated-affine-export-audit-schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_node(path: Path, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"missing function {name} in {path}")


def assigned_names(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
    }


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    if certificate["status"] != "RERUN_FROM_SYMBOLIC_SEED_REQUIRED":
        raise SystemExit("status drift")

    for row in certificate["imports"].values():
        path = ROOT / row["path"]
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"import hash drift: {path}")
    for row in certificate["sources"].values():
        path = ROOT / row["path"]
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"source hash drift: {path}")

    transport_path = HERE / "checkpoint_transport.py"
    step = function_node(transport_path, "taylor_step")
    seed = function_node(transport_path, "seed_vector")
    transport_text = transport_path.read_text()
    if "expression.subs(moving.W, sp.Rational(OMEGA))" not in transport_text:
        raise SystemExit("fixed-frequency substitution not independently found")
    if "coefficients" not in assigned_names(step):
        raise SystemExit("local Taylor coefficients not found")
    if "result = [inflate(value, tail) for value in result]" not in transport_text:
        raise SystemExit("componentwise remainder collapse not found")
    if "inflate" not in {
        child.func.id
        for child in ast.walk(seed)
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
    }:
        raise SystemExit("componentwise seed inflation not found")
    run = json.loads((HERE / "shared-remainder-multipanel-successor-run.json").read_text())
    last = run["checkpoint_chain"][-1]
    if "correlated_state" in last:
        raise SystemExit("last checkpoint unexpectedly contains correlated state")
    if certificate["terminal"]["successor_substep_attempted"]:
        raise SystemExit("successor attempt overclaim")
    if (
        certificate["rerun_export_contract"]["earliest_required_restart"]["rho"]
        != "1/4194304"
    ):
        raise SystemExit("earliest restart drift")
    print("horizon correlated-affine export audit verifier: PASS")


if __name__ == "__main__":
    main()
