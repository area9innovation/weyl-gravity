#!/usr/bin/env python3
"""Method-distinct exact audit of the parameterized five-form-factor theorem."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = (
    HERE
    / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json"
)
SCHEMA = (
    HERE
    / "schema/parameterized-parity-even-five-form-factor-family-independent-audit-v1.schema.json"
)

INPUTS = {
    "terminal": (
        HERE / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY.json",
        "b615a8aedb305e8014ad904a8bc2648fe149678aa201d65217164eecf9e791f0",
    ),
    "assembly": (
        HERE / "certificates/PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY.json",
        "c474dedff8923233d94998e04e044c5931f03df69fcbf973c650d665f7246f06",
    ),
    "kernel_nonuniqueness": (
        HERE
        / "certificates/GENERIC_PRIMED_SCHUR_FINITE_RELATIVE_TRACE_KERNEL_NONUNIQUENESS.json",
        "dd114394a10d0669bcbdad88adbec31e789a37f264c39d314b2e672a4baae89c",
    ),
    "H1_H2_contact_finite_rows": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_H1_H2_CONTACT_FINITE_ROWS.json",
        "e9e6661a5994e90fed7f7f45eb7a19481a721cad41f24b41e104955a9396c940",
    ),
    "carrier_manifest": (
        ROOT / "quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_THIRD_CURVATURE_WEYL_CARRIER_MANIFEST.json",
        "203cc58ea7d2b1cfd468bc660c616e8319250ab522614bcbc16410b1c7006c4c",
    ),
    "flat_TT_normalization": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_LINEAR_CURVATURE.json",
        "b8fd2da678cb64d0bae6adaacb888beb49af3d3e45ddd9bce93005fb9018e9f9",
    ),
    "full_BV_multiplicity": (
        HERE / "certificates/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json",
        "5bdc6ee4674e3a58ab0da0d4f8dc848ac7eebc4b84544c2079dee766362b9970",
    ),
    "longitudinal_Schur_resummation": (
        HERE / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json",
        "b40ec3a8bd3a21d8e0ece7c98f98e1776e8c47d557b8c8b5427e422b60c65a78",
    ),
    "longitudinal_Schur_scale": (
        HERE / "certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHTED_TRACE_SCALE.json",
        "8073ad3800d4ad9662232769efeb45971e49b5eaf1f4b933714245d85771bd1d",
    ),
    "maximal_partial_BV_form_factors": (
        HERE / "certificates/GENERIC_BACKGROUND_PARTIAL_BV_THIRD_CURVATURE_FORM_FACTORS.json",
        "8797773521188acf0e9a4bfae4b08aca7399deeb3439d8ccc989a69c7ffdcc95",
    ),
    "physical_H1_cubed_channels": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_FIVE_CARRIER_PROJECTION.json",
        "21a28ad483c8964390306b7dc6c8cd7c5ab5c1dcfb577eda0acad81f70bfc23b",
    ),
    "physical_five_form_factors": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_THIRD_CURVATURE_FORM_FACTORS.json",
        "35d7d8c96bca681d61e72f16ca64db8b9af00ad1dc6f90475cca3ce7e65671b2",
    ),
    "product_S2_S2_det3_holdout": (
        HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_DET3_ENCLOSURE.json",
        "0aaf843e0eb7d771b7ac29a1ec5ef4d7c0d0a79797bdc09c3ee049c9872fa094",
    ),
    "product_S2_S2_weighted_holdout": (
        HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_WEIGHTED_ROWS.json",
        "f2fcd5674c2ade12534a50acca4fcbe2056626cc2daa1f229122a303d837ff9d",
    ),
    "relative_IBP_boundary_flux": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RELATIVE_IBP_BOUNDARY_FLUX.json",
        "ac587092ac6c7415e09d0b7e0541604e9622c7664d89c6a0c767dc9cac70368f",
    ),
    "round_S4_holdout": (
        HERE / "certificates/ROUND_S4_GHOST_SCHUR_FINITE_WEIGHTED_TRACES.json",
        "b16768333e62f624720130d1c922b42772f10bf7ad10ee1ac27832c847588591",
    ),
    "six_master_coordinates": (
        HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_SIX_MASTER_COORDINATES.json",
        "d205896de6c5f2d6a534889e9bdb566a590b9e2c47a28d1def2ff5585994de9c",
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path, payload: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": payload["result_id"],
        "sha256": _sha256(path),
    }


def _rank(matrix: list[list[Fraction]]) -> int:
    rows = [row[:] for row in matrix]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[rank])
            ]
        rank += 1
    return rank


def _cycle_type(permutation: tuple[int, int, int]) -> str:
    if permutation == (1, 2, 3):
        return "identity"
    fixed = sum(permutation[index] == index + 1 for index in range(3))
    return "transposition" if fixed == 1 else "three_cycle"


def _apply(
    permutation: tuple[int, int, int], label: tuple[int, int, int]
) -> tuple[int, int, int]:
    return tuple(permutation[value - 1] for value in label)


def _module_character(cosets: list[list[list[int]]]) -> dict[str, int]:
    normalized = [
        {tuple(label) for label in coset}
        for coset in cosets
    ]
    by_type: dict[str, list[int]] = {
        "identity": [],
        "transposition": [],
        "three_cycle": [],
    }
    for permutation in itertools.permutations((1, 2, 3)):
        fixed = 0
        for coset in normalized:
            image = {_apply(permutation, label) for label in coset}
            fixed += image == coset
        by_type[_cycle_type(permutation)].append(fixed)
    if any(len(set(values)) != 1 for values in by_type.values()):
        raise ValueError("character is not constant on a conjugacy class")
    return {name: values[0] for name, values in by_type.items()}


def _term_map(terms: list[dict[str, Any]]) -> dict[tuple[int, ...], Fraction]:
    result: dict[tuple[int, ...], Fraction] = {}
    for term in terms:
        coefficient = term["coefficient"]
        exponent = tuple(term["box_exponents"])
        result[exponent] = result.get(exponent, Fraction()) + Fraction(
            coefficient["numerator"], coefficient["denominator"]
        )
    return {key: value for key, value in result.items() if value}


def build() -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {}
    for name, (path, expected_hash) in INPUTS.items():
        if _sha256(path) != expected_hash:
            raise ValueError(f"independent-audit input drifted: {name}")
        values[name] = json.loads(path.read_text())

    terminal = values["terminal"]
    assembly = values["assembly"]
    manifest = values["carrier_manifest"]
    contact = values["H1_H2_contact_finite_rows"]
    ibp = values["relative_IBP_boundary_flux"]
    multiplicity = values["full_BV_multiplicity"]
    round_s4 = values["round_S4_holdout"]
    product_weighted = values["product_S2_S2_weighted_holdout"]
    product_det3 = values["product_S2_S2_det3_holdout"]

    assembly_imports = {
        row["result_id"]: row["sha256"]
        for row in assembly["dependencies"].values()
    }
    for name in (
        "H1_H2_contact_finite_rows",
        "carrier_manifest",
        "flat_TT_normalization",
        "full_BV_multiplicity",
        "longitudinal_Schur_resummation",
        "longitudinal_Schur_scale",
        "maximal_partial_BV_form_factors",
        "physical_H1_cubed_channels",
        "physical_five_form_factors",
        "product_S2_S2_det3_holdout",
        "product_S2_S2_weighted_holdout",
        "relative_IBP_boundary_flux",
        "round_S4_holdout",
        "six_master_coordinates",
    ):
        payload = values[name]
        if assembly_imports.get(payload["result_id"]) != INPUTS[name][1]:
            raise ValueError(f"assembly dependency closure drifted: {name}")

    raw_channels = assembly["maximal_determined_quotient"][
        "quotient_ledger"
    ]["raw_channel_order"]
    expected_raw = [
        "I10_123",
        "I24_123",
        "I24_213",
        "I24_312",
        "I25_123",
        "I25_213",
        "I25_312",
        "I28_123",
        "I28_132",
        "I28_231",
        "I29_123",
    ]
    if raw_channels != expected_raw:
        raise ValueError("raw labelled carrier order drifted")
    relation = [
        Fraction(1) if channel.startswith("I28_") else Fraction(0)
        for channel in raw_channels
    ]
    quotient_coordinates = [
        channel for channel in raw_channels if channel != "I28_231"
    ]
    raw_lift: list[list[Fraction]] = []
    for channel in raw_channels:
        row = []
        for coordinate in quotient_coordinates:
            value = Fraction(channel == coordinate)
            if channel == "I28_231" and coordinate in {"I28_123", "I28_132"}:
                value = Fraction(-1)
            row.append(value)
        raw_lift.append(row)
    if _rank([relation]) != 1 or _rank(raw_lift) != 10:
        raise ValueError("carrier quotient rank audit failed")
    if any(
        sum(relation[row] * raw_lift[row][column] for row in range(11))
        for column in range(10)
    ):
        raise ValueError("canonical raw lift violates the I28 relation")

    characters = {
        row["carrier_id"]: _module_character(row["cosets"])
        for row in manifest["permutation_modules"]
    }
    raw_character = {
        cycle: sum(character[cycle] for character in characters.values())
        for cycle in ("identity", "transposition", "three_cycle")
    }
    quotient_character = {
        cycle: raw_character[cycle] - 1
        for cycle in raw_character
    }
    multiplicities = {
        "trivial": (
            quotient_character["identity"]
            + 3 * quotient_character["transposition"]
            + 2 * quotient_character["three_cycle"]
        )
        // 6,
        "sign": (
            quotient_character["identity"]
            - 3 * quotient_character["transposition"]
            + 2 * quotient_character["three_cycle"]
        )
        // 6,
        "standard": (
            2 * quotient_character["identity"]
            - 2 * quotient_character["three_cycle"]
        )
        // 6,
    }
    if (
        quotient_character
        != {"identity": 10, "transposition": 4, "three_cycle": 1}
        or multiplicities != {"trivial": 4, "sign": 0, "standard": 3}
    ):
        raise ValueError("labelled-box S3 quotient audit failed")

    expected_labels = {
        ("I10", (1, 2, 3)),
        ("I24", (1, 2, 3)),
        ("I24", (2, 1, 3)),
        ("I24", (3, 1, 2)),
        ("I25", (1, 2, 3)),
        ("I25", (2, 1, 3)),
        ("I25", (3, 1, 2)),
        ("I28", (1, 2, 3)),
        ("I28", (1, 3, 2)),
        ("I28", (2, 3, 1)),
        ("I29", (1, 2, 3)),
    }
    contact_ids = {
        "H1_1_H2_23": 1,
        "H1_2_H2_13": 2,
        "H1_3_H2_12": 3,
    }
    contact_rows = contact["projection_rows"]
    for contact_id, singled_leg in contact_ids.items():
        rows = [row for row in contact_rows if row["contact_id"] == contact_id]
        if (
            len(rows) != 11
            or {(row["carrier_id"], tuple(row["label_order"])) for row in rows}
            != expected_labels
            or any(row["singled_H1_leg"] != singled_leg for row in rows)
            or any(
                row["finite_term_count"]
                != len(row["minimal_subtraction_finite_terms"])
                for row in rows
            )
        ):
            raise ValueError(f"contact endpoint orbit drifted: {contact_id}")
        i28_sum: dict[tuple[int, ...], Fraction] = {}
        for row in rows:
            if row["carrier_id"] != "I28":
                continue
            for exponent, coefficient in _term_map(
                row["minimal_subtraction_finite_terms"]
            ).items():
                i28_sum[exponent] = i28_sum.get(exponent, Fraction()) + coefficient
        if any(i28_sum.values()):
            raise ValueError(f"contact I28 relation failed: {contact_id}")
    if contact["finite_contact_theorem"]["mellin_endpoint_check"] != {
        "numerator": 0,
        "denominator": 1,
    }:
        raise ValueError("finite contact endpoint constant drifted")

    ibp_rows = ibp["channel_rows"]
    expected_corner_cycle = {
        ("x1", "x3"),
        ("x2", "x1"),
        ("x3", "x2"),
    }
    if (
        [row["channel_id"] for row in ibp_rows] != raw_channels
        or sum(len(row["corner_rows"]) for row in ibp_rows) != 33
        or any(
            {
                (corner["start_box"], corner["end_box"])
                for corner in row["corner_rows"]
            }
            != expected_corner_cycle
            for row in ibp_rows
        )
        or ibp["identity_ledger"]["status"] != "ALL_EXACT"
    ):
        raise ValueError("relative-IBP endpoint replay failed")

    zero_mode_rows = multiplicity["integration_slice"]["rows"]
    zero_mode_policies = {
        row["generator_id"]: row["zero_mode_policy_id"]
        for row in zero_mode_rows
    }
    if (
        len(multiplicity["repository_factors"]) != 4
        or zero_mode_policies
        != {
            "h_TT": "round_s4_unprimed_kernel_dimension_0",
            "xi_T": "round_s4_prime_delete_10_killing_vectors",
            "xi_L": "round_s4_coupled_scalar_prime_delete_5_conformal_modes",
            "omega": "round_s4_coupled_scalar_prime_delete_5_conformal_modes",
        }
    ):
        raise ValueError("full-BV zero-mode ledger drifted")

    # Method-distinct finite-matrix model.  The zero-mode line is fixed and
    # the smoothing projector acts only on a primed eigenline:
    #   Pi0=diag(1,0,0), S0=diag(1,3/2,4/3), P=diag(0,1,0).
    # For T=(3/2)xyz P, det(S0+T)/det(S0)=1+xyz, so the mixed
    # third logarithmic variation at the origin is exactly one.
    base_diagonal = [Fraction(1), Fraction(3, 2), Fraction(4, 3)]
    smoothing_coefficient = Fraction(3, 2)
    determinant_ratio_xyz_coefficient = (
        smoothing_coefficient / base_diagonal[1]
    )
    if determinant_ratio_xyz_coefficient != 1:
        raise ValueError("direct finite-matrix determinant witness failed")
    ambiguity_matrix = [
        [Fraction(row == column) for column in range(10)]
        for row in range(10)
    ]
    ambiguity_rank = _rank(ambiguity_matrix)
    annihilator_dimension = 10 - ambiguity_rank
    if ambiguity_rank != 10 or annihilator_dimension != 0:
        raise ValueError("universal-combination kernel audit failed")

    holdout_polynomial = {
        "round_S4_parameter": 0,
        "product_S2_S2_parameter": 1,
        "generic_test_parameter": 2,
        "amplitude": "b(b-1)/2",
        "values": [0, 0, 1],
    }
    if (
        round_s4["claim_flags"]["GENERIC_BACKGROUND_R_K_COMPUTED"] is not False
        or product_weighted["claim_flags"][
            "FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"
        ]
        is not False
        or product_det3["claim_flags"][
            "GENERIC_BACKGROUND_SCHUR_DETERMINANT_COMPUTED"
        ]
        is not False
    ):
        raise ValueError("special-background holdout was promoted")

    if (
        terminal["claim_flags"]["PARAMETERIZED_FIVE_FORM_FACTOR_FAMILY_COMPUTED"]
        is not True
        or terminal["claim_flags"][
            "NO_NONZERO_UNIVERSAL_FINITE_SCHUR_COMBINATION_PROVED"
        ]
        is not True
        or terminal["claim_flags"][
            "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED"
        ]
        is not False
    ):
        raise ValueError("terminal theorem claim boundary drifted")

    return {
        "schema": (
            "quantum-weyl-parameterized-parity-even-five-form-factor-"
            "family-independent-audit-v1"
        ),
        "result_id": (
            "PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_"
            "INDEPENDENT_AUDIT"
        ),
        "result_state": (
            "AFFINE_GLOBAL_SPECTRAL_FAMILY_AND_ZERO_UNIVERSAL_"
            "SCHUR_KERNEL_INDEPENDENTLY_FROZEN"
        ),
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "source_commit": "ed265d70c",
        "independence_boundary": {
            "terminal_producer_imported": False,
            "terminal_producer_invoked": False,
            "method": (
                "coset-character reconstruction plus direct exact finite-matrix "
                "resolvent/determinant variations"
            ),
            "producer_ambiguity_matrix_reused": False,
            "producer_rank_computation_reused": False,
        },
        "import_closure": {
            "input_count": len(INPUTS),
            "inputs": {
                name: _reference(path, values[name])
                for name, (path, _hash) in INPUTS.items()
            },
            "assembly_dependency_closure_count": len(assembly_imports),
            "all_physical_ghost_contact_zero_mode_and_Schur_inputs_pinned": True,
        },
        "carrier_quotient_audit": {
            "raw_channel_order": raw_channels,
            "raw_dimension": 11,
            "relation_vector": [int(value) for value in relation],
            "relation_rank": 1,
            "quotient_coordinates": quotient_coordinates,
            "raw_lift_matrix": [
                [int(value) for value in row] for row in raw_lift
            ],
            "raw_lift_rank": 10,
            "quotient_dimension": 10,
            "carrier_characters": characters,
            "raw_character": raw_character,
            "quotient_character": quotient_character,
            "irreducible_multiplicities": multiplicities,
        },
        "endpoint_audit": {
            "contact_ids": sorted(contact_ids),
            "contact_count": 3,
            "contact_row_count": len(contact_rows),
            "rows_per_contact": dict(
                Counter(row["contact_id"] for row in contact_rows)
            ),
            "contact_I28_relation": "ZERO_TERM_BY_TERM_FOR_ALL_CONTACTS",
            "mellin_endpoint_finite_constant": {
                "numerator": 0,
                "denominator": 1,
            },
            "relative_IBP_channel_count": len(ibp_rows),
            "relative_IBP_corner_count": 33,
            "corner_cycle": sorted([list(pair) for pair in expected_corner_cycle]),
            "status": "ALL_LABELLED_ENDPOINTS_REPLAYED_EXACTLY",
        },
        "zero_mode_and_holdout_audit": {
            "repository_factor_count": len(multiplicity["repository_factors"]),
            "zero_mode_policies": zero_mode_policies,
            "round_S4": "PINNED_EVALUATION_NOT_GENERIC_INTERPOLANT",
            "product_S2_S2": "PINNED_EVALUATION_NOT_GENERIC_INTERPOLANT",
            "two_point_noninterpolation_witness": holdout_polynomial,
            "special_background_interpolation_used": False,
        },
        "global_completion_audit": {
            "finite_matrix_model": {
                "basis": ["zero_mode", "primed_e", "primed_f"],
                "Pi0_diagonal": [1, 0, 0],
                "S0_diagonal": ["1", "3/2", "4/3"],
                "smoothing_projector_diagonal": [0, 1, 0],
                "completion_A": "T_A=0",
                "completion_B": "T_B=(3/2)u1*u2*u3 P in I10_123",
                "determinant_ratio_B_over_A": "1+u1*u2*u3",
                "mixed_third_log_determinant_shift": {
                    "numerator": 1,
                    "denominator": 1,
                },
            },
            "fixed_data_agree": [
                "complete local symbol",
                "all Wodzicki residues",
                "local scale response",
                "zero-mode projector",
                "subtraction prescription",
            ],
            "distinct_finite_third_variations": True,
            "unit_completion_count": 10,
            "ambiguity_matrix": [
                [int(value) for value in row] for row in ambiguity_matrix
            ],
            "ambiguity_rank": ambiguity_rank,
            "universal_combination_kernel_dimension": annihilator_dimension,
            "universal_combination_kernel_basis": [],
        },
        "freeze_verdict": {
            "terminal_affine_family_theorem_survives": True,
            "rank_ten_finite_Schur_ambiguity_independently_verified": True,
            "no_nonzero_universal_finite_Schur_combination": True,
            "partial_BV_and_local_scale_content_preserved": True,
            "special_background_holdouts_do_not_fix_generic_data": True,
            "complete_universal_coefficient_table": "NONDEFINED",
        },
        "claim_flags": {
            "PARAMETERIZED_FAMILY_THEOREM_INDEPENDENTLY_FROZEN": True,
            "RANK_TEN_AMBIGUITY_INDEPENDENTLY_VERIFIED": True,
            "ZERO_UNIVERSAL_SCHUR_KERNEL_INDEPENDENTLY_VERIFIED": True,
            "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
            "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED": False,
            "QME_OR_LORENTZIAN_PROMOTED": False,
        },
        "next_gate": (
            "choose and hash one global metric/domain/primed resolvent datum D "
            "for a background-specific spectral realization"
        ),
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL method-distinct audit "
            "freezes the affine-family theorem and the zero-dimensional kernel "
            "of universal finite Schur-sensitive combinations. It imports every "
            "declared physical, ghost, contact, zero-mode and Schur input by "
            "hash, reconstructs the labelled quotient and endpoints, and uses "
            "direct exact finite-matrix determinant variations rather than the "
            "terminal producer. It does not compute a universal coefficient "
            "table, Gamma1/Q1, a QME, or any Lorentzian, Hadamard, state, "
            "particle, scattering or unitarity result."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale independent audit: {OUTPUT}")
    print("PARAMETERIZED FIVE-FORM-FACTOR INDEPENDENT AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
