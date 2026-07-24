#!/usr/bin/env python3
"""Checkpointed evaluation of common-affine boundary panels 16--31."""
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from flint import ctx

from ..axial_qnm_common_affine_evans_boundary_v1.common_affine import (
    PANEL_COUNT,
    compute_panel,
)

HERE = Path(__file__).resolve().parent
RUN = HERE / "chunk-run.json"
CHECKPOINT = HERE / "chunk-checkpoint.json"
PANEL_START = 16
PANEL_STOP = 32
WORKERS = 4
BATCH_SIZE = 4


def _worker(panel: int) -> dict:
    ctx.prec = 128
    return compute_panel(panel, PANEL_COUNT)


def _checkpoint(rows: list[dict], terminal: dict | None) -> dict:
    return {
        "schema": (
            "phase3-axial-qnm-common-affine-evans-chunk-checkpoint-v2"
        ),
        "requested_panels": [PANEL_START, PANEL_STOP - 1],
        "panel_count": PANEL_COUNT,
        "worker_count": WORKERS,
        "batch_size": BATCH_SIZE,
        "completed_panel_count": len(rows),
        "rows": rows,
        "terminal": terminal,
    }


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
            CHECKPOINT.write_text(
                json.dumps(
                    _checkpoint(rows, terminal), indent=2, sort_keys=True
                ) + "\n"
            )
        if terminal is not None:
            break
    complete = terminal is None and len(rows) == PANEL_STOP - PANEL_START
    return {
        "schema": "phase3-axial-qnm-common-affine-evans-chunk-run-v2",
        "requested_panels": [PANEL_START, PANEL_STOP - 1],
        "full_contour_panel_count": PANEL_COUNT,
        "worker_count": WORKERS,
        "batch_size": BATCH_SIZE,
        "stop_rule": "stop after the first non-PASS panel in ordered output",
        "completed_panel_count": len(rows),
        "all_requested_panels_nonzero": complete,
        "terminal": terminal,
        "rows": rows,
        "argument_principle": {
            "status": "NOT_RUN",
            "reason": "the certified chunk is not the complete closed contour",
        },
    }


def main() -> None:
    RUN.write_text(
        json.dumps(compute(write_checkpoint=True), indent=2, sort_keys=True)
        + "\n"
    )
    print(RUN)


if __name__ == "__main__":
    main()
