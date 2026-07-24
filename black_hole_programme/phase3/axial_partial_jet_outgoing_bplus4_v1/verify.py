#!/usr/bin/env python3
"""Independent verifier for the bounded correlated Bplus4 successor."""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

import jsonschema


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def model(text: str, tag: str) -> dict:
    match = re.search(rf"^{re.escape(tag)}_MODEL (.+)$", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"missing run model {tag}")
    return json.loads(match.group(1))


def zero_coefficients(value: dict, rows: tuple[int, ...]) -> bool:
    return all(
        value["coefficients"][degree][row][column] == "0"
        for degree in range(5)
        for row in rows
        for column in range(2)
    )


def padding_contains_zero(value: dict, rows: tuple[int, ...]) -> bool:
    for row in rows:
        for column in range(2):
            lower, upper = (
                struct.unpack(">d", bytes.fromhex(bits))[0]
                for bits in value["remainder_bits"][row][column]
            )
            if not lower <= 0 <= upper:
                return False
    return True


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    if document["status"] != (
        "BPLUS4_CORRELATED_FIRST_PANEL_PASS_R4_OPEN"
    ):
        raise RuntimeError("bounded Bplus4 successor did not pass")
    imported = document["imports"]["common_moving_checkpoint"]
    input_path = ROOT / imported["path"]
    if sha256(input_path) != imported["sha256"]:
        raise RuntimeError("moving-frame checkpoint hash drift")
    input_document = json.loads(input_path.read_text())
    if input_document["payload_sha256"] != imported["payload_sha256"]:
        raise RuntimeError("moving-frame payload hash drift")
    if canonical_sha256(input_document["payload"]) != (
        input_document["payload_sha256"]
    ):
        raise RuntimeError("moving-frame canonical payload mismatch")

    for name in ("source", "compile_log", "run_log"):
        artifact = document["artifacts"][name]
        if sha256(ROOT / artifact["path"]) != artifact["sha256"]:
            raise RuntimeError(f"artifact hash drift: {name}")
    if document["artifacts"]["compile_log"]["exit_code"] != 0:
        raise RuntimeError("Forge compilation did not pass")
    if document["artifacts"]["run_log"]["exit_code"] != 0:
        raise RuntimeError("Forge execution did not pass")

    source = (ROOT / document["artifacts"]["source"]["path"]).read_text()
    for token in (
        "let base:IvTaylor4Mat=initial_base();",
        "let tangent_n:IvTaylor4Mat=sc_scale(initial_tangent(),big(\"1/512\"));",
        "sc_dual_series(models.base,models.tangent,h,96)",
        "sc_series(models.direct,h,96)",
        "sj_coefficients_equal(jp,dp)",
        "sc_contains_zero(jp,dp)",
        "bc_stack(tangent_out,base_out)",
    ):
        if token not in source:
            raise RuntimeError(f"correlated transport source gate missing: {token}")

    run_text = (ROOT / document["artifacts"]["run_log"]["path"]).read_text()
    summary = re.search(
        r"PROBE status=PASS panels=1 final_r=247/8 "
        r"max_tail=(?P<tail>[-+0-9.eE]+) "
        r"max_width=(?P<width>[-+0-9.eE]+)",
        run_text,
    )
    if summary is None:
        raise RuntimeError("bounded pass summary missing")
    if not (
        float(summary.group("tail")) < 1.0
        and float(summary.group("width")) < 2.0
    ):
        raise RuntimeError("bounded tail/width gate failed")
    base = model(run_text, "FINAL_BASE")
    tangent = model(run_text, "FINAL_TANGENT")
    for value in (base, tangent):
        if (
            value["schema"] != "ivtaylor-degree4-v1"
            or value["generator"] != 7315
            or value["degree"] != 4
            or value["rows"] != 8
            or value["cols"] != 2
            or value["refusal_code"] != 0
        ):
            raise RuntimeError("transport output model typing drift")
    zero_rows = (2, 3, 6, 7)
    if not zero_coefficients(tangent, zero_rows):
        raise RuntimeError("frozen spin-one tangent coefficients drifted")
    if not padding_contains_zero(tangent, zero_rows):
        raise RuntimeError("frozen spin-one tangent padding lost zero")

    checkpoint = json.loads((HERE / "checkpoint.json").read_text())
    if canonical_sha256(checkpoint["payload"]) != checkpoint["payload_sha256"]:
        raise RuntimeError("successor checkpoint payload hash drift")
    payload = checkpoint["payload"]
    if payload["radius"] != "247/8" or payload["generator"] != 7315:
        raise RuntimeError("successor checkpoint domain drift")
    if payload["base"] != base or payload["tangent"] != tangent:
        raise RuntimeError("successor checkpoint does not match run")
    h0 = payload["typed_common_unit_h0"]
    if not h0["zero_free"] or h0["analytic_on"] != "entire omega plane":
        raise RuntimeError("typed h0 was not preserved")
    if document["artifacts"]["checkpoint"]["payload_sha256"] != (
        checkpoint["payload_sha256"]
    ):
        raise RuntimeError("certificate/checkpoint hash mismatch")

    transport = document["transport"]
    if (
        transport["shared_generator"] != 7315
        or transport["completed_panels"] != 1
        or not transport["direct_sixteen_state_gate_present"]
        or not transport["direct_jet_coefficients_equal"]
        or not transport["direct_jet_interval_difference_contains_zero"]
    ):
        raise RuntimeError("direct/jet transport audit drift")
    rank = document["rank_preservation"]
    if (
        not rank["same_linear_flow_applied_to_all_columns"]
        or not rank["flow_invertible_by_ODE_uniqueness"]
        or not rank["typed_h0_zero_free"]
        or not rank["rank_three_at_certified_radius"]
    ):
        raise RuntimeError("rank-preservation gate failed")

    flags = document["claim_flags"]
    for name in (
        "sole_admissible_common_moving_checkpoint_imported",
        "shared_omega_generator_preserved",
        "R_and_S_transported_in_one_correlated_state",
        "exact_partial_jet_direct_gate_passed",
        "first_panel_to_247_over_8_certified",
        "rank_three_at_247_over_8_certified",
    ):
        if not flags[name]:
            raise RuntimeError(f"positive claim flag missing: {name}")
    for name in (
        "Bplus4_at_r4_certified",
        "T_plus_certified",
        "stokes_or_scattering_certified",
    ):
        if flags[name]:
            raise RuntimeError(f"downstream claim improperly promoted: {name}")
    diagnosis = document["diagnosis"]
    if diagnosis["full_r4_target_reached"] or diagnosis["scientific_refusal"]:
        raise RuntimeError("shortfall disposition drifted")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent bounded correlated Bplus4 verifier")


if __name__ == "__main__":
    main()
