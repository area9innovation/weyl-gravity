#!/usr/bin/env python3
"""Verify the composite algebraic projector on the prolonged BV complex."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.prolonged_hybrid_algebraic_projector import (
    ProlongedHybridAlgebraicProjector,
    validate_promotion_boundary,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_prolonged_hybrid_algebraic_projector.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not an object")
    return value


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

    auxiliary = _load("curved_auxiliary_canonical_split.json")
    mapping = _load("curved_curvature_mapping_cylinder_substitution.json")
    theorem = ProlongedHybridAlgebraicProjector.build()
    certificate = theorem.certificate(
        curved_auxiliary_certificate=auxiliary,
        mapping_certificate=mapping,
        reverify=False,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    component = certificate["component_projectors"]
    composite = certificate["composite_SDR"]
    endpoint = certificate["retained_endpoint"]
    checks = {
        "auxiliary_projectors": component["auxiliary"][
            "QH_plus_HQ_minus_P_alg"
        ]
        == "zero"
        and component["auxiliary"]["P_alg_squared_minus_P_alg"] == "zero"
        and component["auxiliary"]["P_end_squared_minus_P_end"] == "zero",
        "mapping_projectors": component["mapping_cylinder"][
            "QH_plus_HQ_minus_P_alg"
        ]
        == "zero"
        and component["mapping_cylinder"]["P_alg_squared_minus_P_alg"]
        == "zero"
        and component["mapping_cylinder"]["P_end_squared_minus_P_end"]
        == "zero",
        "cyclicity": component["auxiliary"]["H_alg_cyclicity_defect"] == 0
        and component["mapping_cylinder"]["H_alg_cyclicity_defect"] == 0
        and composite["cyclic_and_formally_self_adjoint"],
        "composite_idempotents": composite["P_alg_idempotent"]
        and composite["P_end_idempotent"]
        and composite["P_alg_P_end"] == "zero",
        "chain_commutation": composite["D_P_alg_equals_P_alg_D"]
        and composite["D_P_end_equals_P_end_D"],
        "support_local": composite["support_local"]
        and not composite["inverse_Laplacian_or_curl"]
        and not composite["spectral_or_helicity_projector"],
        "curvature_graph_retained": endpoint[
            "curvature_variables_retained_as_local_graph_values"
        ]
        and not endpoint["curvature_to_metric_inverse_used"],
        "green_boundary_honest": not endpoint["separate_W_end_constructed"]
        and not endpoint["separate_G_end_constructed"]
        and not endpoint["ruled_out_fallback_used"]
        and "physical triangular biwave extension"
        in endpoint["required_analytic_blocks"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_auxiliary = deepcopy(auxiliary)
        bad_auxiliary["curved_deformation_retract"] = False
        bad_mapping = deepcopy(mapping)
        bad_mapping["kernel"]["odd_BV_cyclicity_defect"] = 1
        bad_promotion = deepcopy(certificate)
        bad_promotion["prolonged_green_witness"] = True
        checks.update(
            {
                "missing_auxiliary_SDR_rejected": _rejects(
                    lambda: theorem.certificate(
                        curved_auxiliary_certificate=bad_auxiliary,
                        mapping_certificate=mapping,
                        reverify=False,
                    )
                ),
                "noncyclic_mapping_SDR_rejected": _rejects(
                    lambda: theorem.certificate(
                        curved_auxiliary_certificate=auxiliary,
                        mapping_certificate=bad_mapping,
                        reverify=False,
                    )
                ),
                "premature_Green_promotion_rejected": _rejects(
                    lambda: validate_promotion_boundary(bad_promotion)
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "PROLONGED HYBRID ALGEBRAIC PROJECTOR: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
