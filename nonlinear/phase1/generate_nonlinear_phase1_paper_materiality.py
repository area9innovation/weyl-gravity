#!/usr/bin/env python3
"""Generate reverse materiality records for Papers 05, 06 and 11."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_REL = "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json"
OUT = ROOT / "planning/paper-coverage/nonlinear-phase1-interaction-materiality-2026-07-21.json"


def build() -> dict:
    source = ROOT / SOURCE_REL
    return {
        "schema": "pure-weyl-paper-materiality-record-v1",
        "result_id": "NONLINEAR_PHASE1_INTERACTION_PAPER_MATERIALITY_2026_07_21",
        "source_result_id": "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "records": [
            {
                "paper": "05",
                "materiality": "NOT_APPLICABLE_DISTINCT_MODEL",
                "required_scope": "Paper 05 treats scalar and two-field oscillator deformation problems, not the compact Berger gravity-clock-Maxwell carrier; no mode or deformation-class identification is authorized.",
                "publication_edit": "NOT_REQUIRED",
            },
            {
                "paper": "06",
                "materiality": "NOT_APPLICABLE_DISTINCT_MODEL",
                "required_scope": "Paper 06 treats its own flat regular-split Einstein-Weyl branch and shell obstruction; it is not evidence for the compact Berger retained ell3 or counterflow candidate.",
                "publication_edit": "NOT_REQUIRED",
            },
            {
                "paper": "11",
                "materiality": "CURRENT_RECONCILED",
                "required_scope": "Retain representative-level q2/q3/ell3 and full-BV cyclicity; keep the complete bounded cyclic class, cohomology operation and branch mixing open; keep counterflow outside this paper without a crosswalk.",
                "publication_edit": "ALREADY_RECONCILED_BY_PAPER11_CURRENT_INTERACTION_STATUS",
            },
        ],
        "claim_boundary": "These reverse materiality records neither edit the live papers nor identify operations across backgrounds, actions or carrier languages.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(rendered, encoding="utf-8")
        return 0
    if not OUT.is_file() or OUT.read_text(encoding="utf-8") != rendered:
        raise SystemExit("FAIL: stale nonlinear Phase-1 paper materiality records")
    print("PASS: nonlinear Phase-1 reverse materiality records are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
