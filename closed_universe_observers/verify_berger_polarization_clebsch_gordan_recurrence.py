#!/usr/bin/env python3
"""Verify the Berger polarization Clebsch--Gordan recurrence independently."""

import hashlib
import json

from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    CERTIFICATE,
    ROOT,
    axial_scalar_recurrence,
    build,
    product_identity_defects,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert product_identity_defects() == 0
    assert product_identity_defects(2, drop_lower_channel=True) > 0

    for two_j in range(8):
        dimension = two_j + 1
        entry_count = 0
        term_count = 0
        maximum = 0
        for coordinate in ("y0", "y1", "y2", "y3"):
            for row in range(dimension):
                for column in range(dimension):
                    terms = axial_scalar_recurrence(two_j, row, column, coordinate)
                    if terms:
                        entry_count += 1
                        term_count += len(terms)
                        maximum = max(maximum, len(terms))
        assert entry_count == 6 * dimension - 4
        assert term_count == 16 * dimension - 12
        assert maximum <= 4

    scale = value["scale_audit_through_two_j138"]
    assert scale == {
        "coordinate_entry_count": 57824,
        "maximum_scalar_terms_per_coordinate_entry": 4,
        "scalar_recurrence_term_count": 154012,
    }
    assert value["flags"]["HIGH_MODE_SCALAR_COEFFICIENT_VALUES_EVALUATED"] is False
    assert value["flags"]["BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_POLARIZATION_CLEBSCH_GORDAN_RECURRENCE verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
