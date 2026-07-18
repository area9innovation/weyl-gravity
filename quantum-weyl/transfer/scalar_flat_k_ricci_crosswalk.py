#!/usr/bin/env python3
"""Certify the scalar-flat linear ``K_munu`` to Ricci crosswalk."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
QROOT = HERE.parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "certificates/SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK.json"
SCHEMA = HERE / "schema/scalar-flat-k-ricci-cubic-crosswalk-v1.schema.json"
DEPENDENCIES = {
    "carrier_manifest": HERE / "certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
    "ghost_triangle": QROOT / "spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json",
}


def _q(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _routing_rows(carriers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_order: dict[int, list[str]] = {}
    for row in carriers:
        by_order.setdefault(row["explicit_derivative_order"], []).append(
            row["carrier_id"]
        )
    rows = []
    for projector_count in range(4):
        derivative_orders = list(range(0, 2 * projector_count + 1, 2))
        rows.append(
            {
                "longitudinal_projector_count": projector_count,
                "possible_external_derivative_orders": derivative_orders,
                "possible_repository_carriers": [
                    carrier
                    for order in derivative_orders
                    for carrier in by_order.get(order, [])
                ],
            }
        )
    return rows


def build() -> dict[str, Any]:
    manifest = json.loads(DEPENDENCIES["carrier_manifest"].read_text())
    triangle = json.loads(DEPENDENCIES["ghost_triangle"].read_text())
    carriers = manifest["carrier_manifest"]
    carrier_ids = [row["carrier_id"] for row in carriers]
    if carrier_ids != ["I10", "I24", "I25", "I28", "I29"]:
        raise ValueError("five-carrier manifest drifted")
    if triangle["carrier_projection"]["source_candidates"] != carrier_ids:
        raise ValueError("triangle five-carrier target drifted")

    dimension = 4
    divergence_prefactor = Fraction(dimension - 3, dimension - 2)
    k_definition_prefactor = Fraction(2)
    normalized_linear_coefficient = divergence_prefactor * k_definition_prefactor
    if normalized_linear_coefficient != 1:
        raise AssertionError("K/Ricci normalization drifted")

    result = {
        "schema": "quantum-weyl-scalar-flat-k-ricci-cubic-crosswalk-v1",
        "result_id": "SCALAR_FLAT_K_RICCI_CUBIC_CROSSWALK",
        "result_state": "K_EQUALS_RICCI_MODULO_QUADRATIC_CURVATURE_ON_SCALAR_FLAT_DOMAIN",
        "lifecycle_state": "CARRIER_NORMALIZATION_CERTIFIED_FIVE_CARRIER_TENSOR_PROJECTION_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": triangle["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "background": "noncompact asymptotically flat scalar-flat conformal representative",
            "inverse_domain": "declared source complement of Box with boundary-compatible normalized inverse",
            "curvature_order": 3,
        },
        "source_convention": {
            "K_definition": "K_munu=(2/Box) nabla^beta nabla^alpha C_alpha_mu_beta_nu",
            "contracted_Weyl_identity": "nabla^alpha C_alpha_mu_beta_nu=((d-3)/(d-2))[nabla_beta Ric_munu-nabla_nu Ric_mubeta-(g_munu nabla_beta R-g_mubeta nabla_nu R)/(2(d-1))]",
            "contracted_Bianchi_identity": "nabla^beta Ric_mubeta=(1/2)nabla_mu R",
            "commutator_order": "[nabla,nabla]Ric=O(curvature^2)",
        },
        "linear_crosswalk": {
            "dimension": dimension,
            "scalar_flat_condition": "R=0",
            "Weyl_divergence_prefactor": _q(divergence_prefactor),
            "double_divergence": "nabla^beta nabla^alpha C_alpha_mu_beta_nu=(1/2)Box Ric_munu+O(curvature^2)",
            "K_definition_prefactor": _q(k_definition_prefactor),
            "normalized_linear_coefficient": _q(normalized_linear_coefficient),
            "identity": "K_munu=Ric_munu+O(curvature^2)",
            "zero_mode_boundary": "identity holds only on the declared Box inverse/source-complement domain",
        },
        "cubic_order_counting": {
            "linear_K_order": 1,
            "crosswalk_remainder_minimum_order": 2,
            "three_linear_factors_order": 3,
            "first_replacement_error_order": 4,
            "conclusion": "K1 K2 K3 may be replaced by Ric1 Ric2 Ric3 modulo O(curvature^4)",
        },
        "five_carrier_target": {
            "carrier_ids": carrier_ids,
            "derivative_orders": {
                row["carrier_id"]: row["explicit_derivative_order"]
                for row in carriers
            },
            "triangle_sector_routing": _routing_rows(carriers),
            "projection_status": "NOT_COMPUTED",
            "four_dimensional_relation_status": "IMPORTED_NOT_YET_APPLIED_TO_TRIANGLE",
        },
        "claim_flags": {
            "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED": True,
            "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED": True,
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE": True,
            "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_PROJECTION_COMPUTED": False,
            "GENERIC_GHOST_N1_N2_CURVED_ENDO_TRACES_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {
            name: _reference(path) for name, path in DEPENDENCIES.items()
        },
        "next_gate": "DECOMPOSE_GHOST_N3_PARAMETRIC_KERNEL_INTO_FIVE_CARRIERS_AND_COMPUTE_N1_N2_CURVED_ENDO_TRACES",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate fixes the normalization between the source tensor K_munu=(2/Box)nabla nabla C and the Ricci endomorphism on the declared four-dimensional scalar-flat inverse domain. The contracted Weyl identity and Bianchi identity give K_munu=Ric_munu+O(curvature^2), so replacing three K factors by three Ricci factors is exact modulo O(curvature^4). It also proves from derivative counting that the generic Endo triangle can feed all five parity-even carriers I10, I24, I25, I28 and I29. It does not perform that tensor/form-factor projection, apply the four-dimensional carrier relation to the triangle, compute the curved-Endo one- or two-insertion rows, complete the ghost or physical determinant, supply Gamma1/Q1, authorize residual transfer, or establish Lorentzian, Hadamard, positivity, particle, scattering or unitarity claims."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    crosswalk = value["linear_crosswalk"]
    if (
        crosswalk["Weyl_divergence_prefactor"] != _q(Fraction(1, 2))
        or crosswalk["K_definition_prefactor"] != _q(2)
        or crosswalk["normalized_linear_coefficient"] != _q(1)
    ):
        raise ValueError("K/Ricci normalization drifted")
    counting = value["cubic_order_counting"]
    if counting["first_replacement_error_order"] != 4:
        raise ValueError("K/Ricci cubic order counting drifted")
    target = value["five_carrier_target"]
    if target["carrier_ids"] != ["I10", "I24", "I25", "I28", "I29"]:
        raise ValueError("five-carrier target drifted")
    expected_routing = _routing_rows(
        [
            {"carrier_id": carrier, "explicit_derivative_order": order}
            for carrier, order in target["derivative_orders"].items()
        ]
    )
    if target["triangle_sector_routing"] != expected_routing:
        raise ValueError("triangle derivative routing drifted")
    flags = value["claim_flags"]
    true_flags = {
        "SCALAR_FLAT_K_RICCI_LINEAR_CROSSWALK_CERTIFIED",
        "CUBIC_K_TO_RICCI_REPLACEMENT_CERTIFIED",
        "GENERIC_GHOST_TRIANGLE_FIVE_CARRIER_TARGET_COMPLETE",
    }
    if any(flags[key] is not True for key in true_flags) or any(
        flag is not False for key, flag in flags.items() if key not in true_flags
    ):
        raise ValueError("K/Ricci crosswalk crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale scalar-flat K/Ricci crosswalk: {OUTPUT}")
    print("SCALAR-FLAT K/RICCI CROSSWALK: CUBIC NORMALIZATION CERTIFIED; FIVE-CARRIER PROJECTION OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
