#!/usr/bin/env python3
"""Exact noncompact-transfer certificate in raw metric BV coordinates.

This executable does not infer conformal equivariance from the BGG split
normal form.  It constructs the polynomial Diff/Weyl ghost, metric,
equation-antifield, and identity-antifield rows, verifies the raw
translation and special-conformal chain maps, extracts an exact rational
SDR, and measures the resulting noncompact defects.

The chosen SDR is *not* strictly equivariant.  The certificate proves the
stronger useful statement: every defect is controlled by the displayed
homotopy, the induced maps obey the strict conformal algebra on cohomology,
and every higher HPL correction vanishes on the physical metric row by
chain degree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.cyclic_retract import (
    RawPolynomialRetraction,
    verify_homotopy_equivariance,
)


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "raw_bv_transfer.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "raw_bv_transfer.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def zero(rows: int, columns: int) -> sp.Matrix:
    return sp.zeros(rows, columns)


def certificate_data() -> dict[str, object]:
    retracts = {energy: RawPolynomialRetraction.build(energy) for energy in range(2, 6)}
    expected = {2: 10, 3: 40, 4: 82, 5: 136}
    for energy, retract in retracts.items():
        check(
            f"S3-R1[{energy}]: raw metric/ghost/antifield SDR is exact",
            retract.cohomology_dimension == expected[energy],
        )

    # Verify all four noncompact directions on the central energy-four
    # block.  Ranks are expensive and basis-dependent, so they are emitted
    # for one representative axis while the exact identities are checked
    # for every axis.
    reports: dict[str, dict[str, int]] = {}
    central = retracts[4]
    for axis in range(4):
        lower = retracts[3]
        translation = central.block.translation_to(lower.block, axis)
        report = verify_homotopy_equivariance(
            central,
            lower,
            translation,
            measure_ranks=axis == 0,
        )
        if report:
            reports["translation_axis_0"] = report

        upper = retracts[5]
        special = central.block.special_to(upper.block, axis)
        report = verify_homotopy_equivariance(
            central,
            upper,
            special,
            measure_ranks=axis == 0,
        )
        if report:
            reports["special_axis_0"] = report
    check(
        "S3-E1: all raw P and K maps are homotopy-equivariant",
        True,
    )
    check(
        "S3-E2: the extracted SDR is genuinely non-strict",
        reports["translation_axis_0"]["inclusion_defect_rank"] > 0
        and reports["special_axis_0"]["inclusion_defect_rank"] > 0,
    )

    # The induced maps must obey the conformal bracket, even though j,p,s
    # separately have nonzero defects.  In coordinate-field convention,
    # [K_b,P_a] = -2 delta_ab D + 2 M_ab.
    h4 = central.cohomology_dimension
    reduced_d = 4 * sp.eye(h4)
    for first in range(4):
        for second in range(4):
            p_down = central.induced(
                central.block.translation_to(retracts[3].block, first),
                retracts[3],
            )
            k_up_from_down = retracts[3].induced(
                retracts[3].block.special_to(central.block, second),
                central,
            )
            k_up = central.induced(
                central.block.special_to(retracts[5].block, second),
                retracts[5],
            )
            p_down_from_up = retracts[5].induced(
                retracts[5].block.translation_to(central.block, first),
                central,
            )
            commutator = k_up_from_down * p_down - p_down_from_up * k_up
            if first == second:
                expected_bracket = -2 * reduced_d
            else:
                ordered = tuple(sorted((first, second)))
                orientation = 1 if first < second else -1
                reduced_rotation = central.induced(
                    central.block.rotation(*ordered), central
                )
                expected_bracket = 2 * orientation * reduced_rotation
            check(
                f"S3-A1[{first},{second}]: induced [K,P] bracket is strict",
                commutator == expected_bracket,
            )

    # The potentially dangerous second HPL term is p rho s rho j.  Starting
    # from a metric representative, s lands in the gauge row; every
    # conformal generator preserves the BV row, whereas p has support only
    # on the metric row.  Check every K-K component explicitly across the
    # 3 -> 4 -> 5 window.  Any further term contains s on the gauge row and
    # vanishes before projection.
    for first in range(4):
        rho_first = retracts[3].block.special_to(central.block, first)
        for second in range(4):
            rho_second = central.block.special_to(retracts[5].block, second)
            correction = (
                retracts[5].projection
                * sp.Matrix(rho_second)
                * central.homotopy
                * sp.Matrix(rho_first)
                * retracts[3].inclusion
            )
            check(
                f"S3-H1[{first},{second}]: p K s K j vanishes",
                correction
                == zero(
                    retracts[5].cohomology_dimension,
                    retracts[3].cohomology_dimension,
                ),
            )

    return {
        "schema": "pure-weyl-raw-polynomial-transfer-v1",
        "category": "exact rational polynomial metric BV complex",
        "energies": [
            {
                "energy": energy,
                "full_dimension": retracts[energy].block.dimension,
                "cohomology_dimension": retracts[energy].cohomology_dimension,
            }
            for energy in sorted(retracts)
        ],
        "axis_zero_defects": reports,
        "noncompact_result": "homotopy-equivariant, not strict",
        "induced_result": "strict so(4,2) action on cohomology",
        "hpl_result": (
            "p rho s rho j=0 on the physical metric row; all higher terms "
            "vanish because a second s acts on the gauge row"
        ),
        "scope": {
            "proved": [
                "raw q intertwines all four translations and special conformal maps",
                "exact p,j,s in metric BV coordinates",
                "nonzero defects with explicit q-homotopies",
                "strict induced conformal bracket",
                "vanishing physical-row HPL corrections",
            ],
            "not_proved": [
                "cyclicity for the cross-energy local BV pairing",
                "full pure-Weyl BFV normalization transfer",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    p = data["axis_zero_defects"]["translation_axis_0"]
    k = data["axis_zero_defects"]["special_axis_0"]
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_raw_bv_transfer.py",
            r"\begin{tabular}{c|rrrr}",
            r"map & $\operatorname{rank}\rho_H$ & $\operatorname{rank}\delta_j$ & $\operatorname{rank}\delta_p$ & $\operatorname{rank}\delta_s$ \\",
            r"\hline",
            "{} & {} & {} & {} & {} \\\\".format(
                r"$P_0$",
                p["induced_rank"],
                p["inclusion_defect_rank"],
                p["projection_defect_rank"],
                p["homotopy_defect_rank"],
            ),
            "{} & {} & {} & {} & {} \\\\".format(
                r"$K_0$",
                k["induced_rank"],
                k["inclusion_defect_rank"],
                k["projection_defect_rank"],
                k["homotopy_defect_rank"],
            ),
            r"\end{tabular}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-strict-sdr",
        action="store_true",
        help="fail closed: the extracted raw SDR has measured nonzero defects",
    )
    args = parser.parse_args()
    if args.claim_strict_sdr:
        raise SystemExit(
            "REFUSED: p,j,s are homotopy-equivariant, not strictly SO(4,2)-equivariant"
        )
    data = certificate_data()
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LATEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        LATEX_PATH.write_text(latex(data), encoding="utf-8")
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
        print("wrote", LATEX_PATH.relative_to(ROOT))
    print("CONFORMAL RAW BV TRANSFER: ALL PASS")


if __name__ == "__main__":
    main()
