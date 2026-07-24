#!/usr/bin/env python3
"""Produce the typed reduced outgoing E/R/S frame certificate at r=31."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path

sys.set_int_max_str_digits(1_000_000)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

R_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_rplus_checkpoint_resume_v1"
)
S_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_r31_v1"
)
FRAME_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_frame_completion_v1"
)
ENDPOINT_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_endpoint_frames_v1"
)
CROSSWALK_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_transport_crosswalk_v1"
)
R_PREFLIGHT_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_infinity_reduced_phase_preflight_v1"
)

CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def import_record(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def parse_tagged_model(text: str, tag: str) -> dict:
    match = re.search(rf"^{re.escape(tag)} (.+)$", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"missing serialized model {tag}")
    return json.loads(match.group(1))


def fraction_from_bits(bits: str) -> Fraction:
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    if not (-float("inf") < value < float("inf")):
        raise RuntimeError("nonfinite interval endpoint")
    return Fraction.from_float(value)


def validate_model(model: dict, rows: int) -> None:
    expected = {
        "schema": "ivtaylor-degree4-v1",
        "generator": 7315,
        "degree": 4,
        "rows": rows,
        "cols": 1,
        "refusal_code": 0,
    }
    for key, value in expected.items():
        if model.get(key) != value:
            raise RuntimeError(f"model field drift: {key}")
    if len(model["coefficients"]) != 5:
        raise RuntimeError("degree-four coefficient rail missing")
    if any(len(block) != rows for block in model["coefficients"]):
        raise RuntimeError("coefficient row count drift")
    if len(model["remainder_bits"]) != rows:
        raise RuntimeError("remainder row count drift")


def exact_hull(model: dict, row: int) -> tuple[Fraction, Fraction]:
    coefficients = [
        Fraction(model["coefficients"][degree][row][0])
        for degree in range(5)
    ]
    radius = sum(abs(value) for value in coefficients[1:])
    lo_bits, hi_bits = model["remainder_bits"][row][0]
    lo = coefficients[0] - radius + fraction_from_bits(lo_bits)
    hi = coefficients[0] + radius + fraction_from_bits(hi_bits)
    if lo > hi:
        raise RuntimeError("invalid exact hull")
    return lo, hi


def interval_record(interval: tuple[Fraction, Fraction]) -> dict:
    lo, hi = interval
    exact_text = f"{lo}|{hi}"
    return {
        "lower_decimal": float(lo),
        "upper_decimal": float(hi),
        "lower_sign": (lo > 0) - (lo < 0),
        "upper_sign": (hi > 0) - (hi < 0),
        "exact_pair_sha256": hashlib.sha256(exact_text.encode()).hexdigest(),
        "excludes_zero": lo > 0 or hi < 0,
    }


def model_coefficients_zero(model: dict, rows: tuple[int, ...]) -> bool:
    return all(
        Fraction(model["coefficients"][degree][row][0]) == 0
        for degree in range(5)
        for row in rows
    )


def produce() -> dict:
    r_certificate_path = R_DIR / "certificate.json"
    r_export_path = R_DIR / "export_run.txt"
    r_restart_path = R_DIR / "restart_run.txt"
    s_certificate_path = S_DIR / "certificate.json"
    s_checkpoint_path = S_DIR / "checkpoint.json"
    frame_path = FRAME_DIR / "certificate.json"
    endpoint_path = ENDPOINT_DIR / "certificate.json"
    crosswalk_path = CROSSWALK_DIR / "certificate.json"
    r_preflight_path = R_PREFLIGHT_DIR / "certificate.json"

    r_certificate = json.loads(r_certificate_path.read_text())
    s_certificate = json.loads(s_certificate_path.read_text())
    frame = json.loads(frame_path.read_text())
    endpoint = json.loads(endpoint_path.read_text())
    crosswalk = json.loads(crosswalk_path.read_text())
    r_preflight = json.loads(r_preflight_path.read_text())
    s_checkpoint_document = json.loads(s_checkpoint_path.read_text())

    if r_certificate["status"] != "RPLUS_CHECKPOINT_RESTART_SECOND_CHUNK_PASS":
        raise RuntimeError("R+ import did not pass")
    if s_certificate["status"] != "SPLUS_REACHES_R31":
        raise RuntimeError("S+ import did not reach r=31")
    if not crosswalk["claim_flags"]["partial_spin_two_row_jet_exact"]:
        raise RuntimeError("partial-jet crosswalk drifted")
    if not endpoint["claim_flags"]["epsilon_copy_identified"]:
        raise RuntimeError("epsilon-copy identification drifted")
    if not frame["claim_flags"]["formal_E_R_S_columns_constructed"]:
        raise RuntimeError("formal outgoing frame drifted")
    if s_checkpoint_document["payload"]["radius"] != "31":
        raise RuntimeError("S+ checkpoint radius drifted")
    if canonical_sha256(s_checkpoint_document["payload"]) != (
        s_checkpoint_document["payload_sha256"]
    ):
        raise RuntimeError("S+ checkpoint payload hash drifted")

    export_text = r_export_path.read_text()
    restart_text = r_restart_path.read_text()
    r_base = parse_tagged_model(export_text, "REFERENCE_BASE")
    r_tangent = parse_tagged_model(export_text, "REFERENCE_TANGENT")
    if r_base != parse_tagged_model(restart_text, "RESTART_BASE"):
        raise RuntimeError("R+ independent restart base drifted")
    if r_tangent != parse_tagged_model(restart_text, "RESTART_TANGENT"):
        raise RuntimeError("R+ independent restart tangent drifted")

    s_payload = s_checkpoint_document["payload"]
    s_base = s_payload["base"]
    s_tangent = s_payload["tangent"]
    validate_model(r_base, 4)
    validate_model(r_tangent, 4)
    validate_model(s_base, 8)
    validate_model(s_tangent, 8)
    if any(
        model["generator"] != 7315
        for model in (r_base, r_tangent, s_base, s_tangent)
    ):
        raise RuntimeError("common generator lost")

    # R realification is (Re state[0:2], Im state[0:2]).
    # S base realification is (Re Y[0:2], Re Z[0:2],
    # Im Y[0:2], Im Z[0:2]); its tangent has (X, 0_Z).
    r_base_x0_re = exact_hull(r_base, 0)
    r_base_x0_im = exact_hull(r_base, 2)
    s_z0_re = exact_hull(s_base, 2)
    s_z0_im = exact_hull(s_base, 6)
    s_tangent_zero_rows = (2, 3, 6, 7)
    zero_coefficients = model_coefficients_zero(
        s_tangent, s_tangent_zero_rows
    )
    zero_hulls = {
        str(row): interval_record(exact_hull(s_tangent, row))
        for row in s_tangent_zero_rows
    }
    padding_contains_zero = all(
        record["lower_decimal"] <= 0 <= record["upper_decimal"]
        for record in zero_hulls.values()
    )

    pivot_r = interval_record(r_base_x0_re)
    pivot_s = interval_record(s_z0_re)
    rank_three = pivot_r["excludes_zero"] and pivot_s["excludes_zero"]

    r_phase = r_preflight["phase_factor"]["factor"]
    s_phase = s_payload["phase"]
    relative_phase_at_r31 = (
        "(32/31)*exp(I*omega*(64+4*log(32)))"
    )

    result = {
        "schema": "phase3-axial-partial-jet-outgoing-joint-frame-r31-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_OUTGOING_JOINT_FRAME_R31_V1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": (
            "JOINT_REDUCED_FRAME_RANK3_KPLUS_ANALYTIC_OPEN"
            if rank_three and zero_coefficients and padding_contains_zero
            else "JOINT_REDUCED_FRAME_REFUSED"
        ),
        "imports": {
            "R_checkpoint_certificate": import_record(r_certificate_path),
            "R_reference_run": import_record(r_export_path),
            "R_independent_restart_run": import_record(r_restart_path),
            "S_r31_certificate": import_record(s_certificate_path),
            "S_r31_checkpoint": import_record(s_checkpoint_path),
            "formal_outgoing_frame": import_record(frame_path),
            "endpoint_frame_audit": import_record(endpoint_path),
            "partial_jet_crosswalk": import_record(crosswalk_path),
            "R_reduced_phase_preflight": import_record(r_preflight_path),
        },
        "domain": {
            "radius": "31",
            "omega_child": ["1/2", "4097/8192"],
            "generator": 7315,
            "degree": 4,
            "parameter_domain": ["-1", "1"],
        },
        "source_layout_audit": {
            "complex_six_state_factor_order": [
                "X_tangent_spin2[0]",
                "X_tangent_spin2[1]",
                "Y_carrier_spin2[0]",
                "Y_carrier_spin2[1]",
                "Z_spin1[0]",
                "Z_spin1[1]",
            ],
            "R_base_real_rows": [
                "Re(Y0)",
                "Re(Y1)",
                "Im(Y0)",
                "Im(Y1)",
            ],
            "R_tangent_real_rows": [
                "Re(X0)",
                "Re(X1)",
                "Im(X0)",
                "Im(X1)",
            ],
            "S_base_real_rows": [
                "Re(Y0)",
                "Re(Y1)",
                "Re(Z0)",
                "Re(Z1)",
                "Im(Y0)",
                "Im(Y1)",
                "Im(Z0)",
                "Im(Z1)",
            ],
            "S_tangent_real_rows": [
                "Re(X0)",
                "Re(X1)",
                "Re(0_Z0)",
                "Re(0_Z1)",
                "Im(X0)",
                "Im(X1)",
                "Im(0_Z0)",
                "Im(0_Z1)",
            ],
            "S_spin_one_tangent_exact_coefficients_zero": zero_coefficients,
            "S_spin_one_tangent_padding_contains_zero": padding_contains_zero,
            "S_spin_one_tangent_padding_hulls": zero_hulls,
            "interpretation": (
                "The four R rows and eight S rows are realifications, not "
                "complex row counts. Padding on S tangent Z placeholders is "
                "not promoted to a physical Z tangent; the exact partial-jet "
                "crosswalk freezes that block."
            ),
        },
        "typed_columns": {
            "column_order": ["E", "R", "S"],
            "E": {
                "complex_blocks": ["R_base", "0", "0"],
                "meaning": "epsilon-copy of the unit outgoing spin-two line",
            },
            "R": {
                "complex_blocks": ["R_tangent", "R_base", "0"],
                "meaning": "repeated-spin-two partial-jet column",
            },
            "S": {
                "complex_blocks": [
                    "S_tangent_X",
                    "S_base_Y",
                    "S_base_Z",
                ],
                "meaning": "unit spin-one quotient partial-jet lift",
            },
        },
        "triangular_minor": {
            "selected_complex_rows": ["X[0]", "Y[0]", "Z[0]"],
            "selected_columns": ["E", "R", "S"],
            "matrix_pattern": [
                ["R_base[0]", "R_tangent[0]", "S_tangent_X[0]"],
                ["0", "R_base[0]", "S_base_Y[0]"],
                ["0", "0", "S_base_Z[0]"],
            ],
            "determinant_factorization": (
                "R_base[0]**2*S_base_Z[0]"
            ),
            "R_base_component0": {
                "real_hull": pivot_r,
                "imag_hull": interval_record(r_base_x0_im),
                "nonzero": pivot_r["excludes_zero"],
            },
            "S_base_Z_component0": {
                "real_hull": pivot_s,
                "imag_hull": interval_record(s_z0_im),
                "nonzero": pivot_s["excludes_zero"],
            },
            "determinant_nonzero": rank_three,
            "complex_rank": 3 if rank_three else None,
            "proof": (
                "The selected minor is block upper triangular. Its two "
                "complex pivot factors are nonzero because their exact real "
                "hulls exclude zero on the complete omega child."
            ),
        },
        "phase_gauge_crosswalk": {
            "R_and_E_reduced_phase": r_phase,
            "S_reduced_phase": s_phase,
            "relative_S_over_R_at_r31": relative_phase_at_r31,
            "relative_factor_nonzero_on_domain": True,
            "rank_invariant_under_column_phase_rescaling": True,
            "common_amplitude_gauge_applied": False,
            "consequence": (
                "The rank-three statement is a reduced/projective frame "
                "statement. No common amplitude-normalized outgoing frame is "
                "claimed."
            ),
        },
        "K_plus_audit": {
            "formal_canonical_K_plus_zero": frame["claim_flags"][
                "formal_K_plus_zero_in_canonical_gauge"
            ],
            "validated_analytic_K_plus": False,
            "promotion_blockers": [
                (
                    "the imported endpoint audit still has "
                    "analytic_tau_endpoint_family_constructed=false"
                ),
                (
                    "the imported endpoint audit still has "
                    "moving_exponent_derivatives_computed=false"
                ),
                (
                    "R/E and S checkpoints use different nonzero analytic "
                    "phase normalizations and no certified common amplitude "
                    "gauge or endpoint derivative matrices have been applied"
                ),
            ],
            "closed_by_this_result": (
                "the prior missing correlated S all-order remainder and the "
                "common-radius reduced-frame rank gate"
            ),
        },
        "claim_flags": {
            "common_generator_preserved": True,
            "typed_E_R_S_reduced_columns_constructed": True,
            "joint_reduced_frame_rank_three_certified": rank_three,
            "formal_K_plus_zero_preserved": True,
            "validated_analytic_K_plus_certified": False,
            "common_amplitude_outgoing_frame_certified": False,
            "T_plus_certified": False,
            "scattering_or_flux_certified": False,
        },
        "does_not_establish": [
            "a common amplitude-normalized analytic outgoing endpoint frame",
            "the analytic endpoint shear K_plus=0",
            "the outgoing trace map T_plus",
            "a Stokes, scattering, reflection, or flux identity",
            "transport of the joint outgoing frame below r=31",
        ],
        "next_gate": (
            "construct and certify one common analytic endpoint phase/"
            "amplitude gauge for E,R,S, including the endpoint tau-family "
            "and its derivative matrices, before promoting formal K_plus=0 "
            "or assembling T_plus"
        ),
        "producer_elapsed_seconds": 0.0,
    }
    return result


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
    return 0 if result["status"] == (
        "JOINT_REDUCED_FRAME_RANK3_KPLUS_ANALYTIC_OPEN"
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
