#!/usr/bin/env python3
"""Build a separating-half-plane and lifted-phase Evans prefix ledger."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from black_hole_programme.phase3.axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
        parse_acb,
    )
else:
    from ...axial_qnm_horizon_reciprocal_checkpoint_transport_v1.checkpoint_transport import (
        parse_acb,
    )


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CURRENT = HERE.parent / "chunk_373_380_v1"
CURRENT_CERT = CURRENT / "certificate.json"
AGGREGATE = CURRENT / "child-grid-aggregate-run.json"
TYPED_SOURCE = ROOT / (
    "black_hole_programme/phase3/"
    "axial_qnm_projective_evans_riccati_rail_v3/rail_v3.py"
)
LEDGER = HERE / "phase-ledger.json"
CERTIFICATE = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
REPORT = HERE / "report.md"
SCHEMA = HERE / "schema.json"
SCALE = 10**9
DIRECTION_COUNT = 64
MODULE = (
    "black_hole_programme.phase3."
    "axial_qnm_projective_evans_contour_completion.phase_ledger_v1"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def directions() -> list[tuple[int, int]]:
    return [
        (
            round(SCALE * math.cos(2 * math.pi * index / DIRECTION_COUNT)),
            round(SCALE * math.sin(2 * math.pi * index / DIRECTION_COUNT)),
        )
        for index in range(DIRECTION_COUNT)
    ]


def _shift_bounds(
    lower, upper, branch_shift: int
) -> tuple[object, object]:
    shift = arb(branch_shift) * 2 * arb.pi()
    return lower + shift.lower(), upper + shift.upper()


def _segment_record(segment: dict, previous: dict | None) -> dict:
    delta = segment["typed_row"]["delta"]
    center = parse_acb(delta["polynomial_coefficients"][0])
    modulus_lower = arb(delta["modulus_lower"])
    if modulus_lower.lower() <= 0:
        raise RuntimeError("phase ledger received a zero-containing panel")

    # typed_row() computed L = |delta_0|_lower - R.  Reissuing
    # R <= |delta_0|_upper - L_lower is conservative and retains the
    # original affine/residual enclosure without needing its generator.
    radius_upper = center.abs_upper().upper() - modulus_lower.lower()
    if radius_upper < 0:
        raise RuntimeError("negative reconstructed enclosure radius")

    best = None
    for index, (real, imag) in enumerate(directions()):
        norm_upper = arb(real * real + imag * imag).sqrt().upper()
        projection_lower = (
            real * center.real + imag * center.imag
        ).lower()
        margin = projection_lower - norm_upper * radius_upper
        normalized = margin / norm_upper
        if best is None or normalized.lower() > best["normalized"].lower():
            best = {
                "index": index,
                "real": real,
                "imag": imag,
                "norm_upper": norm_upper,
                "projection_lower": projection_lower,
                "margin": margin,
                "normalized": normalized,
            }
    assert best is not None
    if best["margin"].lower() <= 0:
        raise RuntimeError("no rational separating half-plane was certified")

    center_abs_lower = center.abs_lower().lower()
    ratio = radius_upper / center_abs_lower
    if ratio.upper() >= 1:
        raise RuntimeError("argument-sector ratio is not strictly below one")
    half_width = ratio.asin().upper()
    center_argument = center.arg()
    principal_lower = center_argument.lower() - half_width
    principal_upper = center_argument.upper() + half_width
    if principal_upper - principal_lower >= arb.pi().lower():
        raise RuntimeError("panel argument sector is not narrower than pi")

    principal_mid = float(center_argument.mid())
    if previous is None:
        branch_shift = 0
    else:
        branch_shift = round(
            (previous["midpoint"] - principal_mid) / (2 * math.pi)
        )
    unwrapped_lower, unwrapped_upper = _shift_bounds(
        principal_lower, principal_upper, branch_shift
    )
    overlap = None
    if previous is not None:
        overlap_lower = max(previous["lower"], unwrapped_lower)
        overlap_upper = min(previous["upper"], unwrapped_upper)
        overlap_margin = overlap_upper - overlap_lower
        if overlap_margin <= 0:
            raise RuntimeError("adjacent argument sectors do not overlap")
        overlap = {
            "lower": str(overlap_lower),
            "upper": str(overlap_upper),
            "width_lower": str(overlap_margin),
            "certified_nonempty": True,
        }

    return {
        "start": segment["start"],
        "stop": segment["stop"],
        "source": segment["source"],
        "source_row_sha256": segment.get("source_row_sha256"),
        "delta_center": str(center),
        "certified_modulus_lower": str(modulus_lower),
        "reconstructed_radius_upper": str(radius_upper),
        "separator": {
            "direction_index": best["index"],
            "integer_vector": [best["real"], best["imag"]],
            "norm_upper": str(best["norm_upper"]),
            "projection_lower": str(best["projection_lower"]),
            "half_plane_margin_lower": str(best["margin"]),
            "normalized_margin_lower": str(best["normalized"]),
            "certified_positive": True,
        },
        "argument_sector": {
            "principal_center": str(center_argument),
            "half_width_upper": str(half_width),
            "principal_lower": str(principal_lower),
            "principal_upper": str(principal_upper),
            "width_less_than_pi": True,
            "branch_shift": branch_shift,
            "unwrapped_lower": str(unwrapped_lower),
            "unwrapped_upper": str(unwrapped_upper),
        },
        "previous_sector_overlap": overlap,
        "_bounds": {
            "lower": unwrapped_lower,
            "upper": unwrapped_upper,
            "midpoint": principal_mid + branch_shift * 2 * math.pi,
        },
    }


def build() -> dict:
    ctx.prec = 128
    certificate = json.loads(CURRENT_CERT.read_text())
    if certificate["runs"]["aggregate"]["sha256"] != sha(AGGREGATE):
        raise RuntimeError("current aggregate hash mismatch")
    aggregate = json.loads(AGGREGATE.read_text())
    records = []
    previous = None
    for segment in aggregate["segments"]:
        record = _segment_record(segment, previous)
        previous = record.pop("_bounds")
        records.append(record)
    if not records:
        raise RuntimeError("empty boundary prefix")
    first = records[0]["argument_sector"]
    last = records[-1]["argument_sector"]
    phase_lower = (
        arb(last["unwrapped_lower"]) - arb(first["unwrapped_upper"])
    ).lower()
    phase_upper = (
        arb(last["unwrapped_upper"]) - arb(first["unwrapped_lower"])
    ).upper()
    weakest = min(
        records,
        key=lambda record: arb(
            record["separator"]["normalized_margin_lower"]
        ).lower(),
    )
    widest = max(
        records,
        key=lambda record: (
            arb(record["argument_sector"]["unwrapped_upper"])
            - arb(record["argument_sector"]["unwrapped_lower"])
        ).upper(),
    )
    overlap_records = [
        record for record in records if record["previous_sector_overlap"]
    ]
    narrowest_overlap = min(
        overlap_records,
        key=lambda record: arb(
            record["previous_sector_overlap"]["width_lower"]
        ).lower(),
    )
    return {
        "schema": "phase3-axial-qnm-projective-evans-phase-ledger-v1",
        "arithmetic": "python-flint acb/arb, 128 bits",
        "status": "PARTIAL_BOUNDARY_LIFTED_PHASE_CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "source": {
            "certificate": {
                "path": rel(CURRENT_CERT),
                "sha256": sha(CURRENT_CERT),
            },
            "aggregate": {
                "path": rel(AGGREGATE),
                "sha256": sha(AGGREGATE),
            },
            "typed_row_implementation": {
                "path": rel(TYPED_SOURCE),
                "sha256": sha(TYPED_SOURCE),
            },
        },
        "method": {
            "direction_count": DIRECTION_COUNT,
            "integer_direction_scale": SCALE,
            "radius_reissue": (
                "abs_upper(delta_center) - "
                "lower(certified_modulus_lower)"
            ),
            "separator_test": (
                "Re((a+ib)*delta_center)_lower "
                "- hypot(a,b)_upper*radius_upper > 0"
            ),
            "argument_half_width": (
                "asin(radius_upper/abs_lower(delta_center))"
            ),
            "branch_rule": (
                "choose the integer 2*pi shift nearest the previous "
                "unwrapped sector midpoint"
            ),
        },
        "segments": records,
        "summary": {
            "segment_count": len(records),
            "coverage_start": str(Fraction(records[0]["start"])),
            "coverage_stop": str(Fraction(records[-1]["stop"])),
            "contiguous_from_zero": (
                Fraction(records[0]["start"]) == 0
                and all(
                    Fraction(left["stop"]) == Fraction(right["start"])
                    for left, right in zip(records, records[1:])
                )
            ),
            "all_separating_half_planes_certified": all(
                record["separator"]["certified_positive"]
                for record in records
            ),
            "all_argument_sectors_narrower_than_pi": all(
                record["argument_sector"]["width_less_than_pi"]
                for record in records
            ),
            "all_adjacent_sector_overlaps_certified": all(
                record["previous_sector_overlap"] is None
                or record["previous_sector_overlap"]["certified_nonempty"]
                for record in records
            ),
            "branch_shift_min": min(
                record["argument_sector"]["branch_shift"]
                for record in records
            ),
            "branch_shift_max": max(
                record["argument_sector"]["branch_shift"]
                for record in records
            ),
            "minimum_normalized_half_plane_margin": {
                "segment_start": weakest["start"],
                "lower": weakest["separator"]["normalized_margin_lower"],
            },
            "maximum_argument_sector_width": {
                "segment_start": widest["start"],
                "upper": str(
                    (
                        arb(widest["argument_sector"]["unwrapped_upper"])
                        - arb(
                            widest["argument_sector"]["unwrapped_lower"]
                        )
                    ).upper()
                ),
            },
            "minimum_adjacent_sector_overlap": {
                "segment_start": narrowest_overlap["start"],
                "lower": narrowest_overlap["previous_sector_overlap"][
                    "width_lower"
                ],
            },
            "partial_argument_increment_enclosure": {
                "lower": str(phase_lower),
                "upper": str(phase_upper),
            },
        },
        "claim_flags": {
            "partial_prefix_nonvanishing_certified": True,
            "panelwise_separating_half_planes_certified": True,
            "continuous_lifted_phase_on_prefix_certified": True,
            "partial_argument_increment_enclosed": True,
            "full_closed_contour_certified": False,
            "winding_number_certified": False,
            "argument_principle_root_count_certified": False,
            "QNM_or_EP2_certified": False,
        },
        "does_not_establish": [
            (
                "boundary nonvanishing after "
                f"{Fraction(records[-1]['stop'])}"
            ),
            "a closed Evans contour",
            "an integer winding number",
            "an argument-principle root count",
            "a QNM location",
            "a Smith selector or EP2",
            "a physical outgoing Bach map T_plus",
            "time-domain stability or a LORENTZIAN-CAUSAL claim",
        ],
    }


def main() -> None:
    started = time.monotonic()
    ledger = build()
    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    certificate = {
        "schema": "phase3-axial-qnm-projective-evans-phase-ledger-certificate-v1",
        "status": ledger["status"],
        "lifecycle": "CLASSIFIED",
        "dependency_tags": ledger["dependency_tags"],
        "claim_flags": ledger["claim_flags"],
        "result": ledger["summary"],
        "artifact": {"path": rel(LEDGER), "sha256": sha(LEDGER)},
        "imports": ledger["source"],
        "does_not_establish": ledger["does_not_establish"],
    }
    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    REPORT.write_text(
        "# Axial QNM projective Evans lifted-phase ledger v1\n\n"
        "Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.\n\n"
        "All 172 accepted segments through the exact boundary prefix "
        "`135/512` admit certified rational separating half-planes and "
        "argument sectors narrower than `pi`. Consecutive sectors overlap, "
        "so they define one continuous lifted argument branch on the "
        "prefix. The partial argument increment is enclosed by "
        f"`[{ledger['summary']['partial_argument_increment_enclosure']['lower']}, "
        f"{ledger['summary']['partial_argument_increment_enclosure']['upper']}]` "
        "radians. This is not a winding number: the contour remains open, "
        "and root-count, QNM, Smith and EP2 flags remain false.\n"
    )
    commands = [
        [
            "python3",
            "-m",
            "py_compile",
            rel(HERE / "produce.py"),
            rel(HERE / "verify.py"),
            rel(HERE / "test_phase_ledger.py"),
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
        ["python3", "-m", "unittest", f"{MODULE}.test_phase_ledger"],
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
                    "phase3-axial-qnm-projective-evans-"
                    "phase-ledger-receipt-v1"
                ),
                "elapsed_seconds": time.monotonic() - started,
                "checks": checks,
                "input_sha256": {
                    key: value["sha256"]
                    for key, value in ledger["source"].items()
                },
                "output_sha256": {
                    "ledger": sha(LEDGER),
                    "certificate": sha(CERTIFICATE),
                    "report": sha(REPORT),
                },
                "higher_tiers_not_run": (
                    "The contour is not closed and no theorem, QNM, Smith "
                    "or EP2 claim is promoted."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if any(check["returncode"] for check in checks):
        raise SystemExit("one or more phase-ledger checks failed")
    print(CERTIFICATE)


if __name__ == "__main__":
    main()
