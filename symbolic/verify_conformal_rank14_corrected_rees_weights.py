#!/usr/bin/env python3
"""Verify the corrected common-Rees rank-14 cone."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_corrected_rees_weights import (  # noqa: E402
    Rank14CorrectedReesWeights,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_rank14_corrected_rees_weights.json"
)


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    weights = certificate["weights"]
    layers = certificate["map_layers"]
    cone = certificate["degree_zero_cone"]
    strata = certificate["causal_strata"]
    decision = certificate["decision"]
    return {
        "algorithmic_integer_solution": certificate["algorithm"]["type"]
        == "integer longest paths in the acyclic map diagram"
        and certificate["algorithm"]["normalization"]
        == "all G[9] weights fixed to zero"
        and not certificate["algorithm"]["hand_fitted"],
        "weights": weights
        == {
            "G": [0] * 9,
            "M": [1] * 24,
            "E": [3] * 24,
            "I": [4] * 9,
            "U": [3] * 10 + [4] * 16,
            "Q": [4] * 10 + [5] * 16 + [4] * 6 + [5] * 8,
            "J": [5] * 6 + [6] * 8,
        },
        "all_maps_filtered": all(
            item["positive_degree_terms"] == 0
            and item["emitted_degrees"][0] == 0
            for item in layers.values()
        ),
        "expected_layers": {
            name: item["emitted_degrees"] for name, item in layers.items()
        }
        == {
            "K": [0, -1],
            "E": [0, -1, -2],
            "C": [0, -1],
            "T": [0],
            "A": [0, -2],
            "B": [0, -1, -2],
            "Ewc": [0, -2],
            "N": [0, -2],
        },
        "corrected_retract_maps": certificate["corrected_retract_maps"]
        == {
            "Tnew": "T_core p_field; degree-zero unchanged",
            "Anew": "A_core p_equation",
            "Bnew": "B_core p_identity with derivative Weyl column",
            "full_T_lower_order_bound_certified": True,
        },
        "complex_before_cohomology": cone["square_nonzero_entries"] == [0, 0, 0]
        and cone["is_complex"]
        and cone["cohomology_computed_after_d2"],
        "off_null_acyclic": all(
            item["differential_ranks"] == [9, 15, 35, 14]
            and item["square_ranks"] == [0, 0, 0]
            and item["cohomology_ranks"] == [0, 0, 0, 0, 0]
            for name, item in strata.items()
            if name != "null_(1,1,0,0)"
        ),
        "null_484": strata["null_(1,1,0,0)"]["differential_ranks"]
        == [9, 11, 31, 14]
        and strata["null_(1,1,0,0)"]["square_ranks"] == [0, 0, 0]
        and strata["null_(1,1,0,0)"]["cohomology_ranks"] == [0, 4, 8, 4, 0],
        "no_overpromotion": decision["common_integer_Rees_weights_found"]
        and decision["all_terms_filtered_degree_nonpositive"]
        and decision["degree_zero_associated_graded_is_a_complex"]
        and not decision["support_local_contraction_constructed"]
        and not decision["prolonged_green_witness"]
        and not decision["causal_green_homotopy"]
        and not decision["rank14_SDR_constructed"]
        and certificate["status_flags_promoted"] == [],
        "fail_closed": certificate["fail_closed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    certificate = Rank14CorrectedReesWeights.build().certificate()
    checks = _checks(certificate)
    if not all(checks.values()):
        raise AssertionError(
            "corrected Rees verifier failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )

    guards: dict[str, bool] = {}
    if args.guards:
        bad = deepcopy(certificate)
        bad["map_layers"]["B"]["positive_degree_terms"] = 1
        guards["positive_B_degree_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["degree_zero_cone"]["square_nonzero_entries"] = [0, 0, 1]
        guards["cohomology_before_d2_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["causal_strata"]["null_(1,1,0,0)"]["cohomology_ranks"] = [
            0,
            0,
            0,
            0,
            0,
        ]
        guards["null_module_erasure_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["decision"]["causal_green_homotopy"] = True
        guards["premature_green_promotion_rejected"] = not all(
            _checks(bad).values()
        )
        if not all(guards.values()):
            raise AssertionError("corrected Rees mutation guard failed")

    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "certificate": str(OUTPUT.relative_to(ROOT)),
                "checks": checks,
                "guards": guards,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
