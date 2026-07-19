"""Certify highest-weight mixed zero subspaces on every odd-L fibre."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_odd_L_highest_weight_zero_subspaces.schema.json"
PARENT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_cross_fibre_amplitude_system.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def build() -> dict[str, object]:
    parent = json.loads(PARENT.read_text())
    angular = {int(item["output_ell"]): item for item in parent["angular_maps"]}
    fibres = [item for item in parent["physical_fibres"] if item["output_ell"] in (1, 3)]
    expected = [1, 2, 6, 10, 14, 16, 17, 18, 20]
    if [item["candidate_index"] for item in fibres] != expected:
        raise AssertionError("odd-L physical-fibre census changed")

    witnesses = []
    for fibre in fibres:
        output_ell = int(fibre["output_ell"])
        amap = angular[output_ell]
        for output in amap["outputs"]:
            for term in output["terms"]:
                expected_cg = clebsch_gordan(
                    2,
                    2,
                    output_ell,
                    int(term["first_m"]),
                    int(term["second_m"]),
                    int(output["M"]),
                )
                if sp.simplify(parse(term["coefficient"]) - expected_cg) != 0:
                    raise AssertionError("parent Clebsch-Gordan coefficient changed")
                if (term["first_m"], term["second_m"]) == (2, 2):
                    raise AssertionError("odd-L projection acquired an M=4 term")
        if clebsch_gordan(2, 2, output_ell, 2, 2, 4) != 0:
            raise AssertionError("highest-weight selection rule failed")

        first_internal = 2 * int(fibre["first_branch_multiplicity_per_parity"])
        second_internal = 2 * int(fibre["second_branch_multiplicity_per_parity"])
        temporal_signs = list(fibre["temporal_signs"])
        if output_ell == 1 and temporal_signs != [1, -1]:
            raise AssertionError("L1 signed difference convention changed")
        if output_ell == 3 and temporal_signs != [1, 1]:
            raise AssertionError("L3 sum convention changed")
        witnesses.append(
            {
                "fibre_id": fibre["fibre_id"],
                "candidate_index": fibre["candidate_index"],
                "rho": fibre["rho"],
                "output_ell": output_ell,
                "temporal_channel": fibre["temporal_channel"],
                "temporal_signs": temporal_signs,
                "signed_momenta": fibre["signed_momenta"],
                "branches": {
                    "first": fibre["first_branch"],
                    "second": fibre["second_branch"],
                    "target": fibre["target_branch"],
                },
                "ambient_complex_amplitude_dimension": fibre["complex_amplitude_variables"],
                "highest_weight_subspace_dimension_over_C": first_internal + second_internal,
                "support": {
                    "first_signed_frequency_carrier": "A[parity,branch-copy,m]=0 unless m=2",
                    "second_signed_frequency_carrier": "B[parity,branch-copy,m]=0 unless m=2",
                    "internal_coordinates": "arbitrary in every declared parity and branch copy",
                },
                "selection_rule": "m1=m2=2 gives M=4, while the certified target has L<4",
                "target_scalar_equations_vanishing": fibre["scalar_magnetic_equations"],
                "mixed_nonzero_point": {
                    "first": "A[axial,branch-copy-0,m=2]=1",
                    "second": "B[axial,branch-copy-0,m=2]=1",
                    "all_other_coordinates": "0",
                },
                "real_tangent_completion": (
                    "For SUM rows add the ordinary conjugate carriers. For DIFFERENCE rows B is the declared negative-frequency carrier; "
                    "its positive-frequency reality partner has m=-2. No positive- and negative-frequency carrier is identified by name."
                ),
            }
        )

    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-odd-L-highest-weight-zero-subspaces-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ODD_L_HIGHEST_WEIGHT_ZERO_SUBSPACES",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "nine separately tuned compact magnetically supported Plebanski-Hacyan products",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "all nine cross-|n| fibres with odd target L=1 or L=3",
            "degree": 2,
            "parity": "all declared input parities and branch copies retained on the aligned support",
            "ell": "2 times 2 -> L=1 or L=3",
            "m": "both signed-frequency input carriers supported at m=2",
            "k": "row-specific signed |n|=1 and |n|=2 momenta",
            "omega": "six SUM rows and three signed DIFFERENCE rows",
        },
        "representation_theorem": {
            "statement": "The tensor product of two ell=2 highest-weight carriers has M=4, hence its projection to every L=1 or L=3 target vanishes identically.",
            "coefficient_independence": "The angular factor vanishes before contraction with any branch, parity or target-adjoint coefficient matrix.",
            "difference_channel_typing": "For temporal sign -1, B denotes the declared negative-frequency carrier; its real-tangent conjugate is a positive-frequency m=-2 carrier.",
        },
        "witnesses": witnesses,
        "summary": {
            "classified_physical_fibres": 9,
            "L1_difference_fibres": 3,
            "L3_sum_fibres": 6,
            "target_scalar_equations_vanishing": sum(int(item["target_scalar_equations_vanishing"]) for item in witnesses),
            "sum_of_highest_weight_subspace_dimensions_over_C": sum(int(item["highest_weight_subspace_dimension_over_C"]) for item in witnesses),
            "remaining_cross_fibre_physical_fibres_without_full_decomposition": 16,
        },
        "classification": {
            "all_nine_odd_L_highest_weight_zero_subspaces_certified": True,
            "mixed_nonzero_points_certified_on_every_odd_L_fibre": True,
            "complete_odd_L_zero_varieties_classified": False,
            "same_fibre_quadratic_sources_classified": False,
            "taub_common_zero_intersection_classified": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "smooth_secular_classified": False,
            "causal_or_quantum_claim": False,
        },
        "provenance": {
            "parent": str(PARENT.relative_to(ROOT)),
            "parent_sha256": sha(PARENT),
        },
        "claim_boundary": "This certifies a nontrivial mixed all-m resonance-zero subspace on each of the nine odd-L fibres, not their irreducible zero-variety decompositions. Same-fibre sources, Taub intersections, bounded and smooth-secular correction classes, residual descent and causal or quantum maps remain fail-closed.",
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
        raise AssertionError("odd-L highest-weight zero-subspace certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_ODD_L_HIGHEST_WEIGHT_ZERO_SUBSPACES: PASS")


if __name__ == "__main__":
    main()
