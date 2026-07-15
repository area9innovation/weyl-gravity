#!/usr/bin/env python3
"""Verify the minimal 16-parameter alternative-incidence no-go."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_alternative_family_no_go import (  # noqa: E402
    AlternativeFamilyNoGo,
    PARAMETER_COUNT,
)


OUTPUT = ROOT / (
    "covariant_completion/certificates/"
    "curved_expanded_relative_witness_alternative_family_no_go.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-complete-family-no-go", action="store_true")
    parser.add_argument("--claim-strong-hyperbolicity", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    args = parser.parse_args()
    if (
        args.claim_complete_family_no_go
        or args.claim_strong_hyperbolicity
        or args.claim_green
    ):
        raise SystemExit(
            "REFUSED: this certificate closes only the deterministic "
            "16-parameter subfamily minimally spanning the known sensitivity "
            "image; it does not close either raw 122-parameter incidence or "
            "construct a Green witness"
        )

    result = AlternativeFamilyNoGo.build()
    certificate = result.certificate()
    pair17 = certificate["pair_1_plus_7"]
    pair27 = certificate["pair_2_plus_7"]
    conclusion = certificate["screening_conclusion"]
    selected = certificate["minimal_sensitivity_surjection"]
    checks = {
        "minimal_slice_has_16_parameters": (
            selected["selected_parameter_count"] == PARAMETER_COUNT
        ),
        "minimal_slice_spans_sensitivity": (
            selected["selected_matrix_rank"] == PARAMETER_COUNT
            and selected["minimal_by_rank"]
        ),
        "pair17_zero_valuation_is_40": (
            pair17["universal_zero_root_valuation"] == 40
        ),
        "pair17_kernel_upper_bound_is_33": (
            pair17["uniform_kernel_upper_bound"] == 33
        ),
        "pair17_uniformly_nonsemisimple": (
            not pair17["regular_specializations_semisimple_at_zero"]
            and pair17["defect_lower_bound"] == 7
        ),
        "pair27_zero_valuation_is_48": (
            pair27["universal_zero_root_valuation"] == 48
        ),
        "pair27_kernel_upper_bound_is_47": (
            pair27["uniform_kernel_upper_bound"] == 47
        ),
        "pair27_uniformly_nonsemisimple": (
            not pair27["semisimple_at_zero"]
            and pair27["defect_lower_bound"] == 1
        ),
        "parameter_uniform_no_go": conclusion[
            "parameter_uniform_zero_root_obstruction"
        ],
        "symmetrizer_correctly_skipped": not conclusion[
            "symmetrizer_attempt_warranted"
        ],
        "scope_does_not_overclaim": (
            not conclusion["complete_pair_1_plus_7_family_ruled_out"]
            and not conclusion["complete_pair_2_plus_7_family_ruled_out"]
            and not conclusion["generalized_green_extension_ruled_out"]
        ),
        "no_green_promotion": (
            not certificate["prolonged_green_witness"]
            and not certificate["status_flags_promoted"]
        ),
        "fail_closed": certificate["fail_closed"],
    }

    if args.guards:
        mutated = result.selected_sensitivity.copy()
        mutated[:, 0] = sp.zeros(mutated.rows, 1)
        checks["mutated_sensitivity_basis_rejected"] = (
            mutated.rank() < result.selected_sensitivity.rank()
        )
        checks["valuation_kernel_mismatch_guard"] = (
            result.pair17_zero_valuation
            > 116 - sum(result.pair17_zero_diagonal_ranks)
            and result.pair27_zero_valuation
            > 116 - result.pair27_fixed_row_rank
        )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"alternative family no-go checks failed: {failed}")
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print("=== Expanded relative alternative-family no-go ===")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"certificate: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
