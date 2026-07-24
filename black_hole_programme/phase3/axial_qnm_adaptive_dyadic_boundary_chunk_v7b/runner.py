#!/usr/bin/env python3
"""Reuse the hashed v7 parent and evaluate only children 212/213."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from flint import arb

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as core
from ..axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = HERE / "adaptive-raw-run.json"
AGG = HERE / "adaptive-aggregate-run.json"
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v7"
)
PRED_CERT = PREDECESSOR / "certificate.json"
PRED_RAW = PREDECESSOR / "adaptive-raw-run.json"
PRED_AGG = PREDECESSOR / "adaptive-aggregate-run.json"
PARENT = 106
CHILDREN = (212, 213)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _passes(row: dict) -> bool:
    return (
        row["boundary_nonvanishing"]["status"] == "PASS"
        and arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
    )


def _checked_parent() -> tuple[dict, dict, dict]:
    certificate = json.loads(PRED_CERT.read_text())
    raw = json.loads(PRED_RAW.read_text())
    aggregate = json.loads(PRED_AGG.read_text())
    if certificate["runs"]["raw"]["sha256"] != sha(PRED_RAW):
        raise RuntimeError("v7 raw hash mismatch")
    if certificate["runs"]["aggregate"]["sha256"] != sha(PRED_AGG):
        raise RuntimeError("v7 aggregate hash mismatch")
    if Fraction(aggregate["summary"]["coverage_stop"]) != Fraction(106, 512):
        raise RuntimeError("v7 coverage is not 106/512")
    candidates = [
        item
        for item in raw["observations"]
        if item["panel"] == PARENT and item["panel_count"] == 512
    ]
    if len(candidates) != 1:
        raise RuntimeError("v7 parent 106 observation is not unique")
    observation = candidates[0]
    if observation["row_sha256"] != core.canonical_sha(observation["row"]):
        raise RuntimeError("v7 parent row hash mismatch")
    if _passes(observation["row"]):
        raise RuntimeError("v7 parent unexpectedly passes")
    return raw, aggregate, observation


def _compute_raw(parent_observation: dict) -> dict:
    started = time.monotonic()
    rows = core._two_children(PARENT)
    if tuple(row["panel"] for row in rows) != CHILDREN:
        raise RuntimeError("generic rail returned the wrong child pair")
    entries = [core._entry("repair_child", row, PARENT) for row in rows]
    accepted = entries if all(_passes(row) for row in rows) else []
    repaired = len(accepted) == 2
    terminal = {
        "code": (
            "REQUESTED_CHILDREN_ACCEPTED"
            if repaired
            else "FIRST_UNREPAIRED_DYADIC_FAILURE"
        ),
        "first_unmaterialized_parent_panel": 107 if repaired else 106,
    }
    if not repaired:
        terminal["child_failures"] = [
            {
                "panel": row["panel"],
                "failure": row["boundary_nonvanishing"].get("failure"),
            }
            for row in rows
            if not _passes(row)
        ]
    return {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-raw-run-v7b",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "requested_parent_range": [PARENT, PARENT],
        "requested_child_segments": ["212/1024", "213/1024"],
        "parent_panel_count": 512,
        "child_panel_count": 1024,
        "maximum_subdivision_depth": 1,
        "elapsed_compute_seconds": time.monotonic() - started,
        "horizon_remainder_root": core.STABLE_ROOT,
        "threshold_lowered": False,
        "observations": [
            {
                **parent_observation,
                "kind": "imported_parent_observation",
                "source_raw_sha256": sha(PRED_RAW),
            },
            *entries,
        ],
        "accepted_segments": accepted,
        "terminal": terminal,
    }


def _build_aggregate(raw: dict, predecessor: dict) -> dict:
    segments = list(predecessor["segments"])
    for entry in raw["accepted_segments"]:
        row = typed_row(entry["row"])
        if not row["delta"]["excludes_zero"]:
            raise RuntimeError("accepted child failed typed Delta gate")
        segments.append(
            {
                "start": f"{row['panel']}/{row['panel_count']}",
                "stop": f"{row['panel'] + 1}/{row['panel_count']}",
                "source": "adaptive-dyadic-boundary-chunk-v7b",
                "source_row_sha256": entry["row_sha256"],
                "typed_row": row,
            }
        )
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    stop = bounds[-1][1]
    next_parent = raw["terminal"]["first_unmaterialized_parent_panel"]
    return {
        "schema": (
            "phase3-axial-qnm-adaptive-dyadic-boundary-aggregate-run-v7b"
        ),
        "status": "CHILD_ONLY_REPAIR_FAIL_CLOSED",
        "predecessor_certificate_sha256": sha(PRED_CERT),
        "predecessor_raw_sha256": sha(PRED_RAW),
        "predecessor_aggregate_sha256": sha(PRED_AGG),
        "predecessor_coverage_stop": predecessor["summary"]["coverage_stop"],
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
            "coverage_stop": f"{stop.numerator}/{stop.denominator}",
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
            "start": f"{next_parent}/512",
            "first_unmaterialized_parent_panel": next_parent,
            "parent_panel_count": 512,
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


def main() -> None:
    started = time.monotonic()
    _, predecessor_aggregate, parent = _checked_parent()
    raw = _compute_raw(parent)
    RAW.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    aggregate = _build_aggregate(raw, predecessor_aggregate)
    AGG.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    repaired = len(raw["accepted_segments"]) == 2
    results = [
        {
            "segment": f"{entry['panel']}/{entry['panel_count']}",
            "status": entry["row"]["boundary_nonvanishing"]["status"],
            "failure": entry["row"]["boundary_nonvanishing"].get("failure"),
            "row_sha256": entry["row_sha256"],
            "delta_modulus_lower": entry["row"][
                "physical_mismatch"
            ]["modulus_lower"],
            "accepted": _passes(entry["row"]),
        }
        for entry in raw["observations"][1:]
    ]
    certificate = {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v7b",
        "status": (
            "CHILDREN_212_213_ACCEPTED_PREFIX_EXTENDED_FAIL_CLOSED"
            if repaired
            else "CHILDREN_212_213_FAILED_PREFIX_UNCHANGED_FAIL_CLOSED"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "hashed_failed_parent_106_reused": True,
            "only_children_212_213_evaluated": True,
            "children_212_213_nonzero_certified": repaired,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
        "method": {
            "requested_parent": "106/512",
            "requested_children": ["212/1024", "213/1024"],
            "parent_recomputed": False,
            "maximum_subdivision_depth_executed": 1,
            "scientific_threshold_policy": (
                "unchanged stable remainder root and unchanged typed "
                "nonvanishing gate; no relaxation"
            ),
            "horizon_remainder_root": raw["horizon_remainder_root"],
            "generic_adaptive_source": rel(Path(core.__file__)),
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "children": results,
            "accepted_child_count": len(raw["accepted_segments"]),
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
            "terminal": raw["terminal"],
        },
        "parent_hash_linkage": {
            "source_raw_sha256": sha(PRED_RAW),
            "parent_row_sha256": parent["row_sha256"],
            "canonical_parent_row_sha256": core.canonical_sha(parent["row"]),
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(PRED_CERT),
                "sha256": sha(PRED_CERT),
            },
            "predecessor_raw": {
                "path": rel(PRED_RAW),
                "sha256": sha(PRED_RAW),
            },
            "predecessor_aggregate": {
                "path": rel(PRED_AGG),
                "sha256": sha(PRED_AGG),
            },
            "generic_adaptive_source": {
                "path": rel(Path(core.__file__)),
                "sha256": sha(Path(core.__file__)),
            },
        },
        "runs": {
            "raw": {"path": rel(RAW), "sha256": sha(RAW)},
            "aggregate": {"path": rel(AGG), "sha256": sha(AGG)},
        },
        "does_not_establish": [
            "boundary nonvanishing beginning at the stated next gap",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle root count",
            "a QNM location or simple-root certificate",
            "a nonzero Delta_tau or Delta_omega selector",
            "a local Smith branch, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Projective Evans child-only repair v7b\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The rail reused the hash-linked failed parent `106/512` from v7 "
        "without recomputing it and evaluated only `212/1024` and "
        f"`213/1024`. Accepted children: `{len(raw['accepted_segments'])}/2`. "
        "Exact contiguous coverage ends at "
        f"`{aggregate['summary']['coverage_stop']}`; the next honest gap "
        f"begins at `{aggregate['next_honest_boundary_gap']['start']}`. "
        "Full-contour, argument-principle, root-count, QNM, Smith and EP2 "
        "flags remain false.\n"
    )

    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            rel(HERE / "runner.py"),
            rel(HERE / "verify.py"),
            rel(HERE / "test_v7b.py"),
        ],
        ["python3", "-m", "jsonschema", "-i", rel(CERT), rel(SCHEMA)],
        [
            "python3",
            "-m",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v7b.verify"
            ),
        ],
        [
            "python3",
            "-m",
            "unittest",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v7b.test_v7b"
            ),
        ],
    ]
    checks = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        checks.append(
            {
                "command": " ".join(command),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": (
                    "phase3-axial-qnm-adaptive-dyadic-boundary-receipt-v7b"
                ),
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    "predecessor_certificate": sha(PRED_CERT),
                    "predecessor_raw": sha(PRED_RAW),
                    "predecessor_aggregate": sha(PRED_AGG),
                    "generic_adaptive_source": sha(Path(core.__file__)),
                },
                "output_sha256": {
                    "raw": sha(RAW),
                    "aggregate": sha(AGG),
                    "certificate": sha(CERT),
                    "report": sha(REPORT),
                },
                "higher_tiers_not_run": (
                    "No closed contour, theorem promotion, freeze or "
                    "release; child-only Tier 1 repair."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if any(check["returncode"] != 0 for check in checks):
        raise SystemExit("one or more scoped checks failed; see receipt.json")
    print(CERT)


if __name__ == "__main__":
    main()
