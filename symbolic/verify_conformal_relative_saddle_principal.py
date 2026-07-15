#!/usr/bin/env python3
"""Verify the principal obstruction for the smallest local saddle ansatz."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.relative_saddle_principal import (
    RelativeSaddlePrincipalDiagnostic,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_relative_saddle_principal.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not an object")
    return value


def _rejects(
    equation: dict[str, object],
    hyperbolic: dict[str, object],
    saddle: dict[str, object],
) -> bool:
    try:
        RelativeSaddlePrincipalDiagnostic.build().certificate(
            equation_chain_certificate=equation,
            hyperbolic_certificate=hyperbolic,
            saddle_certificate=saddle,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    equation = _load("curved_curvature_auxiliary_chain_map.json")
    hyperbolic = _load("curved_weyl_cotton_hyperbolic.json")
    saddle = _load("curved_relative_saddle_witness.json")
    diagnostic = RelativeSaddlePrincipalDiagnostic.build()
    certificate = diagnostic.certificate(
        equation_chain_certificate=equation,
        hyperbolic_certificate=hyperbolic,
        saddle_certificate=saddle,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    weights = certificate["balanced_Douglis_weights"]
    temporal = certificate["timelike_principal_test"]
    characteristic = certificate["characteristic_and_symmetrizer"]
    checks = {
        "local_RS_orders": certificate["instantiated_local_maps"]["R_order"] == 2
        and certificate["instantiated_local_maps"]["S_order"] == 2,
        "source_chain_relation": certificate["instantiated_local_maps"][
            "source_compatibility_relation"
        ] == "A_F Eaux=L_26 T_state",
        "all_rows_retained": certificate["instantiated_local_maps"][
            "all_constraint_and_identity_rows_retained"
        ],
        "balanced_weights": weights["row_weights"] == {"M": 2, "U": 1}
        and weights["column_weights"] == {"M": 3, "U": 0},
        "A_drops_from_principal": weights[
            "A_absent_from_balanced_principal_symbol"
        ],
        "timelike_E_rank15": temporal["Eaux_principal_rank"] == 15,
        "complete_dimension116": temporal["complete_degree_zero_dimension"] == 116,
        "complete_rank_at_most107": temporal[
            "complete_degree_zero_rank_upper_bound"
        ] == 107,
        "rank_defect9": temporal["timelike_rank_defect_lower_bound"] == 9,
        "timelike_singular": not temporal["invertible"],
        "temporal_characteristic_leading_coefficient_zero": characteristic[
            "Douglis_characteristic_temporal_leading_coefficient"
        ] == "zero",
        "no_positive_symmetrizer": not characteristic[
            "positive_temporal_symmetrizer_exists"
        ],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_equation = deepcopy(equation)
        bad_equation["first_chain_relation_exact"] = False
        bad_hyperbolic = deepcopy(hyperbolic)
        bad_hyperbolic["evolution_symmetrizer_positive"] = False
        bad_saddle = deepcopy(saddle)
        bad_saddle["smallest_physical_saddle_candidate"]["relative_pairs"] = [3, 5]
        checks.update(
            {
                "broken_chain_relation_rejected": _rejects(
                    bad_equation, hyperbolic, saddle
                ),
                "nonpositive_J_rejected": _rejects(
                    equation, bad_hyperbolic, saddle
                ),
                "wrong_relative_pairs_rejected": _rejects(
                    equation, hyperbolic, bad_saddle
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "RELATIVE SADDLE PRINCIPAL GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
