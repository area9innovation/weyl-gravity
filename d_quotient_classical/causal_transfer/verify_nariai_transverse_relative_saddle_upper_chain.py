#!/usr/bin/env python3
"""Independent consumer for the transverse upper relative-saddle chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_relative_saddle_upper_chain import exact_data


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"] or _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency mismatch: {path}")
    replay = exact_data()
    if replay != payload["exact_data"]:
        raise AssertionError("upper relative-saddle replay drifted")
    identity = replay["typed_identity"]
    if identity["base_defect"]["nonzero_coefficients"]:
        raise AssertionError("base upper chain failed")
    if identity["first_variation_defect"]["nonzero_coefficients"]:
        raise AssertionError("varied upper chain failed")
    if replay["derivation"]["action_Bach_variation_used"]:
        raise AssertionError("action-Hessian variation was silently assumed")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"]:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_RELATIVE_SADDLE_UPPER_CHAIN_V1 independent verification: PASS")
