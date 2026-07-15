#!/usr/bin/env python3
"""Verify the scoped endpoint no-go for a strict rank-14 cone contraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_strict_local_contraction_no_go import (
    Rank14StrictLocalContractionNoGo,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_strict_local_contraction_no_go.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()

    certificate = Rank14StrictLocalContractionNoGo.build().certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    endpoint = certificate["endpoint_audit"]
    obstruction = certificate["strict_contraction_obstruction"]
    surviving = certificate["surviving_green_witness_route"]
    checks = {
        "gauge_rank_obstruction": endpoint["K_rank"] == 5
        and endpoint["K_kernel_dimension"] == 4,
        "identity_rank_obstruction": endpoint["N_rank"] == 12
        and endpoint["N_left_null_dimension"] == 2,
        "exact_kernel_witnesses": endpoint["exact_witnesses"][
            "K_times_kernel"
        ]
        == "zero"
        and endpoint["exact_witnesses"]["left_null_transpose_times_N"]
        == "zero",
        "strict_identity_contraction_rejected": not obstruction[
            "polynomial_support_local_DH_plus_HD_equals_identity_possible"
        ],
        "green_factor_route_preserved": not surviving[
            "DH_plus_HD_equals_P_cone_ruled_out"
        ],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "RANK-14 STRICT LOCAL CONTRACTION NO-GO: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
