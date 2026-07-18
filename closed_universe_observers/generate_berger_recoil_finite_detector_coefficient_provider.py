#!/usr/bin/env python3
"""Certify the public finite detector-coefficient interval provider."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import detector_profile_coefficient_interval


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER.json"
SCHEMA = PACKAGE / "schema/berger-recoil-finite-detector-coefficient-provider-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-finite-detector-coefficient-provider.md"
DEPENDENCIES = {
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "shell_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
}
SOURCE_FILES = [
    Path(__file__), PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "verify_berger_recoil_finite_detector_coefficient_provider.py",
    PACKAGE / "tests/test_berger_recoil_finite_detector_coefficient_provider.py",
    SCHEMA, REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mutation_detected(certificate: dict[str, Any], **updates: Any) -> bool:
    arguments = {
        "detector": "D0", "two_j": 0,
        "block": "spatial_one_form_advanced_polynomial",
        "coframe_component": 3, "row": 0, "column": 0, "t_power": 0,
    }
    arguments.update(updates)
    try:
        detector_profile_coefficient_interval(certificate, **arguments)
    except ValueError:
        return True
    return False


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    if values["detector_image"]["flags"]["FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED"] is not True:
        raise AssertionError("finite detector image dependency dropped")
    if values["shell_word"]["flags"]["DETECTOR_SELECTED_PREPARATION_WORD_EXPORTED"] is not True:
        raise AssertionError("detector preparation word dependency dropped")
    fixture = detector_profile_coefficient_interval(
        values["detector_image"], detector="D0", two_j=0,
        block="spatial_one_form_advanced_polynomial", coframe_component=3,
        row=0, column=0, t_power=0,
    )
    if not (fixture["real"]["upper"].startswith("-") and fixture["imaginary"]["lower"].startswith("-")):
        raise AssertionError("finite coefficient fixture sign enclosure drifted")
    zero = detector_profile_coefficient_interval(
        values["detector_image"], detector="D0", two_j=0,
        block="temporal_scalar_advanced_polynomial", coframe_component=None,
        row=0, column=0, t_power=0,
    )
    if zero["structural_zero"] is not True:
        raise AssertionError("structural-zero fixture drifted")
    fixture_hash = hashlib.sha256(json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    mutations = [
        {"name": "request_two_j5", "detected": _mutation_detected(values["detector_image"], two_j=5)},
        {"name": "omit_spatial_coframe", "detected": _mutation_detected(values["detector_image"], coframe_component=None)},
        {"name": "unknown_block", "detected": _mutation_detected(values["detector_image"], block="massive_recoil_channel")},
    ]
    if not all(row["detected"] for row in mutations):
        raise AssertionError("finite provider scope mutation escaped")
    boundary = (
        "This validated LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exposes the "
        "certified BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE data through the "
        "public detector_profile_coefficient_interval callable. It returns exact "
        "rational real/imaginary polynomial-coefficient enclosures and the uniform "
        "entire-series remainder for D0 or D1, both advanced Maxwell blocks, and "
        "two_j=0,...,4; omitted entries in the validated index domain are explicit "
        "structural zeros. Mutations reject two_j=5, a missing spatial coframe and "
        "an undeclared block. This is not an all-shell provider and does not evaluate "
        "the massive advanced image, positive-energy Cauchy preparation, nested recoil "
        "convolution, multi-shell tail, physical recoil, cone, Bridge 3 or quantum data."
    )
    return {
        "schema": "closed-universe-berger-recoil-finite-detector-coefficient-provider-v1",
        "result_id": "BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER",
        "setting_id": values["detector_image"]["setting_id"],
        "claim_status": "FINITE_ADVANCED_MAXWELL_DETECTOR_COEFFICIENT_CALLABLE_TWO_J0_TO_4_CERTIFIED",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)} for name, path in DEPENDENCIES.items()},
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock and Maxwell detector apparatus",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "R x S3 with compact detector windows and no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "finite advanced Maxwell detector coefficient polynomials",
            "degree": "spatial one-form and temporal scalar blocks",
            "parity": "D0 axial and D1 transverse detector polarizations",
            "ell": "two_j=0,1,2,3,4",
            "m": "all representation rows",
            "k": "all representation columns",
            "omega": "entire-series advanced Maxwell time kernel through order five plus certified remainder",
        },
        "callable_contract": {
            "module": "closed_universe_observers.berger_recoil_interval_stream",
            "callable": "detector_profile_coefficient_interval",
            "coverage": "D0,D1; spatial/temporal advanced Maxwell blocks; two_j=0,...,4",
            "not_covered": "two_j>=5, massive image and nested recoil channel",
        },
        "fixture": {"lookup": "D0/two_j0/spatial/coframe3/row0/column0/T0", "canonical_sha256": fixture_hash, "structural_zero_lookup_passed": True},
        "mutation_results": mutations,
        "flags": {
            "FINITE_DETECTOR_COEFFICIENT_PROVIDER_TWO_J0_TO_4_EXPORTED": True,
            "COMPLETE_DETECTOR_COEFFICIENT_PROVIDER_EXPORTED": False,
            "NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXTEND_DETECTOR_COEFFICIENT_PROVIDER_BEYOND_TWO_J4_AND_IMPLEMENT_NESTED_TIME_CONVOLUTION",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale finite detector coefficient provider")
    print("BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
