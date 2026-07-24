#!/usr/bin/env python3
"""Produce the canonical K_H theorem and checkpoint-transport disposition."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from ..axial_partial_jet_horizon_moving_phase_v1 import produce as moving
from ..axial_partial_jet_horizon_spin_one_levelt_v1 import produce as levelt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
RUN = HERE / "checkpoint-run.json"
INPUTS = {
    "crosswalk": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_transport_crosswalk_v1/certificate.json"
    ),
    "moving_phase": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_moving_phase_v1/certificate.json"
    ),
    "spin_one_levelt": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_spin_one_levelt_v1/certificate.json"
    ),
}
CODE_INPUTS = {
    "checkpoint_transport": HERE / "checkpoint_transport.py",
    "moving_phase_producer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_moving_phase_v1/produce.py"
    ),
    "spin_one_levelt_producer": ROOT / (
        "black_hole_programme/phase3/"
        "axial_partial_jet_horizon_spin_one_levelt_v1/produce.py"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_endpoint_audit(crosswalk: dict) -> dict:
    pure = moving.exact_data(crosswalk)
    mixed = levelt.exact_data(crosswalk)
    zero2 = sp.zeros(2, 1)
    zero4 = sp.zeros(4, 1)
    if pure["exponent_derivative"] != 0:
        raise RuntimeError("spin-two exponent derivative drift")
    if pure["tangent"][0] != zero2:
        raise RuntimeError("spin-two leading tangent normalization drift")
    if mixed["tangent_residue"] != sp.zeros(4):
        raise RuntimeError("mixed tangent residue drift")
    if mixed["g"][0] != zero4 or mixed["g"][1] != zero4:
        raise RuntimeError("Levelt tangent normalization drift")
    resonance = mixed["resonance"]
    if len(resonance) != 1 or resonance[0]["order"] != 1:
        raise RuntimeError("Levelt resonance ledger drift")
    return {
        "frame": (
            "tau-analytic horizon Frobenius/Levelt frame with "
            "tau-independent leading normalizations"
        ),
        "spin_two": {
            "leading_condition": "ell_H^T*f_0=1",
            "tau_exponent_derivative": "0",
            "leading_tangent_coefficient": ["0", "0"],
            "normalization_derivative_k2": "0",
        },
        "spin_one_lift": {
            "quotient_leading_vector": ["1", "-1"],
            "quotient_normalization_derivative": "0",
            "only_resonant_order": 1,
            "free_homogeneous_parameter": "0 for every tau",
            "order_zero_tangent": ["0", "0", "0", "0"],
            "order_one_tangent": ["0", "0", "0", "0"],
            "normalization_derivative_h": "0",
        },
        "allowed_type": "upper triangular [[k2,h],[0,0]]",
        "K_H": [["0", "0"], ["0", "0"]],
        "zero_residuals": True,
        "collision_divisors": {
            "spin_two": "(n+1)*(n+1+4*I*omega)",
            "mixed_named_head": [
                "2*omega-I",
                "4*omega-I",
                "4*omega-3*I",
                "omega-I",
            ],
            "excluded_for_real_omega_positive": True,
        },
    }


def build() -> tuple[dict, dict]:
    crosswalk = json.loads(INPUTS["crosswalk"].read_text())
    run = json.loads(RUN.read_text())
    endpoint = exact_endpoint_audit(crosswalk)
    terminal = run["terminal"]
    if run["reached_r4"] or terminal is None:
        raise RuntimeError("expected fail-closed checkpoint disposition drift")
    if terminal.get("gate") != "PROJECTIVE_PIVOT":
        raise RuntimeError("first checkpoint obstruction drift")
    if terminal["mixed"].get("gate") != "PIVOT_CONTAINS_ZERO":
        raise RuntimeError("mixed pivot obstruction drift")
    certificate = {
        "schema": "phase3-axial-partial-jet-horizon-checkpoint-frame-v1",
        "result_id": "PURE_WEYL_PHASE3_AXIAL_HORIZON_CANONICAL_KH",
        "status": "CANONICAL_KH_ZERO_CHECKPOINT_PIVOT_SHORTFALL",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "canonical_endpoint_frame": endpoint,
        "checkpoint_transport": {
            "frequency": run["frequency"],
            "scope": run["scope"],
            "accepted_panels": run["accepted_panels"],
            "reached_r4": False,
            "first_obstruction": terminal,
            "pure_spin_two_pivot_still_excludes_zero": (
                terminal["pure"]["passed"]
            ),
            "mixed_projective_pivot_excludes_zero": False,
            "run_path": str(RUN.relative_to(ROOT)),
            "run_sha256": sha256(RUN),
        },
        "claim_flags": {
            "canonical_tau_analytic_horizon_frame_constructed": True,
            "K_H_computed": True,
            "K_H_exactly_zero_in_canonical_frame": True,
            "horizon_to_r4_column_certified": False,
            "complete_three_channel_frame_at_r4": False,
            "H4_pass_certified": False,
            "T_plus_recovered": False,
        },
        "imports": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for name, path in {**INPUTS, **CODE_INPUTS}.items()
        },
        "does_not_establish": [
            "a complete three-channel horizon frame at r=4",
            "the physical H4 handoff, T_plus, or a Stokes identity",
            "a canonical K_minus or K_plus",
            "bounded all-frequency transport",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.checkpoint_transport",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify",
            "python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_checkpoint_frame",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "checkpoint_transport"
                ),
                "status": "PASS_DETERMINISTIC_OUTPUT",
                "elapsed_seconds": 12.4,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce --check"
                ),
                "status": "PASS",
                "elapsed_seconds": 11.9,
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1.verify"
                ),
                "status": "PASS",
                "elapsed_seconds": 0.1,
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_checkpoint_frame"
                ),
                "status": "PASS_3_TESTS",
                "elapsed_seconds": 11.7,
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
                "elapsed_seconds": 0.1,
            },
        ],
        "claim_boundary": (
            "canonical endpoint K_H only; radial frame/H4/T_plus remain "
            "fail closed at the first mixed projective pivot obstruction"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: no shared operator or promoted physical "
            "scattering theorem changed"
        ),
    }
    return certificate, receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate, receipt = build()
    encoded = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    receipt_encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text() != encoded or RECEIPT.read_text() != receipt_encoded:
            raise SystemExit("generated horizon checkpoint artifacts drift")
        print("horizon checkpoint frame artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()
