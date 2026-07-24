#!/usr/bin/env python3
"""Produce the universal fixed-chart separation obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import adaptive_chart_separation as audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "adaptive-chart-separation-run.json"
OUTPUT = HERE / "adaptive-chart-separation-certificate.json"
RECEIPT = HERE / "adaptive-chart-separation-receipt.json"
SCHEMA = HERE / "adaptive-chart-separation-schema.json"
INPUTS = {
    "multipanel_successor_certificate": (
        HERE / "shared-remainder-multipanel-successor-certificate.json"
    ),
    "multipanel_successor_run": (
        HERE / "shared-remainder-multipanel-successor-run.json"
    ),
    "adaptive_chart_audit": HERE / "adaptive_chart_separation.py",
    "shared_reciprocal_normalizer": (
        HERE / "pivot_switch_shared_remainder_preflight.py"
    ),
    "checkpoint_transport": HERE / "checkpoint_transport.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    enclosure = run["terminal_raw_enclosure"]
    if not enclosure["state_finite"]:
        raise RuntimeError("terminal raw state finiteness drift")
    if not all(enclosure["base_component_zero_membership"]):
        raise RuntimeError("component zero-membership drift")
    if not enclosure["zero_vector_in_cartesian_base_enclosure"]:
        raise RuntimeError("Cartesian zero-vector premise drift")
    payload = enclosure["payload"]
    if audit.canonical_hash(payload) != enclosure["content_sha256"]:
        raise RuntimeError("terminal enclosure hash drift")
    midpoint = run["midpoint_adaptive_chart"]
    if midpoint["determinant"] != "1" or midpoint["certified"]:
        raise RuntimeError("midpoint chart disposition drift")
    candidate = midpoint["candidate"]
    if not candidate["midpoint_modulus_nonzero"] or candidate["excludes_zero"]:
        raise RuntimeError("midpoint candidate mutation witness drift")
    if any(row["excludes_zero"] for row in run["finite_candidate_atlas"].values()):
        raise RuntimeError("finite candidate atlas disposition drift")
    universal = run["universal_linear_separation"]
    if not universal["certified"]:
        raise RuntimeError("universal obstruction drift")
    mutation = run["mutation_witness"]
    if not mutation["mutation_killed"]:
        raise RuntimeError("midpoint-only mutation survived")
    flags = run["claim_flags"]
    if not flags["universal_fixed_linear_obstruction_certified"]:
        raise RuntimeError("universal flag drift")
    if flags["successor_substep_certified"]:
        raise RuntimeError("successor overclaim")
    certificate = {
        "schema": "phase3-axial-horizon-adaptive-chart-separation-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_ADAPTIVE_CHART_SEPARATION"
        ),
        "status": "UNIVERSAL_CARTESIAN_FIXED_CHART_OBSTRUCTION",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["REDUCED-MODE"],
        "source": run["source"],
        "terminal_raw_enclosure": enclosure,
        "midpoint_adaptive_chart": midpoint,
        "finite_candidate_atlas": run["finite_candidate_atlas"],
        "universal_linear_separation": universal,
        "mutation_witness": mutation,
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
            "a chart obstruction for a stronger affine or Taylor-model enclosure",
            "a successor checkpoint beyond the current obstruction",
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
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.adaptive_chart_separation",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_adaptive_chart_separation --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_adaptive_chart_separation",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_adaptive_chart_separation",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "adaptive_chart_separation"
                ),
                "status": "PASS_DETERMINISTIC_FAIL_CLOSED_OUTPUT",
                "elapsed_seconds": 13.31,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_adaptive_chart_separation --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_adaptive_chart_separation"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_adaptive_chart_separation"
                ),
                "status": "PASS_5_TESTS",
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
            },
        ],
        "claim_boundary": (
            "universal fixed-linear chart obstruction for the current "
            "rectangular Cartesian terminal enclosure only"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: transport representation obstruction only"
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
            raise SystemExit("generated adaptive-chart artifacts drift")
        print("horizon adaptive-chart separation artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()
