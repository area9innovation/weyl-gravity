#!/usr/bin/env python3
"""Verify the high-mode temporal Green order preflight."""
import json
from fractions import Fraction
from closed_universe_observers.generate_berger_temporal_green_order_preflight import CERTIFICATE, build

def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert [row["first_geometric_contractive_series_order"] for row in value["detector_audits"]] == [8, 14]
    assert all(Fraction(row["cosine_error_absolute_lower"]) > 0 for row in value["detector_audits"])
    print("BERGER_TEMPORAL_GREEN_ORDER_FIVE_HIGH_MODE_PREFLIGHT verification: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
