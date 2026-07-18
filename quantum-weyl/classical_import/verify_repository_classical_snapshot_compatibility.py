"""Independent verifier for the physical classical-snapshot compatibility bridge."""

from __future__ import annotations

from copy import deepcopy
import json

from .classical_snapshot_compatibility_receiver import validate_classical_snapshot_compatibility
from .repository_classical_snapshot_compatibility import LOCAL_IMPORT, OUTPUT, ROOT, build


def verify() -> dict:
    checked = json.loads(OUTPUT.read_text())
    local = json.loads(LOCAL_IMPORT.read_text())
    receipt = validate_classical_snapshot_compatibility(
        checked,
        repository_root=ROOT,
        expected_local_commit=local["classical_commit"],
        expected_local_hashes=local["independent_replay"]["canonical_hashes"],
        expected_analytic_commit=checked["analytic_operator_snapshot"]["classical_commit"],
    )
    if receipt["status"] != "SEMANTIC_RECEIVER_ACCEPTED" or checked != build():
        raise ValueError("physical snapshot compatibility bridge does not reproduce")
    mutant = deepcopy(checked)
    mutant["analytic_operator_snapshot"]["canonical_hashes"]["scope_hash"] = "0" * 64
    try:
        validate_classical_snapshot_compatibility(
            mutant,
            repository_root=ROOT,
            expected_local_commit=local["classical_commit"],
            expected_local_hashes=local["independent_replay"]["canonical_hashes"],
            expected_analytic_commit=checked["analytic_operator_snapshot"]["classical_commit"],
        )
    except ValueError:
        pass
    else:
        raise ValueError("analytic scope-hash mutation crossed compatibility bridge")
    return checked


if __name__ == "__main__":
    verify()
    print("independent repository classical snapshot compatibility verifier: PASS")
