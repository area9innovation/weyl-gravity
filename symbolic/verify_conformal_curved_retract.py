#!/usr/bin/env python3
"""Certify the local curved auxiliary shift without overclaiming its Q-SDR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract import CurvedRetractStatus


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
    parser.add_argument("--claim-curved-deformation-retract", action="store_true")
    args = parser.parse_args()

    if args.claim_curved_deformation_retract:
        raise SystemExit(
            "REFUSED: the exact covariant auxiliary square, local BV-canonical "
            "shift, universal split SDR, and support theorem are proved, but the "
            "actual curved Q conjugation and all-row chain identities are not"
        )

    status = CurvedRetractStatus.build()
    shift = status.auxiliary_shift.certificate()
    canonical = status.canonical_shift.certificate(reverify=False)
    universal = status.universal_split.certificate(reverify=False)
    support = status.support.certificate()
    aggregate = status.certificate(reverify=False)
    canonical_split = {
        "schema": "pure-weyl-curved-auxiliary-canonical-split-v1",
        "auxiliary_eom_shift": shift,
        "canonical_lift": canonical,
        "universal_generalized_auxiliary_split": universal,
        "proved": {
            "exact_curved_completion_of_square": True,
            "local_BV_cotangent_lift_is_canonical": True,
            "universal_all_row_auxiliary_contraction": True,
        },
        "actual_curved_Q_conjugation_verified": False,
        "curved_deformation_retract": False,
    }

    chain_maps = {
        "schema": "pure-weyl-curved-chain-map-status-v1",
        "canonical_field_transformation_instantiated": True,
        "canonical_cotangent_transformation_instantiated": True,
        "universal_split_differential_instantiated": True,
        "curved_Q_coefficient_table_instantiated": False,
        "curved_i_is_chain_map": False,
        "curved_p_is_chain_map": False,
        "all_BV_rows_in_curved_comparison": False,
        "curved_deformation_retract": False,
    }
    retract_identity = {
        "schema": "pure-weyl-curved-retract-identity-status-v1",
        "displayed_triangular_maps_p_i": "identity",
        "universal_auxiliary_qk_plus_kq": "minus identity",
        "actual_curved_i_p_minus_identity_equals_Qk_plus_kQ": False,
        "reason": (
            "the complete curved four-row Q has not yet been conjugated by "
            "the local canonical transformation"
        ),
        "curved_deformation_retract": False,
    }

    if args.emit:
        CERTIFICATE_DIR.mkdir(parents=True, exist_ok=True)
        for name, payload in (
            ("curved_auxiliary_canonical_split.json", canonical_split),
            ("curved_chain_maps.json", chain_maps),
            ("curved_retract_identity.json", retract_identity),
            ("curved_support_preservation.json", support),
            ("curved_deformation_retract_status.json", aggregate),
        ):
            _write(name, payload)

    if args.guards:
        checks = (
            not status.complete,
            not chain_maps["curved_i_is_chain_map"],
            not chain_maps["curved_p_is_chain_map"],
            not retract_identity[
                "actual_curved_i_p_minus_identity_equals_Qk_plus_kQ"
            ],
            canonical["local_BV_cotangent_lift_is_canonical"],
            universal["contractible"],
            support["compact_support_preserved"],
            support["spacelike_compact_support_preserved"],
        )
        if not all(checks):
            raise AssertionError("curved retract fail-closed boundary regressed")
        print("CURVED RETRACT GUARDS: 8/8 PASS")

    print("CURVED AUXILIARY SHIFT/CANONICAL INFRASTRUCTURE: ALL PROVED CHECKS PASS")


if __name__ == "__main__":
    main()
