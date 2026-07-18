#!/usr/bin/env python3
"""Verify the Berger spacetime form-block sign bridge."""

import json

from closed_universe_observers.generate_berger_spacetime_form_block_sign_bridge import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert all(
        not any(row[key])
        for row in value["audited_blocks"]
        for key in (
            "d_squared_defect_counts_degrees_0_to_2",
            "delta_squared_defect_counts_degrees_2_to_4",
            "wave_diagonalization_defect_counts_degrees_1_2",
        )
    )
    assert any(value["mutation_results"][0]["wave_defect_counts"])
    assert value["flags"]["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] is False
    print("Berger spacetime form-block sign-bridge verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
