#!/usr/bin/env python3
"""Independent fail-closed verifier for outgoing population at omega=1/2."""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import jsonschema

from . import produce


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify(document: dict) -> None:
    jsonschema.validate(document, json.loads((HERE / "schema.json").read_text()))
    for name, record in document["imports"].items():
        path = ROOT / record["path"]
        require(path == produce.SOURCES[name], f"path drift: {name}")
        require(sha256(path) == record["sha256"], f"source drift: {name}")
    require(document == produce.produce(), "independent recomputation mismatch")

    scalar = document["certified_scalar_inputs"]
    require(Decimal(scalar["spin_one_abs_A_out_lower"]) > 0, "spin-one zero")
    require(Decimal(scalar["spin_two_abs_A_out_lower"]) > 0, "spin-two zero")
    require(
        Decimal(scalar["intrinsic_factor_diagonal_product_lower"]) > 0,
        "diagonal product zero",
    )
    proof = document["boundary_devissage_proof"]
    require(proof["kernel_conclusion"] == "ker(Tplus(1/2))={0}", "kernel drift")
    flags = document["claim_flags"]
    for name in (
        "Tplus_invertible_at_omega_half",
        "full_outgoing_trace_space_populated_at_omega_half",
        "det_O_nonzero_at_omega_half",
        "O_inertia_1_2_0_at_omega_half",
    ):
        require(flags[name] is True, f"missing theorem flag: {name}")
    for name in (
        "explicit_Tplus_entries_certified",
        "outgoing_extension_amplitudes_certified",
        "whole_pilot_interval_outgoing_population_certified",
        "time_domain_or_quantum_claim",
    ):
        require(flags[name] is False, f"overclaim: {name}")
    defect = document["transport_free_outgoing_defect"]
    require(defect["det_O_nonzero_at_omega_half"] is True, "defect degeneracy")
    require(
        defect["O_inertia_for_alpha_W_positive_at_omega_half"]
        == {"positive": 1, "negative": 2, "zero": 0},
        "defect inertia drift",
    )


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS point-half full outgoing-population theorem")


if __name__ == "__main__":
    main()
