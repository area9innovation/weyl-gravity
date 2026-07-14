#!/usr/bin/env python3
"""Verify and optionally emit the auxiliary mixed-order symbol certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.auxiliary_prenormal_symbol import (
    AuxiliaryPrenormalSymbol,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_auxiliary_prenormal_symbol.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--claim-mixed-order-green", action="store_true")
    parser.add_argument("--claim-local-triangularization", action="store_true")
    parser.add_argument("--claim-lower-order-factorization", action="store_true")
    parser.add_argument("--drop-helicity-two", action="store_true")
    parser.add_argument("--promote-curved-operator", action="store_true")
    args = parser.parse_args()

    forbidden = {
        "--claim-mixed-order-green": args.claim_mixed_order_green,
        "--claim-local-triangularization": args.claim_local_triangularization,
        "--claim-lower-order-factorization": args.claim_lower_order_factorization,
        "--drop-helicity-two": args.drop_helicity_two,
        "--promote-curved-operator": args.promote_curved_operator,
    }
    requested = [name for name, enabled in forbidden.items() if enabled]
    if requested:
        raise SystemExit(
            "REFUSED: prenormal principal-symbol data cannot justify: "
            + ", ".join(requested)
        )

    certificate = AuxiliaryPrenormalSymbol.build().certificate()
    outcome = certificate["outcome"]
    if outcome["mixed_order_green_realization"]:
        raise AssertionError("the diagnostic inferred a Green realization")
    if outcome["curved_operator_identity_promoted"]:
        raise AssertionError("the diagnostic promoted the top-level operator flag")
    if certificate["lower_order_completion"][
        "lower_order_operator_factorization_proved"
    ]:
        raise AssertionError("the unresolved lower-order operator was inferred")
    if certificate["univariate_smith_ledger"][
        "global_unimodular_transform_constructed"
    ]:
        raise AssertionError("aligned Smith data were globalized into a transform")

    if args.emit:
        CERTIFICATE.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "auxiliary prenormal symbol: PASS "
        "((P2-qI)^2=0; Smith 6 algebraic + 12 wave + 6 biwave; "
        "curved lower-order Green completion remains open)"
    )


if __name__ == "__main__":
    main()
