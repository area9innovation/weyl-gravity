#!/usr/bin/env python3
"""Independent verifier for the counterflow full-BV Hadamard nonactivation."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/lorentzian/certificates/TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1.json"
SCHEMA = ROOT / "quantum-weyl/lorentzian/schema/two-phase-counterflow-full-bv-hadamard-nonactivation-v1.schema.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-full-bv-hadamard-nonactivation-fragment-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(cert: dict[str, Any], atlas: dict[str, Any], hashes: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    if hashes:
        for ref in cert["source_refs"].values():
            path = ROOT / ref["path"]
            assert sha(path) == ref["sha256"]
            assert json.loads(path.read_text())["result_id"] == ref["result_id"]
    gate = cert["activation_gate"]
    assert gate["q70_v2_imported"] is True
    assert gate["stale_v1_rejected"] is True
    assert gate["robust_stationary_counterflow_locus"] is False
    assert gate["candidate_specific_quantum_activated"] is False
    assert "DO_NOT_CONSTRUCT" in gate["stop_branch"]
    boundary = cert["classical_quantum_boundary"]
    assert boundary["classical_mode_imported"] is True
    assert boundary["classical_causal_propagator_is_quantum_state"] is False
    assert boundary["robust_physical_clock_carrier"] == "OBSTRUCTED"
    disposition = cert["full_bv_hadamard_disposition"]
    computed = [
        "all_70_rows_covered", "antisymmetric_part_equals_causal_propagator",
        "q54_hadamard_wavefront_set", "q16_contractible_block_treatment",
        "brst_q_ward_identity", "graded_adjoint_reality", "k_stationarity",
    ]
    assert all(disposition[key] == "NOT_COMPUTED" for key in computed)
    inactive = [
        "compatible_complex_structure", "hadamard_two_point_function",
        "state_space_status", "physical_positivity",
    ]
    assert all(disposition[key] == "NOT_ACTIVATED" for key in inactive)
    brst = cert["brst_and_qme_status"]
    assert brst["brst_cocycle"] == "NOT_EVALUATED"
    assert brst["brst_exactness"] == "NOT_EVALUATED"
    assert brst["local_anomaly"] == "NOT_ACTIVATED"
    assert brst["qme"] == "NOT_ACTIVATED"
    assert set(cert["downstream_activation"].values()) == {False}
    assert all(value == "REJECT" for value in cert["mutation_expectations"].values())
    entry = atlas["entries"][0]
    assert entry["descriptions"]["causal"] == "CERTIFIED"
    assert entry["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
    assert "Hadamard" not in entry["mode_data"]["lee_wald"]["statement"]


def reject(cert: dict[str, Any], atlas: dict[str, Any], mutate: Callable[..., None]) -> None:
    c, a = copy.deepcopy(cert), copy.deepcopy(atlas)
    mutate(c, a)
    try:
        verify(c, a, hashes=False)
    except (AssertionError, KeyError, ValidationError):
        return
    raise AssertionError("contradiction mutation accepted")


def main() -> int:
    cert = json.loads(CERT.read_text())
    atlas = json.loads(ATLAS.read_text())
    verify(cert, atlas)
    mutations = [
        lambda c, a: c["activation_gate"].update(robust_stationary_counterflow_locus=True),
        lambda c, a: c["activation_gate"].update(candidate_specific_quantum_activated=True),
        lambda c, a: c["activation_gate"].update(q70_v2_imported=False, stale_v1_rejected=False),
        lambda c, a: c["full_bv_hadamard_disposition"].update(all_70_rows_covered="CERTIFIED"),
        lambda c, a: c["full_bv_hadamard_disposition"].update(q54_hadamard_wavefront_set="CERTIFIED"),
        lambda c, a: c["full_bv_hadamard_disposition"].update(brst_q_ward_identity="CERTIFIED"),
        lambda c, a: c["full_bv_hadamard_disposition"].update(compatible_complex_structure="CERTIFIED"),
        lambda c, a: c["full_bv_hadamard_disposition"].update(physical_positivity="POSITIVE"),
        lambda c, a: c["brst_and_qme_status"].update(qme="QME_RESTORED"),
        lambda c, a: a["entries"][0]["descriptions"].update(quantum="CERTIFIED"),
    ]
    for mutation in mutations:
        reject(cert, atlas, mutation)
    print(f"TWO_PHASE_COUNTERFLOW_FULL_BV_HADAMARD_NONACTIVATION_V1 independent verification: PASS ({len(mutations)} mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
