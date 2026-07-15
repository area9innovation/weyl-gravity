#!/usr/bin/env python3
"""Verify the conditional mixed-order square-root Green promotion theorem."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.mixed_order_green_promotion import (
    MixedOrderGreenPromotion,
    coefficient_certificate_passes,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_mixed_order_green_promotion.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not an object")
    return value


def _synthetic_complete_coefficient_certificate() -> dict[str, object]:
    """Test fixture only; never emitted as a mathematical certificate."""

    return {
        "schema": "pure-weyl-mixed-order-factorization-v1",
        "exact_factorizations": {
            "D_P_equals_Lminus_Lplus": True,
            "P_D_equals_Rminus_Rplus": True,
            "global_coefficientwise": True,
        },
        "green_factors": {
            "Lminus_green_hyperbolic": True,
            "Lplus_green_hyperbolic": True,
            "Rminus_green_hyperbolic": True,
            "Rplus_green_hyperbolic": True,
        },
        "support": {
            "D_finite_order_differential": True,
            "all_factor_Green_operators_metric_causal": True,
        },
        "formal_adjoint_completion": {
            "all_bundle_pairings_nondegenerate": True,
            "factor_adjoint_relations_exact": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    witness = _load("curved_curvature_mapping_cylinder_witness.json")
    bridge = _load("curved_prolonged_green_bridge.json")
    promotion = MixedOrderGreenPromotion(witness, bridge)
    certificate = promotion.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    construction = certificate["exact_formal_construction"]
    insertion = certificate["sixteen_block_insertion"]
    gate = certificate["coefficient_gate"]
    checks = {
        "right_inverse": construction["right_inverse_defect"] == 0,
        "left_inverse": construction["left_inverse_defect"] == 0,
        "formula_equality": construction["formula_equality_defect"] == 0,
        "two_sided": construction["two_sided"],
        "causal_support": certificate["causal_support"][
            "same_sided_factor_composition"
        ],
        "adjoint_order": certificate["formal_adjoint_handling"][
            "operator_order_reversal_checked"
        ],
        "sixteen_block_insertion": insertion[
            "conditional_all_16_blocks_two_sided_and_causal"
        ],
        "actual_coefficient_gate_closed": not gate["certificate_supplied"]
        and not gate["certificate_passes"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        synthetic = _synthetic_complete_coefficient_certificate()
        checks["complete_fixture_recognized"] = coefficient_certificate_passes(
            synthetic
        )
        for section, key in (
            ("exact_factorizations", "D_P_equals_Lminus_Lplus"),
            ("exact_factorizations", "P_D_equals_Rminus_Rplus"),
            ("green_factors", "Lminus_green_hyperbolic"),
            ("support", "D_finite_order_differential"),
            ("formal_adjoint_completion", "factor_adjoint_relations_exact"),
        ):
            broken = deepcopy(synthetic)
            broken[section][key] = False
            checks[f"missing_{key}_rejected"] = not coefficient_certificate_passes(
                broken
            )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "MIXED-ORDER GREEN PROMOTION GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
