#!/usr/bin/env python3
"""Independent consumer for the transverse rank-310 SDR variation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import (
    abstract_fixture,
    coefficient_fixture,
)


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"]:
            raise AssertionError(f"dependency id mismatch: {path}")
        if _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {path}")

    abstract = abstract_fixture()
    if any(abstract["defects"].values()):
        raise AssertionError("dual-number all-row replay failed")
    if len(abstract["defects"]) != 21:
        raise AssertionError("all-row identity coverage drifted")
    for name, matrix in abstract["dotted"].items():
        if repair._serialize_matrix(matrix) != payload["dotted_abstract_matrices"][name]:
            raise AssertionError(f"dotted matrix mismatch: {name}")

    coefficient = coefficient_fixture()
    if any(coefficient["coefficient_defect_counts"].values()):
        raise AssertionError("coefficient relation replay failed")
    if coefficient["coefficient_defect_counts"] != payload["coefficient_relation_defects"]:
        raise AssertionError("coefficient defect ledger mismatch")
    if coefficient["d_aut_dot"]["sha256"] != payload["coefficient_bindings"]["d_aut_dot"]["sha256"]:
        raise AssertionError("d_aut variation binding mismatch")
    if coefficient["g_dot"]["sha256"] != payload["coefficient_bindings"]["g_dot"]["sha256"]:
        raise AssertionError("complement projection variation binding mismatch")

    if payload["carrier"]["total_rank"] != 310 or payload["carrier"]["dropped_rows"]:
        raise AssertionError("rank-310 row coverage failed")
    if not all(payload["all_row_first_variation_checks"].values()):
        raise AssertionError("a serialized all-row check is false")
    if not payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"]:
        raise AssertionError("rank-310 SDR flag was not promoted")
    for forbidden in (
        "TRANSVERSE_CAUSAL_TRANSFER",
        "TRANSVERSE_METRIC_GREEN_HOMOTOPY",
        "TRANSVERSE_RANK_310_GREEN_HOMOTOPY",
    ):
        if payload["flags"][forbidden]:
            raise AssertionError(f"downstream causal flag overpromoted: {forbidden}")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION_V1 independent verification: PASS")
