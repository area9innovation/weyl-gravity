"""Exact same-fibre nonzero-frequency resonance census on candidate 13."""
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
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.schema.json"
INPUTS = {
    "candidate13": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json",
    "candidate13_taub": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json",
    "ell0_nonzero_fourier": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell0_nonzero_fourier.json",
    "ell0_homogeneous_nonzero_frequency": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json",
    "ell1_nonzero_k_cofiber": ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1.json",
}
BRANCH_MASS_SQUARE = {
    "q_minus": 6 - 2 * sp.sqrt(3),
    "p_extra": sp.Rational(16, 3),
    "q_plus": 6 + 2 * sp.sqrt(3),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"sqrt": sp.sqrt})


def interval(value: sp.Expr) -> dict[str, object]:
    witness = certified_nonzero_interval(sp.factor(value))
    if witness is None:
        raise AssertionError(f"candidate-13 same-fibre collision found: {value}")
    bounds, digits = witness
    return {
        "expression": sp.sstr(sp.factor(value)),
        "lower": fraction_string(bounds[0]),
        "upper": fraction_string(bounds[1]),
        "decimal_digits": digits,
        "excludes_zero": bounds[0] > 0 or bounds[1] < 0,
        "sign": "positive" if bounds[0] > 0 else "negative",
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    candidate = records["candidate13"]
    if not candidate["classification"]["candidate_13_ideal_prime"]:
        raise AssertionError("candidate-13 prime parent changed")
    if not records["candidate13_taub"]["classification"]["candidate_13_resonance_Taub_common_zero_is_origin"]:
        raise AssertionError("candidate-13 Taub parent changed")
    ell0 = records["ell0_nonzero_fourier"]
    if not ell0["classification"]["Diff_Weyl_U1_complex_exact_at_every_nonzero_Fourier_pair"]:
        raise AssertionError("ell=0 nonzero-Fourier exactness changed")
    ell0_homogeneous = records["ell0_homogeneous_nonzero_frequency"]
    if not ell0_homogeneous["classification"]["homogeneous_nonzero_frequency_physical_quotient_empty"]:
        raise AssertionError("ell=0 homogeneous nonzero-frequency quotient changed")
    ell1 = records["ell1_nonzero_k_cofiber"]
    shells = ell1["theorem"]["shells"]
    if shells != {"extra": "4/3", "standard": "4"}:
        raise AssertionError("ell=1 nonzero-k shells changed")

    rho = parse(candidate["rho"])
    channels = []
    total_defects = 0
    for momentum_number in (1, 2):
        frequencies = {
            branch: sp.sqrt(momentum_number**2 * rho + mass_square)
            for branch, mass_square in BRANCH_MASS_SQUARE.items()
        }
        for first_branch, second_branch in itertools.combinations_with_replacement(BRANCH_MASS_SQUARE, 2):
            temporal_channels = [
                ("SUM", frequencies[first_branch] + frequencies[second_branch], 4 * momentum_number**2 * rho)
            ]
            if first_branch != second_branch:
                temporal_channels.append(
                    ("DIFFERENCE", frequencies[first_branch] - frequencies[second_branch], sp.S.Zero)
                )
            for temporal_channel, output_frequency, output_momentum_squared in temporal_channels:
                spectral_value = sp.factor(output_frequency**2 - output_momentum_squared)
                defects = [
                    {
                        "output_ell": 1,
                        "target_shell": "extra",
                        "shell_polynomial": "s-4/3",
                        "witness": interval(spectral_value - sp.Rational(4, 3)),
                    },
                    {
                        "output_ell": 1,
                        "target_shell": "standard",
                        "shell_polynomial": "s-4",
                        "witness": interval(spectral_value - 4),
                    },
                ]
                for output_ell in (2, 3, 4):
                    angular_eigenvalue = output_ell * (output_ell + 1)
                    defects.extend(
                        [
                            {
                                "output_ell": output_ell,
                                "target_shell": "p_extra",
                                "shell_polynomial": f"s-({angular_eigenvalue}-2/3)",
                                "witness": interval(spectral_value - (angular_eigenvalue - sp.Rational(2, 3))),
                            },
                            {
                                "output_ell": output_ell,
                                "target_shell": "q_minus_or_q_plus",
                                "shell_polynomial": f"(s-{angular_eigenvalue})^2-{2 * angular_eigenvalue}",
                                "witness": interval((spectral_value - angular_eigenvalue) ** 2 - 2 * angular_eigenvalue),
                            },
                        ]
                    )
                total_defects += len(defects)
                channels.append(
                    {
                        "momentum_fibre_abs_n": momentum_number,
                        "first_branch": first_branch,
                        "second_branch": second_branch,
                        "temporal_channel": temporal_channel,
                        "output_momentum_squared": sp.sstr(output_momentum_squared),
                        "output_frequency": sp.sstr(output_frequency),
                        "spectral_value_s": sp.sstr(spectral_value),
                        "ell0_disposition": (
                            "empty nonzero-Fourier physical quotient at K=2*n*sqrt(rho)"
                            if temporal_channel == "SUM"
                            else "empty homogeneous physical quotient at K=0 and Omega!=0"
                        ),
                        "nonzero_shell_defects": defects,
                    }
                )
    if len(channels) != 18 or total_defects != 144:
        raise AssertionError("candidate-13 same-fibre census size changed")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-same-fibre-resonance-census-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_SAME_FIBRE_RESONANCE_CENSUS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": {
            **candidate["scope"],
            "carrier": "same-fibre quadratic products of q_minus, p_extra and q_plus ell=2 modes on each |n|=1,2 fibre of the candidate-13 circumference",
            "omega": "all positive-positive sums and unequal-branch positive-negative differences; equal-branch zero-frequency products separated",
        },
        "input_branch_mass_squares": {key: sp.sstr(value) for key, value in BRANCH_MASS_SQUARE.items()},
        "target_shells": {
            "ell0": {
                "sum_channels": "the physical quotient is empty at every nonzero Fourier pair K=2*n*sqrt(rho)",
                "unequal_branch_difference_channels": "the homogeneous physical quotient is empty at K=0 and Omega!=0",
            },
            "ell1": {"spectral_variable": "s=Omega^2-K^2", "extra": "s=4/3", "standard": "s=4"},
            "ell_at_least_2": {"p_extra": "s=lambda_L-2/3", "q_minus_or_q_plus": "(s-lambda_L)^2=2 lambda_L"},
        },
        "channel_count": len(channels),
        "nonzero_defect_count": total_defects,
        "channels": channels,
        "zero_frequency_remainder": {
            "source": "equal-branch products with their reality conjugates on each momentum fibre",
            "output_momentum": 0,
            "output_frequency": 0,
            "status": "OPEN",
            "required_join": "restrict the homogeneous and twist adjoint-cokernel rows and all five stabilizer moment maps to the mixed Einstein-extra coefficient carrier",
        },
        "classification": {
            "candidate_13_all_nonzero_same_fibre_channels_off_shell": True,
            "ell0_nonzero_fourier_quotient_empty_imported": True,
            "ell0_homogeneous_nonzero_frequency_quotient_empty_imported": True,
            "ell1_through_ell4_nonzero_shell_defects_certified": True,
            "same_fibre_nonzero_frequency_source_matrices_required_for_bounded_gate": False,
            "same_fibre_zero_frequency_source_matrices_classified": False,
            "mixed_Einstein_extra_taub_intersection_classified": False,
            "complete_mixed_two_fibre_tangent_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "next_gate": "compute only the zero-frequency homogeneous/twist source matrix and intersect it with the five stabilizer moment maps on the mixed q-primary plus p-primary carrier",
        "provenance": {
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()}
        },
        "claim_boundary": "This certificate proves only that every nonzero-frequency same-fibre channel in the declared candidate-13 mixed branch inventory is off shell. For ell=0, positive-positive sums use the empty nonzero-Fourier quotient while unequal-branch differences use the independently empty K=0 nonzero-frequency homogeneous quotient. Equal-branch zero-frequency sources, the mixed Taub intersection, bounded and smooth-secular tangent cones, residual, causal, observational and quantum claims remain OPEN or NO_CERTIFIED_MAP.",
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
        raise AssertionError("candidate-13 same-fibre resonance census is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_SAME_FIBRE_RESONANCE_CENSUS: PASS")


if __name__ == "__main__":
    main()
