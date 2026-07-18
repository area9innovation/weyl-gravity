#!/usr/bin/env python3
"""Verify the streamable Berger polarization sectors independently."""

import hashlib
import json

from closed_universe_observers.generate_berger_streamable_polarization_sectors import (
    CERTIFICATE,
    ROOT,
    build,
    input_entry_upper,
    sector_entry_upper,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    scale = value["capacity_rail_scale"]
    assert scale["max_dimension"] == 139
    assert scale["two_detector_input_entry_upper"] == sum(
        input_entry_upper("D0", d) + input_entry_upper("D1", d) for d in range(1, 140)
    )
    assert scale["charge_block_operator_entry_upper"] == sum(sector_entry_upper(d) for d in range(1, 140))
    assert scale["all_column_charge_block_apply_upper"] < scale["dense_apply_upper_from_preflight"] // 100
    assert all(row["support_defect_count"] == 0 for row in value["low_mode_audits"])
    assert all(row["defect_count"] == 0 for row in value["laplacian_commutator_audits"])
    assert value["flags"]["HIGH_MODE_COEFFICIENT_VALUES_EVALUATED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_STREAMABLE_POLARIZATION_SECTORS verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
