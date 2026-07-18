#!/usr/bin/env python3
"""Independent consumer for the factorized transverse endpoint completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_factorized_endpoint_completion import exact_data


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1.json"


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
        raise AssertionError("factorized endpoint completion drifted")
    if replay["base_reconciliation"]["endpoint_plus_2_B_action_defect"]["nonzero_coefficients"]:
        raise AssertionError("base action endpoint mismatch")
    solve = replay["complete_first_order_solve"]
    if solve["coefficient_map_shape"] != [60, 45] or solve["coefficient_map_rank"] != 45:
        raise AssertionError("complete endpoint ansatz drifted")
    if solve["free_parameter_counts"] != [0] * 9:
        raise AssertionError("endpoint completion lost uniqueness")
    if solve["unique_correction"]["orders"] != [0]:
        raise AssertionError("endpoint completion ceased to be algebraic")
    if replay["factorized_endpoint_target"]["Qdot_fibre_adjoint_defect"]["nonzero_coefficients"]:
        raise AssertionError("endpoint completion lost cyclicity")
    if payload["flags"]["TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION"]:
        raise AssertionError("action third variation was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_FACTORIZED_ENDPOINT_COMPLETION_V1 independent verification: PASS")
