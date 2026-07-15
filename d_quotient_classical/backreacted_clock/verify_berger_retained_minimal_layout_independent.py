#!/usr/bin/env python3
"""Dependency-free independent audit of the retained Berger row layout."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_RETAINED_MINIMAL_LAYOUT.json"
)


def main() -> None:
    payload = json.loads(CERTIFICATE.read_text())
    rows = payload["component_rows"]
    expected_ids = (
        [f"c_spatial_{i}" for i in (1, 2, 3)]
        + [f"h_hat_{ij}" for ij in ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33")]
        + [f"h_hat_star_{ij}" for ij in ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33")]
        + [f"c_spatial_star_{i}" for i in (1, 2, 3)]
    )
    assert [row["index"] for row in rows] == list(range(26))
    assert [row["row_id"] for row in rows] == expected_ids
    assert [row["degree"] for row in rows] == [-1] * 3 + [0] * 10 + [1] * 10 + [2] * 3
    by_id = {row["row_id"]: row for row in rows}
    for row in rows:
        dual = by_id[row["dual_row_id"]]
        assert dual["dual_row_id"] == row["row_id"]
        assert dual["degree"] + row["degree"] == 1

    blocks = payload["q1_block_contract"]
    assert [block["block_id"] for block in blocks] == [
        "K_spatial",
        "H_retained",
        "minus_K_spatial_sharp",
    ]
    assert [block["maximum_differential_order"] for block in blocks] == [1, 4, 1]
    assert all(block["coefficient_status"] == "OPEN" for block in blocks)
    assert payload["gate_split"]["immediate_gate"] == "BERGER_RETAINED_MINIMAL_OPERATOR"
    assert payload["gate_split"]["subsequent_gate"] == "BERGER_NONMINIMAL_COMPLETION"
    assert payload["support_and_order_contract"]["support_preserving"] is True
    assert payload["nonlinear_export_compatibility"]["q2_complete"] is False
    assert payload["nonlinear_export_compatibility"]["satisfies_CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"] is False

    print("BERGER_RETAINED_MINIMAL_LAYOUT_INDEPENDENT: PASS")
    print("row IDs, degrees, duality, q1 blocks, and split gates: PASS")
    print("retained coefficients, nonminimal rows, and q2: OPEN")


if __name__ == "__main__":
    main()
