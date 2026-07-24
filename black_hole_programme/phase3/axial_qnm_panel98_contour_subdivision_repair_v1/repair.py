#!/usr/bin/env python3
"""Reproduce two child panels and assemble the repaired typed prefix."""
from __future__ import annotations

import hashlib
import json
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
CHILD_RUN = HERE / "child-run.json"
AGGREGATE_RUN = HERE / "aggregate-run.json"
PREDECESSOR_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v10/certificate.json"
)
PREDECESSOR_RUN = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v10/rail-v10-run.json"
)
CHILDREN = (196, 197)
CHILD_PANEL_COUNT = 1024
PARENT_PANEL = 98
PARENT_PANEL_COUNT = 512
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


def checked_run(cert_path: Path, run_path: Path) -> dict:
    certificate = json.loads(cert_path.read_text())
    if certificate["run"]["sha256"] != sha(run_path):
        raise RuntimeError(f"run hash mismatch: {run_path}")
    return json.loads(run_path.read_text())


def _worker(panel: int) -> dict:
    ctx.prec = 128
    with patch.object(hp, "forward_remainder", stable_forward_remainder):
        return compute_panel(panel, CHILD_PANEL_COUNT)


def compute_child_run() -> dict:
    """Run exactly the two dyadic children, concurrently."""
    ctx.prec = 128
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_worker, panel): panel for panel in CHILDREN
        }
        unordered = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    rows = [unordered[panel] for panel in CHILDREN]
    entries = [
        {
            "panel": row["panel"],
            "panel_count": row["panel_count"],
            "row_sha256": canonical_sha(row),
            "row": row,
        }
        for row in rows
    ]
    return {
        "schema": (
            "phase3-axial-qnm-panel98-contour-subdivision-"
            "child-run-v1"
        ),
        "arithmetic": "python-flint acb/arb, 128 bits",
        "parent": {"panel": PARENT_PANEL, "panel_count": PARENT_PANEL_COUNT},
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


def _segment(row: dict, source: str) -> dict:
    panel = row["panel"]
    count = row["panel_count"]
    return {
        "start": f"{panel}/{count}",
        "stop": f"{panel + 1}/{count}",
        "source": source,
        "typed_row": row,
    }


def _coverage_is_contiguous(segments: list[dict]) -> bool:
    if not segments:
        return False
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    return (
        bounds[0][0] == 0
        and all(left[1] == right[0] for left, right in zip(bounds, bounds[1:]))
    )


def build_aggregate(child_run: dict) -> dict:
    """Replace failed parent 98/512 by its two certified children."""
    ctx.prec = 128
    predecessor = checked_run(PREDECESSOR_CERT, PREDECESSOR_RUN)
    if predecessor["summary"]["last_panel"] != 97:
        raise RuntimeError("predecessor does not end at parent panel 97")
    if child_run["horizon_remainder_root"] != STABLE_ROOT:
        raise RuntimeError("stable-root identity changed")
    if child_run["threshold_lowered"]:
        raise RuntimeError("threshold relaxation is forbidden")
    if not child_run["all_children_nonzero"]:
        raise RuntimeError("one or more subdivision children failed")

    segments = [
        _segment(row, "projective-evans-riccati-rail-v10")
        for row in predecessor["rows"]
    ]
    typed_children = []
    for entry in child_run["children"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("typed child Delta does not exclude zero")
        typed_children.append(row)
        segments.append(_segment(row, "panel98-subdivision-child-run-v1"))

    contiguous = _coverage_is_contiguous(segments)
    coverage_stop = Fraction(segments[-1]["stop"])
    lowers = [
        (segment["start"], segment["typed_row"]["delta"]["modulus_lower"])
        for segment in segments
    ]
    minimum = min(lowers, key=lambda item: arb(item[1]).lower())
    return {
        "schema": (
            "phase3-axial-qnm-panel98-contour-subdivision-"
            "aggregate-run-v1"
        ),
        "arithmetic": "python-flint acb/arb, 128 bits",
        "status": "PARENT_98_REPLACED_BY_TWO_CERTIFIED_CHILDREN",
        "replacement": {
            "removed_parent": "98/512",
            "removed_parent_status": (
                "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO"
            ),
            "inserted_children": ["196/1024", "197/1024"],
            "same_geometric_interval": (
                Fraction(98, 512) == Fraction(196, 1024)
                and Fraction(99, 512) == Fraction(198, 1024)
            ),
        },
        "segments": segments,
        "summary": {
            "contiguous_from_zero": contiguous,
            "segment_count": len(segments),
            "parent_equivalent_panel_count": 99,
            "coverage_stop": f"{coverage_stop.numerator}/{coverage_stop.denominator}",
            "all_materialized_deltas_exclude_zero": all(
                segment["typed_row"]["delta"]["excludes_zero"]
                for segment in segments
            ),
            "two_sided_interface_gates_pass": all(
                all(segment["typed_row"]["interface_gates"].values())
                for segment in segments
            ),
            "minimum_delta_modulus_lower_segment": minimum[0],
            "minimum_delta_modulus_lower": minimum[1],
        },
        "next_honest_boundary_gap": {
            "start": "99/512",
            "first_unmaterialized_parent_panel": 99,
            "parent_panel_count": 512,
            "reason": (
                "no stable-root shared-generator endpoint export has been "
                "materialized for parent panel 99/512"
            ),
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
