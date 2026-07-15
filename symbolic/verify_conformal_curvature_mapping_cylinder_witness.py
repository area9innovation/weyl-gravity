#!/usr/bin/env python3
"""Verify the coefficientwise canonical curvature-cylinder witness audit."""

from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.curvature_mapping_cylinder_witness import (
    CurvatureMappingCylinderWitness,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_curvature_mapping_cylinder_witness.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate {name} is not an object")
    return value


def _rejects(
    substitution: dict[str, object],
    curvature: dict[str, object],
    auxiliary: dict[str, object],
    no_go: dict[str, object],
) -> bool:
    try:
        CurvatureMappingCylinderWitness.build().certificate(
            substitution_certificate=substitution,
            curvature_witness_certificate=curvature,
            auxiliary_witness_certificate=auxiliary,
            scalar_no_go_certificate=no_go,
        )
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    substitution = _load("curved_curvature_mapping_cylinder_substitution.json")
    curvature = _load("curved_weyl_cotton_block_green_witness.json")
    auxiliary = _load("curved_witness_identity.json")
    no_go = _load("curved_scalar_wave_no_go.json")
    witness = CurvatureMappingCylinderWitness.build()
    certificate = witness.certificate(
        substitution_certificate=substitution,
        curvature_witness_certificate=curvature,
        auxiliary_witness_certificate=auxiliary,
        scalar_no_go_certificate=no_go,
    )
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    checks = {
        "degree_minus_one": certificate["exact_identities"][
            "W_has_degree_minus_one"
        ],
        "QW_identity": certificate["exact_identities"][
            "P_prol_equals_QW_plus_WQ"
        ],
        "QP_chain_commutation": certificate["exact_identities"][
            "Q_prol_P_prol_equals_P_prol_Q_prol"
        ],
        "canonical_diagonalization": certificate["exact_identities"][
            "P_prol_equals_S_Psplit_Sinverse"
        ],
        "split_diagonal": certificate["exact_identities"][
            "split_off_diagonal_blocks"
        ] == 0,
        "fourteen_green_blocks": certificate["certified_green_diagonal_blocks"]
        == 14,
        "two_open_blocks": certificate["open_green_diagonal_blocks"] == 2,
        "offdiagonal_limit_explicit": certificate[
            "design_constraint_for_next_witness"
        ]["block_diagonal_Q_implies_offdiagonal_W_cannot_change_diagonal_P"],
        "triangular_shortcut_rejected": not certificate[
            "design_constraint_for_next_witness"
        ]["lower_triangular_relative_terms_alone_suffice"],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        bad_substitution = deepcopy(substitution)
        bad_substitution["coefficientwise_complete_prolonged_Q"] = False
        bad_curvature = deepcopy(curvature)
        bad_curvature["exact_block_identities"]["P_equals_QW_plus_WQ"] = False
        bad_auxiliary = deepcopy(auxiliary)
        bad_auxiliary["QW_plus_WQ_minus_P"] = "nonzero"
        bad_no_go = deepcopy(no_go)
        bad_no_go["curved_scalar_wave_no_go"] = False
        checks.update(
            {
                "incomplete_Q_rejected": _rejects(
                    bad_substitution, curvature, auxiliary, no_go
                ),
                "broken_curvature_witness_rejected": _rejects(
                    substitution, bad_curvature, auxiliary, no_go
                ),
                "broken_auxiliary_witness_rejected": _rejects(
                    substitution, curvature, bad_auxiliary, no_go
                ),
                "missing_no_go_boundary_rejected": _rejects(
                    substitution, curvature, auxiliary, bad_no_go
                ),
            }
        )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "CURVATURE MAPPING-CYLINDER WITNESS GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
