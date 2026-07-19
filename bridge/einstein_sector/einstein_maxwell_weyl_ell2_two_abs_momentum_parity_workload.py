"""Parity-reduce the 21 isolated two-|n| resonance candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from sympy.physics.wigner import wigner_3j


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.schema.json"
INPUTS = {
    "candidates": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "same_parity": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
    "cross_parity": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.json",
    "axial_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_physical_ring.json",
    "polar_ring": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "exceptional_cofiber": ROOT / "bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json",
}
BRANCH_MULTIPLICITY = {"q_minus": 1, "p_extra": 2, "q_plus": 1, "extra": 1}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def angular_witness(output_ell: int, axisymmetric: bool) -> list[object]:
    pairs = [(0, 0)] if axisymmetric else [
        (m_1, m_2) for m_1 in range(-2, 3) for m_2 in range(-2, 3)
    ]
    for m_1, m_2 in pairs:
        output_m = m_1 + m_2
        if abs(output_m) > output_ell:
            continue
        value = wigner_3j(2, 2, output_ell, m_1, m_2, -output_m)
        if value != 0:
            return [m_1, m_2, output_m, str(value)]
    raise AssertionError(f"no angular witness for L={output_ell}, axisymmetric={axisymmetric}")


def target_parity(first: str, second: str, output_ell: int) -> str:
    same = first == second
    if same:
        return "polar" if output_ell % 2 == 0 else "axial"
    return "axial" if output_ell % 2 == 0 else "polar"


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["candidates"]["classification"]["twenty_one_distinct_admissible_candidates"]
    assert records["same_parity"]["classification"]["same_parity_output_selection_certified"]
    assert records["cross_parity"]["classification"]["cross_parity_angular_selection_certified"]
    assert records["axial_ring"]["classification"]["extra_quotient_two_cyclic_summands_on_every_physical_fiber"]
    assert records["polar_ring"]["classification"]["canonical_extra_polar_quotient_two_p_summands"]
    assert records["exceptional_cofiber"]["classification"]["exceptional_solution_cofiber_certified"]

    rows: list[dict[str, object]] = []
    total_channels = 0
    total_coefficients = 0
    output_counts: dict[str, dict[str, int]] = {}
    for index, candidate in enumerate(records["candidates"]["candidate_ledger"]["rows"], 1):
        output_ell = int(candidate["output_ell"])
        axisymmetric = output_ell % 2 == 0
        witness = angular_witness(output_ell, axisymmetric)
        parity_channels: list[dict[str, object]] = []
        for first_parity, second_parity in (
            ("axial", "axial"),
            ("polar", "polar"),
            ("axial", "polar"),
            ("polar", "axial"),
        ):
            output_parity = target_parity(first_parity, second_parity, output_ell)
            coefficient_count = (
                BRANCH_MULTIPLICITY[str(candidate["first_branch"])]
                * BRANCH_MULTIPLICITY[str(candidate["second_branch"])]
                * BRANCH_MULTIPLICITY[str(candidate["target_branch"])]
            )
            parity_channels.append({
                "first_parity": first_parity,
                "second_parity": second_parity,
                "target_parity": output_parity,
                "angular_witness_m1_m2_M_3j": witness,
                "axisymmetric_fixture_available": axisymmetric,
                "reduced_scalar_source_coefficients": coefficient_count,
            })
            total_channels += 1
            total_coefficients += coefficient_count
            key = str(output_ell)
            count = output_counts.setdefault(key, {"parity_channels": 0, "reduced_scalar_source_coefficients": 0})
            count["parity_channels"] += 1
            count["reduced_scalar_source_coefficients"] += coefficient_count
        rows.append({
            "candidate_index": index,
            "relative_spatial_sign": candidate["relative_spatial_sign"],
            "canonical_signed_momenta": candidate["canonical_signed_momenta"],
            "first_branch": candidate["first_branch"],
            "second_branch": candidate["second_branch"],
            "output_ell": output_ell,
            "target_branch": candidate["target_branch"],
            "rho": candidate["rho"],
            "temporal_channel": candidate["admissible_temporal_channel"],
            "parity_channels": parity_channels,
        })

    assert len(rows) == 21
    assert total_channels == 84
    assert total_coefficients == 164
    assert output_counts == {
        "1": {"parity_channels": 12, "reduced_scalar_source_coefficients": 12},
        "3": {"parity_channels": 24, "reduced_scalar_source_coefficients": 44},
        "4": {"parity_channels": 48, "reduced_scalar_source_coefficients": 108},
    }
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-parity-workload-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_PARITY_WORKLOAD",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": records["candidates"]["scope"],
        "selection_theorem": {
            "same_input_parity": "polar even-L and axial odd-L targets",
            "cross_input_parity": "axial even-L and polar odd-L targets",
            "axisymmetric_fixture": "available for L=4; identically absent for odd L=1,3",
            "all_m_tensor_product": "V_2 tensor V_2 contains each V_L, L=0,...,4, with multiplicity one",
            "candidate_rows_eliminated": 0,
            "naive_input_output_parity_assignments": 168,
            "allowed_parity_channels": total_channels,
        },
        "source_workload": {
            "branch_multiplicity_per_parity": BRANCH_MULTIPLICITY,
            "reduced_scalar_source_coefficients": total_coefficients,
            "by_output_ell": output_counts,
            "target_axial_coefficients": 82,
            "target_polar_coefficients": 82,
            "odd_L_coefficients_requiring_nonaxisymmetric_fixture": 56,
            "even_L4_coefficients_with_axisymmetric_fixture": 108,
            "rows": rows,
        },
        "symmetry_reduction": {
            "already_quotiented": [
                "simultaneous compact-momentum sign reversal",
                "Hessian input exchange before fixing the |n|=1 then |n|=2 canonical order",
            ],
            "not_identified": [
                "axial and polar source coefficients",
                "branch assignments to the two absolute-momentum fibres",
                "distinct algebraic circumference values",
            ],
            "reason": "No action-derived parity-duality intertwiner identifying those coefficient tensors has been certified.",
        },
        "classification": {
            "all_twenty_one_candidates_parity_typed": True,
            "all_m_angular_nonvanishing_witnessed": True,
            "odd_L_axisymmetric_fixtures_excluded": True,
            "reduced_source_workload_complete": True,
            "projected_source_coefficients_computed": False,
            "complete_two_fibre_tangent_cone_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Parity removes half of the naive source assignments but no complete candidate row. The dynamical gate is 164 action-derived reduced scalar adjoint coefficients; 56 odd-L coefficients require a nonaxisymmetric angular fixture.",
        "next_gate": "compute the 108 axisymmetric L=4 coefficients in branch-multiplicity matrices, then the 56 nonaxisymmetric L=1,3 coefficients, preserving axial/polar and |n|-fibre labels",
        "claim_boundary": "This is a parity/angular workload theorem, not a projected-source or tangent-cone theorem. It does not infer any coefficient zero, extension, obstruction, causal, residual, observational or quantum claim.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("stale ell2 two-absolute-momentum parity workload")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_PARITY_WORKLOAD: PASS")


if __name__ == "__main__":
    main()
