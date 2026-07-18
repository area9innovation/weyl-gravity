#!/usr/bin/env python3
"""Independent checks for the generated Paper 12 supplement tables."""

from __future__ import annotations

import json
from pathlib import Path

from generate_12_quantum_anomaly_tables import INPUTS, OUTPUT, build


def main() -> None:
    assert OUTPUT.is_file()
    rendered = OUTPUT.read_text()
    assert rendered == build()
    assert "2.86\\times10^9" in rendered
    assert "Q_Wh+hQ_W=I_4" in rendered
    assert "\\operatorname{rank}B_{\\rm ext}=4" in rendered
    assert "\\frac{199}{30},-\\frac{87}{20},0,0" in rendered
    assert "\\frac{199}{120}" in rendered
    assert "\\frac{29}{120}" in rendered
    assert "A_{\\log}" in rendered
    assert "-\\frac{199}{60}" in rendered
    assert "first admissible operator-choice difference & 3" in rendered
    values = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert values["gauge_fixed"]["gauge_fixed_cohomology"]["H14_classes"] == [
        "ANOM_OMEGA_C2",
        "ANOM_OMEGA_E4",
        "ANOM_OMEGA_C_DUAL_C",
    ]
    assert values["extended"]["H14"]["boundary_matrix"] == [
        [
            {"numerator": int(row == column), "denominator": 1}
            for column in range(4)
        ]
        for row in range(4)
    ]
    assert (
        values["extended"]["one_loop_QME"]["strict_breaking_coordinates"]
        == values["extended"]["one_loop_QME"]["boundary_image_coordinates"]
    )
    assert values["gamma1"]["exact_coefficient_solve"]["solution_vector"] == [
        {"numerator": 199, "denominator": 120},
        {"numerator": -87, "denominator": 160},
        {"numerator": 29, "denominator": 120},
    ]
    assert values["flat_tt_log"]["exact_logarithmic_form_factor"]["RG_scale_response"] == {
        "numerator": 199,
        "denominator": 30,
    }
    assert values["flat_tt_log"]["claim_flags"]["FINITE_C2_NORMALIZATION_FIXED"] is False
    assert values["curvature_squared_log"]["operator_choice_independence"]["first_difference_order"] == 3
    assert values["curvature_squared_log"]["claim_flags"]["COMPLETE_CURVED_WEYL_INVARIANT_REMAINDER_SUPPLIED"] is False
    print("Paper 12 generated quantum-anomaly tables: PASS")


if __name__ == "__main__":
    main()
