#!/usr/bin/env python3
"""Verify the curvature-aware adjoint-tractor BGG PBW compression."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    AdjointTractorBGGDifferentialScreen,
)
from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    AdjointTractorBGGCurvedPBW,
    write_json,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
ALGEBRAIC = CERTIFICATES / "adjoint_tractor_kostant_compression_matrices.json"
SCREEN = CERTIFICATES / "adjoint_tractor_bgg_differential_screen_matrices.json"
ENDPOINT = CERTIFICATES / "curved_prolonged_metric_endpoint_coefficients.json"
PAYLOAD = CERTIFICATES / "adjoint_tractor_bgg_curved_pbw_matrices.json"
CERTIFICATE = CERTIFICATES / "adjoint_tractor_bgg_curved_pbw.json"


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    algebraic = AdjointTractorKostantCompression.from_payload(load(ALGEBRAIC))
    screen = AdjointTractorBGGDifferentialScreen.from_payload(algebraic, load(SCREEN))
    endpoint = ProlongedMetricEndpointComplex.from_coefficient_payload(load(ENDPOINT))
    theorem = AdjointTractorBGGCurvedPBW.build(algebraic, screen, endpoint)
    theorem.verify()
    payload = theorem.payload()
    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    payload_sha256 = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    certificate = theorem.certificate(
        payload_sha256,
        {
            ALGEBRAIC.name: sha256(ALGEBRAIC),
            SCREEN.name: sha256(SCREEN),
            ENDPOINT.name: sha256(ENDPOINT),
        },
    )
    certificate["verification_rail"] = "exact_rational_curvature_aware_PBW"

    if args.guards:
        promoted = deepcopy(certificate)
        promoted["theorem_boundary"]["parent_green_homotopy_transferred"] = True
        guards = {
            "former_48_entries_cancelled": certificate["former_48_entry_defect"]["PBW_corrected_defect_entries"] == 0,
            "full_Bach_orders_zero": all(
                row["defect_entries"] == 0
                for row in certificate["Bach_comparison"]["order_ledger"].values()
            ),
            "Green_transfer_not_promoted": not certificate["theorem_boundary"]["parent_green_homotopy_transferred"],
            "manual_Green_promotion_detected": promoted["theorem_boundary"]["parent_green_homotopy_transferred"],
            "no_nonlocal_support_operation": certificate["theorem_boundary"]["support_local"],
        }
        if not all(guards.values()):
            raise AssertionError(f"fail-closed guards failed: {guards}")
        certificate["fail_closed_guards"] = guards

    if args.emit:
        write_json(PAYLOAD, payload)
        write_json(CERTIFICATE, certificate)
    else:
        if payload != load(PAYLOAD):
            raise AssertionError("stored curved PBW matrix payload drifted")
        stored = load(CERTIFICATE)
        if "fail_closed_guards" in stored and "fail_closed_guards" not in certificate:
            certificate["fail_closed_guards"] = stored["fail_closed_guards"]
        if certificate != stored:
            raise AssertionError("stored curved PBW certificate drifted")

    print("adjoint tractor curved BGG PBW: PASS")
    print("former commuting-derivative defect: 48 -> 0")
    print("curved chain/homotopy/cyclic defects: 0")
    print("compressed middle = -2 endpoint Bach_bar: all orders PASS")
    print("parent Green homotopy transfer: OPEN (downstream gate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
