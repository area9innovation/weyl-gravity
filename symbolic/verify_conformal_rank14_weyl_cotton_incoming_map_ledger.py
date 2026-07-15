#!/usr/bin/env python3
"""Verify the typed rank-14 Weyl--Cotton incoming-map ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.rank14_weyl_cotton_incoming_map_ledger import (  # noqa: E402
    Rank14WeylCottonIncomingMapLedger,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
OUTPUT = CERTIFICATES / "curved_rank14_weyl_cotton_incoming_map_ledger.json"


def _load(name: str) -> dict[str, object]:
    value = json.loads((CERTIFICATES / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"certificate is not an object: {name}")
    return value


def _validate_output(value: dict[str, object]) -> None:
    diagnostic = value.get("raw_curvature_compatibility_diagnostic")
    target = value.get("correct_principal_target")
    if not isinstance(diagnostic, dict) or not isinstance(target, dict):
        raise AssertionError("ledger sections are missing")
    if diagnostic.get("raw_map_may_instantiate_compatible_source_inclusion"):
        raise AssertionError("raw incompatible map was promoted to a source inclusion")
    if target.get("A_F_is_independently_R_src_closed"):
        raise AssertionError("the constraint-source component A_C was dropped")
    if target.get("principal_H7_contraction_certified"):
        raise AssertionError("incoming-map ledger overpromoted H7")
    if value.get("prolonged_green_witness"):
        raise AssertionError("incoming-map ledger overpromoted Green witness")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    ledger = Rank14WeylCottonIncomingMapLedger.build()
    certificate = ledger.certificate(
        symbol_certificate=_load("curved_rank14_weyl_cotton_symbol_audit.json"),
        equation_certificate=_load("curved_curvature_auxiliary_chain_map.json"),
        identity_certificate=_load("curved_curvature_identity_chain_map.json"),
        substitution_certificate=_load(
            "curved_curvature_mapping_cylinder_substitution.json"
        ),
    )
    _validate_output(certificate)
    if args.guards:
        bad = json.loads(json.dumps(certificate))
        bad["raw_curvature_compatibility_diagnostic"][
            "raw_map_may_instantiate_compatible_source_inclusion"
        ] = True
        try:
            _validate_output(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("raw-map promotion mutation was accepted")
        bad = json.loads(json.dumps(certificate))
        bad["correct_principal_target"]["A_F_is_independently_R_src_closed"] = True
        try:
            _validate_output(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError("A_C deletion mutation was accepted")
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "rank14 incoming-map ledger: "
        f"E={certificate['typed_curvature_complex']['sample_symbol_ranks']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
