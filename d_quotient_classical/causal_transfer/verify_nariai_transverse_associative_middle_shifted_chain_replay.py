#!/usr/bin/env python3
"""Independent consumer for the associative parent-middle replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_associative_middle_shifted_chain_replay import (
    exact_data,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1.json"
OLD = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entries(table):
    return {
        (tuple(record["word"]), row, column): value
        for record in table["entries"]
        for row, column, value in record["matrix"]["entries"]
    }


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"] or _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency mismatch: {path}")
    replay = exact_data()
    if replay != payload["exact_data"]:
        raise AssertionError("associative replay drifted")
    if replay["typed_replay"]["variation_associator_coefficients"]:
        raise AssertionError("typed associator is nonzero")
    if replay["parent_identity"]["variation_defect_coefficients"]:
        raise AssertionError("parent identity is nonzero")
    if replay["shifted_chain"]["variation_defect_coefficients"]:
        raise AssertionError("shifted chain is nonzero")
    if replay["typed_replay"]["middle_coefficient_jet_words_requested"] != [[]]:
        raise AssertionError("positive middle coefficient jets were silently used")

    old = json.loads(OLD.read_text())["exact_data"]
    old_phi = old["operator_variations"]["Phi"]
    new_phi = replay["authoritative_phi_variation"]
    defect_empty = replay["old_phi_comparison"]["defect"]["nonzero_coefficients"] == 0
    if (_entries(old_phi) == _entries(new_phi)) != defect_empty:
        raise AssertionError("old/new Phi comparison is inconsistent")
    if replay["shifted_chain"]["old_backend_reported_coefficients"] != old["identity_defects"]["shifted_chain_variation"]["nonzero_coefficients"]:
        raise AssertionError("historical shifted-chain count drifted")
    if payload["flags"]["NARIAI_TRANSVERSE_COMPRESSED_SCHUR_REPLAY"] is not False:
        raise AssertionError("compressed Schur replay was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_ASSOCIATIVE_MIDDLE_SHIFTED_CHAIN_REPLAY_V1 independent verification: PASS")
