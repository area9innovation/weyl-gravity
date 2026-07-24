#!/usr/bin/env python3
"""Aggregate the certified projective prefix through panel 97."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb, ctx

from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "rail-v10-run.json"
V9_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v9/certificate.json"
)
V9_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v9/rail-v9-run.json"
)
CHUNK_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v7/certificate.json"
)
CHUNK_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v7/chunk-run.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_run(cert_path: Path, run_path: Path) -> dict:
    certificate = json.loads(cert_path.read_text())
    if certificate["run"]["sha256"] != sha(run_path):
        raise RuntimeError(f"run hash mismatch: {run_path}")
    return json.loads(run_path.read_text())


def compute() -> dict:
    ctx.prec = 128
    predecessor = checked_run(V9_CERT, V9_RUN)
    chunk = checked_run(CHUNK_CERT, CHUNK_RUN)
    rows = list(predecessor["rows"])
    terminal = None
    for row in chunk["rows"]:
        if row["boundary_nonvanishing"]["status"] != "PASS":
            terminal = {
                "panel": row["panel"],
                "failure": row["boundary_nonvanishing"]["failure"],
                "source_terminal": chunk["terminal"],
            }
            break
        rows.append(typed_row(row))
    if terminal is None and chunk["terminal"] is not None:
        raise RuntimeError("chunk terminal was not found in ordered rows")
    actual = [row["panel"] for row in rows]
    contiguous = actual == list(range(len(rows)))
    interfaces = all(all(row["interface_gates"].values()) for row in rows)
    nonzero = all(row["delta"]["excludes_zero"] for row in rows)
    minimum = min(
        rows,
        key=lambda row: arb(row["delta"]["modulus_lower"]).lower(),
    )
    tau_count = sum(row["delta_tau"]["excludes_zero"] for row in rows)
    omega_count = sum(row["delta_omega"]["excludes_zero"] for row in rows)
    full = 512
    first_missing = len(rows)
    return {
        "schema": "phase3-axial-qnm-projective-evans-riccati-run-v10",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "status": (
            "PANELS_0_THROUGH_97_AGGREGATED_ENDPOINT_EXPORT_FAIL_CLOSED"
        ),
        "rows": rows,
        "summary": {
            "contiguous_prefix": contiguous,
            "completed_panel_count": len(rows),
            "first_panel": actual[0],
            "last_panel": actual[-1],
            "full_contour_panel_count": full,
            "two_sided_interface_gates_pass": interfaces,
            "all_completed_deltas_exclude_zero": nonzero,
            "minimum_delta_modulus_lower": minimum["delta"][
                "modulus_lower"
            ],
            "minimum_delta_modulus_lower_panel": minimum["panel"],
            "delta_tau_excludes_zero_panel_count": tau_count,
            "delta_omega_excludes_zero_panel_count": omega_count,
        },
        "local_qnm_gate": {
            "status": "FAIL_CLOSED",
            "first_obstruction": {
                "code": terminal["failure"],
                "completed_panels": len(rows),
                "required_panels": full,
                "first_missing_panel": first_missing,
                "terminal_observation": terminal,
                "missing_field": (
                    "certified stable-root shared-generator "
                    "horizon/outgoing q,q_tau,q_omega exports at r=32 "
                    f"for panel {first_missing}/{full}"
                ),
            },
            "parallel_quantitative_obstruction": {
                "code": "PROJECTIVE_SENSITIVITY_BALLS_CONTAIN_ZERO",
                "delta_tau_excludes_zero_panel_count": tau_count,
                "delta_omega_excludes_zero_panel_count": omega_count,
                "completed_panel_count": len(rows),
            },
            "interval_newton_run": False,
            "argument_principle_run": False,
        },
        "scope": {
            "common_match_radius": 32,
            "full_closed_contour": False,
            "QNM_or_EP2": False,
        },
    }


if __name__ == "__main__":
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)
