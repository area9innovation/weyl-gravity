"""Classify the two multiplicity-two-source L=4 resonance varieties."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import sympy as sp
from sympy.core.cache import clear_cache
from sympy.polys.numberfields import to_number_field

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_rank_one_branch_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("controlling coefficient vanished")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }


def coefficient_rows(fibre: dict[str, object]) -> dict[str, list[sp.Expr]]:
    rows = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            matrix = sp.Matrix(
                [[parse(value) for value in row] for row in term["coefficient_matrices"][0]]
            )
            row = matrix if matrix.rows == 1 else matrix.T
            if row.shape != (1, 2):
                raise AssertionError("multiplicity-two coefficient ceased to be a row functional")
            rows[term["first_parity"][0] + term["second_parity"][0]] = list(row)
    return rows


def exact_squared_relation_vanishes(
    relation: tuple[sp.Expr, sp.Expr, int, int],
) -> bool:
    left, right, numerator, denominator = relation
    residual = sp.sqrtdenest(denominator * left**2 - numerator * right**2)
    algebraic = to_number_field(residual)
    result = algebraic.as_expr() == 0
    del algebraic, residual
    clear_cache()
    gc.collect()
    return result


def decomposition(fibre: dict[str, object]) -> tuple[dict[str, object], list[tuple[sp.Expr, sp.Expr, int, int]]]:
    rows = coefficient_rows(fibre)
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    candidate = fibre["candidate_index"]
    if candidate == 8:
        relations = (
            [(rows["pa"][j], rows["aa"][j], 3, 40) for j in range(2)]
            + [(rows["pp"][j], rows["ap"][j], 120, 1) for j in range(2)]
        )
        exact_relations = ["c_pa=-(sqrt(30)/20)c_aa", "c_pp=-2sqrt(30)c_ap"]
        scalar = {"aa": sp.S.One, "pp": -2 * sp.sqrt(30), "ap": sp.S.One, "pa": -sp.sqrt(30) / 20}
        spectator = "one kernel quartic in each parity of the second p_extra branch"
    elif candidate == 12:
        relations = (
            [(rows["ap"][j], rows["aa"][j], 3, 40) for j in range(2)]
            + [(rows["pp"][j], rows["pa"][j], 120, 1) for j in range(2)]
        )
        exact_relations = ["c_ap=-(sqrt(30)/20)c_aa", "c_pp=-2sqrt(30)c_pa"]
        scalar = {"aa": sp.S.One, "pp": -2 * sp.sqrt(30), "ap": -sp.sqrt(30) / 20, "pa": sp.S.One}
        spectator = "one kernel quartic in each parity of the first p_extra branch"
    else:
        raise AssertionError("unexpected L4 candidate")
    relations = [
        (sp.radsimp(left * conversion), sp.radsimp(right * conversion), numerator, denominator)
        for left, right, numerator, denominator in relations
    ]
    relation_intervals = [
        {
            "left": interval(left),
            "right": interval(right),
            "squared_ratio_numerator": numerator,
            "squared_ratio_denominator": denominator,
            "coordinate": "axisymmetric source coefficient before division by the common positive conversion",
        }
        for left, right, numerator, denominator in relations
    ]
    if any(item["left"]["sign"] == item["right"]["sign"] for item in relation_intervals):
        raise AssertionError("negative proportionality sign changed")
    r_squared = sp.cancel(scalar["aa"] * scalar["ap"] / (scalar["pp"] * scalar["pa"]))
    s_over_r = sp.cancel(-scalar["pa"] / scalar["ap"])
    generalized_eigenvalue_square = sp.cancel(
        scalar["ap"] * scalar["pa"] / (scalar["aa"] * scalar["pp"])
    )
    if generalized_eigenvalue_square != sp.Rational(1, 40):
        raise AssertionError("canonical parity-pencil invariant changed")
    if r_squared <= 0:
        raise AssertionError("real mixed sheets disappeared")
    sheets = []
    for sign, label in ((1, "plus"), (-1, "minus")):
        r_value = sp.radsimp(sign * sp.sqrt(r_squared))
        s_value = sp.radsimp(s_over_r * r_value)
        if sp.radsimp(scalar["aa"] + scalar["pp"] * r_value * s_value) != 0:
            raise AssertionError("same-parity active equation did not vanish on mixed sheet")
        if sp.radsimp(scalar["ap"] * s_value + scalar["pa"] * r_value) != 0:
            raise AssertionError("cross-parity active equation did not vanish on mixed sheet")
        sheets.append(
            {
                "component_id": f"mixed_{label}",
                "active_dimension_over_C": 10,
                "relations": {"A_polar": f"({sp.sstr(r_value)})*A_axial", "B_polar": f"({sp.sstr(s_value)})*B_axial"},
            }
        )
    record = {
        "candidate_index": candidate,
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "branches": [fibre["first_branch"], fibre["second_branch"], fibre["target_branch"]],
        "signed_momenta": fibre["signed_momenta"],
        "coefficient_rows": {key: [sp.sstr(value) for value in row] for key, row in rows.items()},
        "axisymmetric_to_reduced_conversion": fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"],
        "exact_row_relations": exact_relations,
        "exact_relation_interval_witnesses": relation_intervals,
        "active_scalar_coefficients": {key: sp.sstr(value) for key, value in scalar.items()},
        "spectator_location": spectator,
        "r_squared": sp.sstr(r_squared),
        "s_over_r": sp.sstr(s_over_r),
        "generalized_eigenvalue_square": sp.sstr(generalized_eigenvalue_square),
        "zero_variety": {
            "ambient_dimension_over_C": 30,
            "spectator_dimension_over_C": 10,
            "dimension_per_component_over_C": 20,
            "irreducible_components_over_C": [
                {"component_id": "first_active_fibre_zero", "active_dimension_over_C": 10},
                {"component_id": "second_active_fibre_zero", "active_dimension_over_C": 10},
                *sheets,
            ],
            "all_mixed_components_real": True,
        },
    }
    return record, relations


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibres = [item for item in parent["physical_fibres"] if item["candidate_index"] in (8, 12)]
    if [item["candidate_index"] for item in fibres] != [8, 12]:
        raise AssertionError("multiplicity-two L4 census changed")
    if any(
        item["output_ell"] != 4
        or sorted((item["first_branch_multiplicity_per_parity"], item["second_branch_multiplicity_per_parity"])) != [1, 2]
        or item["target_cokernel_dimension_per_parity"] != 1
        for item in fibres
    ):
        raise AssertionError("multiplicity-two L4 scope changed")
    decompositions = []
    relations = []
    for fibre in fibres:
        record, record_relations = decomposition(fibre)
        decompositions.append(record)
        relations.extend(record_relations)
    with ProcessPoolExecutor(max_workers=len(relations)) as pool:
        if not all(pool.map(exact_squared_relation_vanishes, relations)):
            raise AssertionError("multiplicity-two L4 exact row relations changed")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-rank-one-branch-zero-varieties-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_RANK_ONE_BRANCH_ZERO_VARIETIES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "two separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all-m L4 cross-|n| blocks with one multiplicity-two p_extra source branch",
            "degree": 2,
            "parity": "both axial and polar amplitudes",
            "ell": "2 times 2 -> L=4",
            "m": "all magnetic components through binary-quartic multiplication",
            "k": "candidate-specific signed |n|=1 and |n|=2 momenta",
            "omega": "positive-frequency SUM channel",
        },
        "carrier_crosswalk": {
            "active": "one nonzero internal p_extra functional per parity plus the q_minus quartic",
            "spectator": "the kernel of each internal functional, one quartic per parity",
            "background_rule": "the two fibres share an algebraic type but are not identified across circumference backgrounds",
        },
        "representation_theorem": {
            "model": "V_2=Sym^4(C^2), and the V_4 projection is multiplication in C[x,y]",
            "active_geometry": "the scalar multiplication case split gives two one-fibre-zero planes and two proportionality sheets",
            "spectator_extension": "the free ten-dimensional internal-kernel factor raises every active dimension-ten component to dimension twenty",
        },
        "decompositions": decompositions,
        "summary": {
            "classified_candidates": [8, 12],
            "classified_physical_fibres": 2,
            "parent_physical_fibres_outside_this_certificate": 19,
            "ambient_dimension_per_fibre_over_C": 30,
            "dimension_per_component_over_C": 20,
            "irreducible_components_per_fibre_over_C": 4,
        },
        "classification": {
            "both_multiplicity_two_L4_zero_varieties_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "internal_spectator_split_certified": True,
            "all_mixed_components_real": True,
            "other_nineteen_parent_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This theorem-local certificate classifies candidates 8 and 12 only. Aggregate progress belongs to the generated atlas. Same-fibre sources, Taub intersections and correction classes remain fail-closed.",
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
        raise AssertionError("multiplicity-two L4 certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_RANK_ONE_BRANCH_ZERO_VARIETIES: PASS")


if __name__ == "__main__":
    main()
