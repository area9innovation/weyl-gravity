#!/usr/bin/env python3
"""Independent fail-closed checks for the nonlinear residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from residual_atlas.validate_fragment import validate


ROOT = Path(__file__).resolve().parents[2]
FRAGMENT = ROOT / "d_quotient_classical/atlas/nonlinear-atlas-fragment.json"
CERT = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_FILTERED_CYCLIC_BRANCH_EXTENSION_OBSTRUCTION_V1.json"
)
ENTRY_ID = "nonlinear.berger.filtered_cyclic_branch_extension.beta1_obstruction"
CROSSWALK_ID = "nonlinear.berger.crosswalk.retained36_to_residual_branches"
MIXED_ID = "nonlinear.berger.retained_mixed_ell3.filtered_cyclic_obstruction"
MIXED_DISPOSITION = (
    ROOT
    / "d_quotient_classical/certificates/"
    "BERGER_RETAINED_MIXED_ELL3_SECOND_JET_WITNESS_DISPOSITION_V1.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entry(value: dict, entry_id: str) -> dict:
    matches = [entry for entry in value["entries"] if entry["id"] == entry_id]
    if len(matches) != 1:
        raise ValueError(f"atlas entry cardinality drifted for {entry_id}")
    return matches[0]


def verify() -> dict:
    validate(FRAGMENT)
    value = json.loads(FRAGMENT.read_text())
    certificate = json.loads(CERT.read_text())

    generated_by = ROOT / value["generated_by"]
    if _sha256(generated_by) != value["generated_by_sha256"]:
        raise ValueError("atlas generator digest drifted")
    if certificate["result_state"] != (
        "ARITY_ONE_FILTERED_CYCLIC_BRANCH_SPLITTING_OBSTRUCTED_"
        "MINIMAL_PAGE_REPAIR_CLASSIFIED"
    ):
        raise ValueError("branch-extension authority drifted")

    entry = _entry(value, ENTRY_ID)
    if entry["scope"] != certificate["mode_scope"]:
        raise ValueError("branch-extension atlas scope was not copied exactly")
    expected_descriptions = {
        "causal": "NO_CERTIFIED_MAP",
        "symplectic": "OBSTRUCTED",
        "nonlinear": "OBSTRUCTED",
        "observational": "NO_CERTIFIED_MAP",
        "quantum": "NO_CERTIFIED_MAP",
    }
    if entry["descriptions"] != expected_descriptions:
        raise ValueError("branch-extension atlas lifecycle drifted")
    if entry["mode_data"]["resonance"]["status"] != "OBSTRUCTED":
        raise ValueError("beta_1 obstruction was not ledgered")
    if entry["mode_data"]["taub_maps"]["status"] != "NOT_APPLICABLE":
        raise ValueError("unary beta_1 was mislabelled as a Taub map")
    evidence = {
        (record["result_id"], record["path"], record["sha256"])
        for record in entry["evidence"]
    }
    expected_evidence = (
        certificate["result_id"],
        str(CERT.relative_to(ROOT)),
        _sha256(CERT),
    )
    if expected_evidence not in evidence:
        raise ValueError("branch-extension certificate evidence is absent or stale")

    crosswalk = _entry(value, CROSSWALK_ID)
    if any(status != "NO_CERTIFIED_MAP" for status in crosswalk["descriptions"].values()):
        raise ValueError("obstruction incorrectly activated the branch crosswalk")
    if expected_evidence not in {
        (record["result_id"], record["path"], record["sha256"])
        for record in crosswalk["evidence"]
    }:
        raise ValueError("crosswalk does not cite the unary obstruction")
    if certificate["claim_flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is not False:
        raise ValueError("source certificate authorized ell3 projection")

    disposition = json.loads(MIXED_DISPOSITION.read_text())
    mixed = _entry(value, MIXED_ID)
    if mixed["descriptions"]["nonlinear"] != "OPEN":
        raise ValueError("superseded ell3 obstruction was not reopened")
    if mixed["mode_data"]["resonance"]["status"] != "OPEN":
        raise ValueError("second-jet witness disposition was not ledgered")
    if "755/9" not in mixed["mode_data"]["resonance"]["statement"]:
        raise ValueError("exact second-jet pairing absent from atlas")
    disposition_evidence = (
        disposition["result_id"],
        str(MIXED_DISPOSITION.relative_to(ROOT)),
        _sha256(MIXED_DISPOSITION),
    )
    if disposition_evidence not in {
        (record["result_id"], record["path"], record["sha256"])
        for record in mixed["evidence"]
    }:
        raise ValueError("second-jet disposition evidence is absent or stale")
    if disposition["claim_flags"]["ORDER_TWO_FILTERED_REMOVAL_OBSTRUCTED"] is not False:
        raise ValueError("disposition retained the withdrawn obstruction")

    print("NONLINEAR_RESIDUAL_ATLAS_FRAGMENT_V1 independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
