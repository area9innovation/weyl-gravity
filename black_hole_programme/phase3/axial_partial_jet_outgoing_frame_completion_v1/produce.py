#!/usr/bin/env python3
"""Produce the fail-closed outgoing endpoint-frame completion preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"

INPUTS = {
    "endpoint_frames": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_endpoint_frames_v1/certificate.json"
    ),
    "reduced_rplus": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_infinity_reduced_phase_preflight_v1/certificate.json"
    ),
    "practical_infinity": ROOT / (
        "black_hole_programme/phase3/"
        "axial_infinity_practical_transfer/certificate.json"
    ),
    "crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "metric_heads": ROOT / (
        "black_hole_programme/phase3/"
        "axial_endpoint_remainder_enclosures/infinity-metric-heads.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_audit(frames: dict, heads: dict) -> dict:
    omega = sp.Symbol("omega", nonzero=True)
    I = sp.I
    pi_x_xi2 = 2 * (16 * omega**2 - 4 * I * omega - 5)
    pi_x_xi3 = -2 * I * omega
    r_coefficient = -I * (16 * omega**2 - 4 * I * omega - 5) / omega
    s_rescaling = I / (2 * omega)
    e_rescaling = sp.Integer(2)

    r_quotient = sp.factor(pi_x_xi2 + r_coefficient * pi_x_xi3)
    s_quotient = sp.factor(s_rescaling * pi_x_xi3)
    e_amplitude = sp.factor(e_rescaling * sp.Rational(1, 2))

    plus = frames["endpoint_frames"]["Iplus"]
    if plus["factor_lines"] != {
        "E": "EI2",
        "R": "XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega",
        "S": "XI3",
    }:
        raise RuntimeError("outgoing factor lines drifted")
    if plus["rescalings_to_R_unit_S_unit_E_matches_R"] != [
        "1", "I/(2*omega)", "2"
    ]:
        raise RuntimeError("outgoing factor rescalings drifted")
    for label in ("XI2", "XI3"):
        branch = heads["branches"][label]
        if branch["recurrence"]["forced_log_coefficient"] != "0":
            raise RuntimeError(f"{label} acquired a forced logarithm")
        if branch["recurrence"]["free_EI2_coefficient"] != (
            "0 (canonical particular lift)"
        ):
            raise RuntimeError(f"{label} canonical EI2 shear drifted")
    if r_quotient != 0 or s_quotient != 1 or e_amplitude != 1:
        raise RuntimeError("unit factor normalization identity failed")

    return {
        "pi_x_XI2": sp.sstr(pi_x_xi2),
        "pi_x_XI3": sp.sstr(pi_x_xi3),
        "pi_x_R": sp.sstr(r_quotient),
        "pi_x_S": sp.sstr(s_quotient),
        "normalized_E_scalar_amplitude": sp.sstr(e_amplitude),
        "forced_log_XI2": "0",
        "forced_log_XI3": "0",
        "canonical_free_EI2_XI2": "0",
        "canonical_free_EI2_XI3": "0",
    }


def document() -> dict:
    imported = {
        name: json.loads(path.read_text()) for name, path in INPUTS.items()
    }
    frames = imported["endpoint_frames"]
    reduced = imported["reduced_rplus"]
    practical = imported["practical_infinity"]
    crosswalk = imported["crosswalk"]
    heads = imported["metric_heads"]
    audit = exact_audit(frames, heads)

    if not reduced["claim_flags"]["outgoing_Jost_column_certified"]:
        raise RuntimeError("selected R+ Jost column is not certified")
    if not practical["claim_flags"]["full_rank_R32_initializer_certified"]:
        raise RuntimeError("six-state practical infinity initializer drifted")
    if not crosswalk["claim_flags"]["partial_spin_two_row_jet_exact"]:
        raise RuntimeError("exact partial-jet generator drifted")

    return {
        "schema": "phase3-axial-partial-jet-outgoing-frame-completion-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_PARTIAL_JET_OUTGOING_FRAME_COMPLETION"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "status": "FORMAL_FRAME_COMPLETE_CORRELATED_S_REMAINDER_OPEN",
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in INPUTS.items()
        },
        "typed_conventions": {
            "six_state_factor_order": [
                "X=metric_RW_tau_tangent",
                "Y=carrier_RW_base",
                "Z=Lx_spin_one",
            ],
            "outgoing_trace_order": ["E", "R", "S"],
            "old_endpoint_line_order": ["XI2", "XI3", "EI2"],
            "common_physical_phase": "exp(-2*I*omega*rstar)",
            "formal_phase": "exp(-2*I*omega*r)*r**(-4*I*omega)",
            "bounded_real_axis_conjugator": "(1-2/r)**(4*I*omega)",
            "phase_is_never_omega_taylor_expanded_at_infinity": True,
        },
        "normalized_columns": {
            "E": {
                "line": "2*EI2",
                "role": "epsilon-copy of the unit outgoing spin-two Jost line",
                "quotient": "0",
                "all_order_phase_factored_remainder": "REUSED_FROM_R_PLUS",
            },
            "R": {
                "line": (
                    "XI2-I*(16*omega**2-4*I*omega-5)*XI3/omega"
                ),
                "role": "unit outgoing carrier spin-two base line",
                "quotient": "0",
                "all_order_phase_factored_remainder": "CERTIFIED",
            },
            "S": {
                "line": "I*XI3/(2*omega)",
                "role": "unit outgoing spin-one quotient line",
                "quotient": "1",
                "all_order_six_state_existence": "CERTIFIED_AT_R32",
                "all_order_correlated_omega_dual_tau_remainder": "OPEN",
            },
        },
        "exact_normalization_audit": audit,
        "formal_endpoint_jet": {
            "analytic_formal_tau_recurrence": True,
            "reason": (
                "the real nonzero-frequency pivots are nonzero, XI2/XI3 "
                "have zero forced logs, the leading R and S amplitudes are "
                "tau-independent, and both canonical free EI2 constants "
                "are zero"
            ),
            "K_plus_allowed_shape": [["k2", "h"], ["0", "0"]],
            "unit_leading_amplitudes_force": "k2=0",
            "zero_free_EI2_constants_force": "h=0",
            "K_plus_canonical_formal": [["0", "0"], ["0", "0"]],
            "K_plus_validated_analytic": False,
        },
        "remainder_contract": {
            "E_R_common_omega_dual_tau": True,
            "S_six_state_all_order_existence": True,
            "S_common_omega_dual_tau": False,
            "missing_object": (
                "a phase-factored XI3/S remainder serialized in the same "
                "IvTaylor4_omega tensor dual_tau generator as R+"
            ),
            "why_existing_initializer_is_insufficient": (
                "the practical R=32 six-state box proves existence and rank "
                "but rectangularizes the base/tangent pieces and does not "
                "export their common omega generator or dual coefficient"
            ),
        },
        "claim_flags": {
            "formal_E_R_S_columns_constructed": True,
            "E_all_order_remainder_certified": True,
            "R_all_order_remainder_certified": True,
            "S_six_state_all_order_existence_certified": True,
            "S_correlated_dual_remainder_certified": False,
            "formal_K_plus_zero_in_canonical_gauge": True,
            "validated_analytic_K_plus_certified": False,
            "all_three_correlated_outgoing_columns_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "does_not_establish": [
            "a correlated all-order omega/tau remainder for S",
            "a validated analytic K_plus normalizer",
            "all three outgoing columns in one validated endpoint algebra",
            "T_plus, reflection, Stokes conservation, scattering, or flux",
        ],
        "next_gate": (
            "reissue the normalized XI3/S infinity remainder in the common "
            "IvTaylor4_omega tensor dual_tau algebra; only then promote the "
            "formal K_plus=0 recurrence gauge to an analytic endpoint frame"
        ),
    }


def write_receipt(data: dict) -> None:
    receipt = {
        "schema": "phase3-axial-partial-jet-outgoing-frame-completion-receipt-v1",
        "certificate": str(OUTPUT.relative_to(ROOT)),
        "certificate_sha256": sha256(OUTPUT),
        "dependency_tags": data["dependency_tags"],
        "claim_boundary": (
            "formal E/R/S frame and formal canonical K_plus only; correlated "
            "S remainder, analytic K_plus, T_plus, Stokes and flux remain open"
        ),
        "commands": [
            "python3 -m black_hole_programme.phase3."
            "axial_partial_jet_outgoing_frame_completion_v1.produce --check",
            "python3 -m black_hole_programme.phase3."
            "axial_partial_jet_outgoing_frame_completion_v1.verify",
            "python3 -m unittest black_hole_programme.phase3."
            "axial_partial_jet_outgoing_frame_completion_v1.test_completion",
        ],
        "tiers": {
            "tier0": "producer check, JSON schema, diff check",
            "tier1": "independent verifier and mutation tests",
            "tier2": "not run; no upstream operator or shared schema changed",
            "tier3": "not run; no theorem promotion or release",
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = document()
    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != encoded:
            raise SystemExit("certificate drift")
        print("PASS outgoing frame completion producer check")
        return 0
    OUTPUT.write_text(encoded)
    write_receipt(data)
    print(data["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
