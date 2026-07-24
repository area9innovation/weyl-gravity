#!/usr/bin/env python3
"""Reproduce the two repair children and extend the typed Evans prefix."""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path

from flint import arb

from ...axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as core
from ...axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREDECESSOR = HERE.parent / "chunk_286_293_v1"
PREDECESSOR_CERTIFICATE = PREDECESSOR / "certificate.json"
PREDECESSOR_AGGREGATE = PREDECESSOR / "child-grid-aggregate-run.json"
CHILD_RUN = HERE / "child-grid-child-run.json"
AGGREGATE = HERE / "child-grid-aggregate-run.json"
PARENT_PANEL = 292
PARENT_COUNT = 1024
CHILDREN = (584, 585)
CHILD_COUNT = 2048
STABLE_ROOT = core.STABLE_ROOT


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _worker(panel: int) -> dict:
    return core._worker(panel, CHILD_COUNT)


def compute_child_run() -> dict:
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_worker, panel): panel for panel in CHILDREN
        }
        unordered = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    entries = []
    for panel in CHILDREN:
        row = unordered[panel]
        entries.append({
            "panel": panel,
            "panel_count": CHILD_COUNT,
            "row_sha256": canonical_sha(row),
            "row": row,
        })
    return {
        "schema": (
            "phase3-axial-qnm-projective-evans-panel-292-"
            "subdivision-child-run-v1"
        ),
        "arithmetic": "python-flint acb/arb, 128 bits",
        "parent": {"panel": PARENT_PANEL, "panel_count": PARENT_COUNT},
        "children": entries,
        "horizon_remainder_root": STABLE_ROOT,
        "threshold_lowered": False,
        "worker_count": 2,
        "all_children_nonzero": all(
            entry["row"]["boundary_nonvanishing"]["status"] == "PASS"
            and arb(
                entry["row"]["physical_mismatch"]["modulus_lower"]
            ).lower() > 0
            for entry in entries
        ),
    }


def checked_predecessor() -> dict:
    certificate = json.loads(PREDECESSOR_CERTIFICATE.read_text())
    if certificate["runs"]["aggregate"]["sha256"] != sha(
        PREDECESSOR_AGGREGATE
    ):
        raise RuntimeError("predecessor aggregate hash mismatch")
    aggregate = json.loads(PREDECESSOR_AGGREGATE.read_text())
    if Fraction(aggregate["summary"]["coverage_stop"]) != Fraction(
        PARENT_PANEL, PARENT_COUNT
    ):
        raise RuntimeError("predecessor does not end at parent panel 292")
    terminal = aggregate["terminal"]
    if (
        terminal["code"] != "FIRST_CHILD_GRID_FAILURE"
        or terminal["first_unmaterialized_child_panel"] != PARENT_PANEL
    ):
        raise RuntimeError("predecessor does not record the repaired failure")
    return aggregate


def build_aggregate(child_run: dict) -> dict:
    predecessor = checked_predecessor()
    if child_run["horizon_remainder_root"] != STABLE_ROOT:
        raise RuntimeError("stable-root identity changed")
    if child_run["threshold_lowered"]:
        raise RuntimeError("threshold relaxation is forbidden")
    if not child_run["all_children_nonzero"]:
        raise RuntimeError("one or more repair children failed")

    segments = list(predecessor["segments"])
    for entry in child_run["children"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("typed repair child failed the Delta gate")
        segments.append({
            "start": f"{row['panel']}/{row['panel_count']}",
            "stop": f"{row['panel'] + 1}/{row['panel_count']}",
            "source": "qnm-projective-evans-panel-292-repair-v1",
            "source_row_sha256": entry["row_sha256"],
            "typed_row": row,
        })

    bounds = [
        (Fraction(segment["start"]), Fraction(segment["stop"]))
        for segment in segments
    ]
    coverage_stop = bounds[-1][1]
    return {
        "schema": (
            "phase3-axial-qnm-projective-evans-panel-292-"
            "subdivision-aggregate-v1"
        ),
        "status": "PARENT_292_REPLACED_BY_TWO_CERTIFIED_CHILDREN",
        "predecessor_certificate_sha256": sha(PREDECESSOR_CERTIFICATE),
        "predecessor_aggregate_sha256": sha(PREDECESSOR_AGGREGATE),
        "replacement": {
            "removed_parent": "292/1024",
            "removed_parent_status": "ENDPOINT_EXPORT_TRANSPORT_FAILED",
            "inserted_children": ["584/2048", "585/2048"],
            "same_geometric_interval": (
                Fraction(292, 1024) == Fraction(584, 2048)
                and Fraction(293, 1024) == Fraction(586, 2048)
            ),
        },
        "segments": segments,
        "summary": {
            "contiguous_from_zero": (
                bounds[0][0] == 0
                and all(
                    left[1] == right[0]
                    for left, right in zip(bounds, bounds[1:])
                )
            ),
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
            "new_accepted_segment_count": len(child_run["children"]),
        },
        "terminal": {
            "code": "REQUIRED_DYADIC_REPAIR_PASSED",
            "first_unmaterialized_child_panel": 293,
        },
        "next_honest_boundary_gap": {
            "start": "293/1024",
            "first_unmaterialized_child_panel": 293,
            "child_panel_count": 1024,
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
