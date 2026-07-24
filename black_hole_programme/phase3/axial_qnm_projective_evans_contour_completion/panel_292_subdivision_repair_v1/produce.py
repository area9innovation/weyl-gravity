#!/usr/bin/env python3
"""Produce the panel-292 dyadic repair and replayless receipts."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .repair import (
    AGGREGATE,
    CHILD_RUN,
    HERE,
    PREDECESSOR_AGGREGATE,
    PREDECESSOR_CERTIFICATE,
    ROOT,
    STABLE_ROOT,
    build_aggregate,
    compute_child_run,
    rel,
    sha,
)


CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
ARTIFACTS = (
    "__init__.py",
    "repair.py",
    "produce.py",
    "verify.py",
    "test_repair.py",
    "schema.json",
)
MODULE = (
    "black_hole_programme.phase3."
    "axial_qnm_projective_evans_contour_completion."
    "panel_292_subdivision_repair_v1"
)


def main() -> None:
    started = time.monotonic()
    child_run = compute_child_run()
    CHILD_RUN.write_text(
        json.dumps(child_run, indent=2, sort_keys=True) + "\n"
    )
    aggregate = build_aggregate(child_run)
    AGGREGATE.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n"
    )
    children = [
        {
            "segment": f"{entry['panel']}/{entry['panel_count']}",
            "row_sha256": entry["row_sha256"],
            "delta_modulus_lower": entry["row"][
                "physical_mismatch"
            ]["modulus_lower"],
        }
        for entry in child_run["children"]
    ]
    certificate = {
        "schema": (
            "phase3-axial-qnm-projective-evans-panel-292-"
            "subdivision-repair-v1"
        ),
        "status": "PANEL_292_DYADIC_REPAIR_EXTENDS_PREFIX_TO_293_OVER_1024",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "materialized_prefix_nonzero_certified": True,
            "parent_292_subdivision_repaired": True,
            "both_child_deltas_exclude_zero": True,
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
            "parent": "292/1024",
            "children": ["584/2048", "585/2048"],
            "arithmetic": child_run["arithmetic"],
            "worker_count": child_run["worker_count"],
            "horizon_remainder_root": STABLE_ROOT,
            "threshold_policy": "unchanged; no threshold relaxation",
            "acceptance_policy": (
                "replace only the failed parent by its two exact dyadic "
                "children after both pass the typed Delta gate"
            ),
        },
        "result": {
            "children": children,
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "aggregate_segment_count": aggregate["summary"]["segment_count"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(PREDECESSOR_CERTIFICATE),
                "sha256": sha(PREDECESSOR_CERTIFICATE),
            },
            "predecessor_aggregate": {
                "path": rel(PREDECESSOR_AGGREGATE),
                "sha256": sha(PREDECESSOR_AGGREGATE),
            },
            "generic_adaptive_source": {
                "path": rel(Path(__import__(
                    "black_hole_programme.phase3."
                    "axial_qnm_adaptive_dyadic_boundary_chunk_v1."
                    "adaptive", fromlist=["__file__"]
                ).__file__)),
                "sha256": sha(Path(__import__(
                    "black_hole_programme.phase3."
                    "axial_qnm_adaptive_dyadic_boundary_chunk_v1."
                    "adaptive", fromlist=["__file__"]
                ).__file__)),
            },
            "repair_source": {
                "path": rel(HERE / "repair.py"),
                "sha256": sha(HERE / "repair.py"),
            },
        },
        "runs": {
            "children": {"path": rel(CHILD_RUN), "sha256": sha(CHILD_RUN)},
            "aggregate": {"path": rel(AGGREGATE), "sha256": sha(AGGREGATE)},
        },
        "does_not_establish": [
            "boundary nonvanishing beginning at 293/1024",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle root count",
            "a QNM location or simple-root certificate",
            "a nonzero Delta_tau or Delta_omega selector",
            "a local Smith branch, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim",
        ],
    }
    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    child_lines = "\n".join(
        f"- `{item['segment']}`: Delta lower "
        f"`{item['delta_modulus_lower']}`, row SHA-256 "
        f"`{item['row_sha256']}`."
        for item in children
    )
    REPORT.write_text(
        "# Projective Evans panel 292 subdivision repair\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The fixed `1/1024` panel `292/1024` failed its endpoint export. "
        "Without changing the stable-root or acceptance thresholds, its "
        "two exact dyadic children were evaluated:\n\n"
        f"{child_lines}\n\n"
        "Both typed mismatch enclosures exclude zero. The contiguous "
        "boundary prefix therefore ends at `293/1024`; the next honest "
        "gap starts there. Full-contour, winding, root-count, QNM, Smith "
        "and EP2 claims remain false.\n"
    )

    commands = [
        [
            "python3", "-m", "py_compile",
            rel(HERE / "repair.py"),
            rel(HERE / "produce.py"),
            rel(HERE / "verify.py"),
        ],
        [
            "python3", "-m", "jsonschema",
            "-i", rel(CERTIFICATE), rel(SCHEMA),
        ],
        [
            "python3", "-m", "unittest", "-v",
            f"{MODULE}.test_repair",
        ],
        ["python3", "-m", f"{MODULE}.verify"],
    ]
    checks = []
    for command in commands:
        before = time.monotonic()
        completed = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=False
        )
        checks.append({
            "command": " ".join(command),
            "elapsed_seconds": round(time.monotonic() - before, 6),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        })
    RECEIPT.write_text(json.dumps({
        "schema": (
            "phase3-axial-qnm-projective-evans-panel-292-"
            "subdivision-receipt-v1"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {
            "predecessor_certificate": sha(PREDECESSOR_CERTIFICATE),
            "predecessor_aggregate": sha(PREDECESSOR_AGGREGATE),
        },
        "output_sha256": {
            "child_run": sha(CHILD_RUN),
            "aggregate": sha(AGGREGATE),
            "certificate": sha(CERTIFICATE),
            "report": sha(REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": (
            "two-child producer, scoped mutation tests and independent "
            "replayless verifier"
        ),
        "higher_tiers_not_run": (
            "Local dyadic boundary repair; no full contour, theorem "
            "promotion, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    if not all(check["returncode"] == 0 for check in checks):
        raise RuntimeError("one or more receipt checks failed")
    print(CERTIFICATE)


if __name__ == "__main__":
    main()
