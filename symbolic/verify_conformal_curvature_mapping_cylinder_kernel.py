#!/usr/bin/env python3
"""Verify the canonical 16-block curvature cotangent mapping cylinder."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    CurvatureMappingCylinderKernel,
)


CERTIFICATE = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "curved_curvature_mapping_cylinder_kernel.json"
)


def main() -> int:
    result = CurvatureMappingCylinderKernel.build()
    certificate = result.certificate()

    mutations: list[bool] = []
    for row, column in ((2, 12), (1, 11), (0, 10)):
        broken = [entries[:] for entries in result.new_to_old]
        broken[row][column] = broken[row][column].scale(-1)
        try:
            replace(result, new_to_old=broken).verify()
        except AssertionError:
            mutations.append(True)
        else:
            mutations.append(False)

    broken_dual_q = [entries[:] for entries in result.split_differential]
    # X_Eq# -> X_U# is the Koszul dual of X_U -> X_Eq.
    broken_dual_q[12][11] = broken_dual_q[12][11].scale(-1)
    try:
        replace(result, split_differential=broken_dual_q).verify()
    except AssertionError:
        wrong_dual_koszul_rejected = True
    else:
        wrong_dual_koszul_rejected = False

    broken_odd_pairing = [entries[:] for entries in result.pairing]
    broken_odd_pairing[5][11] = broken_odd_pairing[5][11].scale(-1)
    broken_odd_pairing[11][5] = broken_odd_pairing[11][5].scale(-1)
    try:
        replace(result, pairing=broken_odd_pairing).verify()
    except AssertionError:
        wrong_odd_orientation_rejected = True
    else:
        wrong_odd_orientation_rejected = False

    broken_cotangent_h = [entries[:] for entries in result.homotopy]
    broken_cotangent_h[14][11] = broken_cotangent_h[14][11].scale(-1)
    try:
        replace(result, homotopy=broken_cotangent_h).verify()
    except AssertionError:
        wrong_cotangent_h_rejected = True
    else:
        wrong_cotangent_h_rejected = False

    CERTIFICATE.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checks = {
        "formal_kernel_exact": certificate["exact_formal_kernel"],
        "paired_equation_row_used": certificate["equation_normalization"][
            "p_equation_domain"
        ] == "paired Ebar row",
        "raw_to_paired_conversion_exact": certificate[
            "equation_normalization"
        ]["conversion_defect"] == 0,
        "cone_not_direct_sum": not certificate["mapping_cylinder"][
            "autonomous_curvature_direct_sum_used"
        ],
        "BV_pairing_exact": certificate["mapping_cylinder"][
            "BV_pairing_defect"
        ] == 0,
        "odd_pairing_nondegenerate": certificate["mapping_cylinder"][
            "odd_BV_pairing_squared"
        ] == "-identity",
        "split_Q_odd_cyclic": certificate["odd_BV_cyclicity"][
            "split_Q_cyclicity_defect"
        ] == 0,
        "prolonged_Q_odd_cyclic": certificate["odd_BV_cyclicity"][
            "prolonged_Q_cyclicity_defect"
        ] == 0,
        "homotopy_odd_cyclic": certificate["odd_BV_cyclicity"][
            "homotopy_cyclicity_defect"
        ] == 0,
        "Q_squared": certificate["mapping_cylinder"]["Q_squared"] == "zero",
        "SDR_identity": certificate["mapping_cylinder"][
            "I_P_minus_identity"
        ] == "QH+HQ",
        "Q_degree_plus_one": certificate["degree_checks"][
            "every_split_Q_arrow_raises_degree_by_one"
        ],
        "canonical_shear_degree_zero": certificate["degree_checks"][
            "every_canonical_shear_has_degree_zero"
        ],
        "pairing_degree_one": certificate["degree_checks"][
            "every_incidence_pairing_has_total_degree_one"
        ],
        "wrong_Tsharp_sign_rejected": mutations[0],
        "wrong_Asharp_sign_rejected": mutations[1],
        "wrong_Bsharp_sign_rejected": mutations[2],
        "wrong_dual_Koszul_sign_rejected": wrong_dual_koszul_rejected,
        "wrong_odd_pairing_orientation_rejected": wrong_odd_orientation_rejected,
        "wrong_middle_cotangent_H_sign_rejected": wrong_cotangent_h_rejected,
        "coefficientwise_status_fail_closed": not certificate[
            "coefficientwise_complete_prolonged_Q"
        ],
        "no_flag_promotion": not certificate["warranted_atomic_flags"]
        and not certificate["status_flags_promoted"],
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"certificate: {CERTIFICATE.relative_to(ROOT)}")
    print(
        "CURVATURE COTANGENT MAPPING-CYLINDER KERNEL GUARDS: "
        f"{sum(checks.values())}/{len(checks)} PASS"
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
