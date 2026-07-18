#!/usr/bin/env python3
"""Independent verifier for the generated quantum residual-atlas fragment."""

from __future__ import annotations

import hashlib
import json

from .generate_quantum_atlas_fragment import (
    DEPENDENCIES,
    OUTPUT,
    ROOT,
    STATUSES,
    build,
    validate_fragment,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    value = json.loads(OUTPUT.read_text())
    validate_fragment(value)
    if value != build() or value["status_vocabulary"] != STATUSES:
        raise ValueError("quantum atlas fragment does not reproduce")
    generator = ROOT / value["generated_by"]
    if value["generated_by_sha256"] != _sha256(generator):
        raise ValueError("quantum atlas generator hash drifted")

    evidence_paths = set()
    for entry in value["entries"]:
        for item in entry["evidence"]:
            evidence_path = ROOT / item["path"]
            evidence_value = json.loads(evidence_path.read_text())
            identifier = (
                evidence_value.get("result_id")
                or evidence_value.get("certificate_id")
                or evidence_value.get("schema")
            )
            result_id = str(identifier) if identifier is not None else "UNIDENTIFIED"
            if item["sha256"] != _sha256(evidence_path) or item["result_id"] != result_id:
                raise ValueError(f"quantum atlas evidence drifted: {item['path']}")
            evidence_paths.add(evidence_path.resolve())
    missing = {path.resolve() for path in DEPENDENCIES.values()} - evidence_paths
    if missing:
        raise ValueError(f"quantum atlas dependencies absent from entries: {sorted(map(str, missing))}")

    quantum_rows = [entry["quantum_data"] for entry in value["entries"]]
    if any(row["Hadamard_two_point_function"]["status"] == "CERTIFIED" for row in quantum_rows):
        raise ValueError("uncertified Hadamard state was promoted")
    if any(row["particle_interpretation"]["statement"] == "PARTICLE" for row in quantum_rows):
        raise ValueError("non-particle carrier was promoted")
    tangent = next(
        row for row in quantum_rows if row["entry_kind"] == "CLASSICAL_TO_QUANTUM_CROSSWALK"
    )
    if (
        tangent["carrier_crosswalk"]["status"] != "NO_CERTIFIED_MAP"
        or tangent["anomaly_QME_dependency"]["status"] != "OBSTRUCTED"
    ):
        raise ValueError("classical tangent obstruction crossed the quantum boundary")
    print("quantum residual-atlas fragment independent verification: PASS")
    return value


if __name__ == "__main__":
    verify()
