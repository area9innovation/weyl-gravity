#!/usr/bin/env python3
"""Independent consumer for the transverse action Bach-Hessian variation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.causal_transfer.nariai_transverse_action_bach_leading_variation import (
    action_variation_frozen,
)
from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    _deserialize_table,
    _difference,
)
from d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair import (
    _table_scale,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"] or _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency mismatch: {path}")

    endpoint_path = ROOT / payload["dependency_refs"]["factorized_endpoint"]["path"]
    pbw_path = ROOT / payload["dependency_refs"]["associative_PBW_replay"]["path"]
    pbw = json.loads(pbw_path.read_text())
    if not pbw["exact_checks"]["typed_associator_zero"]:
        raise AssertionError("pinned PBW backend is not associative")
    endpoint = json.loads(endpoint_path.read_text())["exact_data"]
    target = endpoint["factorized_endpoint_target"]
    parent = _deserialize_table(target["compressed_parent_endpoint_variation"])
    action = _deserialize_table(target["action_bach_variation_target"])
    if _difference(action, _table_scale(parent, -sp.Rational(1, 2))):
        raise AssertionError("parent/action normalization failed")

    direct = action_variation_frozen()
    action_two = {word: matrix for word, matrix in action.items() if len(word) == 2}
    if _difference(direct["order_two"], action_two):
        raise AssertionError("direct action order-two replay failed")
    if any(len(word) > 2 for word in direct["frozen_variation"]):
        raise AssertionError("unexpected action order above two")

    exact = payload["exact_data"]
    if exact["lower_order_noether_completion"]["coefficient_map_rank"] != 45:
        raise AssertionError("lower Noether solve lost full column rank")
    if exact["lower_order_noether_completion"]["free_parameter_counts"] != [0] * 9:
        raise AssertionError("lower action completion lost uniqueness")
    if exact["direct_action_leading_derivation"]["frozen_lower_table_authoritative"]:
        raise AssertionError("frozen lower coefficients were overpromoted")
    if not payload["flags"]["TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION"]:
        raise AssertionError("action variation flag was not promoted")
    if not payload["exact_checks"]["associative_PBW_backend_pinned"]:
        raise AssertionError("associative PBW dependency was not promoted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"]:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_ACTION_BACH_HESSIAN_VARIATION_V1 independent verification: PASS")
