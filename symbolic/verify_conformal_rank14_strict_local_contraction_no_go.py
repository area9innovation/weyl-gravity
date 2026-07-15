#!/usr/bin/env python3
"""Verify the scoped endpoint no-go for a strict rank-14 cone contraction."""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_strict_local_contraction_no_go import (
    Rank14StrictLocalContractionNoGo,
    validate_promotion_boundary,
)

import sympy as sp


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_strict_local_contraction_no_go.json"
)
REES = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_corrected_rees_weights.json"
)


def _rejects(action: object) -> bool:
    try:
        if callable(action):
            action()
        else:
            raise AssertionError("guard action is not callable")
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    rees_certificate = json.loads(REES.read_text(encoding="utf-8"))
    witness = Rank14StrictLocalContractionNoGo.build()
    certificate = witness.certificate(rees_certificate=rees_certificate)
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    endpoint = certificate["endpoint_audit"]
    obstruction = certificate["strict_contraction_obstruction"]
    surviving = certificate["surviving_hybrid_projector_route"]
    checks = {
        "gauge_rank_obstruction": endpoint["K_rank"] == 5
        and endpoint["K_kernel_dimension"] == 4,
        "combined_upper_endpoint_typed": endpoint["combined_N_B_rank"] == 13
        and endpoint["combined_N_B_left_null_dimension"] == 1
        and endpoint["upper_endpoint_has_rank_obstruction"],
        "exact_kernel_witness": endpoint["exact_witnesses"][
            "K_times_kernel"
        ]
        == "zero"
        and endpoint["exact_witnesses"][
            "left_null_transpose_times_combined_N_B"
        ]
        == "zero",
        "strict_identity_contraction_rejected": not obstruction[
            "polynomial_support_local_DH_plus_HD_equals_identity_possible"
        ],
        "hybrid_projector_route_preserved": not surviving[
            "idempotent_P_alg_ruled_out"
        ]
        and not surviving["wave_or_subsidiary_operator_used_as_projector"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        broken_rees = deepcopy(rees_certificate)
        broken_rees["schema"] = "wrong"
        broken_promotion = deepcopy(certificate)
        broken_promotion["prolonged_green_witness"] = True
        checks.update(
            {
                "altered_K_rank_rejected": _rejects(
                    lambda: replace(
                        witness, gauge_endpoint=sp.zeros(24, 9)
                    ).verify()
                ),
                "altered_combined_upper_rank_rejected": _rejects(
                    lambda: replace(
                        witness, upper_endpoint=sp.zeros(14, 49)
                    ).verify()
                ),
                "erased_K_null_witness_rejected": _rejects(
                    lambda: replace(
                        witness, gauge_kernel=sp.zeros(9, 4)
                    ).verify()
                ),
                "erased_combined_upper_null_witness_rejected": _rejects(
                    lambda: replace(
                        witness, upper_left_null=sp.zeros(14, 1)
                    ).verify()
                ),
                "wrong_Rees_input_rejected": _rejects(
                    lambda: witness.certificate(rees_certificate=broken_rees)
                ),
                "premature_Green_promotion_rejected": _rejects(
                    lambda: validate_promotion_boundary(broken_promotion)
                ),
            }
        )
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "RANK-14 STRICT LOCAL CONTRACTION NO-GO: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
