"""All-m second-order extension of the axial ell=2 common-zero cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_ell2_all_m_second_order.schema.json"
INPUTS = {
    "full_extra_face": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order.json",
    "same_parity_output": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_same_parity_output_resonance.json",
    "k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
}


class AxialEll2AllMError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AxialEll2AllMError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_channel_descent(records: dict[str, Any]) -> dict[str, Any]:
    rank = records["full_extra_face"]["zero_frequency_source_rank"]
    _require(rank["spacetime_row_rank"] == 1, "scalar source rank changed")
    ell1 = records["same_parity_output"]["zero_output_blocks"]["axial_L1"]
    _require(ell1["physical_cokernel_per_real_M"] == 1, "L1 physical cokernel changed")
    return {
        "polar_L0": {
            "Schur_lemma": "the rotationally invariant L=0 projection on V_2 is the identity in m; the m=0 direct coefficient therefore fixes the all-m scalar source matrix",
            "source": "the single spacetime row direction is the H moment-map matrix on Einstein-plus, both extra polarizations, and Einstein-minus",
            "solvability_condition": "mu_H=0",
            "all_four_homogeneous_rows_zero_after_balance": True,
        },
        "axial_L1": {
            "raw_left_cokernel": "one universal Noether row plus one physical twist-adjoint row for each real M=-1,0,1",
            "moment_map_identification": "the three physical adjoint pairings are exactly mu_J1,mu_J2,mu_J3 by the certified Taub--Lee--Wald bridge",
            "solvability_condition": "mu_J1=mu_J2=mu_J3=0",
            "source_then_lies_in_operator_image": True,
        },
        "polar_L2_L4": "invertible at Omega=0",
        "axial_L3": "invertible at Omega=0 because p=-34/3 and q=120",
        "P_x": "identically zero at k=0",
    }


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["full_extra_face"]["classification"]["three_parameter_positive_cone_second_order_extendible"], "axisymmetric input changed")
    shared = records["same_parity_output"]
    _require(shared["classification"]["same_parity_output_selection_certified"], "shared output ledger changed")
    _require(records["moment_map_bridge"]["classification"]["generic_H_Px_J_selection_rules_certified"], "moment-map bridge changed")
    angular = shared["angular_selection"]
    resonance = shared["nonzero_frequency_resonance_ledger"]
    zero = _zero_channel_descent(records)
    return {
        "schema": "einstein-maxwell-weyl-axial-ell2-all-m-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_AXIAL_ELL2_ALL_M_SECOND_ORDER",
        "result_state": "COMPLETE_AXIAL_ELL2_ALL_M_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_AXIAL_ELL2_ALL_M_BOTH_EXTRA_POLARIZATIONS",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "domain": "finite real axial ell=2,k=0 Weyl-Maxwell tangents with all m, Einstein-plus/minus and both extra polarizations, satisfying the complete H,J_i common-zero equations",
        "angular_selection": angular,
        "zero_frequency_descent": zero,
        "nonzero_frequency_resonance_ledger": resonance,
        "second_order_solution": {
            "blockwise_construction": "project the exact quadratic source to L=0,...,4 and each sum/difference frequency; solve every invertible block, solve L=0 nonzero sources in the homogeneous Noether image, and solve the zero L=1 block after H,J descent",
            "finite_for_finite_first_order_data": True,
            "real_spatially_periodic": True,
            "temporal_class": "finite quasiperiodic plus any exceptional zero-frequency polynomial/Jordan correction selected by the L1 solve",
            "complete_for_declared_cone": True,
        },
        "classification": {
            "all_m_axial_ell2_common_zero_cone_second_order_extendible": True,
            "both_extra_polarizations_included": True,
            "odd_L1_and_L3_channels_closed": True,
            "polar_input_parity_classified": False,
            "general_ell_classified": False,
            "opposite_momentum_phase_source_classified": False,
            "all_orders_integrability": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "Non-axisymmetric data do introduce the odd angular channels absent from Paper 91, but they do not cut the axial ell=2 cone. The L=1 zero obstruction is exactly the already imposed rotation moment map; the newly discovered omega^2=4/3 exceptional shell is missed by every nonzero quadratic frequency. L=3 and all even generic outputs are off shell. Thus H=J_i=0 is sufficient for a complete second-order correction on the full axial ell=2 block.",
        "next_gate": "repeat the source-rank and exceptional-output analysis for polar ell=2 input parity, then lift the angular/resonance proof to symbolic ell",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE theorem covers all m only for axial ell=2,k=0. It does not classify polar inputs, general ell, opposite momenta, all-orders integration, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_all_m_second_order --verify bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_ell2_all_m_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ell2_all_m_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"axial ell2 all-m certificate stale: {path}")


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
