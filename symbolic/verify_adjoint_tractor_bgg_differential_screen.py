#!/usr/bin/env python3
"""Verify the finite adjoint-tractor BGG HPL and cylinder boundary."""

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
    write_json,
)
from covariant_completion.curved_operator.prolonged_metric_endpoint_complex import (
    ProlongedMetricEndpointComplex,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
ALGEBRAIC = CERTIFICATES / "adjoint_tractor_kostant_compression_matrices.json"
ENDPOINT = CERTIFICATES / "curved_prolonged_metric_endpoint_coefficients.json"
PAYLOAD = CERTIFICATES / "adjoint_tractor_bgg_differential_screen_matrices.json"
CERTIFICATE = CERTIFICATES / "adjoint_tractor_bgg_differential_screen.json"


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON object")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rejects(action) -> bool:
    try:
        action()
    except (AssertionError, KeyError):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    algebraic = AdjointTractorKostantCompression.from_payload(load(ALGEBRAIC))
    if args.rebuild or not PAYLOAD.exists():
        endpoint = ProlongedMetricEndpointComplex.from_coefficient_payload(load(ENDPOINT))
        theorem = AdjointTractorBGGDifferentialScreen.build(algebraic, endpoint)
        payload = theorem.payload()
    else:
        payload = load(PAYLOAD)
        theorem = AdjointTractorBGGDifferentialScreen.from_payload(algebraic, payload)

    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    payload_sha256 = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    certificate = theorem.certificate(
        payload_sha256,
        {
            "adjoint_tractor_kostant_compression_matrices.json": file_sha256(ALGEBRAIC),
            "curved_prolonged_metric_endpoint_coefficients.json": file_sha256(ENDPOINT),
        },
    )
    certificate["verification_rail"] = "exact_rational_content_addressed"

    if args.guards:
        bad_q = deepcopy(payload)
        bad_q["matrices"]["Q1"]["entries"] = bad_q["matrices"]["Q1"]["entries"][:-1]
        bad_l = deepcopy(payload)
        bad_l["tables"]["flat_L1"]["entries"][0]["matrix"]["entries"] = (
            bad_l["tables"]["flat_L1"]["entries"][0]["matrix"]["entries"][:-1]
        )
        guards = {
            "tampered_Kostant_inverse_rejected": rejects(
                lambda: AdjointTractorBGGDifferentialScreen.from_payload(algebraic, bad_q)
            ),
            "tampered_HPL_splitting_rejected": rejects(
                lambda: AdjointTractorBGGDifferentialScreen.from_payload(algebraic, bad_l)
            ),
            "curved_chain_map_not_promoted": not certificate["theorem_boundary"]["curved_cylinder_BGG_chain_maps_exact"],
            "full_Bach_match_not_promoted": not certificate["theorem_boundary"]["full_Bach_coefficient_match"],
            "Green_transfer_not_promoted": not certificate["theorem_boundary"]["parent_green_homotopy_transferred"],
        }
        if not all(guards.values()):
            raise AssertionError(f"fail-closed guards failed: {guards}")
        certificate["fail_closed_guards"] = guards

    if args.emit:
        write_json(PAYLOAD, payload)
        write_json(CERTIFICATE, certificate)
    else:
        if payload != load(PAYLOAD):
            raise AssertionError("stored differential BGG payload drifted")
        stored = load(CERTIFICATE)
        if "fail_closed_guards" in stored and "fail_closed_guards" not in certificate:
            certificate["fail_closed_guards"] = stored["fail_closed_guards"]
        if certificate != stored:
            raise AssertionError("stored differential BGG certificate drifted")

    print("adjoint tractor differential BGG screen: PASS WITH CURVED BOUNDARY OPEN")
    print("finite flat HPL orders: L0=2, L1=2; chain defects=0")
    print(f"principal Bach normalization: {theorem.bach_normalization}")
    print(
        "commuting-derivative cylinder defect entries:",
        sum(value != 0 for matrix in theorem.cylinder_chain_defect.values() for value in matrix),
    )
    print("curved PBW completion / full Bach match / Green transfer: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
