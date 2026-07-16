#!/usr/bin/env python3
"""Independent verifier for the axial operator-module preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator_module_preflight.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_operator_module_preflight.schema.json"


def _matrix(rows: list[list[str]], D: sp.Symbol, k: sp.Symbol) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"D": D, "k": k, "I": sp.I}) for value in row] for row in rows])


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        assert hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    D, k = sp.symbols("D k")
    row = payload["gauge_module_contraction"]
    G = _matrix(row["gauge_map_G"], D, k)
    K = _matrix(row["projection_K"], D, k)
    J = _matrix(row["slice_inclusion_J"], D, k)
    H = _matrix(row["gauge_homotopy_H"], D, k)
    assert K * G == sp.zeros(4, 2)
    assert K * J == sp.eye(4)
    assert sp.eye(6) - J * K == G * H
    assert H * G == sp.eye(2)
    assert row["denominators_introduced"] == ["2"]
    assert row["no_inverse_D"] is True and row["no_inverse_k"] is True
    rail = payload["hessian_noether_green_rail"]
    assert rail["target_operator_inserted"] is False
    assert payload["pivot_and_fixture_contract"]["ell2_independent_replay"]["completed"] is False
    assert payload["classification"]["extra_solution_or_particle_certified"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT independent verification: PASS")
