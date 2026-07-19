"""Classify the candidate-4 scalar-input, target-doublet L=4 zero variety."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import certified_nonzero_interval, fraction_string


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_L4_zero_variety.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt, "pi": sp.pi})


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(value)
    if witness is None:
        raise AssertionError("zero entered a nonzero interval")
    bounds, digits = witness
    return {
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
    }


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    fibre = next(item for item in parent["physical_fibres"] if item["candidate_index"] == 4)
    if (
        fibre["output_ell"],
        fibre["first_branch_multiplicity_per_parity"],
        fibre["second_branch_multiplicity_per_parity"],
        fibre["target_cokernel_dimension_per_parity"],
        fibre["temporal_signs"],
    ) != (4, 1, 1, 2, [1, 1]):
        raise AssertionError("candidate-4 target-doublet scope changed")
    coefficients = {
        term["first_parity"][0] + term["second_parity"][0]:
        [parse(component[0][0]) for component in term["coefficient_matrices"]]
        for target in fibre["target_equations"]
        for term in target["terms"]
    }
    if set(coefficients) != {"aa", "pp", "ap", "pa"}:
        raise AssertionError("candidate-4 parity workload changed")
    if not all((coefficients["ap"][i] + coefficients["pa"][i]).equals(0) for i in range(2)):
        raise AssertionError("cross-parity target vectors ceased to be opposite")
    if coefficients["aa"][0] != 0 or coefficients["pp"][0] != 0:
        raise AssertionError("polar null target row changed")
    if not (coefficients["pp"][1] + 3 * coefficients["aa"][1]).equals(0):
        raise AssertionError("same-parity ratio ceased to be -3")
    conversion = parse(fibre["coefficient_coordinate"]["axisymmetric_to_reduced_conversion"])
    nonzero = {
        "cross_target_0": interval(sp.radsimp(coefficients["ap"][0] * conversion)),
        "cross_target_1": interval(sp.radsimp(coefficients["ap"][1] * conversion)),
        "same_target_1": interval(sp.radsimp(coefficients["aa"][1] * conversion)),
    }
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate4-L4-zero-variety-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_L4_ZERO_VARIETY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-4 compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "scalar-input target-doublet all-m L4 cross-|n| resonance block",
            "degree": 2,
            "parity": "both axial and polar amplitudes on both momentum fibres",
            "ell": "2 times 2 -> L=4",
            "m": "all magnetic components",
            "k": "signed momenta (1,-2)",
            "omega": "positive-frequency SUM channel",
        },
        "candidate_index": 4,
        "fibre_id": fibre["fibre_id"],
        "rho": fibre["rho"],
        "coefficients": {
            key: [sp.sstr(component) for component in vector]
            for key, vector in coefficients.items()
        },
        "axisymmetric_to_reduced_conversion": sp.sstr(conversion),
        "coefficient_nonzero_intervals": nonzero,
        "exact_target_relations": {
            "cross_parity": "c_pa[j]=-c_ap[j] for j=0,1, with both c_ap[j] nonzero",
            "same_parity": "c_aa[0]=c_pp[0]=0 and c_pp[1]=-3*c_aa[1], with c_aa[1] nonzero",
            "independent_equations": [
                "F_cross=A_axial*B_polar-A_polar*B_axial=0",
                "F_same=A_axial*B_axial-3*A_polar*B_polar=0",
            ],
        },
        "factorization": {
            "U_minus": "A_axial-sqrt(3)*A_polar",
            "U_plus": "A_axial+sqrt(3)*A_polar",
            "V_plus": "B_axial+sqrt(3)*B_polar",
            "V_minus": "B_axial-sqrt(3)*B_polar",
            "equations": [
                "F_same+sqrt(3)*F_cross=U_minus*V_plus=0",
                "F_same-sqrt(3)*F_cross=U_plus*V_minus=0",
            ],
            "domain_argument": "binary-quartic multiplication occurs in C[x,y], an integral domain",
        },
        "zero_variety": {
            "ambient_dimension_over_C": 20,
            "irreducible_components_over_C": [
                {"component_id": "first_fibre_zero", "dimension_over_C": 10, "equations": ["A_axial=0", "A_polar=0"]},
                {"component_id": "second_fibre_zero", "dimension_over_C": 10, "equations": ["B_axial=0", "B_polar=0"]},
                {"component_id": "mixed_plus", "dimension_over_C": 10, "equations": ["A_axial=sqrt(3)*A_polar", "B_axial=sqrt(3)*B_polar"]},
                {"component_id": "mixed_minus", "dimension_over_C": 10, "equations": ["A_axial=-sqrt(3)*A_polar", "B_axial=-sqrt(3)*B_polar"]},
            ],
            "all_mixed_components_real": True,
        },
        "classification": {
            "candidate_4_target_doublet_L4_zero_variety_classified": True,
            "all_m_irreducible_decomposition_classified": True,
            "two_target_components_reduced_exactly": True,
            "other_twenty_parent_fibre_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {"parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT)},
        "claim_boundary": "This certificate classifies candidate 4, one of the twenty-one parent amplitude fibres. The other twenty parent fibres are outside this certificate; aggregate progress belongs to the generated atlas. Same-fibre sources, Taub intersections and higher correction classes remain fail-closed.",
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
        raise AssertionError("candidate-4 L4 zero-variety certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE4_L4_ZERO_VARIETY: PASS")


if __name__ == "__main__":
    main()
