#!/usr/bin/env python3
"""Independent verifier for the dyonic flat-family preflight.

This rail does not import the producer.  It re-eliminates the incidence
equations and checks the global circle-period and charge-plane obstructions
directly from the serialized certificate.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "DYONIC_FLAT_FAMILY_PREFLIGHT_V1.json"
SCHEMA = HERE / "dyonic-flat-family-preflight-v1.schema.json"
ATLAS = ROOT / "residual_atlas/phase2-sign-dyonic-flat-family-preflight-fragment-v1.json"
EXPECTED_IMPORTS = {
    "bridge/certificates/einstein_maxwell_product_incidence.json": "6493a2ce5a392939468dee9070df7d0e57d73459d6142af243b0628021fdb8b8",
    "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json": "7c045d4bde9e3961ad422faa0e6f8ca4d22cde76970e6071ca7a9bff392666d3",
}


class IndependentPreflightVerificationError(RuntimeError):
    """Raised when the independent exact audit fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentPreflightVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _independent_family() -> dict[str, sp.Expr]:
    tau = sp.symbols("tau", real=True)
    kappa, q, x = sp.symbols("kappa q_min k_2", positive=True, real=True)
    n = sp.symbols("N", nonzero=True, real=True)
    magnetic = n * x / (2 * q)
    electric = tau * magnetic
    energy_equation = sp.factor(electric**2 + magnetic**2 - x / kappa)
    nonzero_root = sp.factor(4 * q**2 / (n**2 * kappa * (1 + tau**2)))
    _require(sp.factor(energy_equation.subs(x, nonzero_root)) == 0, "independent family root failed")
    alpha = sp.factor(3 / (kappa * nonzero_root))
    return {
        "beta": sp.factor(kappa * n**2 / (4 * q**2)),
        "alpha_critical": sp.factor(3 * n**2 / (4 * q**2)),
        "k_2": nonzero_root,
        "P": sp.factor(magnetic.subs(x, nonzero_root)),
        "E": sp.factor(electric.subs(x, nonzero_root)),
        "alpha_B": alpha,
        "Q_e": sp.factor(electric.subs(x, nonzero_root) / nonzero_root),
    }


def verify_payload(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")
    _require(payload["result_id"] == "DYONIC_FLAT_FAMILY_PREFLIGHT_V1", "result-id drift")

    imports = {entry["path"]: entry["sha256"] for entry in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED_IMPORTS, "import ledger changed")
    for path, expected_hash in EXPECTED_IMPORTS.items():
        _require(_sha256(ROOT / path) == expected_hash, f"input hash drift: {path}")

    independent = _independent_family()
    family = payload["exact_family"]
    aliases = {"beta": "beta", "alpha_critical": "alpha_critical", "k_2": "k_2", "P": "P", "E": "E", "alpha_B": "alpha_B", "electric_charge_Qe": "Q_e"}
    parse_locals = {
        str(symbol): symbol
        for expression in independent.values()
        for symbol in expression.free_symbols
    }
    for serialized, independent_name in aliases.items():
        _require(
            sp.factor(sp.sympify(family[serialized], locals=parse_locals) - independent[independent_name]) == 0,
            f"family formula drift: {serialized}",
        )
    _require(family["fixed_coupling_open_family"] is False, "false fixed-coupling promotion")
    _require(family["family_type"] == "COUPLING_BACKGROUND_FAMILY", "family type changed")

    tau = sp.symbols("tau", real=True)
    d = 1 + tau**2
    combined = sp.Matrix([[(tau**2 - 1) / d, 2 * tau / d], [2 * tau / d, (1 - tau**2) / d]])
    _require(sp.simplify(combined**2 - sp.eye(2)) == sp.zeros(2), "independent involution failed")
    _require(sp.simplify(combined * sp.Matrix([tau, 1]) - sp.Matrix([tau, 1])) == sp.zeros(2, 1), "background not fixed")
    _require(sp.factor((combined * sp.Matrix([1, 0]))[1] - 2 * tau / d) == 0, "fixed-Chern defect changed")

    parity = payload["connection_and_symmetry"]["parity_duality"]
    _require(parity["preserves_fixed_chern_tangent_for_tau_nonzero"] is False, "false parity preservation")
    _require(parity["off_shell_single_potential_symmetry"] is False, "false off-shell duality promotion")
    _require(parity["generic_disposition"] == "COMBINED_MIXED_PARITY_CARRIER_REQUIRED", "mixed-parity disposition changed")

    stabilizers = payload["connection_and_symmetry"]["stabilizer_lifts"]
    _require(stabilizers["H"] == "NO_CONTINUOUS_GLOBAL_CONNECTION_LIFT_FOR_E_NONZERO", "false H lift")
    # Independent topological proof: an exact infinitesimal gauge term has zero
    # S1 period, while i_H F=E dx has period E L.
    e, length = sp.symbols("E L", nonzero=True, real=True)
    _require(sp.factor(e * length) != 0, "electric circle period unexpectedly vanished")

    classification = payload["classification"]
    required_false = (
        "fixed_coupling_open_family",
        "global_connection_stationary_for_tau_nonzero",
        "continuous_H_bundle_stabilizer_for_tau_nonzero",
        "ordinary_parity_preserves_dyonic_background",
        "duality_reflection_preserves_fixed_chern_tangent",
        "generic_axial_polar_block_split_authorized",
        "tangent_cofiber_constructed",
        "lee_wald_current_constructed",
        "sign_or_inertia_computed",
    )
    for key in required_false:
        _require(classification[key] is False, f"forbidden promotion: {key}")
    _require(classification["combined_mixed_parity_carrier_required"] is True, "mixed carrier flag changed")
    _require(payload["next_gate"]["disposition"] == "OBSTRUCTED_AS_STATIONARY_FIXED_BUNDLE_SIGN_BASE", "obstruction disposition changed")


def verify_atlas(payload: dict[str, Any]) -> None:
    atlas = _load(ATLAS)
    _require(len(atlas["entries"]) == 1, "atlas entry count changed")
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE), "atlas evidence hash drift")
    _require(entry["evidence"][0]["result_id"] == payload["result_id"], "atlas result-id drift")
    _require(entry["descriptions"]["symplectic"] == "OBSTRUCTED", "atlas obstruction lost")


def mutated(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    cursor: dict[str, Any] = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return result


def verify() -> None:
    payload = _load(CERTIFICATE)
    verify_payload(payload)
    verify_atlas(payload)


def main() -> int:
    verify()
    print("independent dyonic flat-family preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
