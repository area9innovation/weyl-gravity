"""Independent verifier for the Schouten corner zero-mode obstruction."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/ASYMPTOTIC_BACH_SCHOUTEN_CORNER_ZERO_MODE_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/asymptotic-bach-schouten-corner-zero-mode-obstruction-v1.schema.json"
ATLAS = ROOT / "residual_atlas/einstein-asymptotic-bach-schouten-corner-zero-mode-fragment-v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def verify() -> None:
    certificate = _load(CERTIFICATE)
    schema = _load(SCHEMA)
    atlas = _load(ATLAS)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    assert certificate["schema_sha256"] == _sha256(SCHEMA)
    for reference in certificate["provenance"]["inputs"].values():
        path = ROOT / reference["path"]
        assert _sha256(path) == reference["sha256"]
        assert _load(path)["result_id"] == reference["result_id"]

    order = certificate["exact_finite_jet_witness"]["order"]
    derivative = sp.zeros(order, order + 1)
    for row in range(order):
        derivative[row, row + 1] = row + 1
    assert derivative.rank() == order
    assert derivative.nullspace() == [sp.eye(order + 1)[:, 0]]
    selector = sp.zeros(1, order + 1)
    selector[0, 0] = 1
    completed = selector.col_join(derivative)
    assert completed.det() == math.factorial(order)
    assert certificate["exact_finite_jet_witness"]["one_component_corner_completed_determinant"] == str(math.factorial(order))
    assert certificate["exact_finite_jet_witness"]["two_tracefree_components_completed_rank"] == 2 * (order + 1)
    assert certificate["exact_finite_jet_witness"]["one_corner_component_missing_rank"] == 2 * (order + 1) - 1

    flags = certificate["classification"]
    assert flags["principal_Bondi_auxiliary_relation_certified"] is True
    assert flags["retarded_advanced_mismatch_certified"] is True
    assert flags["two_component_corner_kernel_certified"] is True
    assert flags["minimal_bulk_Schouten_pair_nondegenerate_with_memory"] is False
    assert flags["conjugate_corner_momentum_constructed"] is False
    assert flags["P0_charge_computed"] is False
    assert flags["D_M_charge_computed"] is False

    entry = atlas["entries"][0]
    assert entry["id"] == "einstein.asymptotic.minkowski.weyl.schouten_corner_zero_mode"
    assert entry["descriptions"]["symplectic"] == "OBSTRUCTED"
    assert entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE)


if __name__ == "__main__":
    verify()
    print("ASYMPTOTIC_BACH_SCHOUTEN_CORNER_ZERO_MODE_OBSTRUCTION_V1 independent verification: PASS")
