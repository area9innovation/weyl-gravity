#!/usr/bin/env python3
"""Produce and audit adaptive dyadic continuation v3."""
from __future__ import annotations

import json
import subprocess
import time

from .continuation import (
    AGGREGATE_RUN, HERE, PREDECESSOR_AGGREGATE, PREDECESSOR_CERT,
    PREDECESSOR_RAW, RAW_RUN, ROOT, STABLE_ROOT, build_aggregate,
    compute_raw, sha,
)

CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v1/adaptive.py"
)


def rel(path):
    return str(path.relative_to(ROOT))


def main() -> None:
    started = time.monotonic()
    raw = compute_raw()
    RAW_RUN.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    aggregate = build_aggregate(raw)
    AGGREGATE_RUN.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n"
    )
    imports = {
        "predecessor_certificate": PREDECESSOR_CERT,
        "predecessor_raw": PREDECESSOR_RAW,
        "predecessor_aggregate": PREDECESSOR_AGGREGATE,
        "stable_transport_source": SOURCE,
    }
    accepted = [{
        "segment": f"{entry['panel']}/{entry['panel_count']}",
        "kind": entry["kind"],
        "row_sha256": entry["row_sha256"],
        "delta_modulus_lower": entry["row"][
            "physical_mismatch"
        ]["modulus_lower"],
    } for entry in raw["accepted_segments"]]
    cert = {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v3",
        "status": "BOUNDED_ADAPTIVE_BOUNDARY_PREFIX_EXTENDED_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "adaptive_ordered_chunk_materialized": True,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "materialized_prefix_nonzero_certified": True,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
        "method": {
            "compute_budget_seconds": raw["compute_budget_seconds"],
            "reused_failed_parent": "101/512",
            "maximum_subdivision_depth": 1,
            "horizon_remainder_root": STABLE_ROOT,
            "threshold_policy": "unchanged; no threshold relaxation",
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "accepted_segments": accepted,
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "terminal": raw["terminal"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
        },
        "imports": {
            name: {"path": rel(path), "sha256": sha(path)}
            for name, path in imports.items()
        },
        "runs": {
            "raw": {"path": rel(RAW_RUN), "sha256": sha(RAW_RUN)},
            "aggregate": {
                "path": rel(AGGREGATE_RUN), "sha256": sha(AGGREGATE_RUN)
            },
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
    CERT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Adaptive dyadic boundary chunk v3\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"Reused hashed failed parent `101/512`. Compute elapsed "
        f"`{raw['elapsed_compute_seconds']:.6f}` seconds. Exact coverage "
        f"ends at `{aggregate['summary']['coverage_stop']}`; next gap "
        f"`{aggregate['next_honest_boundary_gap']['start']}`. All "
        "root/QNM/Smith/EP2 gates remain fail-closed.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", rel(HERE / "continuation.py"),
         rel(HERE / "produce.py"), rel(HERE / "verify.py")],
        ["python3", "-m", "jsonschema", "-i", rel(CERT), rel(SCHEMA)],
        ["python3", "-m", "unittest", "-v", (
            "black_hole_programme.phase3."
            "axial_qnm_adaptive_dyadic_boundary_chunk_v3."
            "test_continuation"
        )],
        ["python3", "-m", (
            "black_hole_programme.phase3."
            "axial_qnm_adaptive_dyadic_boundary_chunk_v3.verify"
        )],
    ]
    checks = []
    for command in commands:
        before = time.monotonic()
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=False
        )
        checks.append({
            "command": " ".join(command),
            "elapsed_seconds": round(time.monotonic() - before, 6),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        })
    RECEIPT.write_text(json.dumps({
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-receipt-v3",
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "raw": sha(RAW_RUN), "aggregate": sha(AGGREGATE_RUN),
            "certificate": sha(CERT), "report": sha(REPORT),
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": "bounded producer and independent hash-only verifier",
        "higher_tiers_not_run": "No full contour, freeze or release.",
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
