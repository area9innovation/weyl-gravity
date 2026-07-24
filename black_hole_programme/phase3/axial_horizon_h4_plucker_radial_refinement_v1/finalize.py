#!/usr/bin/env python3
"""Write the human report, machine certificate, and scoped receipt."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from . import produce


def artifact_hashes() -> dict[str, str]:
    excluded = {"certificate.json", "receipt.json"}
    return {
        str(path.relative_to(produce.HERE)): produce.sha256(path)
        for path in sorted(produce.HERE.rglob("*"))
        if path.is_file()
        and path.name not in excluded
        and "__pycache__" not in path.parts
    }


def physical_panel(entry: dict) -> dict[str, str]:
    shell_lo = Fraction(1, 262144)
    width = Fraction(entry["radial_panel_width"])
    panel = entry["refusal"]["panel"]
    return {
        "left": str(shell_lo + panel * width),
        "right": str(shell_lo + (panel + 1) * width),
    }


def write_report(manifest: dict) -> None:
    rows = []
    for attempt in manifest["attempts"]:
        for child in attempt["children"]:
            panel = physical_panel(child)
            defect = child["defect"]
            rows.append(
                f"| {attempt['factor']}x | {child['child_index']} | "
                f"`{child['frequency_cell'][0]}..{child['frequency_cell'][1]}` "
                f"| `{child['radial_panel_width']}` | "
                f"{child['refusal']['panel']} | "
                f"`[{defect['lo']}, {defect['hi']}]` | "
                f"`{defect['interval_width']}` | "
                f"`{panel['left']}..{panel['right']}` |"
            )
    report = f"""# H4 shell-4/segment-3 radial refinement

## Scope

This bounded successor preserves the exact q00 half-cell split and the
certified shell-4/segment-2 boundary state.  Only shell 4, segment 3 is
re-panelled: first 64 panels (2x), then 128 panels (4x) because the 2x
cover refused.  Each panel tries an existing raw Pluecker coordinate first
and falls back to the existing midpoint-Hermitian functional only after a
typed code-32 refusal.

The independent verifier requires all 19 preceding segment heartbeats to
match the upstream replay byte for byte.

## Result

Neither refinement certifies a nonzero witness on both frequency halves.
All four attempts stop at the same physical left boundary
`725/134217728`: panel 213 at 2x and panel 426 at 4x.  The 4x interval is
narrower radially, but the correlated functional still strictly straddles
zero.

| depth | child | frequency cell | radial width | refusal panel | functional enclosure | enclosure width | refused radial panel |
|---:|---:|---|---|---:|---|---:|---|
{chr(10).join(rows)}

## Interpretation

This is a certified conditioning obstruction, not a rank-loss theorem.
Radial subdivision by factors two and four does not resolve the q00
shell-4/segment-3 chart with the current interval-Taylor remainder model.
The nearly unchanged functional widths show that panel size is no longer
the dominant enclosure error at the common refusal location.

The result does not establish transport beyond this boundary, a complete
horizon map, canonical endpoint amplitudes, or a scattering theorem.
"""
    produce.REPORT.write_text(report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-ms", type=int, default=0)
    parser.add_argument("--tests-ms", type=int, default=0)
    args = parser.parse_args()
    manifest = json.loads(produce.MANIFEST.read_text())
    write_report(manifest)
    certificate = {
        "schema": (
            "phase3-axial-h4-plucker-radial-refinement-certificate-v1"
        ),
        "status": manifest["status"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "upstream_certificate_sha256": (
            produce.EXPECTED_UPSTREAM_CERTIFICATE_SHA256
        ),
        "upstream_manifest_sha256": (
            produce.EXPECTED_UPSTREAM_MANIFEST_SHA256
        ),
        "result": {
            "target": {"shell": 4, "segment": 3},
            "factors": manifest["scope"]["factors_in_order"],
            "decisive_factor": manifest["decisive_factor"],
            "attempts": manifest["attempts"],
            "common_refusal_left_boundary": "725/134217728",
            "rank_loss_established": False,
        },
        "interpretation": manifest["interpretation"],
        "does_not_establish": manifest["does_not_establish"],
        "hashes": artifact_hashes(),
    }
    produce.CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    run_elapsed = sum(
        child["elapsed_milliseconds"]
        for attempt in manifest["attempts"]
        for child in attempt["children"]
    )
    receipt = {
        "schema": (
            "phase3-axial-h4-plucker-radial-refinement-receipt-v1"
        ),
        "certificate_sha256": produce.sha256(produce.CERTIFICATE),
        "commands": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_radial_refinement_v1."
                    "run_refinement"
                ),
                "status": "PASS_EXPECTED_TYPED_OBSTRUCTION",
                "elapsed_milliseconds": run_elapsed,
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_radial_refinement_v1.verify"
                ),
                "status": "PASS" if args.verify_ms else "PENDING",
                "elapsed_milliseconds": args.verify_ms,
            },
            {
                "command": (
                    "python3 -m unittest black_hole_programme.phase3."
                    "axial_horizon_h4_plucker_radial_refinement_v1."
                    "test_radial_refinement"
                ),
                "status": "PASS" if args.tests_ms else "PENDING",
                "elapsed_milliseconds": args.tests_ms,
            },
        ],
        "tiers": {
            "tier0": "source parse, exact artifact hashes, scoped diff check",
            "tier1": "independent verifier and mutation tests",
            "tier2": (
                "not run: no promoted operator, schema, or downstream "
                "certificate input changed"
            ),
            "tier3": (
                "not run: bounded negative experiment, not a freeze or "
                "theorem promotion"
            ),
        },
    }
    produce.RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(produce.sha256(produce.CERTIFICATE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
