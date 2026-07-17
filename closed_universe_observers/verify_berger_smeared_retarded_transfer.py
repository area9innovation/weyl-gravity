#!/usr/bin/env python3
"""Independent replay of the rank-two Berger retarded transfer."""

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
INPUT = PACKAGE / "fixtures/berger_smeared_retarded_transfer_input.json"
INPUT_SCHEMA = PACKAGE / "schema/berger-smeared-retarded-transfer-input-v1.schema.json"
SCHEMA = PACKAGE / "schema/berger-smeared-retarded-transfer-v1.schema.json"
CERTIFICATE = PACKAGE / "certificates/BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER.json"


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _q(value: str | int) -> sp.Rational:
    item = Fraction(str(value))
    return sp.Rational(item.numerator, item.denominator)


def _prefix() -> str:
    return subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True).strip()


def _replay(data: dict, patch: dict | None = None) -> dict:
    value = json.loads(json.dumps(data))
    value.update(patch or {})
    beta = 2 * sp.sqrt(10) / 3
    rate = _q(value["clock_rate"])
    detector_times = [_q(row["clock_center"]) / rate for row in value["detectors"]]
    half_widths = [
        _q(item) / rate
        for item in value.get("detector_clock_half_widths", [row["clock_half_width"] for row in value["detectors"]])
    ]
    phase_origins = [_q(row["phase_origin_physical_time"]) for row in value["source_channels"]]
    source_polarizations = value.get("source_polarizations", [row["polarization"] for row in value["source_channels"]])
    detector_components = value.get("detector_components", [row["electric_component"] for row in value["detectors"]])
    masses = [_q(row["smearing_mass"]) for row in value["detectors"]]
    source_end = _q(value.get("switch_on_end", value["switch_on"]["physical_time_end"]))
    divergence = value.get("source_divergence_residuals", ["0", "0"])
    operator_frequency_squared = _q(value["forced_operator_frequency_squared"]) if "forced_operator_frequency_squared" in value else beta**2

    time = sp.Symbol("t", real=True)
    amplitude = sp.Function("a")(time)
    modes = [sp.sin(beta * (time - origin)) / beta for origin in phase_origins]
    full_mode = all(sp.trigsimp(sp.diff(mode, time, 2) + operator_frequency_squared * mode) == 0 for mode in modes)
    full_form_residuals = [
        sp.simplify(
            -(sp.diff(amplitude, time, 2) + beta**2 * amplitude)
            + (sp.diff(amplitude, time, 2) + operator_frequency_squared * amplitude)
        ),
        sp.simplify(
            (sp.diff(amplitude, time, 2) + beta**2 * amplitude)
            - (sp.diff(amplitude, time, 2) + operator_frequency_squared * amplitude)
        ),
    ]
    unit_origins = all(sp.trigsimp(sp.diff(modes[index], time).subs(time, phase_origins[index])) == 1 for index in range(2))

    incidence = sp.zeros(2)
    positive = []
    for a in range(2):
        for b in range(2):
            if detector_components[a][-1] != source_polarizations[b][-1]:
                continue
            incidence[a, b] = 1
            span = sp.simplify(beta * (abs(detector_times[a] - phase_origins[b]) + half_widths[a]))
            positive.append(masses[a] > 0 and sp.simplify(sp.Rational(3, 2) - span).is_positive is True)
    rank = int(incidence.rank())
    diagonal_positive = incidence == sp.eye(2) and len(positive) == 2 and all(positive)
    rank_two = rank == 2 and diagonal_positive
    requirements = {
        "currents_conserved": divergence == ["0", "0"],
        "sources_strictly_before_detector_windows": all(source_end < detector_times[a] - half_widths[a] for a in range(2)),
        "full_maxwell_mode_equations_exact": operator_frequency_squared == beta**2 and full_mode and full_form_residuals == [0, 0] and unit_origins,
        "positive_diagonal_response": diagonal_positive,
        "transfer_matrix_rank_two": rank_two,
        "persistent_record_vectors_distinguishable": rank_two,
    }
    return {"requirements": requirements, "rank": rank}


def main() -> int:
    data = json.loads(INPUT.read_text())
    certificate = json.loads(CERTIFICATE.read_text())
    input_schema = json.loads(INPUT_SCHEMA.read_text())
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(input_schema)
    jsonschema.Draft202012Validator(input_schema).validate(data)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(certificate)
    if certificate["provenance"]["declared_input_sha256"] != _hash(INPUT):
        raise AssertionError("transfer input drifted")
    for source in certificate["provenance"]["source_manifest"]:
        if _hash(ROOT / source["path"]) != source["sha256"]:
            raise AssertionError(f"source drift: {source['path']}")
    for dependency in certificate["dependency_refs"].values():
        raw = subprocess.check_output(
            ["git", "show", f"{dependency['snapshot_commit']}:{_prefix()}{dependency['path']}"], cwd=ROOT
        )
        pinned = json.loads(raw)
        if _hash_bytes(raw) != dependency["sha256"]:
            raise AssertionError(f"snapshot dependency hash mismatch: {dependency['path']}")
        if pinned["result_id"] != dependency["result_id"] or pinned["claim_boundary"] != dependency["claim_boundary"]:
            raise AssertionError(f"snapshot dependency metadata mismatch: {dependency['path']}")
        live = json.loads((ROOT / dependency["path"]).read_text())
        for flag in dependency["live_required_flags"]:
            if live.get("flags", {}).get(flag) is not True:
                raise AssertionError(f"live dependency flag dropped: {dependency['path']}:{flag}")

    base = _replay(data)
    if not all(base["requirements"].values()) or base["rank"] != 2:
        raise AssertionError(f"independent transfer replay failed: {base}")
    persisted = {row["name"]: row for row in certificate["mutation_results"]}
    for mutation in data["mutations"]:
        result = _replay(data, mutation["patch"])
        required = mutation["expected_failed_requirement"]
        if result["requirements"][required] is not False:
            raise AssertionError(f"mutation did not fail: {mutation['name']}")
        if persisted[mutation["name"]]["observed_requirement_value"] is not False:
            raise AssertionError(f"persisted mutation mismatch: {mutation['name']}")
    if certificate["transfer_matrix"]["rank"] != 2 or certificate["transfer_matrix"]["determinant_sign"] != "positive":
        raise AssertionError("rank-two transfer witness dropped")
    if certificate["flags"]["SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES"] is not False:
        raise AssertionError("homogeneous sources were promoted to localized emitters")
    if certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is not False:
        raise AssertionError("observer map was promoted before quotient descent")
    print("BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER independent replay: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
