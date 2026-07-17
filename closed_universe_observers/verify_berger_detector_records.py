#!/usr/bin/env python3
"""Independent exact verifier for the localized Berger detector records."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_localized_detector_records_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-localized-detector-records-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-localized-detector-records-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _replay(data: dict, patch: dict | None = None) -> dict[str, bool | int]:
    patched = json.loads(json.dumps(data))
    patched.update(patch or {})
    jacobian = sp.Matrix([[_q(value) for value in row] for row in patched["relational_jacobian"]])
    detectors = patched["detectors"]
    labels = [_q(value) for value in patched.get("detector_clock_labels", [item["clock_label"] for item in detectors])]
    windows = [[_q(value) for value in row] for row in patched.get("detector_clock_windows", [item["clock_window"] for item in detectors])]
    centers = [[_q(value) for value in row] for row in patched.get("detector_rod_centers", [item["rod_center"] for item in detectors])]
    widths = [_q(item["rod_half_width"]) for item in detectors]
    time_disjoint = windows[0][1] <= windows[1][0] or windows[1][1] <= windows[0][0]
    space_disjoint = any(abs(centers[0][axis] - centers[1][axis]) >= widths[0] + widths[1] for axis in range(3))
    ids = [item["id"] for item in detectors]
    matrix = sp.Matrix([[int(support == detector_id) for support in patched["probe_supports"]] for detector_id in ids])
    return {
        "relational_chart_nondegenerate": jacobian.det() != 0,
        "clock_labels_distinct": len(set(labels)) == 2,
        "detector_supports_disjoint": time_disjoint or space_disjoint,
        "record_functionals_independent": matrix.rank() == 2,
        "rank": int(matrix.rank()),
    }


def main() -> int:
    data = json.loads(INPUT.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    if certificate["provenance"]["declared_input_sha256"] != _sha256(INPUT):
        raise AssertionError("detector record input drifted")
    for source in certificate["provenance"]["source_manifest"]:
        if _sha256(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")
    for dependency in certificate["dependency_refs"].values():
        path = ROOT / dependency["path"]
        payload = json.loads(path.read_text())
        if _sha256(path) != dependency["sha256"] or payload["result_id"] != dependency["result_id"]:
            raise AssertionError(f"dependency drift: {dependency['path']}")
        if payload["claim_boundary"] != dependency["claim_boundary"]:
            raise AssertionError(f"dependency boundary drift: {dependency['path']}")
    base = _replay(data)
    if not all(base[name] for name in (
        "relational_chart_nondegenerate", "clock_labels_distinct",
        "detector_supports_disjoint", "record_functionals_independent",
    )) or base["rank"] != 2:
        raise AssertionError(f"independent base replay failed: {base}")
    persisted = {item["name"]: item for item in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        result = _replay(data, mutation["patch"])
        requirement = mutation["expected_failed_requirement"]
        if result[requirement] is not False:
            raise AssertionError(f"mutation did not fail independently: {mutation['name']}")
        if persisted[mutation["name"]]["observed_requirement_value"] is not False:
            raise AssertionError(f"persisted mutation mismatch: {mutation['name']}")
    if certificate["flags"]["TWO_NONZERO_RETARDED_RECORD_VALUES"] is not False:
        raise AssertionError("pointwise retarded response was promoted without a witness")
    if certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is not False:
        raise AssertionError("partial observer map was promoted")
    print("BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
