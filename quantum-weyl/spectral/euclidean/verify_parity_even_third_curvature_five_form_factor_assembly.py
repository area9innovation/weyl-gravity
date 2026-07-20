#!/usr/bin/env python3
"""Method-distinct audit of the maximal parity-even five-form-factor result."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json"
)
SCHEMA = (
    HERE
    / "schema/parity-even-third-curvature-five-form-factor-assembly-v1.schema.json"
)
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
BASIS = (
    "J_triangle",
    "log_x2_over_x1",
    "log_x3_over_x1",
    "rational_corner",
    "M14_singlet",
    "M15_standard_u",
    "M16_standard_v",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _rational(data: dict[str, Any]) -> sp.Expr:
    def polynomial(terms: list[dict[str, Any]]) -> sp.Expr:
        return sum(
            _from_q(term["coefficient"])
            * sp.prod(variable**power for variable, power in zip(XS, term["exponents"]))
            for term in terms
        )

    return sp.cancel(
        polynomial(data["numerator_terms"]) / polynomial(data["denominator_terms"])
    )


def _scale(data: dict[str, Any]) -> sp.Expr:
    numerator = sum(
        _from_q(term["coefficient"])
        * sp.prod(variable**power for variable, power in zip(XS, term["box_exponents"]))
        for term in data["numerator_terms"]
    )
    denominator = sp.prod(
        variable**power
        for variable, power in zip(XS, data["box_denominator_exponents"])
    )
    return sp.cancel(numerator / denominator)


def _load_references(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    dependencies: dict[str, dict[str, Any]] = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash mismatch: {name}")
        payload = json.loads(path.read_text())
        if payload["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result-id mismatch: {name}")
        dependencies[name] = payload
    return dependencies


def _reconstruct_partial(
    partial: dict[str, Any],
) -> tuple[dict[str, dict[str, sp.Expr]], dict[str, sp.Expr]]:
    nested: dict[str, dict[str, Any]] = {}
    for name, reference in partial["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"nested partial dependency hash mismatch: {name}")
        nested[name] = json.loads(path.read_text())

    physical_rows = {
        row["channel_id"]: row
        for carrier in nested["physical_form_factors"]["carrier_functions"]
        for row in carrier["orientation_channels"]
    }
    triangle_rows = {
        row["channel_id"]: row for row in nested["physical_triangle"]["channel_rows"]
    }
    ghost_rows = {
        row["channel_id"]: row
        for row in nested["ghost_pole3_functions"]["channel_rows"]
    }
    ghost_rows["I29_123"] = {
        "function_basis_coordinates": nested["ghost_I29_function"][
            "function_basis_coordinates"
        ]
    }
    vector_rows = {
        row["channel_id"]: row
        for row in nested["ghost_vector_n1_n2_functions"]["channel_rows"]
    }
    expressions: dict[str, dict[str, sp.Expr]] = {}
    scales: dict[str, sp.Expr] = {}
    for output in partial["channel_rows"]:
        channel = output["channel_id"]
        combined: dict[str, sp.Expr] = {}
        for basis_id in BASIS:
            physical = (
                _rational(physical_rows[channel]["assembled_rational_coordinate"])
                if basis_id == "rational_corner"
                else _rational(
                    triangle_rows[channel]["integrated_function_basis"][basis_id]
                )
            )
            ghost = (
                _rational(
                    ghost_rows[channel]["function_basis_coordinates"][basis_id]
                )
                if basis_id in BASIS[:4]
                else 0
            )
            vector = (
                _rational(
                    vector_rows[channel]["function_basis_coordinates"][basis_id]
                )
                if basis_id in BASIS[:4]
                else 0
            )
            combined[basis_id] = sp.cancel(physical + ghost + vector)
        scale = _scale(physical_rows[channel]["combined_scale_derivative"])
        expected_digests = {
            basis_id: _digest(sp.srepr(combined[basis_id])) for basis_id in BASIS
        }
        if output["combined_coordinate_digests"] != expected_digests:
            raise ValueError(f"independent channel reconstruction failed: {channel}")
        if output["combined_scale_digest"] != _digest(sp.srepr(scale)):
            raise ValueError(f"independent scale reconstruction failed: {channel}")
        expressions[channel] = combined
        scales[channel] = scale
    return expressions, scales


def verify_value(
    value: dict[str, Any],
    *,
    validate_schema: bool = True,
) -> dict[str, Any]:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    if validate_schema:
        Draft202012Validator(schema).validate(value)
    dependencies = _load_references(value)

    manifest = dependencies["carrier_manifest"]
    h1 = dependencies["physical_H1_cubed_channels"]
    masters = dependencies["six_master_coordinates"]
    flux = dependencies["relative_IBP_boundary_flux"]
    contact = dependencies["H1_H2_contact_finite_rows"]
    partial = dependencies["maximal_partial_BV_form_factors"]
    multiplicity = dependencies["full_BV_multiplicity"]
    schur = dependencies["longitudinal_Schur_resummation"]
    scale = dependencies["longitudinal_Schur_scale"]
    round_s4 = dependencies["round_S4_holdout"]
    product_rows = dependencies["product_S2_S2_weighted_holdout"]
    product_det3 = dependencies["product_S2_S2_det3_holdout"]
    flat = dependencies["flat_TT_normalization"]

    if (
        manifest["quotient_module"]["generic_label_orbit_dimension"] != 10
        or manifest["four_dimensional_identity"]["relation_rank"] != 1
        or len(h1["projection_rows"]) != 11
        or len(masters["channel_rows"]) != 11
        or len(flux["channel_rows"]) != 11
    ):
        raise ValueError("carrier/channel completeness boundary drifted")

    expressions, scales = _reconstruct_partial(partial)
    i28 = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(expressions[channel][basis_id] for channel in i28)) != 0
        for basis_id in BASIS
    ) or sp.cancel(sum(scales[channel] for channel in i28)) != 0:
        raise ValueError("independent I28 quotient relation failed")

    maximal = value["maximal_determined_quotient"]
    if maximal["formula_digest"] != partial["formula_digest"]:
        raise ValueError("partial formula digest crosswalk failed")
    if maximal["channel_row_digests"] != {
        row["channel_id"]: _digest(row) for row in partial["channel_rows"]
    }:
        raise ValueError("channel-sign/contact assembly digest failed")
    if value["holdouts"]["equal_box_contact"]["data"] != contact[
        "equal_box_regression"
    ]:
        raise ValueError("equal-box contact holdout failed")
    if value["holdouts"]["flat_TT"]["leading_coefficient"] != flat[
        "repository_normalization"
    ]["flat_TT_leading_coefficient"]:
        raise ValueError("flat-TT normalization holdout failed")
    if value["holdouts"]["round_S4"] != {
        "status": "SPECIAL_BACKGROUND_EXACT_NOT_INTERPOLATED",
        "zero_mode_policy_applied": round_s4["claim_flags"][
            "ROUND_S4_ZERO_MODE_POLICY_APPLIED"
        ],
        "finite_rows_digest": _digest(round_s4["exact_finite_rows"]),
    }:
        raise ValueError("round-S4 specialization holdout failed")
    if value["holdouts"]["product_S2_S2"] != {
        "status": "SPECIAL_BACKGROUND_RIGOROUS_INTERVAL_NOT_INTERPOLATED",
        "weighted_rows_digest": _digest(product_rows["weighted_rows"]),
        "det3_enclosure_digest": _digest(product_det3["det3_enclosure"]),
    }:
        raise ValueError("S2xS2 specialization holdout failed")

    boundary = value["longitudinal_Schur_boundary"]
    if (
        boundary["normalized_operator"]
        != schur["exact_determinant_factorization"][
            "normalized_scalar_Schur_operator"
        ]
        or boundary["scale_response"]
        != scale["Schur_determinant_scale_row"]["scale_response"]
        or boundary["scale_density"]
        != scale["Schur_determinant_scale_row"]["Ricci_basis"]
    ):
        raise ValueError("Schur operator/scale crosswalk failed")
    if len(multiplicity["repository_factors"]) != 4 or any(
        row["status"] != "VERIFIED" for row in multiplicity["standard_factor_map"]
    ):
        raise ValueError("full-BV multiplicity ledger is not complete")

    witness = value["first_missing_analytic_datum"]["nondefinition_witness"]
    if (
        witness["status"] != "MINIMAL_MISSING_GLOBAL_CARRIER_THEOREM"
        or Fraction(witness["rank_one_fixture"].split("Delta R_Q(K)=")[1].split()[0])
        != Fraction(7, 11)
        or Fraction(witness["rank_one_fixture"].split("Delta R_Q(K^2)=")[1])
        != Fraction(126, 121)
    ):
        raise ValueError("finite-kernel nondefinition witness failed")
    contract = value["first_missing_analytic_datum"]["receiver_contract"]
    if (
        "Pi_0" not in contract["weight"]
        or not any("zero-mode projector" in item for item in contract["required_checks"])
        or not any("primed Green" in item for item in contract["required_data"])
    ):
        raise ValueError("zero-mode/Green receiver contract is incomplete")
    if any(
        item["folded_into_nonlocal_functions"] is not False
        for item in value["local_normalization_constants"].values()
    ):
        raise ValueError("local normalization was folded into a nonlocal row")
    return value


def mutation_suite(stored: dict[str, Any]) -> int:
    mutations: list[tuple[str, dict[str, Any]]] = []
    dependencies = _load_references(stored)
    partial = dependencies["maximal_partial_BV_form_factors"]
    contact = dependencies["H1_H2_contact_finite_rows"]
    scale = dependencies["longitudinal_Schur_scale"]

    mutation = deepcopy(stored)
    channel = next(iter(mutation["maximal_determined_quotient"]["channel_row_digests"]))
    mutation["maximal_determined_quotient"]["channel_row_digests"][channel] = "0" * 64
    mutations.append(("channel", mutation))

    mutation = deepcopy(stored)
    mutation["holdouts"]["equal_box_contact"]["data"]["combined_contact_finite_value"][
        "numerator"
    ] += 1
    mutations.append(("contact", mutation))

    mutation = deepcopy(stored)
    mutation["longitudinal_Schur_boundary"]["scale_density"] += " + MUTATION"
    mutations.append(("scale", mutation))

    mutation = deepcopy(stored)
    mutation["holdouts"]["round_S4"]["zero_mode_policy_applied"] = False
    mutations.append(("schema", mutation))

    mutation = deepcopy(stored)
    mutation["claim_flags"]["FULL_GENERIC_BV_FIVE_FORM_FACTORS_COMPUTED"] = True
    mutations.append(("schema", mutation))

    rejected = 0
    schema = json.loads(SCHEMA.read_text())
    for index, (kind, mutation) in enumerate(mutations):
        try:
            Draft202012Validator(schema).validate(mutation)
            if kind == "channel":
                if mutation["maximal_determined_quotient"]["channel_row_digests"] != {
                    row["channel_id"]: _digest(row) for row in partial["channel_rows"]
                }:
                    raise ValueError("channel mutation rejected")
            elif kind == "contact":
                if mutation["holdouts"]["equal_box_contact"]["data"] != contact[
                    "equal_box_regression"
                ]:
                    raise ValueError("contact mutation rejected")
            elif kind == "scale":
                if mutation["longitudinal_Schur_boundary"]["scale_density"] != scale[
                    "Schur_determinant_scale_row"
                ]["Ricci_basis"]:
                    raise ValueError("scale mutation rejected")
        except Exception:
            rejected += 1
        else:
            raise ValueError(f"mutation {index} was accepted")
    return rejected


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    verify_value(stored)
    rejected = mutation_suite(stored)
    print(
        "PARITY-EVEN THIRD-CURVATURE FIVE-FORM-FACTOR INDEPENDENT AUDIT: "
        f"PASS ({rejected} mutations rejected)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
