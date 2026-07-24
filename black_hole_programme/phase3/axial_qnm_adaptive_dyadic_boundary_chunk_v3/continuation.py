#!/usr/bin/env python3
"""Continue from the hashed failed parent observation at 101/512."""
from __future__ import annotations

import json
import time
from fractions import Fraction
from pathlib import Path

from flint import arb

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1.adaptive import (
    CHILD_COUNT, PARENT_COUNT, STABLE_ROOT, _entry, _two_children, _worker,
    canonical_sha, sha,
)
from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW_RUN = HERE / "adaptive-raw-run.json"
AGGREGATE_RUN = HERE / "adaptive-aggregate-run.json"
PREDECESSOR_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v2/certificate.json"
)
PREDECESSOR_RAW = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v2/adaptive-raw-run.json"
)
PREDECESSOR_AGGREGATE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v2/adaptive-aggregate-run.json"
)
START, STOP = 101, 110
BUDGET = 42.0


def _passes(row: dict) -> bool:
    return (
        row["boundary_nonvanishing"]["status"] == "PASS"
        and arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
    )


def compute_raw() -> dict:
    certificate = json.loads(PREDECESSOR_CERT.read_text())
    if certificate["runs"]["raw"]["sha256"] != sha(PREDECESSOR_RAW):
        raise RuntimeError("predecessor raw hash mismatch")
    previous = json.loads(PREDECESSOR_RAW.read_text())
    imported = next(
        entry for entry in previous["observations"]
        if entry["kind"] == "parent_observation"
        and entry["parent_panel"] == START
    )
    if imported["row_sha256"] != canonical_sha(imported["row"]):
        raise RuntimeError("imported parent row hash mismatch")
    if imported["row"]["boundary_nonvanishing"]["status"] == "PASS":
        raise RuntimeError("imported parent was not a failing parent")

    started = time.monotonic()
    observations = [{
        **imported,
        "kind": "imported_parent_observation",
        "source_raw_sha256": sha(PREDECESSOR_RAW),
    }]
    accepted = []
    terminal = None
    parent = START
    while parent < STOP:
        if parent == START:
            parent_row = imported["row"]
        else:
            if BUDGET - (time.monotonic() - started) < 8:
                terminal = {
                    "code": "TIME_BUDGET_BEFORE_NEXT_PARENT",
                    "first_unmaterialized_parent_panel": parent,
                }
                break
            parent_row = _worker(parent, PARENT_COUNT)
            observations.append(_entry(
                "parent_observation", parent_row, parent
            ))
        if _passes(parent_row):
            accepted.append(_entry("accepted_parent", parent_row, parent))
            parent += 1
            continue
        if BUDGET - (time.monotonic() - started) < 14:
            terminal = {
                "code": "TIME_BUDGET_BEFORE_REQUIRED_CHILDREN",
                "first_unmaterialized_parent_panel": parent,
                "parent_failure": parent_row[
                    "boundary_nonvanishing"
                ]["failure"],
            }
            break
        children = _two_children(parent)
        entries = [_entry("repair_child", row, parent) for row in children]
        observations.extend(entries)
        if not all(_passes(row) for row in children):
            terminal = {
                "code": "FIRST_UNREPAIRED_DYADIC_FAILURE",
                "first_unmaterialized_parent_panel": parent,
                "child_failures": [
                    row["panel"] for row in children if not _passes(row)
                ],
            }
            break
        accepted.extend(entries)
        parent += 1
    if terminal is None:
        terminal = {
            "code": "REQUESTED_PARENT_STOP_REACHED",
            "first_unmaterialized_parent_panel": STOP,
        }
    return {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-raw-run-v3",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "requested_parent_range": [START, STOP - 1],
        "compute_budget_seconds": BUDGET,
        "elapsed_compute_seconds": time.monotonic() - started,
        "maximum_subdivision_depth": 1,
        "horizon_remainder_root": STABLE_ROOT,
        "threshold_lowered": False,
        "observations": observations,
        "accepted_segments": accepted,
        "terminal": terminal,
    }


def build_aggregate(raw: dict) -> dict:
    certificate = json.loads(PREDECESSOR_CERT.read_text())
    if certificate["runs"]["aggregate"]["sha256"] != sha(
        PREDECESSOR_AGGREGATE
    ):
        raise RuntimeError("predecessor aggregate hash mismatch")
    predecessor = json.loads(PREDECESSOR_AGGREGATE.read_text())
    if predecessor["summary"]["coverage_stop"] != "101/512":
        raise RuntimeError("predecessor coverage mismatch")
    segments = list(predecessor["segments"])
    for entry in raw["accepted_segments"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("accepted row failed typed Delta gate")
        segments.append({
            "start": f"{row['panel']}/{row['panel_count']}",
            "stop": f"{row['panel'] + 1}/{row['panel_count']}",
            "source": "adaptive-dyadic-boundary-chunk-v3",
            "source_row_sha256": entry["row_sha256"],
            "typed_row": row,
        })
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    contiguous = all(
        left[1] == right[0] for left, right in zip(bounds, bounds[1:])
    )
    stop = bounds[-1][1]
    next_parent = raw["terminal"]["first_unmaterialized_parent_panel"]
    return {
        "schema": (
            "phase3-axial-qnm-adaptive-dyadic-boundary-aggregate-run-v3"
        ),
        "status": "BOUNDED_ADAPTIVE_PREFIX_EXTENDED_FAIL_CLOSED",
        "segments": segments,
        "summary": {
            "contiguous_from_zero": contiguous and bounds[0][0] == 0,
            "coverage_stop": f"{stop.numerator}/{stop.denominator}",
            "new_accepted_segment_count": len(raw["accepted_segments"]),
            "all_materialized_deltas_exclude_zero": all(
                item["typed_row"]["delta"]["excludes_zero"]
                for item in segments
            ),
        },
        "terminal": raw["terminal"],
        "next_honest_boundary_gap": {
            "start": f"{next_parent}/512",
            "first_unmaterialized_parent_panel": next_parent,
        },
        "closed_claim_gates": {
            "full_closed_contour": False,
            "argument_principle_run": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
    }
