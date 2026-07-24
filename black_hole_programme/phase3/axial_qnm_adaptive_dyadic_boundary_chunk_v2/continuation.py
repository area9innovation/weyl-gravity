#!/usr/bin/env python3
"""Continue the adaptive dyadic rail from parent 100/512."""
from __future__ import annotations

import json
import time
from fractions import Fraction
from pathlib import Path

from flint import arb

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1.adaptive import (
    CHILD_COUNT,
    PARENT_COUNT,
    STABLE_ROOT,
    _entry,
    _two_children,
    _worker,
    canonical_sha,
    sha,
)
from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW_RUN = HERE / "adaptive-raw-run.json"
AGGREGATE_RUN = HERE / "adaptive-aggregate-run.json"
PREDECESSOR_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v1/certificate.json"
)
PREDECESSOR_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v1/"
    "adaptive-aggregate-run.json"
)
PARENT_START = 100
PARENT_STOP = 110
MAX_COMPUTE_SECONDS = 42.0
MIN_PARENT_LAUNCH_SECONDS = 8.0
MIN_CHILD_LAUNCH_SECONDS = 14.0


def compute_raw() -> dict:
    started = time.monotonic()
    accepted: list[dict] = []
    observations: list[dict] = []
    terminal = None
    for parent in range(PARENT_START, PARENT_STOP):
        if (
            MAX_COMPUTE_SECONDS - (time.monotonic() - started)
            < MIN_PARENT_LAUNCH_SECONDS
        ):
            terminal = {
                "code": "TIME_BUDGET_BEFORE_NEXT_PARENT",
                "first_unmaterialized_parent_panel": parent,
            }
            break
        parent_row = _worker(parent, PARENT_COUNT)
        parent_entry = _entry("parent_observation", parent_row, parent)
        observations.append(parent_entry)
        if parent_row["boundary_nonvanishing"]["status"] == "PASS":
            accepted.append(_entry("accepted_parent", parent_row, parent))
            continue
        if (
            MAX_COMPUTE_SECONDS - (time.monotonic() - started)
            < MIN_CHILD_LAUNCH_SECONDS
        ):
            terminal = {
                "code": "TIME_BUDGET_BEFORE_REQUIRED_CHILDREN",
                "first_unmaterialized_parent_panel": parent,
                "parent_failure": parent_row[
                    "boundary_nonvanishing"
                ]["failure"],
            }
            break
        children = _two_children(parent)
        child_entries = [
            _entry("repair_child", row, parent) for row in children
        ]
        observations.extend(child_entries)
        if all(
            row["boundary_nonvanishing"]["status"] == "PASS"
            and arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
            for row in children
        ):
            accepted.extend(child_entries)
            continue
        terminal = {
            "code": "FIRST_UNREPAIRED_DYADIC_FAILURE",
            "first_unmaterialized_parent_panel": parent,
            "parent_failure": parent_row[
                "boundary_nonvanishing"
            ]["failure"],
            "child_failures": [
                {
                    "panel": row["panel"],
                    "failure": row["boundary_nonvanishing"]["failure"],
                }
                for row in children
                if row["boundary_nonvanishing"]["status"] != "PASS"
            ],
        }
        break
    else:
        terminal = {
            "code": "REQUESTED_PARENT_STOP_REACHED",
            "first_unmaterialized_parent_panel": PARENT_STOP,
        }
    return {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-raw-run-v2",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "requested_parent_range": [PARENT_START, PARENT_STOP - 1],
        "parent_panel_count": PARENT_COUNT,
        "child_panel_count": CHILD_COUNT,
        "maximum_subdivision_depth": 1,
        "compute_budget_seconds": MAX_COMPUTE_SECONDS,
        "elapsed_compute_seconds": time.monotonic() - started,
        "horizon_remainder_root": STABLE_ROOT,
        "threshold_lowered": False,
        "observations": observations,
        "accepted_segments": accepted,
        "terminal": terminal,
    }


def build_aggregate(raw: dict) -> dict:
    predecessor_certificate = json.loads(PREDECESSOR_CERT.read_text())
    if (
        predecessor_certificate["runs"]["aggregate"]["sha256"]
        != sha(PREDECESSOR_RUN)
    ):
        raise RuntimeError("predecessor aggregate hash mismatch")
    predecessor = json.loads(PREDECESSOR_RUN.read_text())
    if predecessor["summary"]["coverage_stop"] != "25/128":
        raise RuntimeError("predecessor does not stop at 100/512")
    if raw["horizon_remainder_root"] != STABLE_ROOT:
        raise RuntimeError("stable-root identity changed")
    if raw["threshold_lowered"]:
        raise RuntimeError("threshold relaxation is forbidden")
    segments = list(predecessor["segments"])
    for entry in raw["accepted_segments"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("accepted raw row failed typed Delta gate")
        segments.append({
            "start": f"{row['panel']}/{row['panel_count']}",
            "stop": f"{row['panel'] + 1}/{row['panel_count']}",
            "source": "adaptive-dyadic-boundary-chunk-v2",
            "source_row_sha256": entry["row_sha256"],
            "typed_row": row,
        })
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    contiguous = (
        bounds[0][0] == 0
        and all(
            left[1] == right[0] for left, right in zip(bounds, bounds[1:])
        )
    )
    coverage_stop = bounds[-1][1]
    next_parent = raw["terminal"]["first_unmaterialized_parent_panel"]
    return {
        "schema": (
            "phase3-axial-qnm-adaptive-dyadic-boundary-aggregate-run-v2"
        ),
        "status": "BOUNDED_ADAPTIVE_PREFIX_EXTENDED_FAIL_CLOSED",
        "predecessor_certificate_sha256": sha(PREDECESSOR_CERT),
        "predecessor_coverage_stop": predecessor["summary"]["coverage_stop"],
        "segments": segments,
        "summary": {
            "contiguous_from_zero": contiguous,
            "segment_count": len(segments),
            "coverage_stop": (
                f"{coverage_stop.numerator}/{coverage_stop.denominator}"
            ),
            "all_materialized_deltas_exclude_zero": all(
                item["typed_row"]["delta"]["excludes_zero"]
                for item in segments
            ),
            "two_sided_interface_gates_pass": all(
                all(item["typed_row"]["interface_gates"].values())
                for item in segments
            ),
            "new_accepted_segment_count": len(raw["accepted_segments"]),
        },
        "terminal": raw["terminal"],
        "next_honest_boundary_gap": {
            "start": f"{next_parent}/{PARENT_COUNT}",
            "first_unmaterialized_parent_panel": next_parent,
            "parent_panel_count": PARENT_COUNT,
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
