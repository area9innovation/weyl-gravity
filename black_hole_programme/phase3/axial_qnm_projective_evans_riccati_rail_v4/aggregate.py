#!/usr/bin/env python3
"""Aggregate the largest contiguous certified projective boundary prefix."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb, ctx

from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = HERE / "rail-v4-run.json"
CHUNK1_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v1/certificate.json"
)
CHUNK1_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v1/chunk-run.json"
)
CHUNK2_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v2/certificate.json"
)
CHUNK2_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_chunk_v2/chunk-run.json"
)
V3 = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v3/certificate.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(cert_path: Path, run_path: Path) -> dict:
    certificate = json.loads(cert_path.read_text())
    if certificate["run"]["sha256"] != sha(run_path):
        raise RuntimeError(f"run hash mismatch: {run_path}")
    return json.loads(run_path.read_text())


def compute() -> dict:
    ctx.prec = 128
    chunk1 = _load(CHUNK1_CERT, CHUNK1_RUN)
    chunk2 = _load(CHUNK2_CERT, CHUNK2_RUN)
    source_rows = chunk1["rows"] + chunk2["rows"]
    expected = list(range(len(source_rows)))
    actual = [row["panel"] for row in source_rows]
    contiguous = actual == expected
    rows = [typed_row(row) for row in source_rows]
    all_interfaces = all(
        all(row["interface_gates"].values()) for row in rows
    )
    all_nonzero = all(row["delta"]["excludes_zero"] for row in rows)
    minimum = min(
        rows,
        key=lambda row: arb(row["delta"]["modulus_lower"]).lower(),
    )
    tau_count = sum(row["delta_tau"]["excludes_zero"] for row in rows)
    omega_count = sum(row["delta_omega"]["excludes_zero"] for row in rows)
    full = chunk1["full_contour_panel_count"]
    first_missing = len(rows) if len(rows) < full else None
    return {
        "schema": "phase3-axial-qnm-projective-evans-riccati-run-v4",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "status": "PANELS_0_THROUGH_31_AGGREGATED_LOCAL_QNM_GATE_FAIL_CLOSED",
        "rows": rows,
        "summary": {
            "contiguous_prefix": contiguous,
            "completed_panel_count": len(rows),
            "first_panel": actual[0] if actual else None,
            "last_panel": actual[-1] if actual else None,
            "full_contour_panel_count": full,
            "two_sided_interface_gates_pass": all_interfaces,
            "all_completed_deltas_exclude_zero": all_nonzero,
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
                "code": "INCOMPLETE_CLOSED_BOUNDARY_COVERAGE",
                "completed_panels": len(rows),
                "required_panels": full,
                "first_missing_panel": first_missing,
                "missing_field": (
                    f"shared-generator horizon/outgoing q,q_tau,q_omega "
                    f"exports at r=32 for panel {first_missing}/{full}"
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


def main() -> None:
    RUN.write_text(json.dumps(compute(), indent=2, sort_keys=True) + "\n")
    print(RUN)


if __name__ == "__main__":
    main()
