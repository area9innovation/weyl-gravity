#!/usr/bin/env python3
"""Verify the complete symbolic Berger per-shell recoil operator word."""

import json

from closed_universe_observers.generate_berger_per_shell_recoil_operator_word import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert len(value["channel_integrands"]) == 8
    assert len(value["aggregate_streams"]) == 4
    assert all(
        row["preparation_composition_defect_count"] == 0
        and row["recoil_composition_defect_count"] == 0
        for row in value["audited_blocks"]
    )
    assert all(row["detected"] for row in value["mutation_results"])
    assert value["flags"]["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] is True
    assert value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"] is False
    print("Berger complete per-shell recoil operator-word verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
