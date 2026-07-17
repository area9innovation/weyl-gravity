"""Complete axial-plus-polar ell=2,k=0 common-zero cone at second order."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_combined_cone_second_order.schema.json"
INPUTS = {
    "axial_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json",
    "polar_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_ell2_all_m_second_order.json",
    "cross_output": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_cross_parity_output_resonance.json",
    "moment_map_bridge": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "k0_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
}


class Ell2CombinedConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Ell2CombinedConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    axial = records["axial_cone"]
    polar = records["polar_cone"]
    cross = records["cross_output"]
    bridge = records["moment_map_bridge"]
    cone = records["k0_cone"]

    _require(axial["classification"]["all_m_axial_ell2_common_zero_cone_second_order_extendible"], "axial cone input changed")
    _require(polar["classification"]["all_m_polar_ell2_common_zero_cone_second_order_extendible"], "polar cone input changed")
    _require(cross["classification"]["cross_zero_frequency_physical_cokernel_absent"], "cross zero-frequency gate changed")
    _require(cross["classification"]["all_nine_cross_frequency_types_off_all_target_shells"], "cross nonzero-frequency gate changed")
    parity_rule = bridge["generic_moment_maps"]["polarized_rules"]["axial_polar_mixed"]
    _require(parity_rule.startswith("zero by"), "axial-polar moment-map orthogonality changed")
    _require(cone["classification"]["full_generic_k0_common_zero_cone_classified"], "k0 cone input changed")

    axial_scalar = axial["zero_frequency_descent"]["polar_L0"]
    polar_scalar = polar["zero_frequency_descent"]["polar_L0"]
    _require(axial_scalar["all_four_homogeneous_rows_zero_after_balance"], "axial scalar-source theorem changed")
    _require(polar_scalar["spacetime_row_rank"] == 1, "polar scalar-source rank changed")

    return {
        "schema": "einstein-maxwell-weyl-ell2-combined-cone-second-order-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_COMBINED_CONE_SECOND_ORDER",
        "result_state": "COMPLETE_AXIAL_POLAR_ELL2_K0_COMMON_ZERO_CONE_SECOND_ORDER_EXTENDIBLE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ELL2_K0_ALL_M_BOTH_PARITIES_ALL_GENERIC_PRIMARIES",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "domain": "finite real generic ell=2,k=0 Weyl-Maxwell tangents with all m, both axial and polar parities, Einstein-plus/minus and both extra polarizations, satisfying total H=J_1=J_2=J_3=0",
        "quadratic_decomposition": {
            "formula": "D2E[u_A+u_P,u_A+u_P]/2 = D2E[u_A,u_A]/2 + D2E[u_P,u_P]/2 + D2E[u_A,u_P]",
            "axial_self_output": "even total parity: polar even-L and axial odd-L",
            "polar_self_output": "even total parity: polar even-L and axial odd-L",
            "axial_polar_cross_output": "odd total parity: polar odd-L and axial even-L; axial L0 absent",
        },
        "obstruction_descent": {
            "moment_map_cross_terms": parity_rule,
            "scalar_L0": "the axial and polar rank-one source columns share (1,0,1/2,0); their coefficients add to the total mu_H and cancel when total H=0",
            "axial_L1": "the pure-sector physical adjoint pairings add to total mu_Ji and cancel when total J_i=0",
            "cross_terms": "no physical adjoint cokernel in any zero-frequency cross-output block",
            "complete_static_condition": "total H=J_1=J_2=J_3=0; P_x vanishes identically at k=0",
        },
        "nonzero_frequency_descent": {
            "pure_same_parity_blocks": "all nine types are off shell by the shared same-parity ledger used in both pure cone theorems",
            "cross_parity_blocks": "all nine types are off every polar L1,L3 and axial L2,L4 shell",
            "relative_phases": "arbitrary constant phases are retained; invertibility is coefficient-independent",
        },
        "second_order_solution": {
            "construction": "project the total exact source by output L, parity, and frequency; use total H,J cancellation in the only physical zero cokernels and invert every remaining quotient block; lift through the target Noether identities",
            "finite_for_finite_first_order_data": True,
            "real_spatially_periodic": True,
            "temporal_class": "finite quasiperiodic plus any zero-frequency polynomial/Jordan correction selected by the axial L1 solve",
            "complete_for_declared_combined_cone": True,
        },
        "classification": {
            "complete_combined_ell2_k0_common_zero_cone_second_order_extendible": True,
            "all_m_both_parities_and_both_extra_polarizations_included": True,
            "cross_parity_sources_solved_without_coefficient_table": True,
            "cancellations_between_axial_and_polar_moment_maps_included": True,
            "general_ell_classified": False,
            "opposite_momentum_phase_source_classified": False,
            "all_orders_integrability": False,
            "final_residual_descent_certified": False,
            "Lorentzian_causal_or_quantum_claim": False,
        },
        "interpretation": "At ell=2,k=0 the nonlinear tangent cone is exactly as large as the stabilizer moment-map test permits at second order. Pure axial and pure polar sources contribute the known H and J_i obstructions, including cancellations between parities, while every axial-polar cross source lands in an invertible quotient block. No additional quadratic condition survives.",
        "next_gate": "test whether the source-rank and resonance argument persists for symbolic ell, then retain opposite-momentum relative phases",
        "claim_boundary": "This theorem is restricted to the generic ell=2,k=0 local-gauge-reduced block. It does not include exceptional/global tangents, general ell, opposite momentum, all-orders integration, final residual states, causal propagation, particles, or quantum theory.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_combined_cone_second_order --verify bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_combined_cone_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_combined_cone_second_order",
        ],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(payload == build_certificate(), f"ell2 combined cone certificate stale: {path}")


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
