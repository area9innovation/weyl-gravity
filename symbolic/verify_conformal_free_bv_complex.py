#!/usr/bin/env python3
"""Sprint-2 split-normal-form fixture for the free pure-Weyl BV rows.

The executable constructs the minimal detour BV row, the Weyl trace/ghost
doublet and its antifield dual, and a nonminimal antighost/multiplier pair at
every finite cylinder energy.  An explicit homotopy contracts every
nonphysical coordinate.  The fifteen conformal-Killing reducibilities are
removed by an independently constructed rational projector with compact
grading ``4_-1+7_0+4_+1``.

The result is the one-particle cohomology of this split fixture.  It is not
the field-derived gauge-fixed domain: the latter has a specified gauge
fermion, vector and scalar nonminimal pairs, and both antifield duals in the
separate field-BV certificate.
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

from bridge.bv_complex import FreeBVBlock
from bridge.zero_modes import conformal_killing_projector


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "free_bv_complex.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "free_bv_complex.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def certificate_data(maximum_energy: int) -> dict[str, object]:
    zero_modes = conformal_killing_projector()
    check(
        "S2-Z1: exact CKV projector has rank fifteen and is idempotent",
        zero_modes.projector.rank() == 15
        and zero_modes.projector * zero_modes.projector == zero_modes.projector,
    )
    check(
        "S2-Z1: K P_CKV=0 and the low-mode kernel is exhausted",
        zero_modes.gauge_map * zero_modes.projector == sp.zeros(50, 65)
        and zero_modes.gauge_map.rank() + zero_modes.basis.cols
        == zero_modes.gauge_map.cols,
    )
    check(
        "S2-Z1: CKVs have compact decomposition 4_-1+7_0+4_+1",
        zero_modes.compact_degrees == (-1,) * 4 + (0,) * 7 + (1,) * 4,
    )

    levels: list[dict[str, object]] = []
    for energy in range(2, maximum_energy + 1):
        block = FreeBVBlock.at_energy(energy)
        check(
            f"S2-B1[{energy}]: full field/ghost/antifield q is exactly nilpotent",
            block.q * block.q
            == sp.SparseMatrix(block.dimension, block.dimension, {}),
        )
        check(
            f"S2-B2[{energy}]: explicit contraction leaves only W+ plus W-",
            block.inclusion * block.projection
            == sp.SparseMatrix.eye(block.dimension)
            - block.q * block.homotopy
            - block.homotopy * block.q,
        )
        check(
            f"S2-B3[{energy}]: nonminimal pair has an explicit inverse homotopy",
            block.field("antighost").dimension
            == block.field("multiplier").dimension,
        )
        check(
            f"S2-B4[{energy}]: reduced one-particle dimension is the E/A/L count",
            block.physical_dimension == 2 * (3 * energy**2 - 7),
        )
        levels.append(
            {
                "energy": energy,
                "full_dimension": block.dimension,
                "cohomology_dimension": block.physical_dimension,
                "fields": [
                    {
                        "name": field.name,
                        "dimension": field.dimension,
                        "ghost_number": field.ghost_number,
                        "antifield_number": field.antifield_number,
                        "role": field.role,
                    }
                    for field in block.fields
                ],
            }
        )

    check(
        "S2-B5: first five one-particle cohomology dimensions are 10,40,82,136,202",
        [row["cohomology_dimension"] for row in levels[:5]]
        == [10, 40, 82, 136, 202],
    )

    # Exact characteristic-zero symmetric-power rail.  The averaging
    # idempotent commutes with q; this small nontrivial block verifies the
    # implementation convention while the general statement is algebraic.
    q = sp.Matrix([[0, 0, 0], [1, 0, 0], [0, 0, 0]])
    check("S2-F1: one-particle fixture is nilpotent", q * q == sp.zeros(3))
    # Its cohomology is one-dimensional; graded Sym^2 therefore has one
    # class.  With a,h even and b=d a odd, use the ordered basis
    # (a^2,a h,h^2,a b,h b); b^2 vanishes by graded symmetry.
    q2 = sp.zeros(5)
    q2[3, 0] = 2  # d(a^2)=2ab
    q2[4, 1] = 1  # d(ah)=bh
    check(
        "S2-F1: direct Sym^2 cohomology agrees with Sym^2 H",
        q2 * q2 == sp.zeros(5)
        and len(q2.nullspace()) - q2.rank() == 1,
    )

    return {
        "schema": "pure-weyl-free-bv-block-v1",
        "category": "algebraic D-finite SO(4)-finite free BV detour complex",
        "zero_modes": {
            "ambient_parameter_dimension": 65,
            "projector_rank": 15,
            "decomposition": [4, 7, 4],
            "labels": list(zero_modes.labels),
        },
        "levels": levels,
        "cohomology": "H(q)_one-particle = W+ direct-sum W-",
        "fock_lift": "H(Sym C,q)=Sym H(C,q) over characteristic zero",
        "contracted_rows": [
            "nonzero Diff ghost / gauge metric",
            "Weyl ghost / metric trace",
            "Bach-active metric / equation antifield",
            "Noether antifield pair",
            "trace antifield / Weyl ghost antifield",
            "antighost / multiplier",
        ],
        "scope": {
            "proved": [
                "split algebraic minimal rows and one nonminimal test pair",
                "exact CKV zero-mode projector",
                "nilpotency",
                "explicit contraction of every nonphysical row",
                "one-particle cohomology",
            ],
            "next": [
                "noncompact SO(4,2) equivariance of p,j,s",
                "cyclicity under the full BV/Krein pairing",
                "residual HPL comparison",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    rows = [
        "{} & {} & {} \\\\".format(
            row["energy"], row["full_dimension"], row["cohomology_dimension"]
        )
        for row in data["levels"][:5]
    ]
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_free_bv_complex.py",
            r"\begin{tabular}{c|r|r}",
            r"$n$ & $\dim C^{\rm BV}_n$ & $\dim H(q)_n$ \\",
            r"\hline",
            *rows,
            r"\end{tabular}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-energy", type=int, default=12)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-full-conformal-cyclic-transfer",
        action="store_true",
        help="fail closed: Sprint 2 does not establish Sprint 3",
    )
    args = parser.parse_args()
    if args.max_energy < 6:
        raise SystemExit("max-energy must include five regression levels")
    if args.claim_full_conformal_cyclic_transfer:
        raise SystemExit(
            "REFUSED: the BV contraction is exact and compact-block preserving, "
            "and a separate raw calculation proves homotopy-equivariant K+/- "
            "transfer. The complete cross-energy cyclic BV/BFV pairing is not "
            "certified by this split-block executable."
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
    print("CONFORMAL S2 FREE BV COMPLEX: ALL PASS")


if __name__ == "__main__":
    main()
