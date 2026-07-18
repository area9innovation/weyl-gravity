#!/usr/bin/env python3
"""Independent consumer for corrected-BGG splitting coefficient jets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    exact_data,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1.json"
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
    if payload["result_id"] != "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1":
        raise AssertionError("wrong result id")
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"] or _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency mismatch: {path}")

    replay = exact_data()
    if replay != payload["exact_data"]:
        raise AssertionError("coefficient-jet replay drifted")
    square = replay["strict_square"]
    if square["base_defect_coefficients"] or set(square["coefficient_jet_defects"].values()) != {0}:
        raise AssertionError("strict-square jet defect")

    # Independent serialization audit: the recovered zeroth coefficient jets
    # must equal the historical point tables coefficient by coefficient.
    old = json.loads(OLD.read_text())["exact_data"]["operator_variations"]
    new = replay["coefficient_jets"]
    if _entries(new["L0"]["()"] ) != _entries(old["corrected_L0"]):
        raise AssertionError("L0 point table changed")
    if _entries(new["L1_corrected"]["()"] ) != _entries(old["corrected_L1"]):
        raise AssertionError("L1 point table changed")
    if len(new["L0"]) != 5 or len(new["L1_corrected"]) != 15:
        raise AssertionError("coefficient-jet family coverage drifted")
    for table in new["L1_algebraic_correction"].values():
        if any(record["word"] for record in table["entries"]):
            raise AssertionError("degree-one correction ceased to be algebraic")
    if payload["flags"]["NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY"] is not False:
        raise AssertionError("middle replay was overpromoted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS_V1 independent verification: PASS")
