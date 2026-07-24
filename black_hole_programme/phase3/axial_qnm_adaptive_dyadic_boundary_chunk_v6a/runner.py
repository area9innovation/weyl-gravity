#!/usr/bin/env python3
"""Observe only parent panel 104/512 with the unchanged v4 adaptive rail."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from ..axial_qnm_adaptive_dyadic_boundary_chunk_v4 import runner as generic

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
    "axial_qnm_adaptive_dyadic_boundary_chunk_v5"
)
PREDECESSOR_CERT = PREDECESSOR / "certificate.json"
PREDECESSOR_AGG = PREDECESSOR / "adaptive-aggregate-run.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _configure_parent_only() -> None:
    core = generic.core
    core.PARENT_START = 104
    core.PARENT_STOP = 105
    core.PREDECESSOR_CERT = PREDECESSOR_CERT
    core.PREDECESSOR_RUN = PREDECESSOR_AGG
    # This is a launch guard, not a scientific threshold.  It makes a failed
    # parent observation terminate before the generic runner launches either
    # child.  A passing parent is accepted normally.
    core.MIN_CHILD_LAUNCH_SECONDS = core.MAX_COMPUTE_SECONDS + 1.0


def _coverage_disposition(raw: dict, aggregate: dict) -> dict:
    observation = raw["observations"][0]
    parent = observation["row"]
    passed = parent["boundary_nonvanishing"]["status"] == "PASS"
    expected = Fraction(105, 512) if passed else Fraction(104, 512)
    actual = Fraction(aggregate["summary"]["coverage_stop"])
    if actual != expected:
        raise RuntimeError(
            f"coverage disposition mismatch: expected {expected}, got {actual}"
        )
    return {
        "parent_segment": "104/512",
        "parent_status": parent["boundary_nonvanishing"]["status"],
        "parent_failure": parent["boundary_nonvanishing"].get("failure"),
        "parent_row_sha256": observation["row_sha256"],
        "delta_modulus_lower": parent["physical_mismatch"]["modulus_lower"],
        "accepted_parent": passed,
        "children_launched": False,
        "coverage_stop": aggregate["summary"]["coverage_stop"],
        "next_honest_boundary_gap": aggregate["next_honest_boundary_gap"],
    }


def main() -> None:
    started = time.monotonic()
    _configure_parent_only()
    raw = generic.core.compute_raw()
    if len(raw["observations"]) != 1:
        raise RuntimeError("parent-only guard materialized more than one row")
    if raw["observations"][0]["panel"] != 104:
        raise RuntimeError("wrong parent panel observed")
    if raw["observations"][0]["panel_count"] != 512:
        raise RuntimeError("wrong parent panel count")
    if any(entry["kind"] == "repair_child" for entry in raw["observations"]):
        raise RuntimeError("parent-only guard launched a child")
    RAW.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")

    aggregate = generic.core.build_aggregate(raw)
    AGG.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    disposition = _coverage_disposition(raw, aggregate)

    flags = {
        "parent_104_observed": True,
        "parent_104_nonzero_certified": disposition["accepted_parent"],
        "children_launched": False,
        "stable_root_reused": True,
        "threshold_lowered": False,
        "full_contour_nonzero_certified": False,
        "argument_principle_certified": False,
        "root_count_certified": False,
        "QNM_location_certified": False,
        "Smith_selector_certified": False,
        "defective_fibre_or_EP2_certified": False,
    }
    certificate = {
        "schema": "phase3-axial-qnm-adaptive-dyadic-boundary-chunk-v6a",
        "status": "PARENT_104_OBSERVED_CHILDREN_NOT_LAUNCHED_FAIL_CLOSED",
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": flags,
        "method": {
            "generic_runner": rel(Path(generic.__file__)),
            "generic_adaptive_source": rel(Path(generic.core.__file__)),
            "requested_parent_range": ["104/512", "104/512"],
            "compute_budget_seconds": raw["compute_budget_seconds"],
            "maximum_subdivision_depth_executed": 0,
            "child_launch_guard": (
                "MIN_CHILD_LAUNCH_SECONDS set above total compute budget; "
                "no child may launch after the parent observation"
            ),
            "scientific_threshold_policy": (
                "unchanged stable remainder root and unchanged nonvanishing "
                "threshold; no relaxation"
            ),
            "horizon_remainder_root": raw["horizon_remainder_root"],
        },
        "result": {
            "elapsed_compute_seconds": raw["elapsed_compute_seconds"],
            "terminal": raw["terminal"],
            "coverage_disposition": disposition,
        },
        "imports": {
            "predecessor_certificate": {
                "path": rel(PREDECESSOR_CERT),
                "sha256": sha(PREDECESSOR_CERT),
            },
            "predecessor_aggregate": {
                "path": rel(PREDECESSOR_AGG),
                "sha256": sha(PREDECESSOR_AGG),
            },
            "generic_v4_runner": {
                "path": rel(Path(generic.__file__)),
                "sha256": sha(Path(generic.__file__)),
            },
            "generic_adaptive_source": {
                "path": rel(Path(generic.core.__file__)),
                "sha256": sha(Path(generic.core.__file__)),
            },
        },
        "runs": {
            "raw": {"path": rel(RAW), "sha256": sha(RAW)},
            "aggregate": {"path": rel(AGG), "sha256": sha(AGG)},
        },
        "does_not_establish": [
            "a repair of parent 104/512 when the parent observation fails",
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
        "# Projective Evans parent observation v6a\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "The unchanged generic adaptive rail observed only parent panel "
        "`104/512`; the child-launch guard stopped the run before any "
        "subdivision. The parent status is "
        f"`{disposition['parent_status']}` with certified mismatch lower "
        f"bound `{disposition['delta_modulus_lower']}`. Exact contiguous "
        f"coverage ends at `{disposition['coverage_stop']}` and the next "
        "honest gap begins at "
        f"`{disposition['next_honest_boundary_gap']['start']}`. "
        "Full-contour, root-count, QNM, Smith and EP2 flags remain false.\n"
    )

    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            rel(HERE / "runner.py"),
            rel(HERE / "verify.py"),
            rel(HERE / "test_v6a.py"),
        ],
        ["python3", "-m", "jsonschema", "-i", rel(CERT), rel(SCHEMA)],
        [
            "python3",
            "-m",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v6a.verify"
            ),
        ],
        [
            "python3",
            "-m",
            "unittest",
            (
                "black_hole_programme.phase3."
                "axial_qnm_adaptive_dyadic_boundary_chunk_v6a.test_v6a"
            ),
        ],
    ]
    checks = []
    for command in commands:
        result = subprocess.run(
            command, cwd=ROOT, text=True, capture_output=True, check=False
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
                    "phase3-axial-qnm-adaptive-dyadic-boundary-receipt-v6a"
                ),
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    "predecessor_certificate": sha(PREDECESSOR_CERT),
                    "predecessor_aggregate": sha(PREDECESSOR_AGG),
                    "generic_v4_runner": sha(Path(generic.__file__)),
                    "generic_adaptive_source": sha(Path(generic.core.__file__)),
                },
                "output_sha256": {
                    "raw": sha(RAW),
                    "aggregate": sha(AGG),
                    "certificate": sha(CERT),
                    "report": sha(REPORT),
                },
                "higher_tiers_not_run": (
                    "No full contour, theorem promotion, freeze or release; "
                    "bounded parent-only Tier 1 rail."
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
