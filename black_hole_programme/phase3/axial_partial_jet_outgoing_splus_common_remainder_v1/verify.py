#!/usr/bin/env python3
"""Independent fail-closed verifier for the outgoing S remainder export."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(data: dict) -> None:
    jsonschema.validate(data, json.loads((HERE / "schema.json").read_text()))
    if data["status"] != "SPLUS_COMMON_GENERATOR_REMAINDER_PASS":
        raise RuntimeError("S common-generator gate is not positive")
    for item in data["imports"].values():
        path = ROOT / item["path"]
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {path}")
    for item in ("source", "compile_log", "run_log"):
        record = data["artifacts"][item]
        path = ROOT / record["path"]
        if sha256(path) != record["sha256"]:
            raise RuntimeError(f"artifact hash drift: {path}")
    runtime = data["common_remainder"]["runtime"]
    expected = {
        "status": "PASS",
        "generator": "7315",
        "contained": "true",
        "coefficients": "true",
    }
    for key, value in expected.items():
        if runtime.get(key) != value:
            raise RuntimeError(f"runtime gate drift: {key}")
    flags = data["claim_flags"]
    if not (
        flags["S_common_omega_generator_certified"]
        and flags["S_partial_dual_tau_remainder_certified"]
    ):
        raise RuntimeError("S correlated remainder was not certified")
    if (
        flags["all_three_correlated_outgoing_columns_certified"]
        or flags["validated_analytic_K_plus_certified"]
        or flags["T_plus_certified"]
        or flags["scattering_or_flux_certified"]
    ):
        raise RuntimeError("downstream claim was promoted")
    if data["factor_column"]["spin_one_tangent_is_exactly_zero"] is not True:
        raise RuntimeError("partial-jet zero tangent drifted")


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    verify(data)
    print("PASS independent outgoing S common-remainder verification")


if __name__ == "__main__":
    main()
