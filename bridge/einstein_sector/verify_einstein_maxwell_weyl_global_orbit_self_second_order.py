#!/usr/bin/env python3
"""Independent verifier for the aligned global self-source correction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_orbit_self_second_order.schema.json"


def main() -> None:
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = payload["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    assert provenance["input"]["sha256"] == hashlib.sha256((ROOT / provenance["input"]["path"]).read_bytes()).hexdigest()

    A, B, Q_e, t = sp.symbols("A B Q_e t", real=True)
    local = {"A": A, "B": B, "Q_e": Q_e, "t": t}
    obstruction = sp.sympify(payload["homogeneous_L0"]["source_factor"], locals=local)
    assert sp.factor(obstruction - (4 * B**2 - 3 * Q_e**2)) == 0
    rows = payload["homogeneous_L0"]["source_rows"]
    assert sp.sympify(rows["metric_00"], locals=local) == obstruction / 6
    assert sp.sympify(rows["metric_11"], locals=local) == -obstruction / 6
    assert sp.sympify(rows["sphere_trace"], locals=local) == obstruction / 6

    correction = payload["second_order_correction"]
    for block in ("polar_L1", "polar_L2"):
        assert all(sp.sympify(value) == 0 for value in correction[block]["all_eight_row_remainders"].values())
    assert sp.sympify(correction["polar_L1"]["A_t2"], locals=local) == -B * Q_e
    assert sp.sympify(correction["polar_L1"]["C_t2"], locals=local) == B * Q_e
    assert payload["classification"]["global_self_second_order_extendible_iff_taub_condition"] is True
    assert payload["classification"]["full_global_extra_orbit_coefficient_explicit"] is False


if __name__ == "__main__":
    main()
