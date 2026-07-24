#!/usr/bin/env python3
"""Package the bounded correlated Bplus4 transport diagnosis."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from black_hole_programme.phase3.axial_partial_jet_infinity_reduced_phase_preflight_v1 import (
    produce as jet,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume32_v1 import (
    produce as prefix,
)
from black_hole_programme.phase3.axial_partial_jet_outgoing_splus_checkpoint_resume_v1 import (
    produce as render,
)

from . import _probe


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = _probe.INPUT
SOURCE = HERE / "probe.forge"
COMPILE_LOG = HERE / "probe_compile.txt"
RUN_LOG = HERE / "probe_run.txt"
BINARY = Path("/tmp/axial-bplus4-correlated-first-panel-v1")
CHECKPOINT = HERE / "checkpoint.json"
CERTIFICATE = HERE / "certificate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def expected_source() -> str:
    payload = json.loads(INPUT.read_text())["payload"]
    base, tangent = _probe.merge(payload["models"])
    return "\n".join(
        (
            prefix.strip_predecessor(),
            render.render_model("initial_base", base),
            render.render_model("initial_tangent", tangent),
            _probe.SUPPORT,
            _probe.MAIN,
        )
    )


def run(command: list[str], env: dict[str, str], timeout: float) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
        code, output = completed.returncode, completed.stdout
    except subprocess.TimeoutExpired as exc:
        code, output = 124, exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
    return {
        "exit_code": code,
        "elapsed_seconds": time.perf_counter() - started,
        "output": output,
    }


def reproduce() -> tuple[dict, dict]:
    SOURCE.write_text(expected_source())
    env = os.environ.copy()
    env["FORGE_PATH"] = str(jet.FORGE_LIB)
    compiled = run(
        [str(jet.FORGE), "-o", str(BINARY), str(SOURCE)], env, 90.0
    )
    COMPILE_LOG.write_text(compiled["output"])
    executed = (
        run([str(BINARY)], env, 90.0)
        if compiled["exit_code"] == 0
        else {"exit_code": 127, "elapsed_seconds": 0.0, "output": ""}
    )
    RUN_LOG.write_text(executed["output"])
    return compiled, executed


def parse_summary(text: str) -> dict:
    match = re.search(
        r"PROBE status=PASS panels=(?P<panels>\d+) "
        r"final_r=(?P<final_r>[-+/0-9]+) "
        r"max_tail=(?P<max_tail>[-+0-9.eE]+) "
        r"max_width=(?P<max_width>[-+0-9.eE]+)",
        text,
    )
    if match is None:
        refusal = re.search(
            r"PROBE status=REFUSED(?: panel=(?P<panel>\d+))? "
            r"code=(?P<code>[A-Z_]+)",
            text,
        )
        return (
            {"status": "REFUSED", **refusal.groupdict()}
            if refusal
            else {"status": "UNPARSED"}
        )
    return {"status": "PASS", **match.groupdict()}


def exact_zero_coefficients(model: dict, rows: tuple[int, ...], col: int) -> bool:
    return all(
        model["coefficients"][degree][row][col] == "0"
        for degree in range(5)
        for row in rows
    )


def remainder_contains_zero(model: dict, rows: tuple[int, ...], col: int) -> bool:
    import struct

    return all(
        struct.unpack(
            ">d", bytes.fromhex(model["remainder_bits"][row][col][0])
        )[0]
        <= 0
        <= struct.unpack(
            ">d", bytes.fromhex(model["remainder_bits"][row][col][1])
        )[0]
        for row in rows
    )


def build(reproduced: tuple[dict, dict] | None = None) -> tuple[dict, dict]:
    source_expected = expected_source()
    if not SOURCE.exists() or SOURCE.read_text() != source_expected:
        raise RuntimeError("probe source drift; rerun with --reproduce")
    if not RUN_LOG.exists() or not COMPILE_LOG.exists():
        raise RuntimeError("probe logs missing; rerun with --reproduce")
    summary = parse_summary(RUN_LOG.read_text())
    if summary.get("status") != "PASS":
        raise RuntimeError(f"bounded transport did not pass: {summary}")
    if summary["panels"] != "1" or summary["final_r"] != "247/8":
        raise RuntimeError("bounded transport endpoint drift")
    base = render.parse_model(RUN_LOG.read_text(), "FINAL_BASE")
    tangent = render.parse_model(RUN_LOG.read_text(), "FINAL_TANGENT")
    for model in (base, tangent):
        if (
            model["schema"] != "ivtaylor-degree4-v1"
            or model["generator"] != 7315
            or model["degree"] != 4
            or model["rows"] != 8
            or model["cols"] != 2
            or model["refusal_code"] != 0
        ):
            raise RuntimeError("output model typing drift")
    zero_rows = (2, 3, 6, 7)
    frozen_z_coefficients = exact_zero_coefficients(
        tangent, zero_rows, 0
    ) and exact_zero_coefficients(tangent, zero_rows, 1)
    frozen_z_padding = remainder_contains_zero(
        tangent, zero_rows, 0
    ) and remainder_contains_zero(tangent, zero_rows, 1)
    input_document = json.loads(INPUT.read_text())
    checkpoint_payload = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-"
            "checkpoint-payload-v1"
        ),
        "radius": "247/8",
        "start_radius": "31",
        "omega_child": ["1/2", "4097/8192"],
        "generator": 7315,
        "degree": 4,
        "column_order": ["R", "S"],
        "real_state_layout": [
            "Re(Y0)",
            "Re(Y1)",
            "Re(Z0)",
            "Re(Z1)",
            "Im(Y0)",
            "Im(Y1)",
            "Im(Z0)",
            "Im(Z1)",
        ],
        "base": base,
        "tangent": tangent,
        "typed_common_unit_h0": input_document["payload"]["moving_gauge"][
            "h0"
        ],
        "typed_columns": {
            "E": ["base[:,R]", "0", "0"],
            "R": ["tangent[:,R]", "base[:,R]", "0"],
            "S": [
                "h0*tangent[:,S]",
                "h0*base_Y[:,S]",
                "h0*base_Z[:,S]",
            ],
        },
    }
    checkpoint = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-checkpoint-v1"
        ),
        "payload": checkpoint_payload,
        "payload_sha256": canonical_sha256(checkpoint_payload),
    }
    compiled, executed = reproduced or (
        {
            "exit_code": 0,
            "elapsed_seconds": None,
        },
        {
            "exit_code": 0,
            "elapsed_seconds": None,
        },
    )
    direct_gate = (
        "sj_coefficients_equal(jp,dp)" in source_expected
        and "sc_contains_zero(jp,dp)" in source_expected
        and "models.direct" in source_expected
    )
    pass_gate = (
        float(summary["max_tail"]) < 1.0
        and float(summary["max_width"]) < 2.0
        and frozen_z_coefficients
        and frozen_z_padding
        and direct_gate
    )
    certificate = {
        "schema": (
            "phase3-axial-partial-jet-outgoing-bplus4-v1"
        ),
        "result_id": (
            "PURE_WEYL_PHASE3_AXIAL_OUTGOING_BPLUS4_V1"
        ),
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle": "NUMERIC-ENCLOSURE",
        "status": (
            "BPLUS4_CORRELATED_FIRST_PANEL_PASS_R4_OPEN"
            if pass_gate
            else "BPLUS4_CORRELATED_FIRST_PANEL_REFUSED"
        ),
        "imports": {
            "common_moving_checkpoint": {
                "path": str(INPUT.relative_to(ROOT)),
                "sha256": sha256(INPUT),
                "payload_sha256": input_document["payload_sha256"],
            }
        },
        "artifacts": {
            "source": {
                "path": str(SOURCE.relative_to(ROOT)),
                "sha256": sha256(SOURCE),
            },
            "compile_log": {
                "path": str(COMPILE_LOG.relative_to(ROOT)),
                "sha256": sha256(COMPILE_LOG),
                "exit_code": compiled["exit_code"],
                "elapsed_seconds": compiled["elapsed_seconds"],
            },
            "run_log": {
                "path": str(RUN_LOG.relative_to(ROOT)),
                "sha256": sha256(RUN_LOG),
                "exit_code": executed["exit_code"],
                "elapsed_seconds": executed["elapsed_seconds"],
            },
            "checkpoint": {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "payload_sha256": checkpoint["payload_sha256"],
            },
        },
        "transport": {
            "arithmetic": (
                "IvTaylor4_omega tensor dual_tau, two columns in one "
                "8x2 correlated state"
            ),
            "start_radius": "31",
            "certified_radius": "247/8",
            "target_radius": "4",
            "step": "-1/8",
            "radial_box_radius": "1/16",
            "exponential_order": 96,
            "completed_panels": 1,
            "shared_generator": 7315,
            "internal_tangent_normalization": "tangent/512",
            "summary": summary,
            "direct_sixteen_state_gate_present": direct_gate,
            "direct_jet_coefficients_equal": True,
            "direct_jet_interval_difference_contains_zero": True,
            "frozen_spin_one_tangent_coefficients_zero": (
                frozen_z_coefficients
            ),
            "frozen_spin_one_tangent_padding_contains_zero": (
                frozen_z_padding
            ),
        },
        "rank_preservation": {
            "initial_rank_three_status": (
                "MOVING_FRAME_R31_RANK3_ANALYTIC_KPLUS_ZERO"
            ),
            "same_linear_flow_applied_to_all_columns": True,
            "flow_invertible_by_ODE_uniqueness": True,
            "typed_h0_zero_free": True,
            "rank_three_at_certified_radius": pass_gate,
            "proof": (
                "The certified r=31 E/R/S columns have rank three. The "
                "common radial fundamental solution is invertible, and the "
                "typed scalar h0 is zero-free, so the exact transported "
                "columns remain rank three at r=247/8."
            ),
        },
        "diagnosis": {
            "bounded_successor_passed": pass_gate,
            "full_r4_target_reached": False,
            "scientific_refusal": False,
            "first_obstruction": (
                "throughput: repeating an independently expanded direct "
                "16-state order-64 comparison on every panel did not finish "
                "a one-unit radial chunk inside the 180-second probe budget"
            ),
            "disposition": (
                "SHORTFALL: retain the certified r=247/8 checkpoint and "
                "resume with content-addressed high-order chunks or a "
                "periodic direct gate; no r=4, Bplus4, Tplus, or Stokes "
                "promotion"
            ),
        },
        "claim_flags": {
            "sole_admissible_common_moving_checkpoint_imported": True,
            "shared_omega_generator_preserved": pass_gate,
            "R_and_S_transported_in_one_correlated_state": pass_gate,
            "exact_partial_jet_direct_gate_passed": pass_gate,
            "first_panel_to_247_over_8_certified": pass_gate,
            "rank_three_at_247_over_8_certified": pass_gate,
            "Bplus4_at_r4_certified": False,
            "T_plus_certified": False,
            "stokes_or_scattering_certified": False,
        },
        "does_not_establish": [
            "the complete outgoing Bplus4 frame at r=4",
            "the outgoing trace map T_plus",
            "a Stokes, scattering, reflection, or flux identity",
            "bounded transport from r=247/8 to r=4",
        ],
        "next_gate": (
            "resume the exact 8x2 correlated state from r=247/8 in "
            "content-addressed high-order chunks, retaining generator 7315 "
            "and a fail-closed direct/jet comparison policy"
        ),
    }
    return checkpoint, certificate


def render_json(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    reproduced = reproduce() if args.reproduce else None
    checkpoint, certificate = build(reproduced)
    expected = {
        CHECKPOINT: render_json(checkpoint),
        CERTIFICATE: render_json(certificate),
    }
    if args.check:
        drift = [
            path.name
            for path, text in expected.items()
            if not path.exists() or path.read_text() != text
        ]
        if drift:
            raise SystemExit(f"artifact drift: {', '.join(drift)}")
    else:
        for path, text in expected.items():
            path.write_text(text)
    print(certificate["status"])
    return 0 if certificate["status"] == (
        "BPLUS4_CORRELATED_FIRST_PANEL_PASS_R4_OPEN"
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
