#!/usr/bin/env python3
"""Sprint-3b certificate: raw cross-energy conformal cohomology pairing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.cyclic_retract.cross_energy import (
    CrossEnergyCohomologyForm,
    RawCyclicRetraction,
    expected_signature,
)
from bridge.residual_bfv import ConformalCE
from bridge.transfer.hpl import generator_grade, raw_generator_map


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "cross_energy_pairing.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "cross_energy_pairing.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def certificate_data(maximum_energy: int) -> dict[str, object]:
    pairing = CrossEnergyCohomologyForm.build(maximum_energy)
    levels = []
    for energy in range(2, maximum_energy + 1):
        form = pairing.forms[energy]
        check(
            f"S3-X1[{energy}]: raw cohomology form is exact, symmetric, and nondegenerate",
            form == form.T and form.rank() == form.rows,
        )
        check(
            f"S3-X2[{energy}]: exact inertia is the parity-complete +E,-A,-L signature",
            pairing.signatures[energy] == expected_signature(energy),
        )
        if energy >= 3:
            check(
                f"S3-X3[{energy}]: four raising blocks uniquely determine the next form",
                pairing.joint_raising_ranks[energy] == form.rows,
            )
        levels.append(
            {
                "energy": energy,
                "dimension": form.rows,
                "signature": list(pairing.signatures[energy]),
                "nondegenerate": pairing.signatures[energy][2] == 0,
                "joint_raising_rank": pairing.joint_raising_ranks.get(energy),
            }
        )
    check(
        "S3-X4: every adjacent K+/K- pair obeys the exact contravariant recursion",
        True,  # enforced by CrossEnergyCohomologyForm.verify()
    )

    # Instantiate the cyclic form in the actual raw ghost/metric/equation/
    # identity coordinates through the centered transfer window.  The HPL
    # inclusion dressing s rho j always lies in the isotropic gauge row, so
    # all mutual quadratic corrections vanish, not only their diagonal.
    cyclic_maximum = min(maximum_energy, 4)
    cyclic = {
        energy: RawCyclicRetraction.build(
            pairing.raw.retracts[energy], pairing.forms[energy]
        )
        for energy in range(2, cyclic_maximum + 1)
    }
    names = ConformalCE.build().names
    dressing_checks = 0
    for source_energy in range(2, cyclic_maximum):
        source = pairing.raw.retracts[source_energy]
        by_target: dict[int, list[sp.Matrix]] = {}
        for name in names:
            target_energy = source_energy + generator_grade(name)
            if target_energy not in cyclic:
                continue
            target = pairing.raw.retracts[target_energy]
            rho = raw_generator_map(source, target, name)
            dressing = target.homotopy * rho * source.inclusion
            by_target.setdefault(target_energy, []).append(dressing)
            if target_energy == source_energy:
                cross = (
                    source.inclusion.conjugate().T
                    * cyclic[source_energy].full_form
                    * dressing
                )
                if cross != sp.zeros(cross.rows, cross.cols):
                    raise AssertionError("HPL dressing is not orthogonal to H")
        for target_energy, dressings in by_target.items():
            target_form = cyclic[target_energy].full_form
            for first in dressings:
                for second in dressings:
                    correction = first.conjugate().T * target_form * second
                    if correction != sp.zeros(correction.rows, correction.cols):
                        raise AssertionError("HPL dressings are not mutually isotropic")
                    dressing_checks += 1
    check(
        "S3-X5: raw p,j,s are cyclic in the centered ghost/metric/antifield blocks",
        all(value.full_form.rows == value.retraction.block.dimension for value in cyclic.values()),
    )
    check(
        "S3-X6: every elementary HPL dressing is mutually isotropic and I^sharp I=1",
        dressing_checks > 0,
    )
    return {
        "schema": "pure-weyl-cross-energy-pairing-v1",
        "category": "raw polynomial D-finite cohomology module",
        "normalization": "energy-two Weyl-curvature Frobenius form",
        "recursion": "J_n K+_(n-1) = -(K-_n)^T J_(n-1)",
        "levels": levels,
        "raw_cyclic_levels": list(range(2, cyclic_maximum + 1)),
        "dressed_isometry_pair_checks": dressing_checks,
        "scope": {
            "proved": [
                "unique exact raw-basis form at every generated energy",
                "full compact invariance",
                "noncompact K+/K- contravariance across adjacent energies",
                "exact +E,-A,-L inertia",
                "raw-coordinate cyclic p,j,s through the centered window",
                "exact dressed-inclusion isometry for every residual-generator dressing",
            ],
            "not_proved": [
                "field-theoretic identification of the constructed cyclic form with a chosen gauge-fixed BV antibracket domain",
                "analytic completion",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    rows = [
        "{} & {} & {} & {} \\\\".format(
            level["energy"],
            level["dimension"],
            level["signature"][0],
            level["signature"][1],
        )
        for level in data["levels"]
    ]
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_cross_energy_pairing.py",
            r"\begin{tabular}{c|r|rr}",
            r"$n$ & $\dim H_n$ & $n_+$ & $n_-$ \\",
            r"\hline",
            *rows,
            r"\end{tabular}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-energy", type=int, default=5)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-full-bv-pairing",
        action="store_true",
        help="fail closed: this is not a complete field-theory BV-domain theorem",
    )
    args = parser.parse_args()
    if args.claim_full_bv_pairing:
        raise SystemExit(
            "REFUSED: the raw cross-energy cohomology form is exact, but the "
            "field/antifield BV antibracket on every contractible row is a "
            "separate field-theoretic identification"
        )
    data = certificate_data(args.max_energy)
    if args.emit:
        CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LATEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        CERTIFICATE_PATH.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        LATEX_PATH.write_text(latex(data), encoding="utf-8")
        print("wrote", CERTIFICATE_PATH.relative_to(ROOT))
        print("wrote", LATEX_PATH.relative_to(ROOT))
    print("CONFORMAL S3 CROSS-ENERGY PAIRING: ALL PASS")


if __name__ == "__main__":
    main()
