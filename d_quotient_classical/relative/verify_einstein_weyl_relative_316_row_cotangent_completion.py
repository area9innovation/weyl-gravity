#!/usr/bin/env python3
"""Independent structural verifier for the 316-row cotangent completion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1.json"
LAYOUT = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_316_row_cotangent_completion_v1/layout.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict[str, object]:
    cert = json.loads(CERT.read_text())
    layout = json.loads(LAYOUT.read_text())
    for artifact in cert["dependencies"].values():
        path = ROOT / artifact["path"]
        if _sha(path) != artifact["sha256"]:
            raise AssertionError(f"dependency hash drift: {path}")
    if _sha(LAYOUT) != cert["generated_layout"]["sha256"]:
        raise AssertionError("generated layout hash drift")
    rows = layout["rows"]
    if len(rows) != 316 or [sum(row["degree"] == degree for row in rows) for degree in range(-2, 4)] != [10, 51, 97, 97, 51, 10]:
        raise AssertionError("completed degree census changed")
    by_index = {row["index"]: row for row in rows}
    if set(by_index) != set(range(316)):
        raise AssertionError("row indices are not exhaustive")
    for row in rows:
        dual = by_index[row["dual_row"]]
        if dual["dual_row"] != row["index"] or row["degree"] + dual["degree"] != 1:
            raise AssertionError(f"bad dual row: {row['row_id']}")
    pairing = layout["odd_pairing"]
    if len(pairing) != 316:
        raise AssertionError("pairing is not one directed term per row")
    directed = {(term["left_row"], term["right_row"]): term["coefficient"] for term in pairing}
    for row in rows:
        pair = (row["index"], row["dual_row"])
        if pair not in directed or directed[pair] not in (-1, 1):
            raise AssertionError(f"missing pairing term: {row['row_id']}")
    if cert["classification"]["complete_q2_on_316_rows"] or cert["classification"]["causal_green_data"]:
        raise AssertionError("downstream claim overpromoted")
    return {"status": "PASS", "rows": 316, "degree_ranks": layout["degree_ranks"], "added_cotangent_rows": 78}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
