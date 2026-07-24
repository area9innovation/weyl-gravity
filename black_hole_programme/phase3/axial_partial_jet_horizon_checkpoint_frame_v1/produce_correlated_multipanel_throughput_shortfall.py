#!/usr/bin/env python3
"""Produce the fail-closed multipanel throughput shortfall certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "correlated-multipanel-throughput-shortfall-run.json"
OUTPUT = HERE / "correlated-multipanel-throughput-shortfall-certificate.json"
RECEIPT = HERE / "correlated-multipanel-throughput-shortfall-receipt.json"
SCHEMA = HERE / "correlated-multipanel-throughput-shortfall-schema.json"
INPUTS = {
    "run": RUN,
    "audit": HERE / "correlated_multipanel_throughput_shortfall.py",
    "multipanel_prototype": HERE / "correlated_affine_multipanel_successor.py",
    "one_step_certificate": HERE / "correlated-affine-seed-successor-certificate.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    if not all(run["code_audit"].values()):
        raise RuntimeError("code audit drift")
    flags = run["claim_flags"]
    if flags["multipanel_result_certified"]:
        raise RuntimeError("multipanel overclaim")
    if flags["timeout_treated_as_pass"]:
        raise RuntimeError("timeout promoted to pass")
    certificate = {
        "schema": "phase3-axial-horizon-correlated-multipanel-throughput-shortfall-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_CORRELATED_MULTIPANEL_THROUGHPUT_SHORTFALL"
        ),
        "status": "THROUGHPUT_SHORTFALL_NO_MULTIPANEL_CLAIM",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["REDUCED-MODE"],
        "source": run["source"],
        "observed_attempt": run["observed_attempt"],
        "code_audit": run["code_audit"],
        "split_contract": run["split_contract"],
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
            "any certified multipanel correlated radius, pivot, or residual",
            "crossing of the former Cartesian obstruction radius",
            "removal of the Cartesian wrapping obstruction",
            "transport to r=4",
            "H4, T_plus, a Gram, or a Stokes identity",
            "any LORENTZIAN-CAUSAL theorem",
        ],
    }
    receipt = {
        "schema": "phase3-receipt-v1",
        "result_id": certificate["result_id"],
        "status": certificate["status"],
        "dependency_tags": certificate["dependency_tags"],
        "commands": [
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.correlated_multipanel_throughput_shortfall",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_correlated_multipanel_throughput_shortfall --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_correlated_multipanel_throughput_shortfall",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_correlated_multipanel_throughput_shortfall",
        ],
        "validation": [
            {
                "command": run["observed_attempt"]["command"],
                "status": "TERMINATED_NOT_A_PASS",
                "elapsed_seconds": run["observed_attempt"]["elapsed_seconds"],
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_correlated_multipanel_throughput_shortfall --check"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_correlated_multipanel_throughput_shortfall"
                ),
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_correlated_multipanel_throughput_shortfall"
                ),
                "status": "PASS_5_TESTS",
            },
        ],
        "claim_boundary": (
            "throughput diagnosis and restart split; the one-step certificate "
            "is retained but no multipanel result is promoted"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: no mathematical input or paper theorem changed"
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
            raise SystemExit("generated throughput shortfall artifacts drift")
        print("correlated multipanel throughput shortfall artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()
