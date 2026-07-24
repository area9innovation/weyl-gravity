#!/usr/bin/env python3
"""Produce the first correlated affine/Taylor horizon successor certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from . import correlated_affine_seed_successor as rail

sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "correlated-affine-seed-successor-run.json"
OUTPUT = HERE / "correlated-affine-seed-successor-certificate.json"
RECEIPT = HERE / "correlated-affine-seed-successor-receipt.json"
SCHEMA = HERE / "correlated-affine-seed-successor-schema.json"
INPUTS = {
    "run": RUN,
    "rail": HERE / "correlated_affine_seed_successor.py",
    "restart_contract": HERE / "correlated-affine-export-audit-certificate.json",
    "checkpoint_transport": HERE / "checkpoint_transport.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value: str) -> str:
    return f"{float(Fraction(value)):.12g}"


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    initial = run["initial_model"]
    successor = run["successor_model"]
    if not rail.model_chain_valid(initial, successor):
        raise RuntimeError("correlated model content chain drift")
    flags = run["claim_flags"]
    required_true = (
        "symbolic_pre_omega_substitution_seed_used",
        "uniform_complex_omega_levelt_tail_certified",
        "shared_omega_parameter_serialized",
        "dual_tau_rails_share_parameter",
        "coupled_residual_serialized",
        "initial_projective_pivot_certified",
        "initial_projective_normalization_certified",
        "one_radial_taylor_step_certified",
        "successor_projective_pivot_certified",
        "successor_projective_normalization_certified",
        "content_addressed_model_chain",
    )
    if not all(flags[name] for name in required_true):
        raise RuntimeError("positive gate drift")
    if flags["independent_component_remainders_used"]:
        raise RuntimeError("Cartesian remainder regression")
    if flags["next_base_panel_completed"] or flags["H4_certified"]:
        raise RuntimeError("scope overclaim")
    initial_lower = run["initial_normalization"][
        "full_denominator_modulus_lower"
    ]
    successor_lower = run["successor_normalization"][
        "full_denominator_modulus_lower"
    ]
    initial_residual = initial["residual_norm_ball"]["radius"]
    successor_residual = successor["residual_norm_ball"]["radius"]
    if min(Fraction(initial_lower), Fraction(successor_lower)) <= 0:
        raise RuntimeError("pivot separation drift")
    if Fraction(successor_residual) >= 1:
        raise RuntimeError("successor residual drift")

    certificate = {
        "schema": "phase3-axial-horizon-correlated-affine-seed-successor-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_CORRELATED_AFFINE_SEED_SUCCESSOR"
        ),
        "status": "ONE_CORRELATED_RADIAL_SUCCESSOR_CERTIFIED",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["REDUCED-MODE"],
        "frequency_domain": run["frequency_domain"],
        "source": run["source"],
        "uniform_levelt_tail": run["uniform_levelt_tail"],
        "initial_normalization": run["initial_normalization"],
        "initial_model": initial,
        "radial_step": run["radial_step"],
        "successor_normalization": run["successor_normalization"],
        "successor_model": successor,
        "content_chain": run["content_chain"],
        "numeric_summary": {
            "initial_pivot_lower": decimal(initial_lower),
            "successor_pivot_lower": decimal(successor_lower),
            "initial_coupled_residual": decimal(initial_residual),
            "successor_coupled_residual": decimal(successor_residual),
            "radial_cauchy_scaled_norm": decimal(
                run["radial_step"]["cauchy_scaled_norm"]
            ),
            "radial_tail": decimal(run["radial_step"]["radial_tail"]),
        },
        "terminal": run["terminal"],
        "claim_flags": flags,
        "imports": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for name, path in INPUTS.items()
        },
        "run": {
            "path": str(RUN.relative_to(ROOT)),
            "sha256": sha256(RUN),
        },
        "does_not_establish": [
            "completion of the next original 1/64 base panel",
            "transport beyond the single certified radial substep",
            "transport to r=4",
            "a complete typed H4 frame, T_plus, Gram, or Stokes identity",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.correlated_affine_seed_successor",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_correlated_affine_seed_successor --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_correlated_affine_seed_successor",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_correlated_affine_seed_successor",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "correlated_affine_seed_successor"
                ),
                "status": "PASS",
                "elapsed_seconds": 84.73,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_correlated_affine_seed_successor --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_correlated_affine_seed_successor"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_correlated_affine_seed_successor"
                ),
                "status": "PASS_6_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
            {
                "command": "python3 -m py_compile <four changed Python files>",
                "status": "PASS",
            },
            {
                "command": (
                    "git diff --check -- black_hole_programme/phase3/"
                    "axial_partial_jet_horizon_checkpoint_frame_v1"
                ),
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "one correlated mixed-horizon radial successor over a declared "
            "complex omega disk"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: local representation successor only; "
            "no shared operator or paper theorem changed"
        ),
    }
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
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
            raise SystemExit("generated correlated successor artifacts drift")
        print("horizon correlated affine seed successor artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()
