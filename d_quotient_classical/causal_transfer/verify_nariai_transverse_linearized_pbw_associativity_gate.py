#!/usr/bin/env python3
"""Independent consumer for the transverse linearized PBW associativity gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_linearized_pbw_associativity_gate import exact_data


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    dependency = payload["dependency_refs"]["jet_aware_backend_output"]
    if _sha(ROOT / dependency["path"]) != dependency["sha256"]:
        raise AssertionError("jet-aware dependency hash mismatch")
    replay = exact_data()
    if replay != payload["exact_data"]:
        raise AssertionError("independent associativity replay drifted")
    if replay["phi_definition"]["variation_defect_coefficients"] != 0:
        raise AssertionError("Phi definition did not replay")
    associator = replay["associator"]
    if associator["base_nonzero_coefficients"] != 0 or associator["variation_nonzero_coefficients"] != 209:
        raise AssertionError("associator multiplicity drifted")
    witness = associator["normalized_witness"]
    if witness != {
        "word": [], "output_row": 0, "input_column": 0,
        "coefficient": "7*sqrt(2)/16", "normalizing_multiplier": "8*sqrt(2)/7",
        "normalized_value": "1",
    }:
        raise AssertionError(f"normalized witness drifted: {witness}")
    if payload["flags"]["TRANSVERSE_SHIFTED_CHAIN_OBSTRUCTION_AUTHORITATIVE"] is not False:
        raise AssertionError("superseded shifted-chain obstruction was promoted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1 independent verification: PASS")
