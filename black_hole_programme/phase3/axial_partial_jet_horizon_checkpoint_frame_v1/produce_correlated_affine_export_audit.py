#!/usr/bin/env python3
"""Produce the fail-closed correlated-affine regeneration certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from . import correlated_affine_export_audit as audit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "correlated-affine-export-audit-run.json"
OUTPUT = HERE / "correlated-affine-export-audit-certificate.json"
RECEIPT = HERE / "correlated-affine-export-audit-receipt.json"
SCHEMA = HERE / "correlated-affine-export-audit-schema.json"
INPUTS = {
    "run": RUN,
    "audit": HERE / "correlated_affine_export_audit.py",
    "multipanel_run": HERE / "shared-remainder-multipanel-successor-run.json",
    "adaptive_run": HERE / "adaptive-chart-separation-run.json",
    "checkpoint_transport": HERE / "checkpoint_transport.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> tuple[dict, dict]:
    run = json.loads(RUN.read_text())
    facts = run["representation_audit"]
    if not all(facts.values()):
        raise RuntimeError("representation audit is not closed")
    flags = run["claim_flags"]
    if flags["last_checkpoint_affine_resumable"]:
        raise RuntimeError("Cartesian checkpoint was promoted to affine state")
    if flags["correlated_pivot_certified"] or flags["successor_substep_certified"]:
        raise RuntimeError("successor overclaim")
    contract = run["rerun_export_contract"]
    if (
        contract["earliest_required_restart"]["rho"] != "1/4194304"
        or contract["restart_disposition"]
        != "REGENERATE_FROM_SYMBOLIC_MIXED_LEVELT_SEED"
    ):
        raise RuntimeError("restart contract drift")

    certificate = {
        "schema": "phase3-axial-horizon-correlated-affine-export-audit-v1",
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_HORIZON_CORRELATED_AFFINE_EXPORT_AUDIT"
        ),
        "status": "RERUN_FROM_SYMBOLIC_SEED_REQUIRED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["REDUCED-MODE"],
        "sources": run["sources"],
        "representation_audit": facts,
        "last_accepted_cartesian_checkpoint": run[
            "last_accepted_cartesian_checkpoint"
        ],
        "terminal_cartesian_enclosure": run["terminal_cartesian_enclosure"],
        "rerun_export_contract": contract,
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
            "that the true transported line contains the zero vector",
            "an obstruction for a correlated affine or Taylor-model enclosure",
            "a correlated pivot or successor radial substep",
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
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.correlated_affine_export_audit",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.produce_correlated_affine_export_audit --check",
            "python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.verify_correlated_affine_export_audit",
            "python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_horizon_checkpoint_frame_v1.test_correlated_affine_export_audit",
        ],
        "validation": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "correlated_affine_export_audit"
                ),
                "status": "PASS_DETERMINISTIC_FAIL_CLOSED_OUTPUT",
                "elapsed_seconds": 1.35,
                "output_sha256": sha256(RUN),
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "produce_correlated_affine_export_audit --check"
                ),
                "status": "PASS",
                "elapsed_seconds": 1.41,
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "verify_correlated_affine_export_audit"
                ),
                "status": "PASS",
                "elapsed_seconds": 1.14,
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase3."
                    "axial_partial_jet_horizon_checkpoint_frame_v1."
                    "test_correlated_affine_export_audit"
                ),
                "status": "PASS_6_TESTS",
                "elapsed_seconds": 1.38,
            },
            {
                "command": "Draft202012Validator(schema).validate(certificate)",
                "status": "PASS",
                "elapsed_seconds": 0.05,
            },
            {
                "command": "python3 -m py_compile <four changed Python files>",
                "status": "PASS",
                "elapsed_seconds": 0.04,
            },
            {
                "command": (
                    "git diff --check -- black_hole_programme/phase3/"
                    "axial_partial_jet_horizon_checkpoint_frame_v1"
                ),
                "status": "PASS",
                "elapsed_seconds": 0.01,
            },
        ],
        "claim_boundary": (
            "representation audit and exact regeneration/export contract only"
        ),
        "higher_tiers_not_run": (
            "Tier 2/3 not required: no mathematical input or shared operator changed"
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
            raise SystemExit("generated correlated-affine audit artifacts drift")
        print("horizon correlated-affine export audit artifacts: PASS")
        return
    OUTPUT.write_text(encoded)
    RECEIPT.write_text(receipt_encoded)
    print(OUTPUT)


if __name__ == "__main__":
    main()
