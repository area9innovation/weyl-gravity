#!/usr/bin/env python3
"""Independent consumer for exceptional/global off-shell chain maps."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-exceptional-global-offshell-chain-maps-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix(value: list[list[str]], k: sp.Symbol, omega: sp.Symbol) -> sp.Matrix:
    local = {"k": k, "omega": omega, "I": sp.I}
    return sp.Matrix([[sp.sympify(entry, locals=local) for entry in row] for row in value])


def _zero(matrix: sp.MatrixBase) -> bool:
    return matrix.applyfunc(lambda value: sp.factor(sp.expand(value))) == sp.zeros(matrix.rows, matrix.cols)


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for reference in value["dependency_refs"].values():
        path = ROOT / reference["path"]
        if not path.is_file() or _sha256(path) != reference["sha256"]:
            raise AssertionError(f"dependency drifted: {reference['path']}")

    k, omega = sp.symbols("k omega", real=True)
    for label, block in value["blocks"].items():
        maps = {name: _matrix(matrix, k, omega) for name, matrix in block["maps"].items()}
        source_dimensions = block["source_dimensions"]
        target_dimensions = block["target_dimensions"]
        expected_shapes = {
            "source_gauge": (source_dimensions[1], source_dimensions[0]),
            "target_gauge": (target_dimensions[1], target_dimensions[0]),
            "source_euler": (source_dimensions[2], source_dimensions[1]),
            "target_euler": (target_dimensions[2], target_dimensions[1]),
            "source_noether": (source_dimensions[3], source_dimensions[2]),
            "target_noether": (target_dimensions[3], target_dimensions[2]),
            "ghost_map": (target_dimensions[0], source_dimensions[0]),
            "field_map": (target_dimensions[1], source_dimensions[1]),
            "equation_map": (target_dimensions[2], source_dimensions[2]),
            "identity_map": (target_dimensions[3], source_dimensions[3]),
        }
        for name, shape in expected_shapes.items():
            if maps[name].shape != shape:
                raise AssertionError(f"{label} {name} shape changed: {maps[name].shape} != {shape}")
        adjoint = lambda matrix: matrix.subs({omega: -omega, k: -k}, simultaneous=True).T
        defects = (
            maps["source_euler"] * maps["source_gauge"],
            maps["source_noether"] * maps["source_euler"],
            maps["target_euler"] * maps["target_gauge"],
            maps["target_noether"] * maps["target_euler"],
            maps["target_gauge"] * maps["ghost_map"] - maps["field_map"] * maps["source_gauge"],
            maps["target_euler"] * maps["field_map"] - maps["equation_map"] * maps["source_euler"],
            maps["target_noether"] * maps["equation_map"] - maps["identity_map"] * maps["source_noether"],
        )
        if not all(_zero(defect) for defect in defects):
            raise AssertionError(f"{label} independent chain replay failed")
        for matrix in maps.values():
            if any(not sp.denom(entry).is_number for entry in matrix):
                raise AssertionError(f"{label} contains a differential inverse")
        if not _zero(maps["target_euler"] - adjoint(maps["target_euler"])):
            raise AssertionError(f"{label} target action-coordinate adjoint replay failed")
        if block["formal_adjoint_audit"]["source"] == "PASS_IN_IDENTITY_ACTION_COORDINATES" and not _zero(maps["source_euler"] - adjoint(maps["source_euler"])):
            raise AssertionError(f"{label} source action-coordinate adjoint replay failed")

    ell0 = value["blocks"]["polar_ell0"]
    ell0_maps = {name: _matrix(matrix, k, omega) for name, matrix in ell0["maps"].items()}
    expected_vector = sp.Matrix([k**2, 2 * k * omega, omega**2, k**2 - omega**2])
    if not _zero(ell0_maps["target_euler"][:4, :4] - expected_vector * expected_vector.T / 2):
        raise AssertionError("ell=0 direct Weyl rank-one Hessian anchor changed")
    if ell0_maps["source_euler"][3, 3] != k**2 - omega**2 - 2:
        raise AssertionError("ell=0 Einstein lower-order anchor changed")
    if ell0_maps["identity_map"][3, :] != sp.zeros(1, 3):
        raise AssertionError("ell=0 Weyl identity is no longer relatively null")

    axial = value["blocks"]["axial_ell1"]
    axial_maps = {name: _matrix(matrix, k, omega) for name, matrix in axial["maps"].items()}
    if axial_maps["source_gauge"][:, 0] != sp.Matrix([-sp.I * omega, sp.I * k, 0, 0, 1]):
        raise AssertionError("axial diffeomorphism incidence changed")
    if axial_maps["source_gauge"][:, 1] != sp.Matrix([0, 0, -sp.I * omega, sp.I * k, 1]):
        raise AssertionError("axial U(1) incidence changed")

    flags = value["classification"]
    if not flags["all_harmonic_sector_coefficient_maps_available"]:
        raise AssertionError("coefficient coverage was dropped")
    if flags["single_covariant_support_local_map_reconstructed"] or flags["EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_certified"]:
        raise AssertionError("global support-local triangle was over-promoted")
    return {"result_id": value["result_id"], "blocks_replayed": sorted(value["blocks"]), "status": "PASS"}


if __name__ == "__main__":
    receipt = verify()
    print(f"{receipt['result_id']} independent verification: {receipt['status']}")
