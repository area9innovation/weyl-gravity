#!/usr/bin/env python3
"""Independent verifier for the hardened Berger detector-record preflight."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
INPUT = PACKAGE / "fixtures/berger_localized_detector_records_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-localized-detector-records-input-v2.schema.json"
SCHEMA = PACKAGE / "schema/berger-localized-detector-records-v2.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _q(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _replay(data: dict, patch: dict | None = None) -> dict[str, bool | int | list[str]]:
    value = json.loads(json.dumps(data))
    value.update(patch or {})
    detectors = value["detectors"]
    labels = [_q(item) for item in value.get("detector_clock_labels", [row["clock_label"] for row in detectors])]
    arclengths = [_q(item) for item in value.get("detector_hopf_arclengths", [row["hopf_arclength"] for row in detectors])]
    centers = [[_q(item) for item in row] for row in value.get("detector_rod_centers", [row["rod_center"] for row in detectors])]
    radii = [_q(row["rod_radius"]) for row in detectors]
    raw_jacobians = value.get("rod_jacobians", [row["relational_jacobian"] for row in value["rod_charts"]])
    jacobians = [sp.Matrix([[_q(item) for item in row] for row in matrix]) for matrix in raw_jacobians]
    cauchy_clocks = [_q(row["cauchy_clock"]) for row in value["rod_charts"]]
    spatially_disjoint = any(abs(centers[0][axis] - centers[1][axis]) >= radii[0] + radii[1] for axis in range(3))
    supports_disjoint = labels[0] != labels[1] or spatially_disjoint
    matrix = sp.eye(2) if supports_disjoint else sp.ones(2)
    emitter_clock = _q(value["emitter"]["clock_label"])
    emitter_position = _q(value["emitter"]["hopf_arclength"])
    rate = _q(value["clock_rate"])
    distances = [abs(item - emitter_position) for item in arclengths]
    residuals = [sp.simplify(labels[index] - emitter_clock - rate * distances[index]) for index in range(2)]
    lower_bound = _q(value["hopf_geometry"]["certified_lower_bound"])
    half_fibre_length = 3 * sp.sqrt(10) * sp.pi / 10
    return {
        "rod_solutions_nondegenerate": all(item.det() != 0 for item in jacobians) and cauchy_clocks == labels,
        "clock_labels_distinct": len(set(labels)) == 2,
        "detector_supports_disjoint": supports_disjoint,
        "central_null_incidence_exact": residuals == [0, 0],
        "central_rays_unique_no_wrap": (
            lower_bound < half_fibre_length
            and all(0 < item < lower_bound for item in distances)
        ),
        "record_functionals_independent": matrix.rank() == 2,
        "probe_memory_persistent": (
            value["memory_model"]["probe_branch"] == "p_a=0"
            and value["memory_model"]["initial_memory"] == ["0", "0"]
        ),
        "rank": int(matrix.rank()),
        "residuals": [sp.sstr(item) for item in residuals],
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
        relative = dependency["path"]
        pinned_bytes = subprocess.check_output(
            ["git", "show", f"{dependency['snapshot_commit']}:{_prefix()}{relative}"], cwd=ROOT
        )
        pinned = json.loads(pinned_bytes)
        if _sha256_bytes(pinned_bytes) != dependency["sha256"]:
            raise AssertionError(f"pinned dependency not reproducible: {relative}")
        if pinned["result_id"] != dependency["result_id"] or pinned["claim_boundary"] != dependency["claim_boundary"]:
            raise AssertionError(f"pinned dependency metadata mismatch: {relative}")
        live = json.loads((ROOT / relative).read_text())
        if live["result_id"] != dependency["result_id"]:
            raise AssertionError(f"live dependency result mismatch: {relative}")
        for flag in dependency["live_required_flags"]:
            if live.get("flags", {}).get(flag) is not True:
                raise AssertionError(f"live compatibility flag dropped ({flag}): {relative}")

    base = _replay(data)
    required = (
        "rod_solutions_nondegenerate", "clock_labels_distinct", "detector_supports_disjoint",
        "central_null_incidence_exact", "central_rays_unique_no_wrap",
        "record_functionals_independent", "probe_memory_persistent",
    )
    if not all(base[name] for name in required) or base["rank"] != 2 or base["residuals"] != ["0", "0"]:
        raise AssertionError(f"independent base replay failed: {base}")
    persisted = {item["name"]: item for item in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        result = _replay(data, mutation["patch"])
        requirement = mutation["expected_failed_requirement"]
        if result[requirement] is not False:
            raise AssertionError(f"mutation did not fail independently: {mutation['name']}")
        if persisted[mutation["name"]]["observed_requirement_value"] is not False:
            raise AssertionError(f"persisted mutation mismatch: {mutation['name']}")
    if certificate["flags"]["SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"] is not False:
        raise AssertionError("retarded transfer matrix was promoted without computation")
    if certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is not False:
        raise AssertionError("partial observer map was promoted")
    print("BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
