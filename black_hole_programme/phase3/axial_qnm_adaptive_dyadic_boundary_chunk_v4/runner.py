#!/usr/bin/env python3
"""Run one bounded generic adaptive continuation from 103/512."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v1 import adaptive as core

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = HERE / "adaptive-raw-run.json"
AGG = HERE / "adaptive-aggregate-run.json"
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
PRED_CERT = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v3/certificate.json"
)
PRED_AGG = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_adaptive_dyadic_boundary_chunk_v3/adaptive-aggregate-run.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    started = time.monotonic()
    core.PARENT_START = 103
    core.PARENT_STOP = 110
    core.PREDECESSOR_CERT = PRED_CERT
    core.PREDECESSOR_RUN = PRED_AGG
    raw = core.compute_raw()
    RAW.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    aggregate = core.build_aggregate(raw)
    AGG.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    accepted = [{
        "segment": f"{entry['panel']}/{entry['panel_count']}",
        "kind": entry["kind"],
        "row_sha256": entry["row_sha256"],
        "delta_modulus_lower": entry["row"][
            "physical_mismatch"
        ]["modulus_lower"],
    } for entry in raw["accepted_segments"]]
    certificate = {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v4",
        "status": "BOUNDED_ADAPTIVE_BOUNDARY_PREFIX_EXTENDED_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "materialized_prefix_nonzero_certified": True,
            "stable_root_reused": True,
            "threshold_lowered": False,
            "full_contour_nonzero_certified": False,
            "argument_principle_certified": False,
            "root_count_certified": False,
            "QNM_location_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False
        },
        "method": {
            "start": "103/512",
            "compute_budget_seconds": raw["compute_budget_seconds"],
            "maximum_subdivision_depth": 1,
            "horizon_remainder_root": raw["horizon_remainder_root"],
            "threshold_policy": "unchanged; no threshold relaxation"
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "accepted_segments": accepted,
            "coverage_stop": aggregate["summary"]["coverage_stop"],
            "terminal": raw["terminal"],
            "next_honest_boundary_gap": aggregate[
                "next_honest_boundary_gap"
            ]
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(PRED_CERT), "sha256": sha(PRED_CERT)
            },
            "predecessor_aggregate": {
                "path": rel(PRED_AGG), "sha256": sha(PRED_AGG)
            },
            "generic_adaptive_source": {
                "path": rel(Path(core.__file__)),
                "sha256": sha(Path(core.__file__))
            }
        },
        "runs": {
            "raw": {"path": rel(RAW), "sha256": sha(RAW)},
            "aggregate": {"path": rel(AGG), "sha256": sha(AGG)}
        },
        "does_not_establish": [
            "boundary nonvanishing beginning at the stated next gap",
            "boundary nonvanishing on the complete closed contour",
            "an argument-principle root count",
            "a QNM location or simple-root certificate",
            "a nonzero Delta_tau or Delta_omega selector",
            "a local Smith branch, defective fibre or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or any LORENTZIAN-CAUSAL claim"
        ]
    }
    CERT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# Adaptive dyadic boundary chunk v4\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"Started from authoritative `103/512`. Exact coverage ends at "
        f"`{aggregate['summary']['coverage_stop']}` and the next gap is "
        f"`{aggregate['next_honest_boundary_gap']['start']}`. Compute "
        f"elapsed `{raw['elapsed_compute_seconds']:.6f}` seconds. Stable "
        "root and thresholds are unchanged. Root/QNM/Smith/EP2 gates "
        "remain false.\n"
    )
    commands = [
        ["python3", "-m", "py_compile", rel(HERE / "runner.py"),
         rel(HERE / "verify.py")],
        ["python3", "-m", "jsonschema", "-i", rel(CERT), rel(SCHEMA)],
        ["python3", "-m", (
            "black_hole_programme.phase3."
            "axial_qnm_adaptive_dyadic_boundary_chunk_v4.verify"
        )]
    ]
    checks = []
    for command in commands:
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=False
        )
        checks.append({
            "command": " ".join(command), "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr
        })
    RECEIPT.write_text(json.dumps({
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-receipt-v4",
        "elapsed_seconds": time.monotonic() - started,
        "checks": checks,
        "input_sha256": {
            "predecessor_certificate": sha(PRED_CERT),
            "predecessor_aggregate": sha(PRED_AGG)
        },
        "output_sha256": {
            "raw": sha(RAW), "aggregate": sha(AGG),
            "certificate": sha(CERT), "report": sha(REPORT)
        },
        "higher_tiers_not_run": "No full contour, freeze or release."
    }, indent=2, sort_keys=True) + "\n")
    print(CERT)


if __name__ == "__main__":
    main()
