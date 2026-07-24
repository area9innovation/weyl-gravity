#!/usr/bin/env python3
"""Independent artifact verifier for Bplus4 successor chunk 01."""
from __future__ import annotations

import hashlib
import json
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
    if document["status"] != "BPLUS4_CONTENT_ADDRESSED_SUCCESSOR_PASS":
        raise RuntimeError("successor chunk did not pass")
    imported = document["imports"]["predecessor_checkpoint"]
    predecessor_path = ROOT / imported["path"]
    if sha256(predecessor_path) != imported["sha256"]:
        raise RuntimeError("predecessor checkpoint hash drift")
    predecessor = json.loads(predecessor_path.read_text())
    if canonical_sha256(predecessor["payload"]) != (
        predecessor["payload_sha256"]
    ):
        raise RuntimeError("predecessor payload drift")
    if predecessor["payload_sha256"] != imported["payload_sha256"]:
        raise RuntimeError("imported predecessor payload mismatch")

    checkpoint = json.loads((HERE / "checkpoint.json").read_text())
    manifest = json.loads((HERE / "run_manifest.json").read_text())
    if canonical_sha256(checkpoint["payload"]) != checkpoint["payload_sha256"]:
        raise RuntimeError("successor checkpoint payload drift")
    if manifest["checkpoint_payload_sha256"] != (
        checkpoint["payload_sha256"]
    ):
        raise RuntimeError("manifest/checkpoint mismatch")
    if manifest["chunk_id"] != canonical_sha256(
        manifest["chunk_descriptor"]
    ):
        raise RuntimeError("content-addressed chunk id mismatch")
    if manifest["source_sha256"] != (
        manifest["chunk_descriptor"]["source_sha256"]
    ):
        raise RuntimeError("source hash descriptor mismatch")
    if manifest["source_retained"] or manifest["run"]["raw_output_retained"]:
        raise RuntimeError("raw source/output retention contract drifted")
    if not manifest["under_sixty_seconds"]:
        raise RuntimeError("under-sixty gate missing")
    if not 0 < manifest["total_elapsed_seconds"] <= 60:
        raise RuntimeError("invalid chunk elapsed time")
    if (
        manifest["compile"]["exit_code"] != 0
        or manifest["run"]["exit_code"] != 0
    ):
        raise RuntimeError("compile/run did not pass")

    selected = manifest["selected_candidate"]
    summary = manifest["run"]["summary"]
    if (
        selected["choice"] != summary["choice"]
        or selected["order"] != summary["order"]
    ):
        raise RuntimeError("adaptive branch mismatch")
    if not summary["coefficients"] or not summary["containment"]:
        raise RuntimeError("boundary direct gate failed")
    if not (
        float(summary["tail"]) < 0.5
        and float(summary["width"]) < 4.0
    ):
        raise RuntimeError("tail/width gate failed")

    payload = checkpoint["payload"]
    if (
        payload["input_payload_sha256"] != predecessor["payload_sha256"]
        or payload["start_radius"] != predecessor["payload"]["radius"]
        or payload["radius"] != selected["final_radius"]
        or payload["generator"] != 7315
        or payload["degree"] != 4
    ):
        raise RuntimeError("successor domain/typing drift")
    for name in ("base", "tangent"):
        value = payload[name]
        if (
            value["schema"] != "ivtaylor-degree4-v1"
            or value["generator"] != 7315
            or value["degree"] != 4
            or value["rows"] != 8
            or value["cols"] != 2
            or value["refusal_code"] != 0
        ):
            raise RuntimeError(f"{name} Taylor model typing drift")
        if canonical_sha256(value) != (
            manifest["run"][f"successor_{name}_sha256"]
        ):
            raise RuntimeError(f"{name} model hash mismatch")
    zero_rows = (2, 3, 6, 7)
    if not zero_coefficients(payload["tangent"], zero_rows):
        raise RuntimeError("frozen spin-one tangent coefficients drifted")
    if not padding_contains_zero(payload["tangent"], zero_rows):
        raise RuntimeError("frozen spin-one tangent padding lost zero")
    h0 = payload["typed_common_unit_h0"]
    if not h0["zero_free"] or h0["analytic_on"] != "entire omega plane":
        raise RuntimeError("typed h0 was not preserved")

    adaptive = document["adaptive_chunk"]
    if (
        adaptive["selected"] != selected
        or adaptive["summary"] != summary
        or not adaptive["under_sixty_seconds"]
        or adaptive["raw_model_stdout_retained"]
        or not adaptive["source_content_addressed"]
    ):
        raise RuntimeError("adaptive chunk certificate drift")
    boundary = document["boundary_gate"]
    if not all(
        boundary[key]
        for key in (
            "direct_sixteen_state_expanded_once",
            "partial_jet_coefficients_equal_direct",
            "interval_difference_contains_zero",
            "rank_three_preserved_by_common_invertible_flow",
        )
    ):
        raise RuntimeError("boundary gate flag missing")
    if boundary["shared_generator"] != 7315:
        raise RuntimeError("boundary generator drift")

    flags = document["claim_flags"]
    for key in (
        "content_addressed_chunk_certified",
        "adaptive_step_order_gate_certified",
        "under_sixty_second_chunk_certified",
        "boundary_direct_gate_certified",
        "successor_checkpoint_serialized",
        "shared_omega_generator_preserved",
    ):
        if not flags[key]:
            raise RuntimeError(f"positive claim flag missing: {key}")
    for key in (
        "full_Bplus4_at_r4_certified",
        "T_plus_certified",
        "stokes_or_scattering_certified",
    ):
        if flags[key]:
            raise RuntimeError(f"downstream claim improperly promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent Bplus4 content-addressed successor verifier")


if __name__ == "__main__":
    main()
