#!/usr/bin/env python3
"""Produce the bounded adaptive dyadic boundary chunk."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .adaptive import (
    AGGREGATE_RUN,
    HERE,
    PREDECESSOR_CERT,
    PREDECESSOR_RUN,
    RAW_RUN,
    ROOT,
    STABLE_ROOT,
    build_aggregate,
    compute_raw,
    sha,
)

CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
REPAIR_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_center_self_map_repair_v1/certificate.json"
)
REPAIR_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_horizon_center_self_map_repair_v1/repair.py"
)
TRANSPORT_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common_affine.py"
)
TYPING_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v3/rail_v3.py"
)
ARTIFACTS = (
    "README.md", "__init__.py", "adaptive.py", "produce.py",
    "verify.py", "test_adaptive.py", "schema.json",
)


def _rel(path: Path) -> str:
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
        "predecessor_aggregate": PREDECESSOR_RUN,
        "stable_root_certificate": REPAIR_CERT,
        "stable_root_source": REPAIR_SOURCE,
        "transport_source": TRANSPORT_SOURCE,
        "typed_projective_source": TYPING_SOURCE,
    }
    certificate = {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v1",
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
            "requested_parent_range": raw["requested_parent_range"],
            "compute_budget_seconds": raw["compute_budget_seconds"],
            "maximum_subdivision_depth": raw[
                "maximum_subdivision_depth"
            ],
            "parent_policy": "ordered sequential evaluation",
            "subdivision_policy": (
                "split only a failing parent into its two dyadic children"
            ),
            "stop_policy": (
                "stop before insufficient launch budget or at first "
                "unrepaired child failure"
            ),
            "horizon_remainder_root": STABLE_ROOT,
            "threshold_policy": "unchanged; no threshold relaxation",
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "new_accepted_segment_count": aggregate[
                "summary"
            ]["new_accepted_segment_count"],
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "terminal": raw["terminal"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
            "accepted_segments": [
                {
                    "segment": (
                        f"{entry['panel']}/{entry['panel_count']}"
                    ),
                    "kind": entry["kind"],
                    "row_sha256": entry["row_sha256"],
                    "delta_modulus_lower": entry["row"][
                        "physical_mismatch"
                    ]["modulus_lower"],
                }
                for entry in raw["accepted_segments"]
            ],
        },
        "imports": {
            name: {"path": _rel(path), "sha256": sha(path)}
            for name, path in imports.items()
        },
        "runs": {
            "raw": {"path": _rel(RAW_RUN), "sha256": sha(RAW_RUN)},
            "aggregate": {
                "path": _rel(AGGREGATE_RUN),
                "sha256": sha(AGGREGATE_RUN),
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
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    accepted = "\n".join(
        f"- `{item['segment']}` ({item['kind']}): Delta lower "
        f"`{item['delta_modulus_lower']}`, row SHA-256 "
        f"`{item['row_sha256']}`."
        for item in certificate["result"]["accepted_segments"]
    )
    REPORT.write_text(
        "# Adaptive dyadic boundary chunk v1\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"Compute elapsed `{raw['elapsed_compute_seconds']:.6f}` seconds. "
        f"The prefix now ends at `{aggregate['summary']['coverage_stop']}`; "
        f"terminal `{raw['terminal']['code']}`. Accepted additions:\n\n"
        f"{accepted or '- none'}\n\n"
        "All root-count, QNM-location, Smith-selector and EP2 gates remain "
        "fail-closed.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", *[
            _rel(HERE / name)
            for name in ("adaptive.py", "produce.py", "verify.py")
        ]],
        ["python3", "-m", "jsonschema", "-i", _rel(CERT), _rel(SCHEMA)],
        [
            "python3", "-m", "unittest", "-v",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v1."
                "test_adaptive"
            ),
        ],
        [
            "python3", "-m",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v1.verify"
            ),
        ],
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
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-receipt-v1",
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "raw_run": sha(RAW_RUN),
            "aggregate_run": sha(AGGREGATE_RUN),
            "certificate": sha(CERT),
            "report": sha(REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": (
            "bounded producer, materialized tests and independent hash-only "
            "verifier"
        ),
        "higher_tiers_not_run": (
            "Bounded contour continuation; no full contour, theorem "
            "lifecycle promotion, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
