#!/usr/bin/env python3
"""Produce the fail-closed outgoing analytic K-plus moving-phase gate."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp

from .algebra import derive


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"

INPUTS = {
    "joint_rank3_frame": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_outgoing_joint_frame_r31_v1/certificate.json"
    ),
    "partial_jet_crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "formal_frame_completion": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_outgoing_frame_completion_v1/certificate.json"
    ),
    "endpoint_frame_audit": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_endpoint_frames_v1/certificate.json"
    ),
    "metric_heads": ROOT / (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/infinity-metric-heads.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def clean(value: sp.Expr) -> str:
    return sp.sstr(sp.factor(value))


def produce() -> dict:
    imported = {
        name: json.loads(path.read_text()) for name, path in INPUTS.items()
    }
    joint = imported["joint_rank3_frame"]
    crosswalk = imported["partial_jet_crosswalk"]
    formal = imported["formal_frame_completion"]
    endpoint = imported["endpoint_frame_audit"]
    heads = imported["metric_heads"]

    if joint["status"] != (
        "JOINT_REDUCED_FRAME_RANK3_KPLUS_ANALYTIC_OPEN"
    ):
        raise RuntimeError("joint reduced frame did not pass")
    if not crosswalk["claim_flags"]["partial_spin_two_row_jet_exact"]:
        raise RuntimeError("partial-jet crosswalk drifted")
    if not formal["claim_flags"]["formal_K_plus_zero_in_canonical_gauge"]:
        raise RuntimeError("formal K-plus zero drifted")
    for label in ("XI2", "XI3"):
        recurrence = heads["branches"][label]["recurrence"]
        if recurrence["forced_log_coefficient"] != "0":
            raise RuntimeError(f"{label} acquired a forced logarithm")
        if recurrence["free_EI2_coefficient"] != (
            "0 (canonical particular lift)"
        ):
            raise RuntimeError(f"{label} free Einstein shear drifted")

    data = derive(crosswalk["exact_blocks"])
    if data["rate_derivative"] != -sp.Rational(3, 4):
        raise RuntimeError("outgoing rate derivative drifted")
    if data["power_derivative"] != 0:
        raise RuntimeError("outgoing logarithmic-power derivative drifted")
    if data["E12_linear_coefficient"] != sp.Rational(3, 4):
        raise RuntimeError("E12 irregular coefficient drifted")
    if data["E22_constant"] != -sp.Rational(3, 4):
        raise RuntimeError("E22 asymptotic coefficient drifted")
    if data["irregular_homological_residual"] != sp.zeros(2):
        raise RuntimeError("polynomial moving gauge did not remove r*E_-1")
    if data["combined_moving_generator"] != sp.diag(
        0, -sp.Rational(3, 4)
    ):
        raise RuntimeError("combined moving generator drifted")

    radius = sp.Integer(31)
    relative_log_derivative = sp.simplify(
        -data["rate_derivative"] * radius
        - data["power_derivative"] * sp.log(radius)
    )
    if relative_log_derivative != sp.Rational(93, 4):
        raise RuntimeError("relative normalizer derivative drifted")

    exact_audit = formal["exact_normalization_audit"]
    free_constants_zero = (
        exact_audit["canonical_free_EI2_XI2"] == "0"
        and exact_audit["canonical_free_EI2_XI3"] == "0"
    )
    leading_amplitudes_tau_independent = (
        formal["formal_endpoint_jet"]["unit_leading_amplitudes_force"]
        == "k2=0"
    )
    rephasing_tau_independent = relative_log_derivative == 0

    return {
        "schema": (
            "phase3-axial-partial-jet-outgoing-kplus-moving-phase-gate-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_OUTGOING_KPLUS_MOVING_PHASE_GATE_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "CLASSIFIED",
        "status": "KPLUS_ZERO_WITHHELD_NONSTATIC_REPHASING",
        "imports": {name: record(path) for name, path in INPUTS.items()},
        "domain": {
            "endpoint": "Iplus",
            "matching_radius": "31",
            "omega_child": joint["domain"]["omega_child"],
            "frequency_excludes_zero": True,
        },
        "exact_asymptotic_audit": {
            "fixed_phase": "exp(-2*I*omega*r)*r**(-4*I*omega)",
            "fixed_rate": clean(data["fixed_rate"]),
            "fixed_power": clean(data["fixed_power"]),
            "intrinsic_rate_derivative": clean(data["rate_derivative"]),
            "intrinsic_power_derivative": clean(data["power_derivative"]),
            "E12_coefficient_of_r": clean(data["E12_linear_coefficient"]),
            "E22_constant_term": clean(data["E22_constant"]),
            "phase_reduced_constant_matrix": [
                [clean(value) for value in row]
                for row in data["reduced_constant"].tolist()
            ],
            "irregular_E_coefficient_matrix": [
                [clean(value) for value in row]
                for row in data["E_irregular"].tolist()
            ],
            "canonical_polynomial_eigenvector_gauge_B": [
                [clean(value) for value in row]
                for row in data["polynomial_gauge"].tolist()
            ],
            "irregular_homological_identity": "E_minus1+[A0,B]=0",
            "irregular_homological_residual": [
                [clean(value) for value in row]
                for row in data["irregular_homological_residual"].tolist()
            ],
            "combined_scalar_and_matrix_moving_generator": [
                [clean(value) for value in row]
                for row in data["combined_moving_generator"].tolist()
            ],
            "local_eigenvalue_derivative": clean(
                data["local_eigenvalue_derivative"]
            ),
            "local_eigenvalue_derivative_series": str(
                data["derivative_remainder_series"]
            ),
            "method": (
                "differentiate the exact characteristic polynomial of the "
                "phase-reduced A_RW+tau*E_RW pencil; the unperturbed outgoing "
                "reduced eigenvalue is O(r^-2), so lambda=0 determines the "
                "constant and r^-1 derivative coefficients exactly"
            ),
        },
        "factor_phase_derivatives": {
            "spin_two_R_E": {
                "rate_derivative": "-3/4",
                "power_derivative": "0",
                "moving_phase": (
                    "exp((-2*I*omega-3*tau/4)*r)"
                    "*r**(-4*I*omega)+O(tau**2)"
                ),
            },
            "spin_one_S": {
                "rate_derivative": "0",
                "power_derivative": "0",
                "reason": (
                    "the exact partial jet holds Z and A_x tau-independent"
                ),
            },
        },
        "common_gauge_reissue_at_r31": {
            "tau_zero_relative_S_over_R": (
                "(32/31)*exp(I*omega*(64+4*log(32)))"
            ),
            "tau_zero_relative_factor_analytic_nonzero": True,
            "relative_log_tau_derivative": clean(relative_log_derivative),
            "relative_rephasing_tau_independent": rephasing_tau_independent,
            "R_moving_reduced_tangent": (
                "R_tangent_fixed + diag(0,93/4)*R_base"
            ),
            "S_in_R_moving_gauge_base": (
                "h0*S_base, h0=(32/31)"
                "*exp(I*omega*(64+4*log(32)))"
            ),
            "S_in_R_moving_gauge_tangent": (
                "h0*(S_tangent_fixed + diag(0,93/4)*S_base_Y)"
            ),
            "interpretation": (
                "The tau-zero phase ratio is harmless, but the analytic "
                "moving spin-two phase and polynomial eigenvector gauge make "
                "the common R/S normalizer tau-dependent. The existing fixed-"
                "phase checkpoints are therefore not yet one analytic "
                "endpoint tau-frame."
            ),
        },
        "recurrence_and_normalization_audit": {
            "forced_log_XI2": exact_audit["forced_log_XI2"],
            "forced_log_XI3": exact_audit["forced_log_XI3"],
            "canonical_free_EI2_XI2": (
                exact_audit["canonical_free_EI2_XI2"]
            ),
            "canonical_free_EI2_XI3": (
                exact_audit["canonical_free_EI2_XI3"]
            ),
            "free_EI2_constants_zero": free_constants_zero,
            "leading_factor_amplitudes_tau_independent_in_formal_gauge": (
                leading_amplitudes_tau_independent
            ),
            "formal_canonical_K_plus": [["0", "0"], ["0", "0"]],
            "analytic_K_plus_promoted": False,
            "reason_not_promoted": (
                "the exact nonzero rate derivative forces a tau-dependent "
                "relative R/S phase normalizer; the fixed-phase correlated "
                "checkpoint has not been reissued with the displayed moving-"
                "phase tangent corrections"
            ),
        },
        "minimal_missing_object": {
            "name": "outgoing_moving_phase_correlated_checkpoint_r31",
            "required_fields": [
                (
                    "R_tangent_moving=R_tangent_fixed"
                    "+diag(0,93/4)*R_base"
                ),
                "S_base_common=h0*S_base",
                (
                    "S_tangent_common=h0*(S_tangent_fixed"
                    "+diag(0,93/4)*S_base_Y)"
                ),
                "one shared analytic omega generator or a typed symbolic h0",
                "independent containment/restart verification",
            ],
            "then_reaudit": (
                "unit leading amplitudes and zero free EI2 constants in the "
                "moving factor phases before deciding analytic K_plus"
            ),
        },
        "claim_flags": {
            "joint_reduced_frame_rank_three_imported": True,
            "outgoing_rate_derivative_exact": True,
            "outgoing_power_derivative_exact": True,
            "tau_zero_common_phase_factor_exact": True,
            "relative_rephasing_tau_independent": False,
            "formal_K_plus_zero_preserved": True,
            "analytic_K_plus_zero_certified": False,
            "T_plus_certified": False,
            "stokes_or_scattering_certified": False,
        },
        "does_not_establish": [
            "an analytic endpoint K_plus=0 theorem",
            "a common moving-phase correlated E/R/S checkpoint",
            "T_plus, Stokes conservation, reflection, scattering, or flux",
        ],
        "next_gate": (
            "apply the exact moving-phase tangent corrections at r=31, "
            "serialize the rephased R/E/S models with preserved correlation, "
            "and independently verify their endpoint normalization before "
            "reconsidering analytic K_plus"
        ),
        "producer_elapsed_seconds": 0.0,
    }


def main() -> int:
    check = "--check" in sys.argv
    result = produce()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if check:
        if not CERTIFICATE.exists() or CERTIFICATE.read_text() != text:
            print("certificate drift", file=sys.stderr)
            return 2
    else:
        CERTIFICATE.write_text(text)
    print(result["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
