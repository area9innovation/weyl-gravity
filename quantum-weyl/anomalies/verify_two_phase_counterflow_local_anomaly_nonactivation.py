#!/usr/bin/env python3
"""Independent verifier for counterflow anomaly nonactivation."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "quantum-weyl/anomalies/certificates/TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1.json"
SCHEMA = ROOT / "quantum-weyl/anomalies/schema/two-phase-counterflow-local-anomaly-nonactivation-v1.schema.json"
ATLAS = ROOT / "residual_atlas/two-phase-counterflow-local-anomaly-nonactivation-fragment-v1.json"
MATERIALITY = ROOT / "planning/paper-coverage/quantum-counterflow-anomaly-nonactivation-2026-07-21.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(cert: dict[str, Any], atlas: dict[str, Any], materiality: dict[str, Any], hashes: bool = True) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(cert)
    if hashes:
        for ref in cert["source_refs"].values():
            path = ROOT / ref["path"]
            assert sha(path) == ref["sha256"]
            source = json.loads(path.read_text())
            assert source["result_id"] == ref["result_id"]
    gate = cert["gate_evaluation"]
    assert gate["q70_v2_imported"] is True
    assert gate["stale_v1_rejected"] is True
    assert gate["robust_stationary_counterflow_locus"] is False
    assert gate["candidate_specific_quantum_activated"] is False
    assert "DO_NOT_COMPUTE" in gate["stop_branch"]
    disposition = cert["local_anomaly_disposition"]
    assert disposition["ghost_number_one_quotient"] == "NOT_COMPUTED"
    assert all(disposition[key] == "NOT_COMPUTED" for key in ["diff_sector", "diagonal_u1_sector", "weyl_compensator_sector", "mixed_sector", "cohomology_coefficients"])
    assert all(disposition[key] == "NOT_ACTIVATED" for key in ["regulator", "qap", "qme", "hadamard"])
    strict = cert["strict_weyl_import"]
    assert strict["imported_as_counterflow_result"] is False
    assert strict["C2_coefficient"] is None and strict["E4_coefficient"] is None
    assert "TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1" in cert["rejected_inputs"]
    assert cert["phase1_crosscheck"]["counterflow_lifecycle"] == "NOT_ACTIVATED"
    assert set(cert["phase1_crosscheck"]["counterflow_promotions"].values()) == {"NOT_ACTIVATED"}
    assert all(value == "REJECT" for value in cert["mutation_expectations"].values())
    assert atlas["entries"][0]["descriptions"]["quantum"] == "NO_CERTIFIED_MAP"
    assert atlas["entries"][0]["descriptions"]["causal"] == "CERTIFIED"
    assert materiality["source_result_id"] == cert["result_id"]
    expected = hashlib.sha256((json.dumps(cert, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    assert materiality["source_sha256"] == expected


def reject(cert: dict[str, Any], atlas: dict[str, Any], materiality: dict[str, Any], mutate: Callable) -> None:
    c, a, m = copy.deepcopy(cert), copy.deepcopy(atlas), copy.deepcopy(materiality)
    mutate(c, a, m)
    try:
        verify(c, a, m, hashes=False)
    except (AssertionError, KeyError, ValidationError):
        return
    raise AssertionError("contradiction mutation accepted")


def main() -> int:
    cert, atlas, materiality = json.loads(CERT.read_text()), json.loads(ATLAS.read_text()), json.loads(MATERIALITY.read_text())
    verify(cert, atlas, materiality)
    mutations = [
        lambda c, a, m: c["gate_evaluation"].update(robust_stationary_counterflow_locus=True),
        lambda c, a, m: c["gate_evaluation"].update(candidate_specific_quantum_activated=True),
        lambda c, a, m: c["gate_evaluation"].update(q70_v2_imported=False, stale_v1_rejected=False),
        lambda c, a, m: c["strict_weyl_import"].update(C2_coefficient="199/30"),
        lambda c, a, m: c["local_anomaly_disposition"].update(ghost_number_one_quotient="ZERO"),
        lambda c, a, m: c["local_anomaly_disposition"].update(qme="QME_RESTORED"),
        lambda c, a, m: c["local_anomaly_disposition"].update(hadamard="CERTIFIED"),
    ]
    for mutation in mutations:
        reject(cert, atlas, materiality, mutation)
    print(f"TWO_PHASE_COUNTERFLOW_LOCAL_ANOMALY_NONACTIVATION_V1 independent verification: PASS ({len(mutations)} mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
