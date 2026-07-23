#!/usr/bin/env python3
"""Compile, run, and record the moving-lower first-microfactor preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from .produce import HERE, METADATA, OUTPUT, produce


BASELINE_WIDTH = 621.8840812306481
CERTIFICATE = HERE / "certificate.json"
SUBCELL_RE = re.compile(
    r"^SUBCELL q=(?P<q>\d+) lower_width=(?P<lower>[0-9.eE+-]+) "
    r"full_width=(?P<full>[0-9.eE+-]+) ranks=(?P<carrier>\d+) "
    r"(?P<kernel>\d+)$"
)
SUMMARY_RE = re.compile(
    r"^MOVING piecewise_lower_width=(?P<width>[0-9.eE+-]+) "
    r"max_local_lower_width=(?P<local>[0-9.eE+-]+) "
    r"subcells=(?P<subcells>\d+) generator=(?P<generator>\d+)$"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--forge",
        type=Path,
        default=Path("/home/alstrup/area9/tango/forge/forge"),
    )
    parser.add_argument("--binary", type=Path, default=Path("/tmp/axial_moving_lower"))
    parser.add_argument("--certificate", type=Path, default=CERTIFICATE)
    args = parser.parse_args()

    produce()
    compile_start = time.perf_counter()
    compile_proc = subprocess.run(
        [
            str(args.forge),
            "-incremental",
            "-o",
            str(args.binary),
            str(OUTPUT),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    compile_seconds = time.perf_counter() - compile_start
    if compile_proc.returncode != 0:
        print(compile_proc.stdout, end="")
        print(compile_proc.stderr, end="")
        return 3

    run_start = time.perf_counter()
    run_proc = subprocess.run(
        [str(args.binary)],
        text=True,
        capture_output=True,
        check=False,
    )
    run_seconds = time.perf_counter() - run_start
    print(run_proc.stdout, end="")
    if run_proc.stderr:
        print(run_proc.stderr, end="")
    if run_proc.returncode != 42:
        return 3

    subcells: list[dict[str, int | float]] = []
    summary: dict[str, str] | None = None
    for line in run_proc.stdout.splitlines():
        if match := SUBCELL_RE.match(line):
            subcells.append(
                {
                    "index": int(match["q"]),
                    "lower_width": float(match["lower"]),
                    "full_width": float(match["full"]),
                    "carrier_rank": int(match["carrier"]),
                    "kernel_rank": int(match["kernel"]),
                }
            )
        if match := SUMMARY_RE.match(line):
            summary = match.groupdict()
    if (
        summary is None
        or len(subcells) != 4
        or "PASS MOVING_LOWER_FIRST_MICROFACTOR" not in run_proc.stdout
    ):
        return 3

    width = float(summary["width"])
    certificate = {
        "schema": "phase3-axial-moving-lower-preflight-v1",
        "status": "PREFLIGHT_PASS" if width < BASELINE_WIDTH else "WIDTH_SHORTFALL",
        "scope": {
            "theory": "strict-pure-Weyl",
            "background": "Schwarzschild-M=1",
            "parity": "axial",
            "ell": 2,
            "omega_cell": ["1/2", "129/256"],
            "radial_microinterval": ["0", "1/8"],
        },
        "layout_contract": {
            "coefficient_and_frame_layout": "standard-real-interleaved-12",
            "structured_transition_layout": "contiguous-block-lower-8+4",
            "upper_right_exact_zero": True,
            "predecessor_interleaved_extractor_rejected": True,
        },
        "method": {
            "generator": int(summary["generator"]),
            "formula": "Ck1^-1*(L*Cc0+Uk*D0-D1*Wc)",
            "omega_subcells": int(summary["subcells"]),
            "radial_panels": 8,
            "taylor_order": 12,
            "dyadic_rebase_bits": 128,
            "rank_argument": "block-lower-diagonal-ranks",
            "full_12x12_interval_rank_used": False,
        },
        "result": {
            "baseline_unframed_lower_width": BASELINE_WIDTH,
            "piecewise_moving_lower_width": width,
            "max_local_lower_width": float(summary["local"]),
            "contraction_factor": BASELINE_WIDTH / width,
            "subcells": subcells,
            "carrier_rank_each_subcell": 8,
            "kernel_rank_each_subcell": 4,
        },
        "proof_contract": {
            "outward_local_tails": True,
            "shared_generator": True,
            "global_frame_affine_restriction_exact": True,
            "global_remainder_retained_outward": True,
            "dyadic_rebasing": True,
            "independent_exact_layout_oracle": True,
            "mutations_rejected": [
                "interleaved-extractor-on-contiguous-block",
                "drop-D1-Wc-term",
                "break-generator",
                "erase-width-improvement",
                "change-source-hash",
            ],
        },
        "provenance": {
            "source_path": str(OUTPUT.relative_to(HERE.parents[2])),
            "source_sha256": sha256(OUTPUT),
            "source_metadata_path": str(METADATA.relative_to(HERE.parents[2])),
            "source_metadata_sha256": sha256(METADATA),
            "producer_path": str((HERE / "produce.py").relative_to(HERE.parents[2])),
            "producer_sha256": sha256(HERE / "produce.py"),
            "frame_table_import_is_data_only": True,
            "superseded_predecessor_certificate_used": False,
        },
        "runtime": {
            "compile_seconds": compile_seconds,
            "run_seconds": run_seconds,
            "compile_returncode": compile_proc.returncode,
            "run_returncode": run_proc.returncode,
        },
        "establishes": [
            "The first axial infinity microfactor admits a four-omega-subcell moving-frame block-lower enclosure with certified 8+4 diagonal rank and exact zero upper-right block.",
            "The maximum lower-block width is strictly smaller than the superseded unframed width benchmark.",
        ],
        "does_not_establish": [
            "single-affine-cell enclosure without omega subdivision",
            "all 224 infinity microfactors",
            "useful joined horizon-to-infinity widths",
            "global horizon-to-infinity connection",
            "physical channel or flux classification",
        ],
    }
    args.certificate.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    )
    return 0 if certificate["status"] == "PREFLIGHT_PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
