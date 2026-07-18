#!/usr/bin/env python3
"""Independent checks for the transverse Nariai curvature-jet gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-pbw-curvature-jet-gate-v1.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if value["lifecycle_state"] != "OBSTRUCTED":
        raise AssertionError("parallel-PBW obstruction lifecycle drifted")
    if not all(value["exact_checks"].values()):
        raise AssertionError("an exact curvature-jet check failed")
    if value["exact_data"]["curvature_jet"]["nonparallel_witness"]["value"] != "-sqrt(2)":
        raise AssertionError("nonparallel witness drifted")
    t = sp.symbols("t", real=True)
    independent = sp.diff(-sp.sinh(t), t)
    independent_at_star = sp.expand_trig(independent).subs(
        {sp.sinh(t): 1, sp.cosh(t): sp.sqrt(2)}
    )
    if str(sp.simplify(independent_at_star)) != "-sqrt(2)":
        raise AssertionError("independent curvature-jet reconstruction failed")
    variations = value["exact_data"]["frozen_parallel_PBW_audit"]["variations"]
    expected_counts = {
        "inclusion0": 2,
        "inclusion1": 21,
        "first_bgg": 0,
        "normal_tractor_square": 48,
        "yang_mills_middle": 126,
        "compressed_middle": 130,
    }
    actual_counts = {name: variations[name]["nonzero_coefficients"] for name in expected_counts}
    if actual_counts != expected_counts:
        raise AssertionError(f"frozen PBW response drifted: {actual_counts}")
    if value["flags"]["PARALLEL_CURVATURE_PBW_SUFFICIENT"] is not False:
        raise AssertionError("parallel PBW backend was overpromoted")
    for flag in (
        "TRANSVERSE_JET_AWARE_PBW_VARIATION",
        "TRANSVERSE_MIDDLE_SCHUR_VARIATION",
        "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION",
        "TRANSVERSE_CAUSAL_TRANSFER",
    ):
        if value["flags"][flag] is not False:
            raise AssertionError(f"downstream flag promoted: {flag}")
    for path, digest in value["source_manifest"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"source drift: {path}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1 independent verification: PASS")
