"""Decompose the five scalar-internal L=4 cross-fibre amplitude ideals."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    certified_nonzero_interval,
    fraction_string,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.schema.json"
AMPLITUDE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def canonical(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.simplify(sp.sqrtdenest(sp.radsimp(value))))


def interval_record(value: sp.Expr) -> dict[str, object]:
    certified = certified_nonzero_interval(value)
    if certified is None:
        raise AssertionError("expected a nonzero algebraic coefficient")
    interval, digits = certified
    return {
        "lower": fraction_string(interval[0]),
        "upper": fraction_string(interval[1]),
        "decimal_digits": digits,
        "positive": interval[0] > 0,
        "excludes_zero": interval[0] > 0 or interval[1] < 0,
    }


def coefficients(fibre: dict[str, object]) -> dict[str, sp.Expr]:
    result = {}
    for target in fibre["target_equations"]:
        for term in target["terms"]:
            key = term["first_parity"][0] + term["second_parity"][0]
            result[key] = parse(term["coefficient_matrices"][0][0][0])
    if set(result) != {"aa", "pp", "ap", "pa"}:
        raise AssertionError("scalar parity coefficient support changed")
    return result


def build() -> dict[str, object]:
    parent = json.loads(AMPLITUDE.read_text())
    fibres = [
        fibre
        for fibre in parent["physical_fibres"]
        if fibre["output_ell"] == 4
        and fibre["first_branch_multiplicity_per_parity"] == 1
        and fibre["second_branch_multiplicity_per_parity"] == 1
        and fibre["target_cokernel_dimension_per_parity"] == 1
    ]
    if [fibre["candidate_index"] for fibre in fibres] != [3, 5, 9, 15, 21]:
        raise AssertionError("scalar L4 fibre census changed")
    decompositions = []
    for fibre in fibres:
        c = coefficients(fibre)
        conversion = parse(
            fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"]
        )
        witnesses = {
            key: interval_record(canonical(value * conversion))
            for key, value in c.items()
        }
        if not all(item["excludes_zero"] for item in witnesses.values()):
            raise AssertionError("scalar coefficient lost nonzero witness")
        r_squared = canonical(c["aa"] * c["ap"] / (c["pp"] * c["pa"]))
        r_interval = interval_record(r_squared)
        if not r_interval["positive"]:
            raise AssertionError("real mixed sheets disappeared")
        s_over_r = canonical(-c["pa"] / c["ap"])
        sheets = []
        for sign, label in ((1, "plus"), (-1, "minus")):
            r_value = canonical(sign * sp.sqrt(r_squared))
            s_value = canonical(s_over_r * r_value)
            if canonical(c["aa"] + c["pp"] * r_value * s_value) != 0:
                raise AssertionError("same-parity equation did not vanish")
            if canonical(c["ap"] * s_value + c["pa"] * r_value) != 0:
                raise AssertionError("cross-parity equation did not vanish")
            sheets.append(
                {
                    "component_id": f"mixed_{label}",
                    "dimension_over_C": 10,
                    "relations": {
                        "A_polar": f"({sp.sstr(r_value)})*A_axial",
                        "B_polar": f"({sp.sstr(s_value)})*B_axial",
                    },
                    "r": sp.sstr(r_value),
                    "s": sp.sstr(s_value),
                }
            )
        decompositions.append(
            {
                "fibre_id": fibre["fibre_id"],
                "candidate_index": fibre["candidate_index"],
                "rho": fibre["rho"],
                "branches": {
                    "first": fibre["first_branch"],
                    "second": fibre["second_branch"],
                    "target": fibre["target_branch"],
                },
                "ambient_dimension_over_C": 20,
                "coefficients": {key: sp.sstr(value) for key, value in c.items()},
                "axisymmetric_source_coordinate_nonzero_intervals": witnesses,
                "r_squared": sp.sstr(r_squared),
                "r_squared_interval": r_interval,
                "s_over_r": sp.sstr(s_over_r),
                "irreducible_components_over_C": [
                    {
                        "component_id": "first_fibre_zero",
                        "dimension_over_C": 10,
                        "relations": {"A_axial": "0", "A_polar": "0"},
                    },
                    {
                        "component_id": "second_fibre_zero",
                        "dimension_over_C": 10,
                        "relations": {"B_axial": "0", "B_polar": "0"},
                    },
                    *sheets,
                ],
            }
        )
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-scalar-L4-zero-varieties-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L4_ZERO_VARIETIES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "five separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "the five L=4 cross-|n| fibres with one input copy per parity and one target adjoint component per parity",
            "degree": 2,
            "parity": "axial and polar amplitudes retained",
            "ell": "2 times 2 -> L=4",
            "m": "all input m and all output M via the highest-spin Clebsch-Gordan map",
            "k": "row-specific |n|=1 and |n|=2 signed momenta",
            "omega": "positive-frequency SUM channel",
        },
        "representation_theorem": {
            "model": "V_2 is Sym^4(C^2); the V_4 projection is multiplication Sym^4(C^2) x Sym^4(C^2) -> Sym^8(C^2)",
            "integral_domain_step": "C[x,y] has no zero divisors, so a nonzero scalar-block solution either lies on a one-fibre-zero plane or has all four parity polynomials nonzero",
            "fraction_field_step": "for r=A_polar/A_axial and s=B_polar/B_axial, the two equations give r*s=-c_aa/c_pp and s=-(c_pa/c_ap)r; hence r and s are constants and r^2=c_aa*c_ap/(c_pp*c_pa)",
            "completeness": "the case split gives exactly the two one-sided planes and the two displayed proportionality sheets over C",
        },
        "decompositions": decompositions,
        "summary": {
            "classified_physical_fibres": 5,
            "irreducible_components_per_fibre_over_C": 4,
            "one_sided_components_per_fibre": 2,
            "mixed_proportionality_components_per_fibre": 2,
            "mixed_components_real_on_declared_coefficient_embedding": 10,
            "remaining_cross_fibre_physical_fibres_open": 16,
        },
        "classification": {
            "complete_scalar_internal_L4_zero_varieties_classified": True,
            "all_m_mixed_components_classified": True,
            "all_five_r_squared_values_positive_exactly": True,
            "remaining_sixteen_cross_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {
            "parent": str(AMPLITUDE.relative_to(ROOT)),
            "parent_sha256": sha(AMPLITUDE),
        },
        "claim_boundary": "This decomposes exactly five scalar-internal L4 cross-fibre resonance varieties. The other sixteen fibrewise varieties, same-fibre sources, five Taub maps, complete tangent cone, smooth-secular and causal correction classes remain fail-closed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("scalar L4 zero-variety certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_SCALAR_L4_ZERO_VARIETIES: PASS")


if __name__ == "__main__":
    main()
