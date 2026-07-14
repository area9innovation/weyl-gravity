#!/usr/bin/env python3
"""Sprint-1 certificate: all-energy E/A/L metric-to-curvature preimages.

This is a coordinate differential-operator calculation on the Lorentzian
conformal cylinder.  It is not a character-only test.  For symbolic compact
energy ``n`` it constructs the normalized highest-weight metric oscillator
in every E/A/L family, computes its full 256-component linearized Weyl
tensor, verifies chirality and the linear Bach equation, and records a
nonzero exact curvature pivot.  ``SO(4)`` equivariance and multiplicity one
then extend the right inverse from the highest weight to the complete irrep.

The certificate closes the explicit *physical-block preimage* obligation.
It does not yet claim that the surrounding off-shell metric/gauge/BGG block
matrices or the complete local BV complex have been constructed.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.cylinder_harmonics.linearized_geometry import (
    I,
    LinearizedCylinderGeometry,
    canonical,
    highest_weight_mode,
    n_symbol,
    tensor_get,
)
from bridge.metric_preimages.all_energy import (
    BRANCH_MINIMUM,
    block_dimension,
    curvature_basis,
    level_dimension,
    right_inverse,
)


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "cylinder_metric_preimages.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "cylinder_metric_preimages.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def certificate_data() -> dict[str, object]:
    geometry = LinearizedCylinderGeometry()
    check(
        "S1-R1: rational cylinder metric and inverse multiply to identity",
        (geometry.metric * geometry.inverse).applyfunc(canonical) == sp.eye(4),
    )
    check(
        "S1-R1: cylinder background has Ricci=(0,2 gamma) and scalar curvature six",
        geometry.ricci[0, 0] == 0
        and geometry.scalar_curvature == 6
        and geometry.ricci[1:, 1:] == 2 * geometry.metric[1:, 1:],
    )

    records: list[dict[str, object]] = []
    positive_vectors = {}
    for family in ("E", "A", "L"):
        mode = highest_weight_mode(family, n_symbol, 1)
        check(
            f"S1-R2: {family}_n metric representative has the exact tower irrep",
            sp.expand((2 * mode.spin_left + 1) * (2 * mode.spin_right + 1))
            == block_dimension(family, n_symbol),
        )
        check(
            f"S1-R2: {family}_n metric representative is trace-free symbolically",
            geometry.trace(mode) == 0,
        )

        vector = curvature_basis(family, n_symbol, 1, geometry=geometry)
        positive_vectors[family] = vector
        check(
            f"S1-R3: C_n has a nonzero exact {family}_n highest-weight pivot",
            vector.pivot != 0,
        )
        check(
            f"S1-R3: C_n R_n is identity on the normalized {family}_n curvature basis",
            right_inverse(vector) == mode,
        )
        check(
            f"S1-R4: {family}_n Weyl image is algebraically trace-free",
            geometry.weyl_trace(vector.tensor) == sp.zeros(4),
        )
        star = geometry.hodge_first_pair(vector.tensor)
        check(
            f"S1-R4: {family}_n Weyl image has positive-tower Hodge chirality",
            all(
                canonical(
                    tensor_get(star, *key) + I * tensor_get(vector.tensor, *key)
                )
                == 0
                for key in set(star) | set(vector.tensor)
            ),
        )
        check(
            f"S1-R5: B_n R_n=C_n^sharp C_n R_n vanishes for symbolic {family}_n",
            geometry.bach_from_weyl(mode, vector.tensor) == sp.zeros(4),
        )
        records.append(
            {
                "family": family,
                "minimum_energy": BRANCH_MINIMUM[family],
                "chirality": "+",
                "energy": "n",
                "irrep": [str(mode.spin_left), str(mode.spin_right)],
                "dimension": str(block_dimension(family, n_symbol)),
                "radial_exponent": str(mode.radial_exponent),
                "metric_amplitude": str(mode.amplitude),
                "curvature_pivot_index": list(vector.pivot_index),
                "curvature_pivot": str(vector.pivot),
                "hodge_eigenvalue": "-I",
                "right_inverse": f"R_n(U_{family},n,M)=h_{family},n,M",
            }
        )

    # Parity is an exact orientation-reversing cylinder isometry alpha<->gamma.
    parity = sp.zeros(4)
    parity[0, 0] = parity[2, 2] = 1
    parity[1, 3] = parity[3, 1] = 1
    check(
        "S1-R6: alpha-gamma parity preserves the cylinder metric",
        (parity.T * geometry.metric * parity).applyfunc(canonical) == geometry.metric,
    )
    check("S1-R6: alpha-gamma parity reverses orientation", parity.det() == -1)

    # One direct opposite-chirality calculation checks the pullback convention;
    # isometry/naturality and orientation reversal supply all other blocks.
    negative_e = curvature_basis("E", n_symbol, -1, geometry=geometry)
    negative_star = geometry.hodge_first_pair(negative_e.tensor)
    check(
        "S1-R6: parity partner has the opposite Hodge eigenvalue",
        all(
            canonical(
                tensor_get(negative_star, *key)
                - I * tensor_get(negative_e.tensor, *key)
            )
            == 0
            for key in set(negative_star) | set(negative_e.tensor)
        ),
    )
    check(
        "S1-R6: parity exchanges the two SU(2) labels",
        negative_e.spin_left == positive_vectors["E"].spin_right
        and negative_e.spin_right == positive_vectors["E"].spin_left,
    )

    # A deliberately mistuned low mode must not solve the Bach equation.
    # This guards against a vacuous implementation of C^sharp.
    e2 = highest_weight_mode("E", sp.Integer(2), 1)
    mistuned = replace(e2, energy=sp.Integer(3))
    mistuned_weyl = geometry.linearized_weyl(mistuned)
    check(
        "S1-R6: Bach operator rejects a deliberately mistuned TT frequency",
        geometry.bach_from_weyl(mistuned, mistuned_weyl) != sp.zeros(4),
    )

    expected_dimensions = [10, 40, 82, 136, 202]
    actual_dimensions = [level_dimension(energy) for energy in range(2, 7)]
    check(
        "S1-R7: symbolic tower formula reproduces levels 2..6",
        actual_dimensions == expected_dimensions,
    )

    return {
        "schema": "pure-weyl-cylinder-preimages-v1",
        "category": "D-finite SO(4)-finite highest-weight blocks",
        "coordinate_chart": "r=tan(beta/2), r>0",
        "common_factor": "exp[-i(E tau+mL alpha+mR gamma)]*(1+r^2)^(-a)",
        "curvature_convention": "U_(F,n,M)=C1 h_(F,n,M)",
        "right_inverse_identity": "C1 R_n=id on E/A/L curvature image blocks",
        "records": records,
        "parity_completion": {
            "map": "alpha<->gamma",
            "orientation": -1,
            "hodge_eigenvalues": {"+": "-I", "-": "+I"},
        },
        "level_dimensions_2_through_6": actual_dimensions,
        "scope": {
            "proved": [
                "symbolic all-n normalized metric preimage in each E/A/L irrep",
                "nonzero full coordinate Weyl image",
                "chiral algebraic Weyl identities",
                "linear Bach equation",
                "same-energy and same-SO(4)-block right inverse",
            ],
            "not_yet_proved": [
                "complete off-shell K_n/C_n/D2_n harmonic complex",
                "full one-particle BV cohomology",
                "SO(4,2)-equivariant cyclic transfer",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    rows = []
    for record in data["records"]:
        irrep = ",".join(
            sp.latex(sp.sympify(value)) for value in record["irrep"]
        )
        dimension = sp.latex(sp.sympify(record["dimension"]))
        pivot = sp.latex(sp.sympify(record["curvature_pivot"]))
        rows.append(
            "{} & ${}$ & ${}$ & ${}$ \\\\".format(
                record["family"],
                irrep,
                dimension,
                pivot,
            )
        )
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_cylinder_preimages.py",
            r"\begin{tabular}{c|c|c|c}",
            r"tower & $(j_L,j_R)$ & dimension & nonzero $C_1h$ pivot \\",
            r"\hline",
            *rows,
            r"\end{tabular}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="write JSON and generated LaTeX artifacts"
    )
    parser.add_argument(
        "--claim-complete-harmonic-complex",
        action="store_true",
        help="fail closed: physical preimages are not the full off-shell complex",
    )
    args = parser.parse_args()
    if args.claim_complete_harmonic_complex:
        raise SystemExit(
            "REFUSED: this executable contains the raw physical E/A/L "
            "preimages only. Off-shell BGG split blocks and raw polynomial "
            "BV rows are certified by separate bridge executables; a full "
            "raw magnetic-state cylinder tensor complex is not stored here."
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

    print("pivot formulas:")
    for record in data["records"]:
        print(f"  {record['family']}_n: {record['curvature_pivot']}")
    print("level dimensions:", data["level_dimensions_2_through_6"])
    print("CONFORMAL S1 CYLINDER METRIC PREIMAGES: ALL PASS")


if __name__ == "__main__":
    main()
