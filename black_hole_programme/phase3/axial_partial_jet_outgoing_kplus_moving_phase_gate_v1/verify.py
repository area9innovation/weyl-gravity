#!/usr/bin/env python3
"""Independent verifier for the outgoing moving-phase K-plus gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from .algebra import derive


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    if document["status"] != "KPLUS_ZERO_WITHHELD_NONSTATIC_REPHASING":
        raise RuntimeError("moving-phase gate status drifted")
    for item in document["imports"].values():
        if sha256(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"import hash drift: {item['path']}")

    crosswalk_item = document["imports"]["partial_jet_crosswalk"]
    crosswalk = json.loads(
        (ROOT / crosswalk_item["path"]).read_text()
    )
    data = derive(crosswalk["exact_blocks"])
    if data["rate_derivative"] != -sp.Rational(3, 4):
        raise RuntimeError("rate derivative is not -3/4")
    if data["power_derivative"] != 0:
        raise RuntimeError("power derivative is not zero")
    if data["E12_linear_coefficient"] != sp.Rational(3, 4):
        raise RuntimeError("E12 irregular coefficient mismatch")
    if data["E22_constant"] != -sp.Rational(3, 4):
        raise RuntimeError("E22 constant mismatch")
    if data["irregular_homological_residual"] != sp.zeros(2):
        raise RuntimeError("irregular homological identity failed")
    if data["combined_moving_generator"] != sp.diag(
        0, -sp.Rational(3, 4)
    ):
        raise RuntimeError("combined moving generator mismatch")

    reissue = document["common_gauge_reissue_at_r31"]
    if reissue["relative_log_tau_derivative"] != "93/4":
        raise RuntimeError("relative phase derivative mismatch")
    if reissue["relative_rephasing_tau_independent"]:
        raise RuntimeError("nonstatic rephasing promoted to static")
    recurrence = document["recurrence_and_normalization_audit"]
    if not recurrence["free_EI2_constants_zero"]:
        raise RuntimeError("free Einstein shear returned")
    if recurrence["analytic_K_plus_promoted"]:
        raise RuntimeError("analytic K-plus improperly promoted")
    if recurrence["formal_canonical_K_plus"] != [
        ["0", "0"],
        ["0", "0"],
    ]:
        raise RuntimeError("formal K-plus drifted")

    flags = document["claim_flags"]
    for key in (
        "joint_reduced_frame_rank_three_imported",
        "outgoing_rate_derivative_exact",
        "outgoing_power_derivative_exact",
        "tau_zero_common_phase_factor_exact",
        "formal_K_plus_zero_preserved",
    ):
        if not flags[key]:
            raise RuntimeError(f"positive flag missing: {key}")
    for key in (
        "relative_rephasing_tau_independent",
        "analytic_K_plus_zero_certified",
        "T_plus_certified",
        "stokes_or_scattering_certified",
    ):
        if flags[key]:
            raise RuntimeError(f"downstream flag promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent outgoing moving-phase K-plus verifier")


if __name__ == "__main__":
    main()
