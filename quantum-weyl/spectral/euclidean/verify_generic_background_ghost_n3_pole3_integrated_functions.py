#!/usr/bin/env python3
"""Independent exact replay of the ten integrated pole-three ghost rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_INTEGRATED_FUNCTIONS.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-pole3-integrated-functions-v1.schema.json"
RELATIVE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json"
TRIANGLE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
SYMMETRIC = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json"

X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
BASIS_IDS = ("J_triangle", "log_x2_over_x1", "log_x3_over_x1", "rational_corner")


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _poly(terms: list[dict[str, Any]]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * X1 ** term["exponents"][0]
            * X2 ** term["exponents"][1]
            * X3 ** term["exponents"][2]
            for term in terms
        )
    )


def _rf(value: dict[str, Any]) -> sp.Expr:
    return sp.cancel(_poly(value["numerator_terms"]) / _poly(value["denominator_terms"]))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _primitive_constant_terms(primitive: dict[str, Any]) -> dict[str, sp.Expr]:
    values = {"U": sp.S.Zero, "V": sp.S.Zero, "W": sp.S.Zero}
    for row in primitive["coefficients"]:
        if row["monomial_exponents"] == [0, 0]:
            values[row["group"]] += _rf(row["coefficient"])
    return {key: sp.cancel(value) for key, value in values.items()}


def verify() -> None:
    stored = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)
    relative = json.loads(RELATIVE.read_text())
    triangle = json.loads(TRIANGLE.read_text())
    symmetric = json.loads(SYMMETRIC.read_text())
    source_paths = {
        "relative_IBP": RELATIVE,
        "scalar_triangle_differential_system": TRIANGLE,
        "symmetric_point_integration": SYMMETRIC,
    }
    for dependency_id, path in source_paths.items():
        dependency = stored["dependencies"][dependency_id]
        source = json.loads(path.read_text())
        if dependency["sha256"] != _sha256(path) or dependency["result_id"] != source["result_id"]:
            raise ValueError(f"dependency drifted: {dependency_id}")

    triangle_masters = {
        master_id: {basis_id: _rf(value) for basis_id, value in row.items()}
        for master_id, row in triangle["master_rows"].items()
    }
    representative_fluxes = {}
    for representative_id, corner in stored["representative_corner_fluxes"].items():
        constants = _primitive_constant_terms(relative["representative_primitives"][representative_id])
        if sp.cancel(constants["U"] - constants["V"]) != 0:
            raise ValueError(f"independent equal-corner check failed: {representative_id}")
        expected_flux = sp.cancel(-constants["U"] / (X1 * X3))
        if sp.cancel(_rf(corner["U_C"]) - constants["U"]) != 0:
            raise ValueError(f"stored U_C drifted: {representative_id}")
        if sp.cancel(_rf(corner["V_C"]) - constants["V"]) != 0:
            raise ValueError(f"stored V_C drifted: {representative_id}")
        if sp.cancel(_rf(corner["oriented_integrated_flux"]) - expected_flux) != 0:
            raise ValueError(f"stored corner flux drifted: {representative_id}")
        representative_fluxes[representative_id] = expected_flux

    relative_rows = {row["channel_id"]: row for row in relative["channel_rows"]}
    symmetric_rows = {
        row["channel_id"]: row["integrated_value"] for row in symmetric["channel_rows"]
    }
    expressions = {}
    fixture = {X1: 1, X2: 1, X3: 1}
    for row in stored["channel_rows"]:
        channel_id = row["channel_id"]
        source = relative_rows[channel_id]
        master_coordinates = {
            master_id: _rf(value) for master_id, value in source["master_coordinates"].items()
        }
        expected = {}
        for basis_id in BASIS_IDS[:3]:
            expected[basis_id] = sp.cancel(
                (master_coordinates["J_triangle"] if basis_id == "J_triangle" else 0)
                + master_coordinates["M_x1"] * triangle_masters["M_x1"][basis_id]
                + master_coordinates["M_x2"] * triangle_masters["M_x2"][basis_id]
            )
        permutation = source["x_permutation"]
        substitution = {XS[i]: XS[permutation[i]] for i in range(3)}
        expected["rational_corner"] = sp.cancel(
            representative_fluxes[source["representative_id"]].subs(
                substitution, simultaneous=True
            )
        )
        actual = {
            basis_id: _rf(value)
            for basis_id, value in row["function_basis_coordinates"].items()
        }
        for basis_id in BASIS_IDS:
            if sp.cancel(actual[basis_id] - expected[basis_id]) != 0:
                raise ValueError(f"integrated basis coordinate drifted: {channel_id}/{basis_id}")
        regression = row["symmetric_point_regression"]
        expected_symmetric = symmetric_rows[channel_id]
        if actual["J_triangle"].subs(fixture) != _q(expected_symmetric["scalar_triangle_master_coefficient"]):
            raise ValueError(f"symmetric J regression failed: {channel_id}")
        if actual["rational_corner"].subs(fixture) != _q(expected_symmetric["rational"]):
            raise ValueError(f"symmetric rational regression failed: {channel_id}")
        if _q(regression["J_triangle_coefficient"]) != actual["J_triangle"].subs(fixture):
            raise ValueError(f"stored symmetric J coordinate drifted: {channel_id}")
        if _q(regression["rational_term"]) != actual["rational_corner"].subs(fixture):
            raise ValueError(f"stored symmetric rational coordinate drifted: {channel_id}")
        expressions[channel_id] = actual

    for basis_id in BASIS_IDS:
        defect = sp.cancel(
            expressions["I28_123"][basis_id]
            + expressions["I28_132"][basis_id]
            + expressions["I28_231"][basis_id]
        )
        if defect != 0:
            raise ValueError(f"independent integrated I28 relation failed: {basis_id}")

    payload = {
        "representative_corner_fluxes": stored["representative_corner_fluxes"],
        "channel_rows": stored["channel_rows"],
        "identity_ledger": stored["identity_ledger"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("integrated pole-three formula digest drifted")
    flags = stored["claim_flags"]
    required = (
        "TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED",
        "CORNER_ANGULAR_FLUXES_EVALUATED",
        "TWO_BUBBLE_LOG_RATIOS_EXPLICIT",
        "SYMMETRIC_POINT_REGRESSION_EXACT",
        "INTEGRATED_I28_RELATION_VERIFIED",
    )
    forbidden = (
        "I29_POLE4_REDUCED",
        "ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED",
        "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED",
        "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
        "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
        "RESIDUAL_TRANSFER_AUTHORIZED",
        "LORENTZIAN_CERTIFIED",
    )
    if not all(flags[name] for name in required) or any(flags[name] for name in forbidden):
        raise ValueError("integrated pole-three claim boundary drifted")


def main() -> int:
    verify()
    print("independent generic ghost n=3 pole-three integrated functions: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
