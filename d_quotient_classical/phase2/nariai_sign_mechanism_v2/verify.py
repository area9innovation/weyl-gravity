#!/usr/bin/env python3
"""Independent verifier for the Nariai opposite-residue mechanism.

This rail never imports the producer.  It reimports the frozen certificates,
reconstructs all exact matrices, rederives the factor gap, curvature-channel
identity, solution-projector polynomial identities, and branch residues, and
then audits the static-patch and claim-boundary declarations.
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
CERTIFICATE = HERE / "NARIAI_SIGN_MECHANISM_V2.json"
SCHEMA = HERE / "nariai-sign-mechanism-v2.schema.json"
ATLAS = ROOT / "residual_atlas/phase2-sign-nariai-mechanism-v2-fragment-v1.json"
EXPECTED_IMPORTS = {
    "d_quotient_classical/certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json": "1dcc5e83f6942b3598930b8ffe206bc8ff0b0f821d74b9925ad61e5db9b8267d",
    "d_quotient_classical/certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json": "3333074f4a7b94b9d36ce9d20927155fa61b1541f02b152cfd179e8e50f76dcc",
    "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json": "5d755293ffbe32585fb1d6afc4ccb3643784306236e4b456777040858f5266bc",
    "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json": "e2978cf23f577ab365729d139c8eabf0bcbc2277bc2a124d872c03c94b7b8a75",
    "d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json": "0e7774b93f54d5cdc45385b5b119d7508173622fb0d4a7ca93618738971ac2ff",
}


class IndependentNariaiVerificationError(RuntimeError):
    """Raised when the independent exact audit rejects a payload."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IndependentNariaiVerificationError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dense(serialized: dict[str, Any]) -> sp.Matrix:
    rows, cols = serialized["shape"]
    matrix = sp.zeros(rows, cols)
    for row, col, value in serialized["entries"]:
        matrix[row, col] = sp.Rational(value)
    return matrix


def verify_payload(payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    _require(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash drift")
    _require(payload["result_id"] == "NARIAI_SIGN_MECHANISM_V2", "result-id drift")
    _require(
        payload["result_state"] == "STATIC_PATCH_OPPOSITE_LEE_WALD_RESIDUE_MECHANISM_EXACT",
        "result state drift",
    )

    imports = {entry["path"]: entry["sha256"] for entry in payload["provenance"]["imported_artifacts"]}
    _require(imports == EXPECTED_IMPORTS, "import ledger changed")
    for path, expected_hash in EXPECTED_IMPORTS.items():
        _require(_sha256(ROOT / path) == expected_hash, f"input hash drift: {path}")

    frozen = _load(ROOT / "d_quotient_classical/certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json")
    invariant_einstein = _load(ROOT / "d_quotient_classical/certificates/EINSTEIN_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json")
    _require(
        invariant_einstein["result_state"] == "EINSTEIN_BACKGROUND_FOUR_ROW_METRIC_CAUSAL_GREEN_HOMOTOPY_EXACT",
        "invariant Einstein factor authority changed",
    )
    source = frozen["metric_factorization"]
    _require(source["factors_commute"] is True, "source factor commutation lost")
    _require(source["factors_are_G_H_formally_self_adjoint"] is True, "source adjoint property lost")
    source_a, source_b = _dense(source["factor_a_matrix"]), _dense(source["factor_b_matrix"])
    serialized = payload["exact_factorization_and_projectors"]
    a, b = _dense(serialized["factor_a_matrix"]), _dense(serialized["factor_b_matrix"])
    _require(a == source_a and b == source_b, "serialized factor matrices changed")
    identity = sp.eye(9)
    gap = sp.Rational(2, 3)
    _require(b == a - gap * identity, "independent factor-gap check failed")
    _require(serialized["factor_definitions"]["scalar_gap_L_E_minus_L_C"] == "2/3", "declared gap changed")

    channels = serialized["curvature_channels"]
    projectors = [_dense(item) for item in channels["projectors"]]
    _require(channels["ordered_names"] == ["intrafactor_tracefree", "relative_trace", "mixed"], "channel order changed")
    _require(channels["ranks"] == [4, 1, 4], "channel ranks changed")
    _require(channels["A_eigenvalues"] == ["-2", "2", "0"], "curvature eigenvalues changed")
    _require(sum(projectors, sp.zeros(9)) == identity, "projector completeness failed")
    for index, projector in enumerate(projectors):
        _require(projector**2 == projector, f"projector {index} idempotence failed")
        _require(projector.rank() == (4, 1, 4)[index], f"projector {index} rank failed")
        for other_index, other in enumerate(projectors):
            if index != other_index:
                _require(projector * other == sp.zeros(9), "projector orthogonality failed")
    _require(a == -2 * projectors[0] + 2 * projectors[1], "curvature-action reconstruction failed")

    solution = serialized["solution_space_projectors"]
    _require(solution["Pi_E"] == "-(3/2)L_C", "Einstein projector formula changed")
    _require(solution["Pi_C"] == "(3/2)L_E", "complementary projector formula changed")
    # Polynomial identities follow in Q[x]/(x(x-gap)).  x=L_E, L_C=x-gap.
    x = sp.symbols("x")
    product = sp.expand(x * (x - gap))
    pi_e = -sp.Rational(3, 2) * (x - gap)
    pi_c = sp.Rational(3, 2) * x
    for expression in (pi_e + pi_c - 1, pi_e**2 - pi_e, pi_c**2 - pi_c, pi_e * pi_c):
        _require(sp.rem(sp.Poly(sp.expand(expression), x), sp.Poly(product, x)).as_expr() == 0, "solution-projector identity failed")
    _require(solution["lift_or_mode_choice_used"] is False, "raw lift/mode choice was introduced")

    theorem = payload["static_patch_residue_theorem"]
    structure = theorem["sign_structure"]
    _require(structure["choice"] == "STATIC_PATCH_WITH_HORIZON_FLUX_BOUNDARIES", "invalid sign structure")
    _require(structure["norm_g_H_H"] == "-(1-r^2)", "static Killing norm changed")
    _require(structure["boundary_components"] == ["r=-1 Killing horizon", "r=+1 Killing horizon"], "horizon boundary ledger changed")
    _require(structure["global_timelike_generator_claimed"] is False, "global timelike promotion")
    _require("Both horizon fluxes are retained" in structure["horizon_flux_policy"], "horizon flux omission")

    current = theorem["lee_wald_concomitant"]
    residue_e = -sp.Rational(1, 2) * gap
    residue_c = sp.Rational(1, 2) * gap
    _require(sp.Rational(current["Einstein_residue_multiplier"]) == residue_e == -sp.Rational(1, 3), "Einstein residue changed")
    _require(sp.Rational(current["complementary_residue_multiplier"]) == residue_c == sp.Rational(1, 3), "complementary residue changed")
    _require(current["opposite_nonzero_residues"] is True and residue_e * residue_c < 0, "opposite residue theorem lost")
    _require(current["applies_to"] == ["static-patch slice term", "r=-1 horizon flux", "r=+1 horizon flux"], "flux application ledger changed")

    classification = payload["classification"]
    for key in (
        "Einstein_factor_identified",
        "complementary_factor_identified",
        "invariant_solution_projectors_constructed",
        "lee_wald_residue_multipliers_exact",
        "opposite_residue_mechanism_established",
    ):
        _require(classification[key] is True, f"established flag lost: {key}")
    for key in (
        "global_timelike_killing_used",
        "horizon_boundaries_omitted",
        "zero_horizon_flux_assumed",
        "same_Weyl_Maxwell_family_claimed",
        "real_symplectic_inertia_claimed",
        "positive_energy_claimed",
        "Hadamard_state_constructed",
        "quantum_unitarity_claimed",
    ):
        _require(classification[key] is False, f"forbidden promotion: {key}")
    _require(theorem["mechanism"]["same_Weyl_Maxwell_family_as_phase1"] is False, "false family identification")
    _require(payload["next_gate"]["disposition"] == "DONE_SCOPED_MECHANISM_THEOREM", "close-out changed")


def verify_atlas(payload: dict[str, Any]) -> None:
    atlas = _load(ATLAS)
    _require(len(atlas["entries"]) == 1, "atlas entry count changed")
    entry = atlas["entries"][0]
    _require(entry["evidence"][0]["sha256"] == _sha256(CERTIFICATE), "atlas evidence hash drift")
    _require(entry["evidence"][0]["result_id"] == payload["result_id"], "atlas result-id drift")
    _require(entry["descriptions"]["absolute_energy_sign"] == "NOT_ESTABLISHED", "atlas overpromotion")


def mutated(payload: dict[str, Any], path: tuple[Any, ...], value: Any) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    cursor: Any = result
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
    print("independent Nariai sign-mechanism verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
