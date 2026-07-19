#!/usr/bin/env python3
"""Independent verifier for the factorized cross-fibre amplitude system."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.schema.json"
ODD = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json"
L4 = {
    ("axial", "axial"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json",
    ("polar", "polar"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json",
    ("axial", "polar"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json",
    ("polar", "axial"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi, "I": sp.I})


def source_fixture_lookup() -> dict[tuple[int, str, str, int, int], list[str]]:
    result: dict[tuple[int, str, str, int, int], list[str]] = {}
    odd = json.loads(ODD.read_text())
    for row in odd["candidate_rows"]:
        for channel in row["parity_channels"]:
            for fixture in channel["basis_fixtures"]:
                result[
                    (
                        row["candidate_index"],
                        channel["first_parity"],
                        channel["second_parity"],
                        fixture["first_basis_index"],
                        fixture["second_basis_index"],
                    )
                ] = fixture["scaled_pairings"]
    for parities, path in L4.items():
        value = json.loads(path.read_text())
        for row in value["candidate_rows"]:
            for fixture in row["basis_fixtures"]:
                result[
                    (
                        row["candidate_index"],
                        parities[0],
                        parities[1],
                        fixture["first_basis_index"],
                        fixture["second_basis_index"],
                    )
                ] = fixture["pairings"]
    return result


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == sha(SCHEMA)
    for path, expected in value["provenance"]["input_sha256"].items():
        assert sha(ROOT / path) == expected

    fibres = value["physical_fibres"]
    sources = source_fixture_lookup()
    input_scale = sp.sqrt(4 * sp.pi / 5)
    output_scale = sp.sqrt(4 * sp.pi / 9)
    l4_divisor = sp.factor(
        input_scale**2 * clebsch_gordan(2, 2, 4, 0, 0, 0) / output_scale
    )
    assert len(fibres) == 21
    assert sorted(fibre["candidate_index"] for fibre in fibres) == list(range(1, 22))
    rhos = [parse(fibre["rho"]) for fibre in fibres]
    for left in range(len(rhos)):
        for right in range(left + 1, len(rhos)):
            assert not sp.to_number_field(rhos[left] - rhos[right]).is_zero

    angular = {item["input_ell"][0] * 0 + int(item["output_ell"]): item for item in value["angular_maps"]}
    for ell in (1, 3, 4):
        stored = angular[ell]
        assert len(stored["outputs"]) == 2 * ell + 1
        for output in stored["outputs"]:
            total = sp.S.Zero
            for term in output["terms"]:
                coefficient = clebsch_gordan(
                    2,
                    2,
                    ell,
                    term["first_m"],
                    term["second_m"],
                    output["M"],
                )
                assert sp.simplify(coefficient - parse(term["coefficient"])) == 0
                total += coefficient**2
            assert sp.simplify(total - 1) == 0

    coefficient_count = nonzero_count = fixture_count = adjoint_equations = magnetic_equations = 0
    odd_coordinate_rewrites = 0
    for fibre in fibres:
        first_dimension = fibre["first_branch_multiplicity_per_parity"]
        second_dimension = fibre["second_branch_multiplicity_per_parity"]
        target_dimension = fibre["target_cokernel_dimension_per_parity"]
        assert fibre["complex_amplitude_variables"] == 10 * (
            first_dimension + second_dimension
        )
        expected_internal = 4 * first_dimension * second_dimension * target_dimension
        expected_equations = 2 * target_dimension * (2 * fibre["output_ell"] + 1)
        assert fibre["reduced_internal_coefficients"] == expected_internal
        assert fibre["scalar_magnetic_equations"] == expected_equations
        assert {item["target_parity"] for item in fibre["target_equations"]} == {
            "axial",
            "polar",
        }
        if fibre["output_ell"] == 4:
            assert sp.simplify(
                parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
                - l4_divisor
            ) == 0
        for target in fibre["target_equations"]:
            assert target["target_component_count"] == target_dimension
            assert len(target["terms"]) == 2
            for term in target["terms"]:
                matrices = term["coefficient_matrices"]
                assert len(matrices) == target_dimension
                for component, matrix in enumerate(matrices):
                    assert len(matrix) == first_dimension
                    assert all(len(matrix_row) == second_dimension for matrix_row in matrix)
                    for first_index, matrix_row in enumerate(matrix):
                        for second_index, coefficient in enumerate(matrix_row):
                            source = sources[
                                (
                                    fibre["candidate_index"],
                                    term["first_parity"],
                                    term["second_parity"],
                                    first_index,
                                    second_index,
                                )
                            ][component]
                            if fibre["output_ell"] != 4:
                                odd_coordinate_rewrites += coefficient != source
        coefficient_count += expected_internal
        fixture_count += 4 * first_dimension * second_dimension
        adjoint_equations += 2 * target_dimension
        magnetic_equations += expected_equations
        nonzero_count += sum(
            parse(coefficient) != 0
            for target in fibre["target_equations"]
            for term in target["terms"]
            for matrix in term["coefficient_matrices"]
            for row in matrix
            for coefficient in row
        )
    summary = value["summary"]
    assert (coefficient_count, magnetic_equations) == (
        summary["certified_reduced_internal_coefficients"],
        summary["factorized_complex_scalar_magnetic_equations"],
    ) == (164, 418)
    assert (
        fixture_count,
        adjoint_equations,
        nonzero_count,
        coefficient_count - nonzero_count,
    ) == (
        summary["ordered_branch_basis_fixtures"],
        summary["target_parity_adjoint_equations_before_M_expansion"],
        summary["nonzero_reduced_internal_coefficients"],
        summary["zero_reduced_internal_coefficients"],
    ) == (128, 54, 162, 2)
    assert (summary["L1_fibres"], summary["L3_fibres"], summary["L4_fibres"]) == (
        3,
        6,
        12,
    )
    assert odd_coordinate_rewrites == 4
    classification = value["classification"]
    assert classification["factorized_cross_fibre_resonance_system_certified"]
    assert classification["physical_circumference_fibres_kept_separate"]
    assert classification["mandatory_first_fibre_zero_plane_certified"]
    assert classification["mandatory_second_fibre_zero_plane_certified"]
    assert not classification["irreducible_zero_variety_decomposition_classified"]
    assert not classification["taub_common_zero_intersection_classified"]
    assert not classification["same_fibre_quadratic_sources_classified"]
    assert not classification["complete_two_fibre_tangent_cone_classified"]
    assert not classification["causal_or_quantum_claim"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CROSS_FIBRE_AMPLITUDE_SYSTEM independent verification: PASS")
