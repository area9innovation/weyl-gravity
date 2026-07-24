#!/usr/bin/env python3
"""Checkpointed stable-root boundary panels 78--93."""
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

from flint import ctx

import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
from ..axial_qnm_common_affine_evans_boundary_v1.common_affine import (
    PANEL_COUNT,
    compute_panel,
)
from ..axial_qnm_horizon_center_self_map_repair_v1.repair import (
    stable_forward_remainder,
)

HERE = Path(__file__).resolve().parent
RUN = HERE / "chunk-run.json"
CHECKPOINT = HERE / "chunk-checkpoint.json"
PANEL_START, PANEL_STOP = 78, 94
WORKERS, BATCH_SIZE = 4, 4


def _worker(panel: int) -> dict:
    ctx.prec = 128
    with patch.object(hp, "forward_remainder", stable_forward_remainder):
        return compute_panel(panel, PANEL_COUNT)


def compute(*, write_checkpoint: bool = False) -> dict:
    ctx.prec = 128
    rows: list[dict] = []
    terminal = None
    for lower in range(PANEL_START, PANEL_STOP, BATCH_SIZE):
        panels = list(range(lower, min(lower + BATCH_SIZE, PANEL_STOP)))
        with ProcessPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(_worker, panel): panel for panel in panels
            }
            unordered = {
                futures[future]: future.result()
                for future in as_completed(futures)
            }
        for panel in panels:
            row = unordered[panel]
            rows.append(row)
            if row["boundary_nonvanishing"]["status"] != "PASS":
                terminal = {
                    "panel": panel,
                    "failure": row["boundary_nonvanishing"]["failure"],
                }
                break
        if write_checkpoint:
            CHECKPOINT.write_text(json.dumps({
                "schema": (
                    "phase3-axial-qnm-common-affine-evans-"
                    "chunk-checkpoint-v6"
                ),
                "requested_panels": [PANEL_START, PANEL_STOP - 1],
                "panel_count": PANEL_COUNT,
                "completed_panel_count": len(rows),
                "rows": rows,
                "terminal": terminal,
            }, indent=2, sort_keys=True) + "\n")
        if terminal is not None:
            break
    complete = terminal is None and len(rows) == PANEL_STOP - PANEL_START
    return {
        "schema": "phase3-axial-qnm-common-affine-evans-chunk-run-v6",
        "requested_panels": [PANEL_START, PANEL_STOP - 1],
        "full_contour_panel_count": PANEL_COUNT,
        "worker_count": WORKERS,
        "batch_size": BATCH_SIZE,
        "horizon_remainder_root": (
            "stable interval smaller root with exact 1000001/1000000 "
            "strict enlargement"
        ),
        "threshold_lowered": False,
        "stop_rule": (
            "stop after the first boundary, pivot, or self-map non-PASS "
            "panel in ordered output"
        ),
        "completed_panel_count": len(rows),
        "all_requested_panels_nonzero": complete,
        "terminal": terminal,
        "rows": rows,
        "argument_principle": {
            "status": "NOT_RUN",
            "reason": "the certified chunk is not the complete closed contour",
        },
    }


if __name__ == "__main__":
    RUN.write_text(
        json.dumps(compute(write_checkpoint=True), indent=2, sort_keys=True)
        + "\n"
    )
    print(RUN)
