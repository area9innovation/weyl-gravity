#!/usr/bin/env python3
"""Verify the bounded chunk-03 runtime refusal."""
from __future__ import annotations

import hashlib
import json
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


def verify(document: dict) -> None:
    jsonschema.validate(
        document, json.loads((HERE / "schema.json").read_text())
    )
    manifest = json.loads((HERE / "run_manifest.json").read_text())
    imported = document["imports"]["predecessor_checkpoint"]
    path = ROOT / imported["path"]
    predecessor = json.loads(path.read_text())
    if sha256(path) != imported["sha256"]:
        raise RuntimeError("predecessor file hash drift")
    if (
        canonical_sha256(predecessor["payload"])
        != predecessor["payload_sha256"]
        or imported["payload_sha256"] != predecessor["payload_sha256"]
    ):
        raise RuntimeError("predecessor payload drift")
    if (
        manifest["chunk_id"]
        != canonical_sha256(manifest["chunk_descriptor"])
        or manifest["source_sha256"]
        != manifest["chunk_descriptor"]["source_sha256"]
        or manifest["source_retained"]
        or manifest["raw_output_retained"]
    ):
        raise RuntimeError("content-addressed attempt drift")
    attempt = manifest["attempt"]
    if (
        attempt["status"] != "TIMEOUT"
        or attempt["compile_exit_code"] != 0
        or attempt["run_exit_code"] != 124
        or attempt["runtime_timeout_seconds"] != 42
        or not attempt["stdout_was_empty"]
        or attempt["completed_boundary_diagnostic_available"]
        or not attempt["selected_candidate_not_inferred"]
        or manifest["successor_checkpoint_emitted"]
    ):
        raise RuntimeError("timeout boundary drift")
    adaptive = document["adaptive_chunk"]
    if (
        adaptive["terminal_gate"] != "RUNTIME_TIMEOUT"
        or not adaptive["larger_step_probed_first"]
        or adaptive["completed_boundary_diagnostic_available"]
        or not adaptive["selected_candidate_not_inferred"]
        or adaptive["raw_model_stdout_retained"]
        or not adaptive["source_content_addressed"]
    ):
        raise RuntimeError("adaptive refusal drift")
    if (HERE / "checkpoint.json").exists():
        raise RuntimeError("uncertified successor checkpoint exists")
    boundary = document["boundary_gate"]
    if (
        boundary["direct_sixteen_state_expanded_once"]
        or boundary["partial_jet_coefficients_equal_direct"]
        or boundary["interval_difference_contains_zero"]
        or boundary["rank_three_preserved_by_common_invertible_flow"]
    ):
        raise RuntimeError("boundary gate promoted after timeout")
    flags = document["claim_flags"]
    for key in (
        "under_sixty_second_chunk_certified",
        "boundary_direct_gate_certified",
        "successor_checkpoint_serialized",
        "shared_omega_generator_preserved_at_successor",
        "full_Bplus4_at_r4_certified",
        "T_plus_certified",
        "stokes_or_scattering_certified",
    ):
        if flags[key]:
            raise RuntimeError(f"downstream claim promoted: {key}")


def main() -> None:
    verify(json.loads((HERE / "certificate.json").read_text()))
    print("PASS independent Bplus4 chunk-03 runtime-refusal verifier")


if __name__ == "__main__":
    main()
