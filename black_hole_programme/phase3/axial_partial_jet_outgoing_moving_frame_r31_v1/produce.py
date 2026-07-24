#!/usr/bin/env python3
"""Produce the common moving-frame outgoing checkpoint at r=31."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from .model_ops import (
    add_scaled_rows,
    canonical_sha256,
    correction_row_receipt,
    exact_hull,
    interval_record,
    tagged_model,
    validate_model,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKPOINT = HERE / "checkpoint.json"
RESTART = HERE / "restart_manifest.json"
CERTIFICATE = HERE / "certificate.json"

R_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_rplus_checkpoint_resume_v1"
)
S_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_splus_r31_v1"
)
PHASE_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_kplus_moving_phase_gate_v1"
)
JOINT_DIR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_partial_jet_outgoing_joint_frame_r31_v1"
)
FORMAL_DIR = ROOT / (
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

INPUTS = {
    "R_certificate": R_DIR / "certificate.json",
    "R_reference_run": R_DIR / "export_run.txt",
    "R_independent_restart_run": R_DIR / "restart_run.txt",
    "S_certificate": S_DIR / "certificate.json",
    "S_checkpoint": S_DIR / "checkpoint.json",
    "moving_phase_gate": PHASE_DIR / "certificate.json",
    "joint_rank3_frame": JOINT_DIR / "certificate.json",
    "formal_frame_completion": FORMAL_DIR / "certificate.json",
    "endpoint_frame_audit": ENDPOINT_DIR / "certificate.json",
    "partial_jet_crosswalk": CROSSWALK_DIR / "certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_record(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def load_sources() -> dict:
    r_reference_text = INPUTS["R_reference_run"].read_text()
    r_restart_text = INPUTS["R_independent_restart_run"].read_text()
    r_base = tagged_model(r_reference_text, "REFERENCE_BASE")
    r_tangent = tagged_model(r_reference_text, "REFERENCE_TANGENT")
    if r_base != tagged_model(r_restart_text, "RESTART_BASE"):
        raise RuntimeError("R base restart mismatch")
    if r_tangent != tagged_model(r_restart_text, "RESTART_TANGENT"):
        raise RuntimeError("R tangent restart mismatch")
    s_document = json.loads(INPUTS["S_checkpoint"].read_text())
    if canonical_sha256(s_document["payload"]) != (
        s_document["payload_sha256"]
    ):
        raise RuntimeError("S checkpoint payload hash mismatch")
    s_payload = s_document["payload"]
    if s_payload["radius"] != "31":
        raise RuntimeError("S checkpoint is not at r=31")
    s_base = s_payload["base"]
    s_tangent = s_payload["tangent"]
    for model, rows in (
        (r_base, 4),
        (r_tangent, 4),
        (s_base, 8),
        (s_tangent, 8),
    ):
        validate_model(model, rows)
    return {
        "r_base": r_base,
        "r_tangent_fixed": r_tangent,
        "s_base_core": s_base,
        "s_tangent_fixed_core": s_tangent,
    }


def build_artifacts() -> tuple[dict, dict, dict]:
    source = load_sources()
    phase = json.loads(INPUTS["moving_phase_gate"].read_text())
    joint = json.loads(INPUTS["joint_rank3_frame"].read_text())
    formal = json.loads(INPUTS["formal_frame_completion"].read_text())
    endpoint = json.loads(INPUTS["endpoint_frame_audit"].read_text())
    crosswalk = json.loads(INPUTS["partial_jet_crosswalk"].read_text())
    r_cert = json.loads(INPUTS["R_certificate"].read_text())
    s_cert = json.loads(INPUTS["S_certificate"].read_text())
    if phase["status"] != "KPLUS_ZERO_WITHHELD_NONSTATIC_REPHASING":
        raise RuntimeError("moving-phase prerequisite drifted")
    if joint["status"] != "JOINT_REDUCED_FRAME_RANK3_KPLUS_ANALYTIC_OPEN":
        raise RuntimeError("joint rank-three prerequisite drifted")
    if r_cert["status"] != "RPLUS_CHECKPOINT_RESTART_SECOND_CHUNK_PASS":
        raise RuntimeError("R checkpoint prerequisite drifted")
    if s_cert["status"] != "SPLUS_REACHES_R31":
        raise RuntimeError("S checkpoint prerequisite drifted")
    if not crosswalk["claim_flags"]["partial_spin_two_row_jet_exact"]:
        raise RuntimeError("partial-jet crosswalk drifted")

    r_moving = add_scaled_rows(
        source["r_tangent_fixed"],
        source["r_base"],
        ((1, 1), (3, 3)),
    )
    s_moving = add_scaled_rows(
        source["s_tangent_fixed_core"],
        source["s_base_core"],
        ((1, 1), (5, 5)),
    )
    corrections = {
        "R": [
            correction_row_receipt(
                source["r_tangent_fixed"],
                source["r_base"],
                r_moving,
                tangent_row,
                base_row,
            )
            for tangent_row, base_row in ((1, 1), (3, 3))
        ],
        "S": [
            correction_row_receipt(
                source["s_tangent_fixed_core"],
                source["s_base_core"],
                s_moving,
                tangent_row,
                base_row,
            )
            for tangent_row, base_row in ((1, 1), (5, 5))
        ],
    }
    payload = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-moving-frame-r31-"
            "checkpoint-payload-v1"
        ),
        "radius": "31",
        "omega_child": ["1/2", "4097/8192"],
        "generator": 7315,
        "degree": 4,
        "parameter_domain": ["-1", "1"],
        "moving_gauge": {
            "R_tangent_formula": (
                "Rdot_fixed+diag(0,93/4)*Rbase"
            ),
            "S_base_formula": "h0*Sbase_core",
            "S_tangent_formula": (
                "h0*(Sdot_fixed_core+diag(0,93/4)*Sbase_Y_core)"
            ),
            "h0": {
                "expression": (
                    "(32/31)*exp(I*omega*(64+4*log(32)))"
                ),
                "representation": (
                    "typed analytic unit; not expanded into the rational "
                    "IvTaylor4 core"
                ),
                "analytic_on": "entire omega plane",
                "zero_free": True,
                "tau_zero_only": True,
            },
            "moving_spin_two_factor": (
                "exp(-3*tau*r/4)*(I+tau*r*diag(3/4,0))"
                "+O(tau**2)"
            ),
            "combined_logarithmic_generator": "diag(0,-3/4)",
        },
        "models": {
            "R_base": source["r_base"],
            "R_tangent_moving": r_moving,
            "S_base_core": source["s_base_core"],
            "S_tangent_moving_core": s_moving,
        },
        "typed_columns": {
            "E": ["R_base", "0", "0"],
            "R": ["R_tangent_moving", "R_base", "0"],
            "S": [
                "h0*S_tangent_moving_core_X",
                "h0*S_base_core_Y",
                "h0*S_base_core_Z",
            ],
        },
        "correction_enclosures": corrections,
    }
    checkpoint = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-moving-frame-r31-"
            "checkpoint-v1"
        ),
        "payload": payload,
        "payload_sha256": canonical_sha256(payload),
    }
    model_hashes = {
        name: canonical_sha256(model)
        for name, model in payload["models"].items()
    }
    roundtrip = json.loads(json.dumps(checkpoint, sort_keys=True))
    restart = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-moving-frame-r31-"
            "restart-v1"
        ),
        "checkpoint_payload_sha256": checkpoint["payload_sha256"],
        "model_canonical_sha256": model_hashes,
        "json_roundtrip_exact": roundtrip == checkpoint,
        "roundtrip_payload_sha256": canonical_sha256(roundtrip["payload"]),
        "shared_generator": 7315,
        "restart_ready": (
            roundtrip == checkpoint
            and canonical_sha256(roundtrip["payload"])
            == checkpoint["payload_sha256"]
        ),
    }

    r_pivot = interval_record(exact_hull(source["r_base"], 0))
    s_pivot = interval_record(exact_hull(source["s_base_core"], 2))
    rank_three = (
        r_pivot["excludes_zero"]
        and s_pivot["excludes_zero"]
        and payload["moving_gauge"]["h0"]["zero_free"]
    )
    normalization = formal["exact_normalization_audit"]
    zero_logs = (
        normalization["forced_log_XI2"] == "0"
        and normalization["forced_log_XI3"] == "0"
    )
    zero_free_shears = (
        normalization["canonical_free_EI2_XI2"] == "0"
        and normalization["canonical_free_EI2_XI3"] == "0"
    )
    unit_amplitudes = (
        formal["formal_endpoint_jet"]["unit_leading_amplitudes_force"]
        == "k2=0"
    )
    common_tau_frame = (
        phase["exact_asymptotic_audit"][
            "combined_scalar_and_matrix_moving_generator"
        ]
        == [["0", "0"], ["0", "-3/4"]]
        and all(
            row["emitted_remainder_contains_exact_sum"]
            for group in corrections.values()
            for row in group
        )
        and restart["restart_ready"]
    )
    analytic_kplus = (
        rank_three
        and common_tau_frame
        and zero_logs
        and zero_free_shears
        and unit_amplitudes
        and formal["claim_flags"]["formal_K_plus_zero_in_canonical_gauge"]
    )
    status = (
        "MOVING_FRAME_R31_RANK3_ANALYTIC_KPLUS_ZERO"
        if analytic_kplus
        else "MOVING_FRAME_R31_REFUSED"
    )
    certificate = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-moving-frame-r31-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_OUTGOING_MOVING_FRAME_R31_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": status,
        "imports": {
            name: import_record(path) for name, path in INPUTS.items()
        },
        "artifacts": {
            "checkpoint": {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "payload_sha256": checkpoint["payload_sha256"],
            },
            "restart_manifest": {
                "path": str(RESTART.relative_to(ROOT)),
                "model_canonical_sha256": model_hashes,
            },
        },
        "domain": {
            "endpoint": "Iplus",
            "matching_radius": "31",
            "omega_child": ["1/2", "4097/8192"],
            "generator": 7315,
            "degree": 4,
            "parameter_domain": ["-1", "1"],
        },
        "moving_frame_reissue": {
            "Rdot_moving": (
                "Rdot_fixed+diag(0,93/4)*Rbase"
            ),
            "Sbase_common": "h0*Sbase_core",
            "Sdot_common": (
                "h0*(Sdot_fixed_core+diag(0,93/4)*Sbase_Y_core)"
            ),
            "h0_expression": (
                "(32/31)*exp(I*omega*(64+4*log(32)))"
            ),
            "h0_analytic_entire": True,
            "h0_zero_free": True,
            "h0_typed_not_interval_expanded": True,
            "shared_omega_generator": 7315,
            "correction_enclosures": corrections,
            "common_tau_frame_supplied": common_tau_frame,
        },
        "rank_three_minor": {
            "selected_complex_rows": ["X[0]", "Y[0]", "Z[0]"],
            "selected_columns": ["E", "R", "S"],
            "determinant_factorization": (
                "h0*R_base[0]**2*S_base_Z_core[0]"
            ),
            "R_base_component0_real_hull": r_pivot,
            "S_base_Z_component0_real_hull": s_pivot,
            "h0_zero_free": True,
            "determinant_nonzero": rank_three,
            "complex_rank": 3 if rank_three else None,
        },
        "restart_serialization_audit": {
            "json_roundtrip_exact": restart["json_roundtrip_exact"],
            "payload_sha256_stable": (
                restart["roundtrip_payload_sha256"]
                == restart["checkpoint_payload_sha256"]
            ),
            "model_hashes_recorded": True,
            "independent_source_restart_imported": True,
            "restart_ready": restart["restart_ready"],
        },
        "endpoint_normalization_audit": {
            "complete_moving_factor_extracted": True,
            "moving_scalar_rate_derivative": "-3/4",
            "moving_polynomial_gauge": [["3/4", "0"], ["0", "0"]],
            "combined_moving_generator": [["0", "0"], ["0", "-3/4"]],
            "forced_log_XI2": normalization["forced_log_XI2"],
            "forced_log_XI3": normalization["forced_log_XI3"],
            "forced_logs_zero": zero_logs,
            "canonical_free_EI2_XI2": (
                normalization["canonical_free_EI2_XI2"]
            ),
            "canonical_free_EI2_XI3": (
                normalization["canonical_free_EI2_XI3"]
            ),
            "free_EI2_constants_zero": zero_free_shears,
            "residual_unit_leading_amplitudes_force": (
                formal["formal_endpoint_jet"][
                    "unit_leading_amplitudes_force"
                ]
            ),
            "residual_leading_amplitude_derivative_zero": unit_amplitudes,
            "formal_K_plus": [["0", "0"], ["0", "0"]],
            "analytic_first_jet_K_plus": [["0", "0"], ["0", "0"]],
            "analytic_K_plus_zero_certified": analytic_kplus,
            "scope": (
                "first intrinsic tau jet in the complete moving factor "
                "gauge on the certified pilot child"
            ),
            "reason": (
                "the componentwise r=31 correction realizes the exact "
                "moving scalar-plus-polynomial factor; after extraction, "
                "the analytic recurrence has zero forced logs, unit residual "
                "leading amplitudes, and zero canonical Einstein shears"
            ),
        },
        "claim_flags": {
            "moving_phase_correction_exact": True,
            "correction_remainder_containment_certified": True,
            "shared_omega_generator_preserved": True,
            "typed_h0_analytic_zero_free": True,
            "restart_serialization_certified": restart["restart_ready"],
            "joint_moving_frame_rank_three_certified": rank_three,
            "common_tau_frame_supplied": common_tau_frame,
            "analytic_K_plus_zero_certified": analytic_kplus,
            "T_plus_certified": False,
            "stokes_or_scattering_certified": False,
        },
        "does_not_establish": [
            "the outgoing trace map T_plus",
            "a Stokes, scattering, reflection, or flux identity",
            "an interval expansion or uniform modulus bound for h0",
            "transport of the joint moving frame below r=31",
            "higher-than-first-order dependence on the intrinsic tau",
        ],
        "next_gate": (
            "use this common moving endpoint checkpoint as the only allowed "
            "outgoing restart for T_plus transport; do not assemble T_plus "
            "or Stokes in this result"
        ),
    }
    return checkpoint, restart, certificate


def rendered(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    check = "--check" in sys.argv
    checkpoint, restart, certificate = build_artifacts()
    expected = {
        CHECKPOINT: rendered(checkpoint),
        RESTART: rendered(restart),
        CERTIFICATE: rendered(certificate),
    }
    if check:
        drift = [
            str(path.name)
            for path, text in expected.items()
            if not path.exists() or path.read_text() != text
        ]
        if drift:
            print(f"artifact drift: {', '.join(drift)}", file=sys.stderr)
            return 2
    else:
        for path, text in expected.items():
            path.write_text(text)
    print(certificate["status"])
    return 0 if certificate["status"] == (
        "MOVING_FRAME_R31_RANK3_ANALYTIC_KPLUS_ZERO"
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
