#!/usr/bin/env python3
"""Independent consumer for the factorized transverse Hom/Schur replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_factorized_hom_schur_replay import (
    exact_data,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1.json"


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
        raise AssertionError("factorized Hom/Schur replay drifted")
    if replay["jet_coverage"]["curvature_max_requested_order"] != 5:
        raise AssertionError("order-five jet layer was not exercised")
    if replay["factorized_Hom_adjoint"]["naive_normal_table_adjoint_authoritative"]:
        raise AssertionError("normal-table Hom adjoint was overpromoted")
    for key in ("base_defect", "old_point_defect", "curvature_action_base_cyclic_defect", "curvature_action_variation_cyclic_defect"):
        if replay["parent_middle"][key]["nonzero_coefficients"]:
            raise AssertionError(f"parent middle defect: {key}")
    for key in ("phi_base_defect", "phi_variation_defect"):
        if replay["compressed_schur"][key]["nonzero_coefficients"]:
            raise AssertionError(f"compressed Schur defect: {key}")
    if replay["next_gate_requirements"]["upper_chain_replayed"]:
        raise AssertionError("upper relative-saddle chain was overpromoted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_FACTORIZED_HOM_SCHUR_REPLAY_V1 independent verification: PASS")
