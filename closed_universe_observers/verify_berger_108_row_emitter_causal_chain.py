#!/usr/bin/env python3
"""Independent verifier for the coefficientwise 108-row causal chain."""

from __future__ import annotations

import hashlib
import json

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_108_row_emitter_causal_chain import CERTIFICATE, DEPENDENCIES, SCHEMA, SOURCE_FILES, build


def verify() -> dict:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value != build():
        raise ValueError("108-row emitter causal-chain certificate is stale")
    for name, path in DEPENDENCIES.items():
        if value["dependency_refs"][name]["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"dependency hash drifted: {name}")
    manifest = {item["path"]: item["sha256"] for item in value["provenance"]["source_manifest"]}
    for path in SOURCE_FILES.values():
        relative = str(path.relative_to(CERTIFICATE.parents[2]))
        if manifest.get(relative) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"source hash drifted: {relative}")
    fixture = value["graded_exact_fixture"]
    if fixture["degrees"] != [-1, 0, 0, 0, 0, 1, 1, 1, 1, 2]:
        raise ValueError("independent graded carrier replay failed")
    for key in ("q_squared_defect_count", "left_green_defect_count_through_g2", "right_green_defect_count_through_g2", "chain_homotopy_defect_count_through_g2"):
        if fixture[key] != 0:
            raise ValueError(f"exact fixture defect: {key}")
    for key in ("UNQUALIFIED_FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED", "FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED", "DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED", "DETECTOR_RECOIL_COEFFICIENT_EVALUATED", "EMITTER_STRESS_BACKREACTION_INCLUDED", "QUANTUM_CLAIM"):
        if value["flags"][key] is not False:
            raise ValueError(f"overclaim accepted: {key}")
    return value


def main() -> int:
    verify()
    print("BERGER_108_ROW_POLARIZATION_EMITTER_CAUSAL_CHAIN_HOMOTOPY independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
