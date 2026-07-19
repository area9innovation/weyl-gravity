"""Classify the three scalar-internal L=1 amplitude zero varieties."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("zero entered a nonzero interval")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "positive": bounds[0] > 0,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
    }


def monic_strings(polynomials: list[sp.Expr], variables: tuple[sp.Symbol, ...]) -> list[str]:
    unique: dict[str, None] = {}
    for expression in polynomials:
        if expression == 0:
            continue
        normalized = sp.Poly(sp.expand(expression), *variables).monic().as_expr()
        unique[sp.sstr(normalized)] = None
    return sorted(unique)


def transvectant_certificate() -> dict[str, object]:
    f = sp.symbols("f0:5")
    f0, f1, f2, f3, f4 = f
    matrix = sp.Matrix(
        [
            [-f3, 3 * f2, -3 * f1, f0, 0],
            [-f4, 2 * f3, 0, -2 * f1, f0],
            [0, -f4, 3 * f3, -3 * f2, f1],
        ]
    )
    maximal_minors = [
        matrix[:, columns].det()
        for columns in itertools.combinations(range(5), 3)
    ]
    rank_drop_basis = monic_strings(maximal_minors, f)
    if len(rank_drop_basis) != 7:
        raise AssertionError("third-transvectant rank-drop ideal changed")

    a, b, c = sp.symbols("a b c")
    square_relations = [
        f0 - a**2,
        f1 - a * b,
        3 * f2 - a * c - 2 * b**2,
        f3 - b * c,
        f4 - c**2,
    ]
    elimination = sp.groebner(square_relations, a, b, c, *f, order="lex")
    eliminated = [
        polynomial.as_expr()
        for polynomial in elimination.polys
        if not any(polynomial.as_expr().has(variable) for variable in (a, b, c))
    ]
    elimination_basis = monic_strings(eliminated, f)
    if elimination_basis != rank_drop_basis:
        raise AssertionError("rank-drop locus is no longer the square-quartic cone")

    two_minors = [
        matrix.extract(rows, columns).det()
        for rows in itertools.combinations(range(3), 2)
        for columns in itertools.combinations(range(5), 2)
    ]
    rank_one = sp.groebner(two_minors, *f, order="grevlex")
    rank_one_basis = monic_strings([polynomial.as_expr() for polynomial in rank_one.polys], f)
    expected_rank_one = monic_strings(
        [f[left] * f[right] for left in range(5) for right in range(left, 5)],
        f,
    )
    if rank_one_basis != expected_rank_one:
        raise AssertionError("nonzero rank-one transvectant carrier appeared")
    if matrix.subs({f0: 1, f1: 0, f2: 0, f3: 0, f4: 1})[:, (0, 1, 3)].det() != 1:
        raise AssertionError("generic rank-three witness changed")
    return {
        "matrix_A_f": [[sp.sstr(entry) for entry in row] for row in matrix.tolist()],
        "rank_at_most_two_monic_groebner_basis": rank_drop_basis,
        "square_quartic_parametrization": {
            "f0": "a^2",
            "f1": "a*b",
            "f2": "(a*c+2*b^2)/3",
            "f3": "b*c",
            "f4": "c^2",
        },
        "square_elimination_monic_groebner_basis": elimination_basis,
        "rank_at_most_one_monic_groebner_basis": rank_one_basis,
        "generic_rank_three_witness": {
            "f": ["1", "0", "0", "0", "1"],
            "columns": [0, 1, 3],
            "minor": "1",
        },
    }


def coefficients(fibre: dict[str, object]) -> dict[str, sp.Expr]:
    result = {
        term["first_parity"][0] + term["second_parity"][0]:
        parse(term["coefficient_matrices"][0][0][0])
        for target in fibre["target_equations"]
        for term in target["terms"]
    }
    if set(result) != {"aa", "pp", "ap", "pa"}:
        raise AssertionError("scalar L1 parity pencil changed")
    return result


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibres = [item for item in parent["physical_fibres"] if item["output_ell"] == 1]
    if [item["candidate_index"] for item in fibres] != [14, 17, 20]:
        raise AssertionError("scalar L1 fibre census changed")
    decompositions = []
    for fibre in fibres:
        c = coefficients(fibre)
        witnesses = {key: interval(value) for key, value in c.items()}
        if not all(item["excludes_zero"] for item in witnesses.values()):
            raise AssertionError("scalar L1 pencil coefficient vanished")
        if canonical(c["pp"] - 3 * c["aa"]) != 0 or canonical(c["ap"] - c["pa"]) != 0:
            raise AssertionError("scalar L1 pencil relations changed")
        lambda_squared = canonical(c["ap"] * c["pa"] / (c["aa"] * c["pp"]))
        if canonical(lambda_squared - sp.Rational(128, 5)) != 0:
            raise AssertionError("scalar L1 parity eigenvalue changed")
        decompositions.append(
            {
                "fibre_id": fibre["fibre_id"],
                "candidate_index": fibre["candidate_index"],
                "rho": fibre["rho"],
                "temporal_channel": fibre["temporal_channel"],
                "temporal_signs": fibre["temporal_signs"],
                "signed_momenta": fibre["signed_momenta"],
                "branches": {
                    "first": fibre["first_branch"],
                    "second": fibre["second_branch"],
                    "target": fibre["target_branch"],
                },
                "coefficients": {key: sp.sstr(value) for key, value in c.items()},
                "coefficient_nonzero_intervals": witnesses,
                "parity_pencil": {
                    "relations": ["c_pp=3*c_aa", "c_ap=c_pa"],
                    "lambda_squared": "128/5",
                    "lambda": "8*sqrt(10)/5",
                    "Q": [["c_ap/(c_aa*lambda)", "-c_ap/(c_aa*lambda)"], ["1", "1"]],
                    "P_transpose": "inverse(C0*Q)",
                    "normal_form": [
                        "T3(A_plus,B_plus)=0",
                        "T3(A_minus,B_minus)=0",
                    ],
                },
                "zero_variety": {
                    "ambient_dimension_over_C": 20,
                    "dimension_over_C": 14,
                    "codimension_over_C": 6,
                    "irreducible_components_over_C": 1,
                    "defining_equations": "six bilinear equations, three in each parity eigenchannel",
                    "factorization": "the Cartesian product K_T3_plus x K_T3_minus of two irreducible dimension-7 third-transvectant kernels",
                },
            }
        )
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-scalar-L1-zero-varieties-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L1_ZERO_VARIETIES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "three separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "the complete scalar-internal all-m L1 cross-|n| resonance blocks",
            "degree": 2,
            "parity": "both axial and polar amplitudes on both momentum fibres",
            "ell": "2 times 2 -> L=1",
            "m": "all magnetic components through the third binary-quartic transvectant",
            "k": "row-specific signed |n|=1 and |n|=2 momenta",
            "omega": "signed DIFFERENCE channel with temporal signs (+1,-1)",
        },
        "carrier_crosswalk": {
            "statement": "The multiplicity-one odd V1 summand of V2 tensor V2 is, under the standard magnetic-to-binary-quartic diagonal intertwiner, the third transvectant T3.",
            "reality": "B is the declared negative-frequency carrier; its positive-frequency real-tangent partner has opposite magnetic number.",
        },
        "third_transvectant_certificate": transvectant_certificate(),
        "kernel_theorem": {
            "rank_strata": "For non-square f, rank(A_f)=3 and ker(A_f) has dimension 2. For nonzero square quartics rank(A_f)=2 and the kernel has dimension 3. At f=0 the kernel has dimension 5.",
            "stratum_dimensions": {
                "generic_rank_three_incidence": 7,
                "square_rank_two_incidence": 6,
                "zero_rank_zero_incidence": 5,
            },
            "complete_intersection_step": "The three T3 coefficients generate an ideal of height three in the ten-variable regular ring, so the kernel is an unmixed complete intersection.",
            "irreducibility_step": "The generic rank-three incidence is an irreducible rank-two vector bundle over an irreducible open subset of C^5. Its closure is the unique dimension-7 component; the lower rank strata have dimensions 6 and 5 and cannot be components of the unmixed complete intersection.",
        },
        "decompositions": decompositions,
        "summary": {
            "classified_physical_fibres": 3,
            "irreducible_components_per_fibre_over_C": 1,
            "dimension_per_fibre_over_C": 14,
            "ambient_dimension_per_fibre_over_C": 20,
            "parent_physical_fibres_outside_this_certificate": 18,
        },
        "classification": {
            "all_three_scalar_L1_zero_varieties_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "third_transvectant_rank_stratification_certified": True,
            "parity_pencils_diagonalized_exactly": True,
            "other_eighteen_parent_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This certificate classifies three of the twenty-one parent amplitude fibres. The other eighteen parent fibres are outside this certificate; aggregate progress belongs to the generated atlas. Same-fibre sources, Taub intersections and higher correction classes remain fail-closed.",
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
        raise AssertionError("scalar L1 zero-variety certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L1_ZERO_VARIETIES: PASS")


if __name__ == "__main__":
    main()
