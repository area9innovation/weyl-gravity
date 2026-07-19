"""Classify the remaining three multiplicity-two-source L=3 varieties."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import sympy as sp
from sympy.polys.numberfields import to_number_field
from sympy.core.cache import clear_cache

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import certified_nonzero_interval, fraction_string


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"
SQRT2 = sp.sqrt(2)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("controlling source functional vanished")
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
            matrix = sp.Matrix([
                [parse(value) for value in row]
                for row in term["coefficient_matrices"][0]
            ])
            row = matrix if matrix.rows == 1 else matrix.T
            if row.shape != (1, 2):
                raise AssertionError("multiplicity-two coefficient ceased to be a row functional")
            rows[term["first_parity"][0] + term["second_parity"][0]] = list(row)
    return rows


def exact_squared_relation_vanishes(relation: tuple[sp.Expr, sp.Expr, int]) -> bool:
    """Prove one magnitude relation in its real algebraic number field."""
    left, right, square_factor = relation
    residual = sp.sqrtdenest(left**2 - square_factor * right**2)
    algebraic = to_number_field(residual)
    result = algebraic.as_expr() == 0
    del algebraic, residual
    clear_cache()
    gc.collect()
    return result


def exact_squared_relations_vanish(relations: list[tuple[sp.Expr, sp.Expr, int]]) -> bool:
    """Prove independent algebraic-number relations concurrently."""
    with ProcessPoolExecutor(max_workers=min(12, len(relations))) as pool:
        return all(pool.map(exact_squared_relation_vanishes, relations))


def decomposition(fibre: dict[str, object]) -> dict[str, object]:
    rows = coefficient_rows(fibre)
    candidate = fibre["candidate_index"]
    if candidate == 6:
        relation_pairs = (
            [(rows["pa"][j], rows["aa"][j], 1152) for j in range(2)]
            + [(rows["ap"][j], rows["pp"][j], 128) for j in range(2)]
        )
        controls = {"axial_extra_row": rows["aa"][0], "polar_extra_row": rows["pp"][0]}
        reduced_pencil = {
            "same_equation": "T1(X,U)+T1(Y,V)=0",
            "cross_equation": "-8*sqrt(2)*T1(X,V)-24*sqrt(2)*T1(Y,U)=0",
            "lambda_squared": "384",
            "spectator_location": "one kernel quartic in each parity of the second p_extra branch",
        }
    else:
        relation_pairs = (
            [(rows["ap"][j], rows["aa"][j], 1152) for j in range(2)]
            + [(rows["pa"][j], rows["pp"][j], 128) for j in range(2)]
        )
        controls = {"axial_extra_row": rows["aa"][0], "polar_extra_row": rows["pp"][0]}
        reduced_pencil = {
            "same_equation": "T1(X,U)+T1(Y,V)=0",
            "cross_equation": "-24*sqrt(2)*T1(X,V)-8*sqrt(2)*T1(Y,U)=0",
            "lambda_squared": "384",
            "spectator_location": "one kernel quartic in each parity of the first p_extra branch",
        }
    if not exact_squared_relations_vanish(relation_pairs):
        raise AssertionError("multiplicity-two exact row relations changed")
    relation_intervals = [
        {"left": interval(left), "right": interval(right), "square_factor": square_factor}
        for left, right, square_factor in relation_pairs
    ]
    if any(item["left"]["sign"] == item["right"]["sign"] for item in relation_intervals):
        raise AssertionError("multiplicity-two relation sign changed")
    return {
        "candidate_index": candidate,
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "branches": [fibre["first_branch"], fibre["second_branch"], fibre["target_branch"]],
        "signed_momenta": fibre["signed_momenta"],
        "temporal_channel": fibre["temporal_channel"],
        "coefficient_rows": {key: [sp.sstr(value) for value in row] for key, row in rows.items()},
        "controlling_nonzero_intervals": {key: interval(value) for key, value in controls.items()},
        "exact_relation_interval_witnesses": relation_intervals,
        "exact_row_relations": (
            ["c_pa=-24*sqrt(2)*c_aa", "c_ap=-8*sqrt(2)*c_pp"]
            if candidate == 6 else
            ["c_ap=-24*sqrt(2)*c_aa", "c_pa=-8*sqrt(2)*c_pp"]
        ),
        "reduced_parity_pencil": reduced_pencil,
        "zero_variety": {
            "ambient_dimension_over_C": 30,
            "active_dimension_over_C": 12,
            "spectator_dimension_over_C": 10,
            "dimension_over_C": 22,
            "irreducible_components_over_C": 1,
            "description": "A^10 times DetRank1(5x2)_plus times DetRank1(5x2)_minus after invertible internal and parity transformations",
        },
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibres = [item for item in parent["physical_fibres"] if item["candidate_index"] in (6, 10, 18)]
    if [item["candidate_index"] for item in fibres] != [6, 10, 18]:
        raise AssertionError("multiplicity-two L3 census changed")
    for fibre in fibres:
        if not (
            fibre["output_ell"] == 3
            and sorted((fibre["first_branch_multiplicity_per_parity"], fibre["second_branch_multiplicity_per_parity"])) == [1, 2]
            and fibre["target_cokernel_dimension_per_parity"] == 1
        ):
            raise AssertionError("multiplicity-two L3 scope changed")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-multiplicity-two-L3-zero-varieties-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_MULTIPLICITY_TWO_L3_ZERO_VARIETIES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "three separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all-m L3 cross-|n| blocks with one multiplicity-two p_extra source branch",
            "degree": 2,
            "parity": "both axial and polar amplitudes",
            "ell": "2 times 2 -> L=3",
            "m": "all magnetic components through the first binary-quartic transvectant",
            "k": "candidate-specific signed |n|=1 and |n|=2 momenta",
            "omega": "positive-frequency SUM channel",
        },
        "carrier_crosswalk": {
            "active": "one nonzero internal p_extra functional per parity plus the q_minus quartic",
            "spectator": "the kernel of each internal functional, one quartic per parity",
            "background_rule": "the three fibres share a certified algebraic type but are not identified across circumference backgrounds",
        },
        "representation_theorem": {
            "active_normal_form": "two nonzero real-eigenvalue first-transvectant equations",
            "kernel": "T1(f,g)=0 iff equal-degree binary quartics f and g are proportional",
            "geometry": "two irreducible six-dimensional rank-one cones times a ten-dimensional spectator affine space",
        },
        "decompositions": [decomposition(fibre) for fibre in fibres],
        "summary": {
            "classified_physical_fibres": 3,
            "parent_physical_fibres_outside_this_certificate": 18,
            "ambient_dimension_per_fibre_over_C": 30,
            "dimension_per_fibre_over_C": 22,
            "irreducible_components_per_fibre_over_C": 1,
        },
        "classification": {
            "all_three_multiplicity_two_L3_zero_varieties_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "internal_spectator_split_certified": True,
            "real_parity_pencils_diagonalizable": True,
            "other_eighteen_parent_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This theorem-local certificate classifies candidates 6, 10 and 18 only. Aggregate progress belongs to the generated atlas. Same-fibre sources, Taub intersections and correction classes remain fail-closed.",
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
        raise AssertionError("multiplicity-two L3 certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_MULTIPLICITY_TWO_L3_ZERO_VARIETIES: PASS")


if __name__ == "__main__":
    main()
