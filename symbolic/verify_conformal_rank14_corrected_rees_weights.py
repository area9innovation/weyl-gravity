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
HELICITY = (
    ROOT / "covariant_completion" / "certificates" / "curved_helicity_two_channel.json"
)
CURVED_CORE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_core_curvature_chain_map.json"
)


def _checks(certificate: dict[str, object]) -> dict[str, bool]:
    weights = certificate["weights"]
    layers = certificate["map_layers"]
    page_layers = certificate["PBW_page_chart_layers"]
    cone = certificate["degree_zero_cone"]
    strata = certificate["causal_strata"]
    decision = certificate["decision"]
    multicomplex = certificate["degree_minus_one_multicomplex"]
    page = certificate["null_spectral_sequence"]
    reps = certificate["null_representative_classification"]
    helicity = certificate["helicity_two_cross_binding"]
    correction = certificate["curved_core_coordinate_correction"]
    return {
        "schema": certificate["schema"]
        == "pure-weyl-rank14-corrected-rees-weights-v2",
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
            item["positive_degree_terms"] == 0 for item in layers.values()
        )
        and all(item["emitted_degrees"][0] == 0 for item in page_layers.values()),
        "expected_layers": {
            name: item["emitted_degrees"] for name, item in layers.items()
        }
        == {
            "K": [0, -1],
            "E": [0, -1, -2],
            "C": [0, -1],
            "T": [0],
            "A": [0, -2],
            "B": [-2],
            "Ewc": [0, -2],
            "N": [0, -2],
        },
        "PBW_page_chart": {
            name: item["emitted_degrees"] for name, item in page_layers.items()
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
        "curved_core_cross_binding": correction["cross_certificate"]
        == "curved_core_curvature_chain_map.json"
        and correction["A_old_minus_page_chart_emitted_degrees"] == [-2]
        and correction["A_old_minus_page_chart_nonzero_entries"] == 15
        and correction["curved_attachment_coefficient_multiindices"] == 15
        and correction["curved_attachment_nonzero_coefficients"] == 149
        and correction["curved_identity_attachment_nonzero_coefficients"] == 4
        and correction["lifted_chain_squares_exact"]
        and correction["full_T_lower_order_bound_certified"],
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
        "degree_minus_one_relation": multicomplex["square_nonzero_entries"]
        == [0, 0, 0]
        and multicomplex["exact"]
        and multicomplex["PBW_degree_minus_two_checked"] == "null induced page only",
        "induced_page": page["E0_cohomology_ranks"] == [0, 4, 8, 4, 0]
        and page["induced_d_minus_one_ranks"] == [0, 2, 2, 0]
        and page["E1_cohomology_ranks"] == [0, 2, 4, 2, 0]
        and page["induced_d_minus_two_D12"]
        == [["1/16", "0"], ["0", "1/8"], ["1", "0"], ["0", "1"]]
        and page["induced_d_minus_two_D23_corrected"]
        == [["0", "1", "0", "-1/8"], ["-4", "0", "1/4", "0"]]
        and page["induced_d_minus_two_ranks"] == [2, 2]
        and page["induced_d_minus_two_composition"] == "zero"
        and page["E2_cohomology_ranks"] == [0, 0, 0, 0, 0]
        and page["Euler_characteristic"] == 0,
        "null_page_contraction": certificate["null_page_contraction"]
        == {
            "h12": [["0", "0", "1", "0"], ["0", "0", "0", "1"]],
            "h23": [["0", "-1/4"], ["1", "0"], ["0", "0"], ["0", "0"]],
            "h12_D12": "I2",
            "D12_h12_plus_h23_D23": "I4",
            "D23_h23": "I2",
            "scope": "finite null PBW page only",
            "polynomial_full_operator_homotopy": False,
        },
        "representative_classification": reps["degree_minus_one"][
            "surviving_f_rank"
        ]
        == 2
        and reps["degree_minus_one"]["surviving_h_rank"] == 0
        and reps["degree_minus_one"]["surviving_v_rank"] == 0
        and reps["degree_minus_one"]["killed_v_rank"] == 2
        and reps["degree_zero"]["curvature_U_rank"] == 2
        and reps["degree_zero"]["paired_equation_E_rank"] == 2
        and reps["degree_zero"]["Weyl_EB_rank"] == 2
        and reps["degree_zero"]["Cotton_rank"] == 0
        and reps["degree_plus_one"]["curvature_equation_Q_rank"] == 2
        and reps["degree_plus_one"]["auxiliary_identity_I_rank"] == 0,
        "helicity_cross_binding": helicity["certificate"]
        == "curved_helicity_two_channel.json"
        and helicity["middle_Weyl_EB_rank"] == 2
        and helicity["target_quotient_dimension"] == 2
        and helicity["induced_quotient_matrix"]
        == [["1/4", "0"], ["0", "1/4"]]
        and helicity["isomorphism"],
        "no_overpromotion": decision["common_integer_Rees_weights_found"]
        and decision["all_terms_filtered_degree_nonpositive"]
        and decision["degree_zero_associated_graded_is_a_complex"]
        and decision["degree_minus_one_multicomplex_relation"]
        and decision["null_E1_page_is_02420"]
        and decision["null_PBW_E2_page_is_exact"]
        and not decision["PBW_degree_minus_two_completed"]
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

    certificate = Rank14CorrectedReesWeights.build().certificate(
        helicity_certificate=json.loads(HELICITY.read_text(encoding="utf-8")),
        curved_core_certificate=json.loads(CURVED_CORE.read_text(encoding="utf-8")),
    )
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
        bad["null_spectral_sequence"]["induced_d_minus_one_ranks"] = [0, 0, 0, 0]
        guards["induced_page_erasure_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["null_spectral_sequence"]["induced_d_minus_two_D23_corrected"][0][3] = "0"
        guards["curved_page_two_correction_rejected"] = not all(
            _checks(bad).values()
        )
        bad = deepcopy(certificate)
        bad["curved_core_coordinate_correction"][
            "A_old_minus_page_chart_nonzero_entries"
        ] = 14
        guards["fifteen_entry_curved_delta_rejected"] = not all(
            _checks(bad).values()
        )
        bad = deepcopy(certificate)
        bad["helicity_two_cross_binding"]["induced_quotient_matrix"] = [
            ["0", "0"],
            ["0", "0"],
        ]
        guards["helicity_cross_binding_rejected"] = not all(_checks(bad).values())
        bad = deepcopy(certificate)
        bad["decision"]["PBW_degree_minus_two_completed"] = True
        guards["premature_full_PBW_minus_two_rejected"] = not all(
            _checks(bad).values()
        )
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
