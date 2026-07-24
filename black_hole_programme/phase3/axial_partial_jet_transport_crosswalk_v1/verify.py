#!/usr/bin/env python3
"""Independent verifier for the exact partial-jet crosswalk."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

from .produce import (
    HERE,
    INPUTS,
    ROOT,
    derive,
    matrix,
    parse,
    reduce_expr,
)

CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_equal(left: sp.Matrix, right: sp.Matrix) -> bool:
    return left.shape == right.shape and all(
        reduce_expr(left[i, j] - right[i, j]) == 0
        for i in range(left.rows)
        for j in range(left.cols)
    )


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-partial-jet-transport-crosswalk-v1"
    ):
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("lifecycle") != "CLASSIFIED":
        errors.append("lifecycle promotion")
    if document.get("status") != (
        "EXACT_LOCAL_PARTIAL_JET_CROSSWALK_ENDPOINT_OPEN"
    ):
        errors.append("status drift")

    imported: dict[str, dict] = {}
    references = document.get("imports", {})
    for name, expected_path in INPUTS.items():
        reference = references.get(name)
        if not reference:
            errors.append(f"missing import: {name}")
            continue
        path = ROOT / reference["path"]
        if path.resolve() != expected_path.resolve():
            errors.append(f"import path drift: {name}")
            continue
        if not path.is_file() or sha256(path) != reference["sha256"]:
            errors.append(f"input hash drift: {name}")
            continue
        imported[name] = json.loads(path.read_text())
    if len(imported) != len(INPUTS):
        return errors

    result = derive(imported)
    crosswalk = document["full_transform_crosswalk"]
    if not matrix_equal(
        result["transformed"], matrix(crosswalk["transformed_full_6x6"])
    ):
        errors.append("recorded transformed six-state matrix mismatch")
    if not matrix_equal(
        result["expected"], matrix(crosswalk["expected_block_matrix"])
    ):
        errors.append("recorded expected block matrix mismatch")
    if not matrix_equal(result["transformed"], result["expected"]):
        errors.append("full six-state factor-gauge identity failed")
    if not crosswalk["exact_identity_verified"]:
        errors.append("exact crosswalk flag demoted")

    blocks = document["exact_blocks"]
    block_map = {
        "A_RW": "A",
        "A_x": "Ax",
        "D_Lx_to_carrier_RW": "D",
        "E_RW_self_extension": "E",
        "C_Lx_to_metric_RW": "C",
    }
    for recorded_name, derived_name in block_map.items():
        if not matrix_equal(
            result[derived_name], matrix(blocks[recorded_name])
        ):
            errors.append(f"exact block mismatch: {recorded_name}")
    if result["E"].rank() != 1 or blocks["E_rank"] != 1:
        errors.append("E rank-one identity failed")
    if result["C"].rank() != 1 or blocks["C_rank"] != 1:
        errors.append("C rank-one identity failed")
    witness = parse(
        imported["triangular_factorization"][
            "complete_six_state_filtration"
        ]["natural_gauge_Lx_to_metric_extension_witness"]
    )
    if reduce_expr(result["C"][0, 0] - witness) != 0:
        errors.append("C witness mismatch")

    jet = document["partial_jet"]
    if "not the full jet" not in jet["type"]:
        errors.append("partial/full jet distinction lost")
    if not matrix_equal(result["base"], matrix(
        jet["base_four_state_connection_B0"]
    )):
        errors.append("base four-state connection mismatch")
    if not matrix_equal(result["tangent"], matrix(
        jet["tangent_four_state_connection_B1"]
    )):
        errors.append("tangent four-state connection mismatch")
    if not matrix_equal(result["expected"], matrix(
        jet["expanded_six_state_connection"]
    )):
        errors.append("partial-jet expansion mismatch")
    if not jet["exact_identity_verified"]:
        errors.append("partial-jet identity flag demoted")

    boundary = document["transport_method_boundary"]
    if boundary["tau_dual_alone_cures_H4"]:
        errors.append("tau-only H4 repair was promoted")
    if boundary["bounded_transport_attempted"]:
        errors.append("bounded transport was falsely attempted")
    if "tensor" not in boundary["required_successor_algebra"]:
        errors.append("mixed omega/tau successor algebra omitted")
    if document["endpoint_hypotheses"]["constructed_here"]:
        errors.append("endpoint jet frames were promoted")

    flags = document["claim_flags"]
    for name in (
        "exact_full_six_state_factor_gauge_crosswalk",
        "missing_C_derived",
        "E_rank_one",
        "C_rank_one",
        "partial_spin_two_row_jet_exact",
    ):
        if flags.get(name) is not True:
            errors.append(f"proved flag demoted: {name}")
    for name in (
        "tau_only_H4_repair_certified",
        "endpoint_partial_jet_frames_constructed",
        "T_plus_recovered",
        "scattering_identity_certified",
        "bounded_transport_certified",
        "H4_pass_certified",
    ):
        if flags.get(name) is not False:
            errors.append(f"open claim promoted: {name}")
    return errors


def verify() -> list[str]:
    return verify_document(json.loads(CERTIFICATE.read_text()))


if __name__ == "__main__":
    failures = verify()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(1)
    print(
        "verified=true exact_local_partial_jet=true "
        "endpoint_open=true bounded_transport=false"
    )
