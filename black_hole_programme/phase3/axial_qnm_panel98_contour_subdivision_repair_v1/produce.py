#!/usr/bin/env python3
"""Produce the panel-98 subdivision repair and its receipts."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from flint import arb

from .repair import (
    AGGREGATE_RUN,
    CHILD_RUN,
    HERE,
    PREDECESSOR_CERT,
    PREDECESSOR_RUN,
    ROOT,
    STABLE_ROOT,
    build_aggregate,
    compute_child_run,
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
    "README.md",
    "__init__.py",
    "repair.py",
    "produce.py",
    "verify.py",
    "test_repair.py",
    "schema.json",
)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    started = time.monotonic()
    child_run = compute_child_run()
    CHILD_RUN.write_text(json.dumps(child_run, indent=2, sort_keys=True) + "\n")
    aggregate = build_aggregate(child_run)
    AGGREGATE_RUN.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n"
    )
    child_results = []
    for entry in child_run["children"]:
        row = entry["row"]
        child_results.append({
            "segment": f"{row['panel']}/{row['panel_count']}",
            "row_sha256": entry["row_sha256"],
            "delta_modulus_lower": row[
                "physical_mismatch"
            ]["modulus_lower"],
        })
    imports = {
        "predecessor_certificate": PREDECESSOR_CERT,
        "predecessor_run": PREDECESSOR_RUN,
        "stable_root_certificate": REPAIR_CERT,
        "stable_root_source": REPAIR_SOURCE,
        "transport_source": TRANSPORT_SOURCE,
        "typed_projective_source": TYPING_SOURCE,
    }
    certificate = {
        "schema": (
            "phase3-axial-qnm-panel98-contour-subdivision-repair-v1"
        ),
        "status": (
            "PANEL_98_SUBDIVISION_REPAIRED_BOUNDARY_PREFIX_TO_99_OVER_512"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "parent_98_subdivision_repaired": True,
            "both_child_deltas_exclude_zero": True,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "boundary_prefix_through_99_over_512_certified": True,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
        },
        "method": {
            "parent": "98/512",
            "children": ["196/1024", "197/1024"],
            "worker_count": child_run["worker_count"],
            "arithmetic": child_run["arithmetic"],
            "horizon_remainder_root": STABLE_ROOT,
            "threshold_policy": "unchanged; no threshold relaxation",
            "reuse_policy": (
                "raw child rows are persisted once and all verification "
                "reuses their content hashes without rerunning transport"
            ),
        },
        "result": {
            "children": child_results,
            "aggregate_segment_count": aggregate["summary"]["segment_count"],
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ],
            "minimum_delta_modulus_lower_segment": aggregate[
                "summary"
            ]["minimum_delta_modulus_lower_segment"],
            "minimum_delta_modulus_lower": aggregate[
                "summary"
            ]["minimum_delta_modulus_lower"],
        },
        "imports": {
            name: {"path": _rel(path), "sha256": sha(path)}
            for name, path in imports.items()
        },
        "runs": {
            "children": {"path": _rel(CHILD_RUN), "sha256": sha(CHILD_RUN)},
            "aggregate": {
                "path": _rel(AGGREGATE_RUN),
                "sha256": sha(AGGREGATE_RUN),
            },
        },
        "does_not_establish": [
            "boundary nonvanishing beginning with parent panel 99/512",
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
    child_lines = "\n".join(
        f"- `{item['segment']}`: Delta lower "
        f"`{item['delta_modulus_lower']}`, row SHA-256 "
        f"`{item['row_sha256']}`."
        for item in child_results
    )
    REPORT.write_text(
        "# Panel 98 contour subdivision repair v1\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The failed parent segment `98/512` is replaced exactly by its "
        "two dyadic children under the unchanged stable self-map root:\n\n"
        f"{child_lines}\n\n"
        "Both child mismatch enclosures exclude zero. Together with the "
        "previous typed prefix, this certifies boundary nonvanishing only "
        "through `99/512`. The next honest boundary gap starts at "
        "`99/512`. No argument principle, root count, QNM location, Smith "
        "selector, defective fibre, or EP2 is certified.\n"
    )

    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            _rel(HERE / "repair.py"),
            _rel(HERE / "produce.py"),
            _rel(HERE / "verify.py"),
        ],
        [
            "python3",
            "-m",
            "jsonschema",
            "-i",
            _rel(CERT),
            _rel(SCHEMA),
        ],
        [
            "python3",
            "-m",
            "unittest",
            "-v",
            (
                "black_hole_programme.phase3."
                "axial_qnm_panel98_contour_subdivision_repair_v1."
                "test_repair"
            ),
        ],
        [
            "python3",
            "-m",
            (
                "black_hole_programme.phase3."
                "axial_qnm_panel98_contour_subdivision_repair_v1.verify"
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
        "schema": (
            "phase3-axial-qnm-panel98-contour-subdivision-receipt-v1"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": checks,
        "input_sha256": {name: sha(path) for name, path in imports.items()},
        "output_sha256": {
            "child_run": sha(CHILD_RUN),
            "aggregate_run": sha(AGGREGATE_RUN),
            "certificate": sha(CERT),
            "report": sha(REPORT),
        },
        "artifact_sha256": {
            name: sha(HERE / name) for name in ARTIFACTS
        },
        "tier_0": "py_compile and JSON Schema validation",
        "tier_1": (
            "two-child producer, materialized scoped tests and independent "
            "hash-only verifier"
        ),
        "higher_tiers_not_run": (
            "Local contour subdivision repair; no full contour, theorem "
            "lifecycle promotion, freeze or release."
        ),
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
