#!/usr/bin/env python3
"""Verify exact curved-operator inputs and the fail-closed globalization gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator import CurvedOperatorIdentityStatus


CERTIFICATE_DIR = ROOT / "covariant_completion" / "certificates"


def _write(name: str, payload: dict[str, object]) -> None:
    path = CERTIFICATE_DIR / name
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--claim-curved-operator-identity", action="store_true")
    args = parser.parse_args()

    status = CurvedOperatorIdentityStatus.build()
    certificate = status.certificate()

    if args.claim_curved_operator_identity:
        if not status.complete:
            raise SystemExit(
                "REFUSED: the exact covariant action, curved gauge map, and derivative "
                "normal form are implemented, but the expanded curved Hessian/companion, "
                "formal-adjoint defects, and exhaustive lower-jet coverage remain open"
            )

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        _write("curved_auxiliary_action_definition.json", status.action.certificate())
        _write("curved_derivative_normal_form.json", status.normal_form.certificate())
        _write("curved_globalization.json", status.globalization.certificate())
        _write("curved_operator_identity_status.json", certificate)

    if args.guards:
        if status.complete:
            raise AssertionError("curved operator identity closed without its jet proof")
        if status.globalization.complete:
            raise AssertionError("globalization ledger closed without coefficient tables")
        if not certificate["exact_inputs_now"]["linearized_curved_gauge_map"]:
            raise AssertionError("the exact curved gauge-map input regressed")
        if certificate["promotion_criteria"]["globalization_coverage"] != "incomplete":
            raise AssertionError("globalization guard regressed")
        if certificate["promotion_flags"]["all_degree_wave_symbol_defects_zero"] is not True:
            raise AssertionError("wave-symbol theorem regressed")
        if len(certificate["blocking_criteria"]) != 8:
            raise AssertionError("the curved A5 blocker inventory changed unexpectedly")
        print("CURVED OPERATOR WORKSTREAM GUARDS: 6/6 PASS")

    print("CURVED OPERATOR WORKSTREAM: ALL IMPLEMENTED CHECKS PASS")


if __name__ == "__main__":
    main()
