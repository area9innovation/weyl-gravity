#!/usr/bin/env python3
"""Verify the pair-(1,6) formal-adjoint signs and coverage boundary."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.expanded_relative_witness_adjoint_sign_audit import (
    ExpandedRelativeWitnessAdjointSignAudit,
)


OUTPUT = ROOT / "covariant_completion/certificates/curved_expanded_relative_witness_adjoint_sign.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-arbitrary-covector", action="store_true")
    parser.add_argument("--claim-green", action="store_true")
    parser.add_argument("--promote-flag", action="store_true")
    args = parser.parse_args()
    if args.claim_arbitrary_covector or args.claim_green or args.promote_flag:
        raise SystemExit(
            "REFUSED: R6sharp has only its temporal coefficient and Dscalar has "
            "no cyclic all-row lift; the audit proves no arbitrary-covector or Green claim"
        )

    audit = ExpandedRelativeWitnessAdjointSignAudit.build()
    certificate = audit.certificate()
    signs = certificate["formal_adjoint_convention"]
    schur = certificate["corrected_temporal_Schur_calculation"]
    coverage = certificate["operator_coverage_boundary"]
    checks = {
        "first_order_adjoint_sign": signs["NcurvSharp_coefficients_equal_minus_transpose"],
        "corrected_BC": schur["BC"] == "-Pi_vector_gauge",
        "corrected_BDinvC": schur["B_Dinverse_C"] == "+Pi_vector_gauge",
        "field_schur_exact": schur["field_Schur_rank"] == 24
        and schur["field_Schur_determinant"] == 1,
        "temporal_rank116": schur["complete_rank"] == 116
        and schur["complete_determinant"] == 1,
        "R6_spatial_missing": coverage["R6sharp_missing_spatial_coefficients"] == 3
        and not coverage["R6sharp_covariant_formula_constructed"],
        "scalar_lift_missing": not coverage["Dscalar_cyclic_witness_lift_constructed"],
        "fail_closed": certificate["fail_closed"]
        and not certificate["status_flags_promoted"],
    }
    if args.guards:
        broken_sharps = list(audit.n_sharp_principal_coefficients)
        broken_sharps[0] = -broken_sharps[0]
        broken = replace(audit, n_sharp_principal_coefficients=tuple(broken_sharps))
        try:
            broken.verify()
        except AssertionError:
            checks["wrong_Nsharp_sign_rejected"] = True
        else:
            checks["wrong_Nsharp_sign_rejected"] = False
        broken_symbol = sp.Matrix(audit.complete_temporal_symbol)
        broken_symbol[0, 0] = 0
        broken = replace(audit, complete_temporal_symbol=broken_symbol)
        try:
            broken.verify()
        except AssertionError:
            checks["temporal_mutation_rejected"] = True
        else:
            checks["temporal_mutation_rejected"] = False

    if not all(checks.values()):
        raise AssertionError({key: value for key, value in checks.items() if not value})
    if args.emit:
        OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    if args.emit:
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
