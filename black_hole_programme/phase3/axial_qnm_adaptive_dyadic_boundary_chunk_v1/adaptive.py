#!/usr/bin/env python3
"""Bounded ordered parent transport with one-level dyadic repair."""
from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

from flint import arb, ctx

import black_hole_programme.phase3.axial_qnm_horizon_projective_preflight_v1.horizon_preflight as hp
from ..axial_qnm_common_affine_evans_boundary_v1.common_affine import (
    compute_panel,
)
from ..axial_qnm_horizon_center_self_map_repair_v1.repair import (
    stable_forward_remainder,
)
from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW_RUN = HERE / "adaptive-raw-run.json"
AGGREGATE_RUN = HERE / "adaptive-aggregate-run.json"
PREDECESSOR_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_panel98_contour_subdivision_repair_v1/certificate.json"
)
PREDECESSOR_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_panel98_contour_subdivision_repair_v1/aggregate-run.json"
)
PARENT_START = 99
PARENT_STOP = 110
PARENT_COUNT = 512
CHILD_COUNT = 1024
MAX_COMPUTE_SECONDS = 42.0
MIN_PARENT_LAUNCH_SECONDS = 8.0
MIN_CHILD_LAUNCH_SECONDS = 14.0
STABLE_ROOT = (
    "stable interval smaller root with exact 1000001/1000000 "
    "strict enlargement"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _worker(panel: int, panel_count: int) -> dict:
    ctx.prec = 128
    with patch.object(hp, "forward_remainder", stable_forward_remainder):
        return compute_panel(panel, panel_count)


def _two_children(parent: int) -> list[dict]:
    panels = (2 * parent, 2 * parent + 1)
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_worker, panel, CHILD_COUNT): panel
            for panel in panels
        }
        unordered = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    return [unordered[panel] for panel in panels]


def _entry(kind: str, row: dict, parent: int) -> dict:
    return {
        "kind": kind,
        "parent_panel": parent,
        "panel": row["panel"],
        "panel_count": row["panel_count"],
        "row_sha256": canonical_sha(row),
        "row": row,
    }


def compute_raw() -> dict:
    ctx.prec = 128
    started = time.monotonic()
    accepted: list[dict] = []
    observations: list[dict] = []
    terminal = None
    for parent in range(PARENT_START, PARENT_STOP):
        elapsed = time.monotonic() - started
        if MAX_COMPUTE_SECONDS - elapsed < MIN_PARENT_LAUNCH_SECONDS:
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

        elapsed = time.monotonic() - started
        if MAX_COMPUTE_SECONDS - elapsed < MIN_CHILD_LAUNCH_SECONDS:
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
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-raw-run-v1",
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


def _checked_predecessor() -> tuple[dict, dict]:
    certificate = json.loads(PREDECESSOR_CERT.read_text())
    expected = certificate["runs"]["aggregate"]["sha256"]
    if expected != sha(PREDECESSOR_RUN):
        raise RuntimeError("predecessor aggregate hash mismatch")
    return certificate, json.loads(PREDECESSOR_RUN.read_text())


def _bounds(segment: dict) -> tuple[Fraction, Fraction]:
    return Fraction(segment["start"]), Fraction(segment["stop"])


def build_aggregate(raw: dict) -> dict:
    predecessor_certificate, predecessor = _checked_predecessor()
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
            "source": "adaptive-dyadic-boundary-chunk-v1",
            "source_row_sha256": entry["row_sha256"],
            "typed_row": row,
        })
    bounds = [_bounds(segment) for segment in segments]
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
            "phase3-axial-qnm-adaptive-dyadic-boundary-aggregate-run-v1"
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
                segment["typed_row"]["delta"]["excludes_zero"]
                for segment in segments
            ),
            "two_sided_interface_gates_pass": all(
                all(segment["typed_row"]["interface_gates"].values())
                for segment in segments
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
        "predecessor_claim_flags": predecessor_certificate["claim_flags"],
    }
