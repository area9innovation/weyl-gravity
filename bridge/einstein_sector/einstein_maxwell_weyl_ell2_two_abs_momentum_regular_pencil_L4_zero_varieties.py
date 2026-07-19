"""Classify the candidate-7/11/19 regular-pencil L=4 zero varieties."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def exact_interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("regular-pencil invariant vanished")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }


def det2(matrix: sp.Matrix) -> sp.Expr:
    if matrix.shape != (2, 2):
        raise AssertionError("expected a 2-by-2 internal matrix")
    return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]


def adj2(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]])


def internal_matrices(fibre: dict[str, object]) -> dict[str, sp.Matrix]:
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    matrices: dict[str, sp.Matrix] = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            key = term["first_parity"][0] + term["second_parity"][0]
            rows = []
            for component in term["coefficient_matrices"]:
                source = sp.Matrix(
                    [[parse(value) * conversion for value in row] for row in component]
                )
                row = source if source.rows == 1 else source.T
                if row.shape != (1, 2):
                    raise AssertionError("regular-pencil source ceased to be a doublet")
                rows.append(list(row))
            matrix = sp.Matrix(rows)
            if matrix.shape != (2, 2):
                raise AssertionError("regular-pencil target ceased to be a doublet")
            if fibre["first_branch_multiplicity_per_parity"] == 2:
                key = key[::-1]
            matrices[key] = matrix
    if set(matrices) != {"aa", "ap", "pa", "pp"}:
        raise AssertionError("regular-pencil parity census changed")
    if any(value.has(sp.pi) for matrix in matrices.values() for value in matrix):
        raise AssertionError("the common positive coordinate conversion failed to cancel pi")
    return matrices


def pencil_invariants(matrices: dict[str, sp.Matrix]) -> dict[str, sp.Expr]:
    determinants = {key: det2(matrix) for key, matrix in matrices.items()}
    denominator = determinants["ap"] * determinants["aa"]
    numerator_matrix = (
        adj2(matrices["ap"])
        * matrices["pa"]
        * adj2(matrices["aa"])
        * matrices["pp"]
    )
    trace_square_pencil = (numerator_matrix[0, 0] + numerator_matrix[1, 1]) / denominator
    determinant_square_pencil = (
        determinants["pa"] * determinants["pp"] / denominator
    )
    discriminant = trace_square_pencil**2 - 4 * determinant_square_pencil
    return {
        **{f"det_{key}": value for key, value in determinants.items()},
        "trace_square_pencil": trace_square_pencil,
        "determinant_square_pencil": determinant_square_pencil,
        "discriminant_square_pencil": discriminant,
    }


def decomposition(fibre: dict[str, object]) -> dict[str, object]:
    matrices = internal_matrices(fibre)
    invariants = pencil_invariants(matrices)
    witnesses = {key: exact_interval(value) for key, value in invariants.items()}
    for key in ("trace_square_pencil", "determinant_square_pencil", "discriminant_square_pencil"):
        if witnesses[key]["sign"] != "positive":
            raise AssertionError(f"four-real-root pencil criterion failed: {key}")
    components = [
        {
            "component_id": "scalar_fibre_zero",
            "dimension_over_C": 20,
            "equations": ["S_axial=0", "S_polar=0"],
        },
        {
            "component_id": "doublet_fibre_zero",
            "dimension_over_C": 10,
            "equations": ["D_axial=0", "D_polar=0"],
        },
    ]
    for index in range(4):
        components.append(
            {
                "component_id": f"mixed_eigenline_{index + 1}",
                "dimension_over_C": 10,
                "definition": "S_axial+z_i*S_polar=0 and D lies in the z_i pencil eigenline",
            }
        )
    return {
        "candidate_index": fibre["candidate_index"],
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "branches": [fibre["first_branch"], fibre["second_branch"], fibre["target_branch"]],
        "signed_momenta": fibre["signed_momenta"],
        "scalar_source_fibre": "first" if fibre["first_branch_multiplicity_per_parity"] == 1 else "second",
        "axisymmetric_to_reduced_conversion": fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"],
        "internal_matrices": {
            key: [[sp.sstr(value) for value in row] for row in matrix.tolist()]
            for key, matrix in matrices.items()
        },
        "exact_interval_witnesses": witnesses,
        "pencil": {
            "normalized_operator": "T=C_ap^{-1} C_pa C_aa^{-1} C_pp",
            "characteristic_polynomial": "z^4-tr(T) z^2+det(T)",
            "root_structure": "four distinct nonzero real roots z_i",
            "proof": "tr(T)>0, det(T)>0 and tr(T)^2-4 det(T)>0 give two distinct positive z^2 roots",
        },
        "zero_variety": {
            "ambient_dimension_over_C": 30,
            "irreducible_components_over_C": components,
            "component_dimensions_over_C": [20, 10, 10, 10, 10, 10],
            "all_mixed_components_real_supported": True,
        },
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibres = [item for item in parent["physical_fibres"] if item["candidate_index"] in (7, 11, 19)]
    if [item["candidate_index"] for item in fibres] != [7, 11, 19]:
        raise AssertionError("regular-pencil L4 census changed")
    for fibre in fibres:
        if (
            fibre["output_ell"] != 4
            or sorted((fibre["first_branch_multiplicity_per_parity"], fibre["second_branch_multiplicity_per_parity"])) != [1, 2]
            or fibre["target_cokernel_dimension_per_parity"] != 2
            or fibre["complex_amplitude_variables"] != 30
        ):
            raise AssertionError("regular-pencil L4 scope changed")
    decompositions = [decomposition(fibre) for fibre in fibres]
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-regular-pencil-L4-zero-varieties-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_REGULAR_PENCIL_L4_ZERO_VARIETIES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "three separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all-m L4 cross-|n| blocks with one scalar and one multiplicity-two source branch and a target doublet",
            "degree": 2,
            "parity": "both axial and polar amplitudes",
            "ell": "2 times 2 -> L=4",
            "m": "all magnetic components through binary-quartic multiplication",
            "k": "candidate-specific signed |n|=1 and |n|=2 momenta",
            "omega": "positive-frequency SUM channel",
        },
        "representation_theorem": {
            "model": "V_2=Sym^4(C^2), with V_4 projection equal to multiplication in C[x,y]",
            "pencil_reduction": "the four target-doublet equations diagonalize over C to (S_axial+z_i*S_polar) D_i=0",
            "domain_argument": "C[x,y] is an integral domain, so every diagonal product has a vanishing factor",
            "component_argument": "two or more distinct scalar pencil relations force the scalar fibre to vanish; maximal cases give exactly six components",
        },
        "decompositions": decompositions,
        "summary": {
            "classified_candidates": [7, 11, 19],
            "classified_physical_fibres": 3,
            "parent_physical_fibres_outside_this_certificate": 18,
            "ambient_dimension_per_fibre_over_C": 30,
            "irreducible_components_per_fibre_over_C": 6,
            "component_dimensions_over_C": [20, 10, 10, 10, 10, 10],
            "remaining_unclassified_cross_fibre_candidates": [13],
        },
        "classification": {
            "three_regular_pencil_L4_zero_varieties_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "four_distinct_real_pencil_roots_certified": True,
            "candidate_13_zero_variety_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This theorem-local certificate classifies candidates 7, 11 and 19 only and does not identify their backgrounds. Candidate 13, same-fibre sources, Taub intersections and correction classes remain fail-closed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("regular-pencil L4 certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_REGULAR_PENCIL_L4_ZERO_VARIETIES: PASS")


if __name__ == "__main__":
    main()
