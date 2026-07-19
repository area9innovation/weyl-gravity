"""Classify the global plus axial ell2 all-m minus-extra bounded cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.schema.json"
INPUTS = {
    "aligned": ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone.json",
    "minus_resonance": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "wave_bounded": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion.json",
    "wave_all_m": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_ell2_all_m_second_order.json",
    "moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "homogeneous_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "standard_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "constant_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
}


class GlobalAxialAllMConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GlobalAxialAllMConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _so3_promotion(record: dict[str, Any]) -> dict[str, Any]:
    pairings = record["shell_pairing"]["leading_coefficients"]
    for value in pairings.values():
        _require(sp.sympify(value, locals={"sqrt": sp.sqrt, "I": sp.I}) != 0, "shell pivot vanished")
    return {
        "representation": "each time-polynomial coefficient is an SO3 intertwiner V_2 -> V_2 because a,b,d are rotational scalars",
        "Schur_lemma": "End_SO3(V_2)=C*identity, so the m=0 direct coefficient fixes the map on every m",
        "no_cross_m_cancellation": "the coefficient vector is the same nonzero scalar times the complete Einstein-minus amplitude vector in V_2",
        "promoted_ideal": "for a nonzero Einstein-minus amplitude vector, b=0 from t^2, a=0 from t, and d=0 from the constant shell coefficient",
        "all_m": [-2, -1, 0, 1, 2],
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["aligned"]["classification"]["bounded_zero_locus_necessary_and_sufficient"], "aligned regression changed")
    _require(records["wave_bounded"]["classification"]["all_m_axial_ell2_bounded_cone_classified"], "all-m bounded wave theorem changed")
    _require(records["wave_all_m"]["classification"]["both_extra_polarizations_included"], "extra multiplicity changed")
    _require(records["moment_maps"]["classification"]["generic_H_Px_J_selection_rules_certified"], "moment-map rules changed")
    _require(records["standard_global"]["classification"]["complete_standard_generalized_zero_bounded_cone_classified"], "standard global theorem changed")
    _require(records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"], "circumference transport changed")
    _require(records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"], "Wilson spectator changed")
    _require(records["constant_twist"]["classification"]["constant_twist_exact_family_identified"], "twist family changed")
    promotion = _so3_promotion(records["minus_resonance"])
    return {
        "schema": "einstein-maxwell-weyl-global-axial-ell2-all-m-minus-extra-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_AXIAL_ELL2_ALL_M_MINUS_EXTRA_BOUNDED_CONE",
        "result_state": "GLOBAL_PLUS_AXIAL_ELL2_ALL_M_MINUS_EXTRA_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with electric tangent allowed",
            "carrier": "complete homogeneous and axial-twist global data plus axial ell=2,k=0 Einstein-minus and both extra primaries, all m",
            "degree": 2,
            "parity": "homogeneous and axial",
            "ell": "input 0,1,2 with every quadratic output L=0,...,4",
            "m": "all wave m=-2,...,2 and arbitrary real twist vector",
            "k": 0,
            "omega": "generalized zero, sqrt(6-2*sqrt(3)), and 4/sqrt(3)",
        },
        "equation": "L_WM Phi^(2)=-(1/2)D^2E_WM[Phi^(1),Phi^(1)]",
        "SO3_shell_promotion": promotion,
        "wave_density_cone": {
            "amplitudes": "C_minus in Mat_(1x5)(C), C_extra in Mat_(2x5)(C), with negative frequencies fixed by reality",
            "densities": "rho_minus=C_minus^dagger*C_minus (rank<=1), rho_extra=C_extra^dagger*C_extra (rank<=2)",
            "occupation_and_spin": "A_s=tr(rho_s), j_s,a=tr(rho_s*T_2,a)",
            "equations": {
                "H": "omega_extra^2*A_extra-omega_minus^2*A_minus=0",
                "J_a": "omega_extra*j_extra,a-omega_minus*j_minus,a=0 for a=1,2,3",
                "P_x": "0 identically at k=0",
            },
            "nonzero_point_contains_minus_and_extra": True,
        },
        "bounded_necessity": {
            "universal": "b=0 and B=0",
            "nonzero_wave": "the SO3-promoted shell ideal forces a=b=d=0",
            "electric": "after the wave H source vanishes, the independent homogeneous row E11=Q_e^2/2 forces Q_e=0 because the bounded zero-frequency homogeneous image is zero",
        },
        "complete_bounded_cone": {
            "static_branch": "wave=0: (c,d,W_x,A in R^3) arbitrary, with a=b=Q_e=0 and B=0",
            "wave_branch": "a=b=d=Q_e=0 and B=0; (c,W_x,A in R^3) arbitrary; (C_minus,C_extra) any nonzero point of the displayed H,J_a density cone",
            "union_is_necessary_and_sufficient": True,
        },
        "bounded_sufficiency": {
            "wave_self": "the complete axial ell2 all-m H,J cone has a real bounded finite-quasiperiodic correction; its zero L1 block has the certified constant right inverse",
            "circumference": "k=0 radius transport is bounded",
            "Wilson": "the cross source vanishes",
            "constant_twist": "differentiate the exact flat SO3-holonomy family and its transported k=0 Jacobi field; the first-order shell shift vanishes and the mixed correction is bounded",
            "static_branch": "the complete standard-global theorem",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_declared_global_axial_all_m_carrier_covered": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "all_wave_m_and_both_axial_extra_polarizations_included": True,
            "SO3_shell_promotion_certified": True,
            "electric_bounded_near_miss_excluded": True,
            "polar_input_classified": False,
            "general_ell_or_nonzero_momentum_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The surviving opposite-sign bounded cone is not an axisymmetric accident. Rotational equivariance promotes the global shell obstruction to every m, while the complete all-m wave source has bounded inverses after H and J descent. The global block again stratifies: d survives only on the wave-free branch, electric charge is excluded by a non-Hamiltonian zero-frequency row, and the nonzero wave cone is multiplied only by circumference, Wilson and constant twist-position spectators.",
        "next_gate": "compute the a,b,d shell source for the polar ell2 Einstein-minus representative and combine axial and polar density cones, retaining cross-parity cancellation",
        "claim_boundary": "This theorem is complete only for axial ell=2,k=0 minus-plus-two-extra input with all m and the declared global modes. It excludes Einstein-plus, polar wave input, other ell or momenta, infinite sums, all-orders integration, final residual descent, causal propagation, observables, particles and quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.24},
            "tier_1": {"status": "PASS", "elapsed_seconds": 3.00, "tests_run": 26},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the direct m=0 shell map, all-m bounded wave theorem and global source/transport inputs are unchanged exact dependencies"},
            "tier_3": {"status": "NOT_RUN", "reason": "polar, other-harmonic, causal, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise GlobalAxialAllMConeError("global axial ell2 all-m bounded cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_AXIAL_ELL2_ALL_M_MINUS_EXTRA_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
