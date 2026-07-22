#!/usr/bin/env python3
"""Independently replay the Hadamard nonactivation receipt against Git blobs."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "quantum-weyl/lorentzian/receipts/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1_TIER_RECEIPT.json"
REPO_PREFIX = "physics/symplectic-reconstruction/"
OUTPUT_PATHS = {
    "generator": "quantum-weyl/lorentzian/two_phase_counterflow_full_bv_hadamard_nonactivation.py",
    "verifier": "quantum-weyl/lorentzian/verify_two_phase_counterflow_full_bv_hadamard_nonactivation.py",
    "schema": "quantum-weyl/lorentzian/schema/two-phase-counterflow-full-bv-hadamard-nonactivation-v1.schema.json",
    "certificate": "quantum-weyl/lorentzian/certificates/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1.json",
    "tests": "quantum-weyl/lorentzian/tests/test_two_phase_counterflow_full_bv_hadamard_nonactivation.py",
    "report": "quantum-weyl/reports/two-phase-counterflow-full-bv-hadamard-nonactivation-v1.md",
    "atlas": "residual_atlas/two-phase-counterflow-full-bv-hadamard-nonactivation-fragment-v1.json",
    "team_brief": "notes/d-quotient-quantum-team-brief.md",
    "closeout": "reports/quantum-two-phase-counterflow-v2-full-bv-hadamard-preflight-closeout-2026-07-21.md",
}


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{REPO_PREFIX}{path}"], cwd=ROOT
    )


def verify(receipt: dict[str, object]) -> None:
    assert receipt["result_id"] == "TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1_TIER_RECEIPT"
    commit = str(receipt["scientific_result_commit"])
    subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    recorded = receipt["output_hashes"]
    assert isinstance(recorded, dict)
    assert set(recorded) == set(OUTPUT_PATHS)
    for name, path in OUTPUT_PATHS.items():
        actual = hashlib.sha256(git_blob(commit, path)).hexdigest()
        assert recorded[name] == actual, (name, recorded[name], actual)


def main() -> int:
    receipt = json.loads(RECEIPT.read_text())
    verify(receipt)
    mutated = copy.deepcopy(receipt)
    mutated["output_hashes"]["certificate"] = "0" * 64
    try:
        verify(mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError("mutated committed-blob hash accepted")
    print("TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1 receipt replay: PASS (1 mutation rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
