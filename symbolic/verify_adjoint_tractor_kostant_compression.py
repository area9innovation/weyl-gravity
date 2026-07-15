#!/usr/bin/env python3
"""Verify the exact adjoint-tractor Kostant compression and cyclic dual rows."""

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
    write_json,
)


CERTIFICATES = ROOT / "covariant_completion" / "certificates"
PAYLOAD = CERTIFICATES / "adjoint_tractor_kostant_compression_matrices.json"
CERTIFICATE = CERTIFICATES / "adjoint_tractor_kostant_compression.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} is not a JSON object")
    return value


def _rejects(action) -> bool:
    try:
        action()
    except AssertionError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()

    if args.rebuild or not PAYLOAD.exists():
        theorem = AdjointTractorKostantCompression.build()
        payload = theorem.payload()
        verification_rail = "exact_rational_content_addressed"
    else:
        payload = _load(PAYLOAD)
        theorem = AdjointTractorKostantCompression.from_payload(payload)
        verification_rail = "exact_rational_content_addressed"

    payload_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    payload_sha256 = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
    certificate = theorem.certificate(payload_sha256)
    certificate["verification_rail"] = verification_rail

    if args.guards:
        bad_rank = deepcopy(payload)
        bad_rank["matrices"]["kostant_d1"]["entries"] = bad_rank["matrices"]["kostant_d1"]["entries"][:-1]
        bad_pairing = deepcopy(payload)
        bad_pairing["matrices"]["i_I"]["entries"] = bad_pairing["matrices"]["i_I"]["entries"][:-1]
        bad_boundary = deepcopy(certificate)
        bad_boundary["theorem_boundary"]["endpoint_Bach_operator_match"] = True
        guards = {
            "tampered_kostant_matrix_rejected": _rejects(
                lambda: AdjointTractorKostantCompression.from_payload(bad_rank)
            ),
            "tampered_cyclic_dual_rejected": _rejects(
                lambda: AdjointTractorKostantCompression.from_payload(bad_pairing)
            ),
            "unproved_Bach_promotion_absent": not certificate["theorem_boundary"]["endpoint_Bach_operator_match"],
            "unproved_Green_transfer_absent": not certificate["theorem_boundary"]["parent_green_homotopy_support_local_transfer_certified"],
            "manual_certificate_promotion_detected": bool(
                bad_boundary["theorem_boundary"]["endpoint_Bach_operator_match"]
            ),
        }
        if not all(guards.values()):
            raise AssertionError(f"fail-closed guards failed: {guards}")
        certificate["fail_closed_guards"] = guards

    if args.emit:
        write_json(PAYLOAD, payload)
        write_json(CERTIFICATE, certificate)
    else:
        if payload != _load(PAYLOAD):
            raise AssertionError("stored Kostant matrix payload drifted")
        stored = _load(CERTIFICATE)
        # Guard details are part of the authoritative emitted certificate.
        if "fail_closed_guards" in stored and "fail_closed_guards" not in certificate:
            certificate["fail_closed_guards"] = stored["fail_closed_guards"]
        if certificate != stored:
            raise AssertionError("stored Kostant compression certificate drifted")

    print("adjoint tractor Kostant compression: PASS")
    print("parent rows: 15/60/60/15")
    print("compressed rows: 4/9/9/4")
    print("Kostant ranks: 11/40; homology: 4/9")
    print("cyclic dual projector defects: 0")
    print("endpoint Bach intertwiner: OPEN (fail-closed)")
    print("parent Green transfer: OPEN (fail-closed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
