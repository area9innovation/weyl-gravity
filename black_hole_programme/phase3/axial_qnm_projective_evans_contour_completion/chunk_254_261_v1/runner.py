#!/usr/bin/env python3
"""Evaluate a bounded 1/1024 Evans boundary block in parallel."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from pathlib import Path

from flint import arb

from ...axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as core
from ...axial_qnm_projective_evans_riccati_rail_v3.rail_v3 import typed_row


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = HERE / "child-grid-raw-run.json"
AGG = HERE / "child-grid-aggregate-run.json"
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
PREDECESSOR = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_child_grid_boundary_chunk_v9"
)
PRED_CERT = PREDECESSOR / "certificate.json"
PRED_AGG = PREDECESSOR / "child-grid-aggregate-run.json"
PANEL_COUNT = 1024
START = 254
STOP = 262
MAX_WORKERS = 8


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _passes(row: dict) -> bool:
    return (
        row["boundary_nonvanishing"]["status"] == "PASS"
        and arb(row["physical_mismatch"]["modulus_lower"]).lower() > 0
    )


def _compute_rows() -> list[dict]:
    panels = list(range(START, STOP))
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(core._worker, panel, PANEL_COUNT): panel
            for panel in panels
        }
        unordered = {
            futures[future]: future.result()
            for future in as_completed(futures)
        }
    return [unordered[panel] for panel in panels]


def _build_raw() -> dict:
    started = time.monotonic()
    rows = _compute_rows()
    observations = [
        core._entry("fixed_child_grid_observation", row, row["panel"] // 2)
        for row in rows
    ]
    accepted = []
    first_failure = None
    for entry in observations:
        if _passes(entry["row"]):
            accepted.append(entry)
            continue
        first_failure = entry
        break
    terminal = {
        "code": (
            "REQUESTED_CHILD_GRID_STOP_REACHED"
            if first_failure is None
            else "FIRST_CHILD_GRID_FAILURE"
        ),
        "first_unmaterialized_child_panel": (
            STOP if first_failure is None else first_failure["panel"]
        ),
    }
    if first_failure is not None:
        terminal["failure"] = first_failure["row"][
            "boundary_nonvanishing"
        ].get("failure")
    return {
        "schema": "phase3-axial-qnm-projective-evans-contour-raw-run-254-261-v1",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "requested_child_range": [START, STOP - 1],
        "child_panel_count": PANEL_COUNT,
        "maximum_parallel_workers": MAX_WORKERS,
        "maximum_subdivision_depth": 1,
        "elapsed_compute_seconds": time.monotonic() - started,
        "horizon_remainder_root": core.STABLE_ROOT,
        "threshold_lowered": False,
        "observations": observations,
        "accepted_segments": accepted,
        "terminal": terminal,
    }


def _checked_predecessor() -> dict:
    certificate = json.loads(PRED_CERT.read_text())
    if certificate["runs"]["aggregate"]["sha256"] != sha(PRED_AGG):
        raise RuntimeError("predecessor aggregate hash mismatch")
    aggregate = json.loads(PRED_AGG.read_text())
    if Fraction(aggregate["summary"]["coverage_stop"]) != Fraction(
        START, PANEL_COUNT
    ):
        raise RuntimeError("predecessor coverage does not meet child block")
    return aggregate


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
                "source": "qnm-projective-evans-contour-chunk-254-261-v1",
                "source_row_sha256": entry["row_sha256"],
                "typed_row": row,
            }
        )
    bounds = [
        (Fraction(item["start"]), Fraction(item["stop"]))
        for item in segments
    ]
    coverage_stop = bounds[-1][1]
    next_child = raw["terminal"]["first_unmaterialized_child_panel"]
    return {
        "schema": "phase3-axial-qnm-projective-evans-contour-aggregate-run-254-261-v1",
        "status": "FIXED_CHILD_GRID_PREFIX_EXTENDED_FAIL_CLOSED",
        "predecessor_certificate_sha256": sha(PRED_CERT),
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
            "start": f"{next_child}/{PANEL_COUNT}",
            "first_unmaterialized_child_panel": next_child,
            "child_panel_count": PANEL_COUNT,
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
    predecessor = _checked_predecessor()
    raw = _build_raw()
    RAW.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    aggregate = _build_aggregate(raw, predecessor)
    AGG.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")

    accepted = [
        {
            "segment": f"{entry['panel']}/{entry['panel_count']}",
            "row_sha256": entry["row_sha256"],
            "delta_modulus_lower": entry["row"][
                "physical_mismatch"
            ]["modulus_lower"],
        }
        for entry in raw["accepted_segments"]
    ]
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-contour-chunk-254-261-v1",
        "status": "FIXED_CHILD_GRID_BOUNDARY_PREFIX_EXTENDED_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "materialized_prefix_nonzero_certified": True,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "fixed_child_grid_only": True,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
        "method": {
            "start": f"{START}/{PANEL_COUNT}",
            "requested_stop": f"{STOP}/{PANEL_COUNT}",
            "child_panel_count": PANEL_COUNT,
            "maximum_parallel_workers": MAX_WORKERS,
            "maximum_subdivision_depth": 1,
            "horizon_remainder_root": raw["horizon_remainder_root"],
            "threshold_policy": "unchanged; no threshold relaxation",
            "acceptance_policy": (
                "accept only the ordered contiguous prefix before the first "
                "typed zero-exclusion failure"
            ),
            "performance_disposition": (
                "The eight-panel scoped producer must remain below 60 seconds; "
                "the replayless verifier is the per-commit Tier 1 rail. "
                "Future transport chunks retain the same bounded size."
            ),
            "generic_adaptive_source": rel(Path(core.__file__)),
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "accepted_segments": accepted,
            "new_accepted_segment_count": len(raw["accepted_segments"]),
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "terminal": raw["terminal"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(PRED_CERT),
                "sha256": sha(PRED_CERT),
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
        "# Projective Evans contour continuation panels 254--261\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"The unchanged 1/{PANEL_COUNT} projective transport evaluated "
        f"child panels `{START}` through `{STOP - 1}` with "
        f"`{MAX_WORKERS}` workers and accepted only the ordered contiguous "
        "prefix. It accepted "
        f"`{len(raw['accepted_segments'])}/{STOP - START}` panels. Exact "
        f"coverage ends at `{aggregate['summary']['coverage_stop']}` and "
        "the next honest gap begins at "
        f"`{aggregate['next_honest_boundary_gap']['start']}`. "
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
            rel(HERE / "test_chunk.py"),
        ],
        ["python3", "-m", "jsonschema", "-i", rel(CERT), rel(SCHEMA)],
        [
            "python3",
            "-m",
            (
                "black_hole_programme.phase3."
                "axial_qnm_projective_evans_contour_completion.chunk_254_261_v1.verify"
            ),
        ],
        [
            "python3",
            "-m",
            "unittest",
            (
                "black_hole_programme.phase3."
                "axial_qnm_projective_evans_contour_completion.chunk_254_261_v1.test_chunk"
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
                "schema": "phase3-axial-qnm-projective-evans-contour-receipt-254-261-v1",
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    "predecessor_certificate": sha(PRED_CERT),
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
                    "release. The eight-panel transport is the fast "
                    "certificate-chain producer; replayless verification "
                    "is the fast Tier 1 rail."
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
