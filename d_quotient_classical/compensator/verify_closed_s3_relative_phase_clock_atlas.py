#!/usr/bin/env python3
"""Independent exact replay of the closed-S3 relative-phase quotient atlas."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


ROOT = Path(__file__).resolve().parents[2]
RAW = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_CLOCK_CONFLUX_EXPORT_V1.json"
)
RESULT = (
    ROOT
    / "d_quotient_classical/compensator/"
    "CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1.json"
)
ATLAS = ROOT / "residual_atlas/closed-s3-relative-phase-clock-fragment-v1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rat(value: Any) -> sp.Rational:
    if isinstance(value, bool) or isinstance(value, float):
        raise AssertionError("independent replay refuses inexact tokens")
    return sp.Rational(value)


def _matrix(rows: list[list[Any]], n: int, r: int) -> sp.Matrix:
    if r == 0:
        if rows != [[] for _ in range(n)]:
            raise AssertionError("zero-column shape drift")
        return sp.zeros(n, 0)
    result = sp.Matrix([[_rat(value) for value in row] for row in rows])
    if result.shape != (n, r):
        raise AssertionError("matrix shape drift")
    return result


def _inertia(matrix: sp.Matrix) -> tuple[int, int, int]:
    if matrix.rows == 0:
        return (0, 0, 0)
    polynomial = sp.Poly(matrix.charpoly().as_expr())
    negative = int(polynomial.count_roots(-sp.oo, 0))
    positive = int(polynomial.count_roots(0, sp.oo))
    return positive, negative, matrix.rows - positive - negative


def _walk_no_float(value: Any) -> None:
    if isinstance(value, float):
        raise AssertionError("float reached exact raw export")
    if isinstance(value, dict):
        for child in value.values():
            _walk_no_float(child)
    elif isinstance(value, list):
        for child in value:
            _walk_no_float(child)


def _replay_case(raw: dict[str, Any], certified: dict[str, Any]) -> None:
    n = raw["field_count"]
    r = raw["gauge_generator_count"]
    q = _matrix(raw["Q"], n, r)
    m = _matrix(raw["M"], n, n)
    rank = int(q.rank())
    diagonal = smith_normal_form(q, domain=ZZ)
    factors = [abs(int(diagonal[i, i])) for i in range(rank)]

    smith = certified["smith"]
    u = _matrix(smith["U"], n, n)
    v = _matrix(smith["V"], r, r)
    d = _matrix(smith["D"], n, r)
    if (
        rank != certified["rank"]
        or factors != smith["invariant_factors"]
        or u * q * v != d
        or abs(int(u.det())) != 1
        or (r and abs(int(v.det())) != 1)
    ):
        raise AssertionError(f"Smith replay failed: {raw['case_id']}")

    lattices = certified["lattices"]
    j = _matrix(lattices["primitive_image_lattice_basis_J"], n, rank)
    relative_dimension = n - rank
    b = _matrix(
        lattices["relative_tangent_lattice_basis_B"], n, relative_dimension
    )
    character = _matrix(
        lattices["relative_character_lattice_basis_N"], n, relative_dimension
    )
    if (
        q.T * character != sp.zeros(r, relative_dimension)
        or character.T * j != sp.zeros(relative_dimension, rank)
        or character.T * b != sp.eye(relative_dimension)
        or int(j.rank()) != rank
        or int(character.rank()) != relative_dimension
    ):
        raise AssertionError(f"lattice replay failed: {raw['case_id']}")
    if rank:
        expected_qv = j * sp.diag(*factors)
    else:
        expected_qv = sp.zeros(n, 0)
    if r > rank:
        expected_qv = expected_qv.row_join(sp.zeros(n, r - rank))
    if q * v != expected_qv:
        raise AssertionError(f"primitive image replay failed: {raw['case_id']}")

    pi = (
        sp.zeros(0, 1)
        if relative_dimension == 0
        else sp.Matrix([_rat(value) for value in raw["relative_momentum_coordinates_Pi"]])
    )
    p = character * pi
    if q.T * p != sp.zeros(r, 1):
        raise AssertionError(f"Gauss replay failed: {raw['case_id']}")
    a = character.T * m.inv() * character
    inertia = _inertia(a)
    recorded = certified["kinetic_restriction"]
    if recorded["A_inertia"] != {
        "positive": inertia[0],
        "negative": inertia[1],
        "zero": inertia[2],
    }:
        raise AssertionError(f"inertia replay failed: {raw['case_id']}")
    expected_sign = (
        "NOT_APPLICABLE_ZERO_DIMENSION"
        if relative_dimension == 0
        else "DEGENERATE_DIRAC_REQUIRED"
        if inertia[2]
        else "POSITIVE"
        if inertia[0] == relative_dimension
        else "NEGATIVE"
        if inertia[1] == relative_dimension
        else "INDEFINITE_KREIN"
    )
    if recorded["sign_status"] != expected_sign:
        raise AssertionError(f"sign replay failed: {raw['case_id']}")
    velocity = m.inv() * p
    relative_velocity = character.T * velocity
    raw_d = (p.T * velocity)[0]
    if (
        str(raw_d) != certified["moment_maps"]["raw_D_per_unit_volume"]
        or raw_d != (pi.T * relative_velocity)[0]
    ):
        raise AssertionError(f"moment-map replay failed: {raw['case_id']}")
    finite = [factor for factor in factors if factor > 1]
    finite_order = 1
    for factor in finite:
        finite_order *= factor
    stabilizer = certified["orbit_and_stabilizer"]
    if (
        stabilizer["compact_gauge_orbit_dimension"] != rank
        or stabilizer["continuous_stabilizer_dimension"] != r - rank
        or stabilizer["finite_stabilizer_invariant_factors"] != finite
        or stabilizer["finite_stabilizer_order"] != finite_order
        or stabilizer["relative_phase_torus_dimension"] != relative_dimension
        or stabilizer["original_torus_action_faithful"]
        != (r == rank and not finite)
    ):
        raise AssertionError(f"stabilizer replay failed: {raw['case_id']}")


def verify() -> None:
    raw = json.loads(RAW.read_text())
    result = json.loads(RESULT.read_text())
    atlas = json.loads(ATLAS.read_text())
    _walk_no_float(raw)
    allowed_case_keys = {
        "case_id",
        "field_count",
        "gauge_generator_count",
        "input_class",
        "Q",
        "M",
        "relative_momentum_coordinates_Pi",
    }
    forbidden_oracles = set(raw["oracle_exclusion"]["excluded_fields"])
    for case in raw["cases"]:
        if set(case) != allowed_case_keys or set(case) & forbidden_oracles:
            raise AssertionError("raw export oracle exclusion failed")
    if result["conflux_export"]["raw_export_sha256"] != _sha(RAW):
        raise AssertionError("raw export hash drifted")
    for imported in result["imports"]:
        source = json.loads((ROOT / imported["path"]).read_text())
        if (
            _sha(ROOT / imported["path"]) != imported["sha256"]
            or source["result_id"] != imported["result_id"]
            or source["result_state"] != imported["result_state"]
        ):
            raise AssertionError("predecessor import drifted")

    raw_by_id = {item["case_id"]: item for item in raw["cases"]}
    exact_by_id = {item["case_id"]: item for item in result["exact_cases"]}
    if set(raw_by_id) != set(exact_by_id) or len(raw_by_id) != 19:
        raise AssertionError("exact case census drifted")
    for case_id in sorted(raw_by_id):
        _replay_case(raw_by_id[case_id], exact_by_id[case_id])

    expected_strata = {
        (2, 0, "n2_rank0"),
        (2, 1, "n2_rank1_primitive"),
        (2, 1, "n2_rank1_nonprimitive"),
        (2, 2, "n2_rank2_primitive"),
        (2, 2, "n2_rank2_nonprimitive"),
        (3, 0, "n3_rank0"),
        (3, 1, "n3_rank1_primitive"),
        (3, 1, "n3_rank1_nonprimitive"),
        (3, 2, "n3_rank2_primitive"),
        (3, 2, "n3_rank2_nonprimitive"),
        (3, 3, "n3_rank3_primitive"),
        (3, 3, "n3_rank3_nonprimitive"),
    }
    actual_strata = {
        (item["field_count"], item["rank"], item["stratum_id"])
        for item in result["strata"]
    }
    if actual_strata != expected_strata:
        raise AssertionError("rank/stabilizer stratum coverage failed")
    for item in result["strata"]:
        dimension = item["field_count"] - item["rank"]
        if (
            item["relative_phase_torus_dimension"] != dimension
            or item["zero_charge_fibre_dimension"] != dimension
            or item["nonzero_physical_relative_momentum_exists"] != (dimension > 0)
        ):
            raise AssertionError("stratum quotient formula drifted")

    evidence_sha = _sha(RESULT)
    if len(atlas["entries"]) != 12:
        raise AssertionError("atlas fragment stratum count drifted")
    for entry in atlas["entries"]:
        if (
            entry["descriptions"]["symplectic"] != "CERTIFIED"
            or entry["descriptions"]["causal"] != "NO_CERTIFIED_MAP"
            or entry["descriptions"]["quantum"] != "NO_CERTIFIED_MAP"
            or entry["evidence"][0]["sha256"] != evidence_sha
        ):
            raise AssertionError("atlas claim boundary drifted")
    if (
        result["conflux_export"]["certified_conflux_map"]
        or result["conflux_export"]["lifecycle_status"]
        != "NO_CERTIFIED_CONFLUX_IMPORTER"
        or result["claim_flags"]["CONFLUX_IDENTIFICATION"]
        or result["claim_flags"]["PHYSICAL_RESIDUAL_MODE"]
        or result["claim_flags"]["FULL_BV_OR_CAUSAL_PARENT"]
    ):
        raise AssertionError("forbidden lifecycle promotion")
    print("CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1 independent exact replay: PASS")


if __name__ == "__main__":
    verify()
