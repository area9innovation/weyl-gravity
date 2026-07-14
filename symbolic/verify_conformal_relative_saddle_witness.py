#!/usr/bin/env python3
"""Verify the minimal two-way auxiliary--curvature saddle diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.relative_saddle_witness import (
    ADJOINT_RELATIVE_PAIRS,
    RelativeSaddleWitnessDiagnostic,
    _cyclic_defect,
    _derived_partner,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_relative_saddle_witness.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    diagnostic = RelativeSaddleWitnessDiagnostic.build()
    certificate = diagnostic.certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))

    classification = certificate["relative_degree_minus_one_classification"]
    candidate = certificate["smallest_physical_saddle_candidate"]
    boundary = certificate["analytic_boundary"]
    checks = {
        "eighteen_entries": classification["allowed_directed_entries"] == 18,
        "nine_adjoint_pairs": classification["odd_cotangent_adjoint_pairs"] == 9,
        "no_single_pair_saddle": classification[
            "no_single_pair_makes_two_way_saddle"
        ],
        "minimal_pair_45": candidate["relative_pairs"] == [4, 5],
        "two_way_field_coupling": candidate["two_way_aux_curvature_coupling"],
        "cotangent_partner": candidate["degree_one_cotangent_partner_forced"],
        "oriented_partner_signs": classification["derived_partner_signs"]
        == [1] * 9,
        "DeltaW_cyclic": candidate["DeltaW_BV_cyclicity_defect"] == 0,
        "schur_factors_exact": certificate["exact_schur_factorization"][
            "finite_block_algebra"
        ],
        "nonlocal_schur_visible": not boundary[
            "Schur_Z_is_local_differential_operator"
        ],
        "first_order_not_claimed": not boundary[
            "first_order_symmetric_hyperbolic_certificate_applies"
        ],
        "no_overpromotion": not certificate["prolonged_green_witness"]
        and not certificate["curvature_causal_green_operators"]
        and not certificate["causal_green_homotopy"],
    }
    if args.guards:
        original = ADJOINT_RELATIVE_PAIRS[4]
        if original != ((1, 7), (15, 2)):
            raise AssertionError("minimal R-pair incidence drifted")
        if diagnostic.single_pair_reciprocal_counts != (0,) * 9:
            raise AssertionError("single-pair negative guard drifted")
        checks["pair_incidence_guard"] = True
        checks["single_pair_negative_guard"] = True
        bad_sign = [row[:] for row in diagnostic.relative_witness]
        bad_sign[15][2] = bad_sign[15][2].scale(-1)
        checks["wrong_Rsharp_sign_rejected"] = any(
            entry != OperatorPolynomial.zero()
            for row in _cyclic_defect(bad_sign, diagnostic.kernel.pairing)
            for entry in row
        )
        bad_partner = [row[:] for row in diagnostic.relative_witness]
        bad_partner[15][2] = OperatorPolynomial.zero()
        bad_partner[14][2] = OperatorPolynomial.atom("Rsharp")
        checks["wrong_Rsharp_partner_rejected"] = any(
            entry != OperatorPolynomial.zero()
            for row in _cyclic_defect(bad_partner, diagnostic.kernel.pairing)
            for entry in row
        )
        reoriented = [row[:] for row in diagnostic.kernel.pairing]
        reoriented[1][2] = reoriented[1][2].scale(-1)
        reoriented[2][1] = reoriented[2][1].scale(-1)
        _, _, reoriented_sign = _derived_partner(reoriented, 1, 7)
        checks["pairing_orientation_changes_partner_sign"] = reoriented_sign == -1

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(
        "RELATIVE SADDLE WITNESS GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
