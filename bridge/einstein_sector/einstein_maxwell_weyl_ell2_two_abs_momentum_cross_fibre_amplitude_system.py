"""Assemble the exact fibrewise cross-|n| resonance amplitude system."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.schema.json"
L4_PATHS = {
    ("axial", "axial"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json",
    ("polar", "polar"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json",
    ("axial", "polar"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json",
    ("polar", "axial"): ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json",
}
ODD = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json"
PARITY_PAIRS = tuple(L4_PATHS)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def text(value: sp.Expr) -> str:
    return sp.sstr(canonical(value))


def angular_map(output_ell: int) -> dict[str, object]:
    outputs = []
    for magnetic in range(-output_ell, output_ell + 1):
        terms = []
        norm = sp.S.Zero
        for first_magnetic in range(-2, 3):
            second_magnetic = magnetic - first_magnetic
            if not -2 <= second_magnetic <= 2:
                continue
            coefficient = clebsch_gordan(
                2, 2, output_ell,
                first_magnetic, second_magnetic, magnetic,
            )
            if coefficient == 0:
                continue
            norm += coefficient**2
            terms.append(
                {
                    "first_m": first_magnetic,
                    "second_m": second_magnetic,
                    "coefficient": text(coefficient),
                }
            )
        if canonical(norm - 1) != 0:
            raise AssertionError((output_ell, magnetic, norm))
        outputs.append({"M": magnetic, "terms": terms})
    return {
        "id": f"cg_2x2_to_{output_ell}",
        "input_ell": [2, 2],
        "output_ell": output_ell,
        "convention": "SymPy/Wigner Clebsch-Gordan <2,m1;2,m2|L,M>",
        "outputs": outputs,
    }


def fixture_matrices(
    fixtures: list[dict[str, object]],
    coefficient_key: str,
    divisor: sp.Expr = sp.S.One,
) -> tuple[list[list[list[str]]], int, int, int]:
    first_dimension = 1 + max(int(item["first_basis_index"]) for item in fixtures)
    second_dimension = 1 + max(int(item["second_basis_index"]) for item in fixtures)
    target_dimension = len(fixtures[0][coefficient_key])
    if len(fixtures) != first_dimension * second_dimension:
        raise AssertionError("basis fixture grid is incomplete")
    matrices = [
        [["0" for _ in range(second_dimension)] for _ in range(first_dimension)]
        for _ in range(target_dimension)
    ]
    seen: set[tuple[int, int]] = set()
    for item in fixtures:
        first = int(item["first_basis_index"])
        second = int(item["second_basis_index"])
        if (first, second) in seen:
            raise AssertionError("duplicate basis fixture")
        seen.add((first, second))
        values = item[coefficient_key]
        if len(values) != target_dimension:
            raise AssertionError("target cokernel dimension changed within a row")
        for component, value in enumerate(values):
            matrices[component][first][second] = text(parse(value) / divisor)
    return matrices, first_dimension, second_dimension, target_dimension


def l4_conversion() -> sp.Expr:
    input_scale = sp.sqrt(4 * sp.pi / 5)
    output_scale = sp.sqrt(4 * sp.pi / 9)
    return canonical(
        input_scale**2
        * clebsch_gordan(2, 2, 4, 0, 0, 0)
        / output_scale
    )


def l4_rows(values: dict[tuple[str, str], dict[str, object]]) -> list[dict[str, object]]:
    indexed = {
        pair: {int(row["candidate_index"]): row for row in value["candidate_rows"]}
        for pair, value in values.items()
    }
    candidate_indices = sorted(indexed[("axial", "axial")])
    if any(sorted(rows) != candidate_indices for rows in indexed.values()):
        raise AssertionError("L4 parity matrices have different candidate rows")
    conversion = l4_conversion()
    result = []
    for candidate_index in candidate_indices:
        reference = indexed[("axial", "axial")][candidate_index]
        terms_by_target = {"axial": [], "polar": []}
        first_dimensions: set[int] = set()
        second_dimensions: set[int] = set()
        target_dimensions: dict[str, set[int]] = {"axial": set(), "polar": set()}
        coefficient_count = 0
        for first_parity, second_parity in PARITY_PAIRS:
            row = indexed[(first_parity, second_parity)][candidate_index]
            for key in (
                "rho", "first_branch", "second_branch", "signed_momenta",
                "target_branch", "target_cokernel_dimension",
            ):
                if row[key] != reference[key]:
                    raise AssertionError((candidate_index, key, row[key], reference[key]))
            matrices, first_dimension, second_dimension, target_dimension = fixture_matrices(
                row["basis_fixtures"], "pairings", conversion
            )
            target_parity = "polar" if first_parity == second_parity else "axial"
            terms_by_target[target_parity].append(
                {
                    "first_parity": first_parity,
                    "second_parity": second_parity,
                    "coefficient_matrices": matrices,
                }
            )
            first_dimensions.add(first_dimension)
            second_dimensions.add(second_dimension)
            target_dimensions[target_parity].add(target_dimension)
            coefficient_count += first_dimension * second_dimension * target_dimension
        if len(first_dimensions) != 1 or len(second_dimensions) != 1:
            raise AssertionError("branch multiplicity depends on parity")
        if any(len(value) != 1 for value in target_dimensions.values()):
            raise AssertionError("L4 target multiplicity depends on parity")
        target_dimension = target_dimensions["axial"].pop()
        if target_dimensions["polar"].pop() != target_dimension:
            raise AssertionError("L4 target multiplicities disagree")
        first_dimension = first_dimensions.pop()
        second_dimension = second_dimensions.pop()
        result.append(
            {
                "fibre_id": f"L4_candidate_{candidate_index}",
                "candidate_index": candidate_index,
                "rho": reference["rho"],
                "output_ell": 4,
                "temporal_channel": "SUM",
                "temporal_signs": [1, 1],
                "signed_momenta": reference["signed_momenta"],
                "first_branch": reference["first_branch"],
                "second_branch": reference["second_branch"],
                "target_branch": reference["target_branch"],
                "first_branch_multiplicity_per_parity": first_dimension,
                "second_branch_multiplicity_per_parity": second_dimension,
                "target_cokernel_dimension_per_parity": target_dimension,
                "complex_amplitude_variables": 10 * (first_dimension + second_dimension),
                "reduced_internal_coefficients": coefficient_count,
                "scalar_magnetic_equations": 2 * target_dimension * 9,
                "angular_map": "cg_2x2_to_4",
                "coefficient_coordinate": {
                    "statement": "stored axisymmetric P2 x P2 -> P4 pairings divided by the common exact conversion factor",
                    "axisymmetric_to_reduced_conversion": text(conversion),
                },
                "target_equations": [
                    {
                        "target_parity": target_parity,
                        "target_component_count": target_dimension,
                        "terms": terms_by_target[target_parity],
                    }
                    for target_parity in ("axial", "polar")
                ],
            }
        )
    return result


def odd_rows(value: dict[str, object]) -> list[dict[str, object]]:
    result = []
    for row in value["candidate_rows"]:
        terms_by_target = {"axial": [], "polar": []}
        first_dimensions: set[int] = set()
        second_dimensions: set[int] = set()
        target_dimensions: dict[str, set[int]] = {"axial": set(), "polar": set()}
        coefficient_count = 0
        phase_coordinates: dict[str, list[str]] = {}
        for channel in row["parity_channels"]:
            matrices, first_dimension, second_dimension, target_dimension = fixture_matrices(
                channel["basis_fixtures"], "scaled_pairings"
            )
            target_parity = channel["target_parity"]
            terms_by_target[target_parity].append(
                {
                    "first_parity": channel["first_parity"],
                    "second_parity": channel["second_parity"],
                    "coefficient_matrices": matrices,
                }
            )
            phase = channel["basis_fixtures"][0]["phase_normalizations"]
            if any(item["phase_normalizations"] != phase for item in channel["basis_fixtures"]):
                raise AssertionError("phase coordinate changed within a parity channel")
            if target_parity in phase_coordinates and phase_coordinates[target_parity] != phase:
                raise AssertionError("phase coordinate changed between target terms")
            phase_coordinates[target_parity] = phase
            first_dimensions.add(first_dimension)
            second_dimensions.add(second_dimension)
            target_dimensions[target_parity].add(target_dimension)
            coefficient_count += first_dimension * second_dimension * target_dimension
        if len(first_dimensions) != 1 or len(second_dimensions) != 1:
            raise AssertionError("odd-L branch multiplicity depends on parity")
        if any(len(item) != 1 for item in target_dimensions.values()):
            raise AssertionError("odd-L target multiplicity depends on parity")
        target_dimension = target_dimensions["axial"].pop()
        if target_dimensions["polar"].pop() != target_dimension:
            raise AssertionError("odd-L target multiplicities disagree")
        first_dimension = first_dimensions.pop()
        second_dimension = second_dimensions.pop()
        output_ell = int(row["output_ell"])
        result.append(
            {
                "fibre_id": f"L{output_ell}_candidate_{row['candidate_index']}",
                "candidate_index": row["candidate_index"],
                "rho": row["rho"],
                "output_ell": output_ell,
                "temporal_channel": row["temporal_channel"],
                "temporal_signs": row["temporal_signs"],
                "signed_momenta": row["signed_momenta"],
                "first_branch": row["first_branch"],
                "second_branch": row["second_branch"],
                "target_branch": row["target_branch"],
                "first_branch_multiplicity_per_parity": first_dimension,
                "second_branch_multiplicity_per_parity": second_dimension,
                "target_cokernel_dimension_per_parity": target_dimension,
                "complex_amplitude_variables": 10 * (first_dimension + second_dimension),
                "reduced_internal_coefficients": coefficient_count,
                "scalar_magnetic_equations": 2 * target_dimension * (2 * output_ell + 1),
                "angular_map": f"cg_2x2_to_{output_ell}",
                "coefficient_coordinate": {
                    "statement": "the stored reduced pairing is multiplied by a fixed nonzero target-coordinate phase; zero loci are unchanged",
                    "phase_normalizations_by_target_parity": phase_coordinates,
                },
                "target_equations": [
                    {
                        "target_parity": target_parity,
                        "target_component_count": target_dimension,
                        "terms": terms_by_target[target_parity],
                    }
                    for target_parity in ("axial", "polar")
                ],
            }
        )
    return result


def build() -> dict[str, object]:
    l4_values = {pair: json.loads(path.read_text()) for pair, path in L4_PATHS.items()}
    odd_value = json.loads(ODD.read_text())
    rows = l4_rows(l4_values) + odd_rows(odd_value)
    if len(rows) != 21:
        raise AssertionError("physical fibre count changed")
    for index, left in enumerate(rows):
        left_rho = parse(left["rho"])
        for right in rows[:index]:
            if canonical(left_rho - parse(right["rho"])) == 0:
                raise AssertionError((left["fibre_id"], right["fibre_id"]))
    coefficient_count = sum(int(row["reduced_internal_coefficients"]) for row in rows)
    equation_count = sum(int(row["scalar_magnetic_equations"]) for row in rows)
    adjoint_equation_count = sum(
        2 * int(row["target_cokernel_dimension_per_parity"])
        for row in rows
    )
    fixture_count = sum(
        4
        * int(row["first_branch_multiplicity_per_parity"])
        * int(row["second_branch_multiplicity_per_parity"])
        for row in rows
    )
    nonzero_count = sum(
        parse(coefficient) != 0
        for row in rows
        for target in row["target_equations"]
        for term in target["terms"]
        for matrix in term["coefficient_matrices"]
        for matrix_row in matrix
        for coefficient in matrix_row
    )
    if (
        coefficient_count,
        nonzero_count,
        fixture_count,
        adjoint_equation_count,
        equation_count,
    ) != (164, 162, 128, 54, 418):
        raise AssertionError(
            (
                coefficient_count,
                nonzero_count,
                fixture_count,
                adjoint_equation_count,
                equation_count,
            )
        )
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-cross-fibre-amplitude-system-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CROSS_FIBRE_AMPLITUDE_SYSTEM",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; each algebraic circumference is a separate fibre",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "all complex positive-frequency ell=2 amplitudes on |n|=1 and |n|=2 for the certified isolated cross-fibre collisions",
            "degree": 2,
            "parity": "both input parities and both target parities retained",
            "ell": "2 times 2 -> L=1,3,4",
            "m": "all m=-2,...,2 inputs and every output M",
            "k": "signed |n|=1 and |n|=2 pairs retained row by row",
            "omega": "certified SUM or signed DIFFERENCE channel retained row by row",
        },
        "amplitude_convention": {
            "first": "A[parity,branch-copy,m] on the declared |n|=1 signed momentum",
            "second": "B[parity,branch-copy,m] on the declared |n|=2 signed momentum",
            "equation": "for every target parity, cokernel component j and M, sum C_j^{parity-pair}[r,s] <2,m1;2,m2|L,M> A[r,m1] B[s,m2] = 0",
            "reality": "positive-frequency amplitudes are arbitrary complex coordinates; the negative-frequency equations are their conjugates for a real tangent",
        },
        "angular_maps": [angular_map(output_ell) for output_ell in (1, 3, 4)],
        "physical_fibres": rows,
        "summary": {
            "pairwise_distinct_algebraic_circumference_fibres": 21,
            "L1_fibres": sum(row["output_ell"] == 1 for row in rows),
            "L3_fibres": sum(row["output_ell"] == 3 for row in rows),
            "L4_fibres": sum(row["output_ell"] == 4 for row in rows),
            "target_parity_adjoint_equations_before_M_expansion": adjoint_equation_count,
            "ordered_branch_basis_fixtures": fixture_count,
            "certified_reduced_internal_coefficients": coefficient_count,
            "nonzero_reduced_internal_coefficients": nonzero_count,
            "zero_reduced_internal_coefficients": coefficient_count - nonzero_count,
            "factorized_complex_scalar_magnetic_equations": equation_count,
        },
        "classification": {
            "all_certified_cross_fibre_coefficients_lifted_to_all_m_equations": True,
            "physical_circumference_fibres_kept_separate": True,
            "factorized_cross_fibre_resonance_system_certified": True,
            "mandatory_first_fibre_zero_plane_certified": True,
            "mandatory_second_fibre_zero_plane_certified": True,
            "irreducible_zero_variety_decomposition_classified": False,
            "taub_common_zero_intersection_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {
            "input_sha256": {
                str(path.relative_to(ROOT)): sha(path)
                for path in (*L4_PATHS.values(), ODD)
            }
        },
        "claim_boundary": "This is the complete factorized necessary cross-fibre resonance system on the 21 separately tuned isolated-collision fibres. It defines, but does not irreducibly decompose, each amplitude zero variety. Same-fibre sources, the Taub intersection, the complete two-fibre tangent cone, smooth-secular and causal corrections remain fail-closed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    if args.check or not args.write:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("cross-fibre amplitude-system certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CROSS_FIBRE_AMPLITUDE_SYSTEM: PASS")


if __name__ == "__main__":
    main()
