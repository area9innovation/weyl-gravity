#!/usr/bin/env python3
"""Produce the independent closing-sector and winding certificate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE = HERE.parent / "phase_ledger_v1"
LEDGER = PHASE / "phase-ledger.json"
LEDGER_CERT = PHASE / "certificate.json"
FINAL = HERE.parent / "chunk_1021_1023_v1"
AGGREGATE = FINAL / "child-grid-aggregate-run.json"
FINAL_CERT = FINAL / "certificate.json"
ANALYTIC = (
    ROOT / "black_hole_programme/certificates/"
    "BH3_ANALYTIC_CONTINUATION_GATE.json"
)
ECS = (
    ROOT / "black_hole_programme/phase3/"
    "axial_qnm_ecs_inverse_tortoise_v1/certificate.json"
)
COMMON = (
    ROOT / "black_hole_programme/phase3/"
    "axial_qnm_common_affine_evans_boundary_v1/common_affine.py"
)
GEOMETRY = (
    ROOT / "black_hole_programme/phase3/"
    "axial_qnm_ecs_centered_projective_initializer_v1/"
    "centered_initializer.py"
)
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
MODULE = (
    "black_hole_programme.phase3."
    "axial_qnm_projective_evans_contour_completion."
    "full_contour_winding_v1"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _bounds(sector: dict) -> tuple[object, object]:
    return (
        arb(sector["unwrapped_lower"]).lower(),
        arb(sector["unwrapped_upper"]).upper(),
    )


def build() -> dict:
    ctx.prec = 128
    ledger_cert = json.loads(LEDGER_CERT.read_text())
    ledger = json.loads(LEDGER.read_text())
    aggregate = json.loads(AGGREGATE.read_text())
    final_cert = json.loads(FINAL_CERT.read_text())
    analytic = json.loads(ANALYTIC.read_text())
    ecs = json.loads(ECS.read_text())

    if ledger_cert["artifact"]["sha256"] != sha(LEDGER):
        raise RuntimeError("phase-ledger artifact hash mismatch")
    if Fraction(ledger["summary"]["coverage_start"]) != 0:
        raise RuntimeError("phase ledger does not start at zero")
    if Fraction(ledger["summary"]["coverage_stop"]) != 1:
        raise RuntimeError("phase ledger does not close the contour")
    if Fraction(aggregate["summary"]["coverage_stop"]) != 1:
        raise RuntimeError("aggregate does not close the contour")
    if Fraction(final_cert["result"]["coverage_stop"]) != 1:
        raise RuntimeError("final chunk does not close the contour")
    if not ledger["summary"]["contiguous_from_zero"]:
        raise RuntimeError("phase ledger is not contiguous")
    if not aggregate["summary"]["all_materialized_deltas_exclude_zero"]:
        raise RuntimeError("boundary zero exclusion is incomplete")
    if not aggregate["summary"]["two_sided_interface_gates_pass"]:
        raise RuntimeError("an endpoint interface gate is open")
    if not ecs["volterra"]["uniform_contraction_on_closed_disk"]:
        raise RuntimeError("outgoing analytic Volterra family is uncertified")
    if "uniformly convergent Neumann series" not in ecs["volterra"][
        "analytic_frequency_dependence"
    ]:
        raise RuntimeError("outgoing analytic dependence is uncertified")
    axial = analytic["axial_analytic_continuation"]
    if not axial["mode_families"]["boundary_exponents_entire_in_omega"]:
        raise RuntimeError("boundary exponents are not certified analytic")
    if not analytic["claim_flags"]["no_branch_points_axial_certified"]:
        raise RuntimeError("axial no-branch gate is open")

    first = ledger["segments"][0]["argument_sector"]
    last = ledger["segments"][-1]["argument_sector"]
    first_lower, first_upper = _bounds(first)
    last_lower, last_upper = _bounds(last)
    winding = int(last["branch_shift"]) - int(first["branch_shift"])
    shift = 2 * arb.pi() * winding
    shifted_first_lower = first_lower + shift.lower()
    shifted_first_upper = first_upper + shift.upper()
    overlap_lower = max(last_lower, shifted_first_lower)
    overlap_upper = min(last_upper, shifted_first_upper)
    overlap_width = overlap_upper - overlap_lower
    if overlap_width.lower() <= 0:
        raise RuntimeError("closing argument sectors do not overlap")
    total_width = (
        first_upper - first_lower + last_upper - last_lower
    ).upper()
    if total_width >= (2 * arb.pi()).lower():
        raise RuntimeError("closing winding shift is not unique")
    phase = ledger["summary"]["partial_argument_increment_enclosure"]
    phase_lower = arb(phase["lower"]).lower()
    phase_upper = arb(phase["upper"]).upper()
    if phase_lower > shift.lower() or phase_upper < shift.upper():
        raise RuntimeError("integer phase increment is outside ledger bounds")
    if winding != 1:
        raise RuntimeError(
            f"certified winding is {winding}, expected one for this item"
        )

    return {
        "schema": "phase3-axial-qnm-full-contour-winding-v1",
        "status": (
            "FULL_CLOSED_PROJECTIVE_EVANS_CONTOUR_NONZERO_"
            "WITH_WINDING_ONE"
        ),
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "claim_flags": {
            "full_closed_contour_nonzero_certified": True,
            "closing_sector_compatibility_certified": True,
            "winding_number_certified": True,
            "argument_principle_root_count_certified": True,
            "unique_simple_spin_two_QNM_in_disk_certified": True,
            "QNM_location_certified": False,
            "intrinsic_tangent_selector_certified": False,
            "Smith_selector_certified": False,
            "defective_fibre_or_EP2_certified": False,
            "Green_resolvent_double_pole_certified": False,
        },
        "domain": {
            "contour": "Gamma(t)=c+R*exp(2*pi*I*t), 0<=t<=1",
            "orientation": "counterclockwise",
            "center_re": ecs["disk"]["center_re"],
            "center_im": ecs["disk"]["center_im"],
            "radius": ecs["disk"]["radius"],
            "coverage_start": ledger["summary"]["coverage_start"],
            "coverage_stop": ledger["summary"]["coverage_stop"],
        },
        "method": {
            "boundary_nonvanishing": (
                "all contiguous projective mismatch panels exclude zero"
            ),
            "continuous_lift": (
                "adjacent argument sectors overlap and each has width < pi"
            ),
            "closing_test": (
                "the final unwrapped sector overlaps the initial sector "
                "shifted by 2*pi*w; the sum of their widths is <2*pi, "
                "so the integer w is unique"
            ),
            "root_count": (
                "argument principle for the certified holomorphic scalar "
                "projective Evans mismatch on the counterclockwise disk"
            ),
        },
        "result": {
            "segment_count": ledger["summary"]["segment_count"],
            "winding_number": winding,
            "argument_principle_root_count_with_multiplicity": winding,
            "unique_simple_root": winding == 1,
            "phase_increment_enclosure": phase,
            "integer_phase_increment": str(shift),
            "closing_sector_overlap": {
                "lower": str(overlap_lower),
                "upper": str(overlap_upper),
                "width_lower": str(overlap_width.lower()),
            },
            "closing_sector_total_width_upper": str(total_width),
            "minimum_boundary_half_plane_margin": ledger["summary"][
                "minimum_normalized_half_plane_margin"
            ],
            "minimum_adjacent_sector_overlap": ledger["summary"][
                "minimum_adjacent_sector_overlap"
            ],
        },
        "imports": {
            "phase_ledger_certificate": {
                "path": rel(LEDGER_CERT),
                "sha256": sha(LEDGER_CERT),
            },
            "phase_ledger": {
                "path": rel(LEDGER),
                "sha256": sha(LEDGER),
            },
            "final_aggregate": {
                "path": rel(AGGREGATE),
                "sha256": sha(AGGREGATE),
            },
            "final_chunk_certificate": {
                "path": rel(FINAL_CERT),
                "sha256": sha(FINAL_CERT),
            },
            "analytic_continuation_gate": {
                "path": rel(ANALYTIC),
                "sha256": sha(ANALYTIC),
            },
            "ecs_analytic_volterra_gate": {
                "path": rel(ECS),
                "sha256": sha(ECS),
            },
            "projective_mismatch_implementation": {
                "path": rel(COMMON),
                "sha256": sha(COMMON),
            },
            "contour_geometry_implementation": {
                "path": rel(GEOMETRY),
                "sha256": sha(GEOMETRY),
            },
        },
        "does_not_establish": [
            "a numerical enclosure of the unique QNM location",
            "nonvanishing of the intrinsic tangent selector Delta_tau",
            "a local Smith type (0,0,2) or defective fibre",
            "an exceptional point or generalized QNM",
            "a second-order Green-resolvent pole",
            "a physical outgoing Bach connection T_plus",
            "time-domain stability or decay",
            "any LORENTZIAN-CAUSAL, particle or quantum claim",
        ],
    }


def main() -> None:
    started = time.monotonic()
    certificate = build()
    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    result = certificate["result"]
    REPORT.write_text(
        "# Axial QNM full projective Evans contour winding v1\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        f"All {result['segment_count']} contiguous boundary segments exclude "
        "zero. Their certified argument sectors form a continuous lift, and "
        "the closing sector overlaps the initial sector shifted by one full "
        "turn. The counterclockwise projective Evans winding is therefore "
        "`+1`. By the argument principle the certified disk contains exactly "
        "one spin-two zero counted with multiplicity, hence one simple scalar "
        "QNM. No location, intrinsic tangent, Smith, EP2 or Green-resolvent "
        "promotion is made by this certificate.\n"
    )
    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            rel(HERE / "produce.py"),
            rel(HERE / "verify.py"),
            rel(HERE / "test_winding.py"),
        ],
        [
            "python3",
            "-m",
            "jsonschema",
            "-i",
            rel(CERTIFICATE),
            rel(SCHEMA),
        ],
        ["python3", "-m", f"{MODULE}.verify"],
        ["python3", "-m", "unittest", f"{MODULE}.test_winding"],
    ]
    checks = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        checks.append(
            {
                "command": " ".join(command),
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
    RECEIPT.write_text(
        json.dumps(
            {
                "schema": (
                    "phase3-axial-qnm-full-contour-winding-receipt-v1"
                ),
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    key: value["sha256"]
                    for key, value in certificate["imports"].items()
                },
                "output_sha256": {
                    "certificate": sha(CERTIFICATE),
                    "report": sha(REPORT),
                },
                "higher_tiers_not_run": (
                    "No Smith/EP2/Fredholm theorem promotion, freeze or "
                    "release. This is the affected closed-contour chain."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if any(check["returncode"] != 0 for check in checks):
        raise SystemExit("one or more winding checks failed; see receipt.json")
    print(CERTIFICATE)


if __name__ == "__main__":
    main()

