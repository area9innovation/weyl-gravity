"""All-m second-order extension of the polar ell=2 common-zero cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_all_m_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_polar_ell2_all_m_second_order.schema.json"
INPUTS = {
    "same_parity_output": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "polar_linear_completion": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "polar_plus_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_plus_zero_source_fixture.json",
    "polar_minus_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_minus_zero_source_fixture.json",
    "polar_extra_e1_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_e1_zero_source_fixture.json",
    "polar_extra_e2_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_e2_zero_source_fixture.json",
    "polar_extra_cross_fixture": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_extra_cross_zero_source_fixture.json",
}


class PolarEll2AllMError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarEll2AllMError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_channel_descent(records: dict[str, Any]) -> dict[str, Any]:
    ell1 = records["same_parity_output"]["zero_output_blocks"]["axial_L1"]
    _require(ell1["physical_cokernel_per_real_M"] == 1, "L1 physical cokernel changed")
    fixture_names = ("polar_plus_fixture", "polar_minus_fixture", "polar_extra_e1_fixture", "polar_extra_e2_fixture")
    sources = {
        name: [sp.sympify(value) for value in records[name]["homogeneous_source_rows_E00_E11_E22_Maxwell1"]]
        for name in fixture_names
    }
    source_matrix = sp.Matrix.hstack(*(sp.Matrix(sources[name]) for name in fixture_names))
    _require(source_matrix.rank() == 1, f"polar Hermitian source rank changed: {source_matrix}")
    for source in sources.values():
        _require(source[1] == 0 and source[3] == 0 and sp.simplify(2 * source[2] - source[0]) == 0, "polar source row direction changed")
    cross = records["polar_extra_cross_fixture"]["homogeneous_source_rows_E00_E11_E22_Maxwell1"]
    _require(cross == ["0", "0", "0", "0"], "polar extra interference source changed")
    return {
        "polar_L0": {
            "formal_obstruction": "the constant-lapse adjoint pairing is exactly mu_H by the Taub--Lee--Wald bridge",
            "solvability_condition": "mu_H=0",
            "direct_Hermitian_source_columns_plus_minus_e1_e2": {
                name: [str(value) for value in sources[name]] for name in fixture_names
            },
            "spacetime_row_rank": 1,
            "common_row_direction": ["1", "0", "1/2", "0"],
            "extra_e1_e2_interference": cross,
            "basis_normalization": "the unit e1=(0,1,0,0) has k=0 Hermitian current weight 9; the published Lee--Wald basis vector is 16*omega_e times e1",
            "source_cancellation": "Schur's lemma promotes the m=0 internal source matrix to every m; H=0 therefore cancels all four homogeneous source rows exactly",
        },
        "axial_L1": {
            "raw_left_cokernel": "one universal Noether row plus one physical twist-adjoint row for each real M=-1,0,1",
            "moment_map_identification": "the three physical adjoint pairings are mu_J1,mu_J2,mu_J3",
            "solvability_condition": "mu_J1=mu_J2=mu_J3=0",
            "source_then_lies_in_operator_image": True,
        },
        "polar_L2_L4": "invertible at Omega=0",
        "axial_L3": "invertible at Omega=0 because p=-34/3 and q=120",
        "P_x": "identically zero at k=0",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    polar_completion = records["polar_linear_completion"]
    _require(
        polar_completion["classification"]["canonical_extra_polar_quotient_two_p_summands"],
        "polar primary decomposition changed",
    )
    _require(
        records["polar_current"]["classification"]["direct_four_dimensional_Lee_Wald_match"],
        "polar current gate changed",
    )
    shared_output = records["same_parity_output"]
    _require(
        shared_output["classification"]["same_parity_output_selection_certified"],
        "shared output audit changed",
    )
    resonance = shared_output["nonzero_frequency_resonance_ledger"]
    _require(len(resonance["nine_nonzero_frequency_types"]) == 9, "frequency ledger changed")
    return {
        "schema": "einstein-maxwell-weyl-polar-ell2-all-m-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_POLAR_ELL2_ALL_M_SECOND_ORDER",
        "result_state": "COMPLETE_POLAR_ELL2_ALL_M_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_POLAR_ELL2_ALL_M_BOTH_EXTRA_POLARIZATIONS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "finite real polar ell=2,k=0 Weyl-Maxwell tangents with all m, Einstein-plus/minus and both extra polarizations, satisfying the complete H,J_i common-zero equations",
        "linear_input": {
            "target_module": "K[omega]/(q) direct-sum (K[omega]/(p))^2",
            "two_extra_polarizations": True,
            "extra_current_positive_nondegenerate_before_residual_descent": True,
        },
        "angular_selection": shared_output["angular_selection"],
        "zero_frequency_descent": _zero_channel_descent(records),
        "nonzero_frequency_resonance_ledger": resonance,
        "second_order_solution": {
            "construction": "project the exact quadratic source to L=0,...,4 and every sum/difference frequency; impose H=J_i=0 on the only physical zero-frequency adjoint pairings and invert all remaining blocks",
            "why_source_rank_is_not_an_extra_assumption": "Fredholm solvability depends on the complete adjoint cokernel, not on literal vanishing of each source row; the Taub bridge exhausts the physical L=0,1 pairings",
            "finite_for_finite_first_order_data": True,
            "real_spatially_periodic": True,
            "temporal_class": "finite quasiperiodic plus any exceptional zero-frequency polynomial/Jordan correction selected by the L1 solve",
            "complete_for_declared_polar_cone": True,
        },
        "classification": {
            "all_m_polar_ell2_common_zero_cone_second_order_extendible": True,
            "both_extra_polarizations_included": True,
            "odd_L1_and_L3_channels_closed": True,
            "axial_polar_mixed_cross_terms_classified": False,
            "general_ell_classified": False,
            "opposite_momentum_phase_source_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "The polar ell=2 sector has the same output parity and frequency ledger as the axial sector. Its only physical zero-frequency obstructions are again H and the rotation triplet. Hence the common-zero moment-map equations are sufficient for a complete second-order correction on the full polar block; the direct unit-extra source independently fixes the normalization of the scalar pairing.",
        "next_gate": "classify axial--polar cross sources, whose odd total parity produces polar odd-L and axial even-L outputs, before taking the direct sum of the two cone theorems",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers all m only for pure polar ell=2,k=0 input. It does not include axial--polar cross terms, general ell, opposite momenta, all-orders integration, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ell2_all_m_second_order --verify bridge/certificates/einstein_maxwell_weyl_polar_ell2_all_m_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_ell2_all_m_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ell2_all_m_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"polar ell2 all-m certificate stale: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.write:
        DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify:
        verify_certificate(args.verify)
    if not args.write and not args.verify:
        parser.error("one of --write or --verify is required")


if __name__ == "__main__":
    main()
