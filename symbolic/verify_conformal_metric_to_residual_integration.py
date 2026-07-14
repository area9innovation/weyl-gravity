#!/usr/bin/env python3
"""End-to-end metric-BV to centered residual-cohomology certificate.

The coefficient matrices in this executable are not the hand-specified
``E/A/L`` matrices.  They are induced by the exact raw polynomial metric BV
retraction, then coupled to the independently generated residual CE ghosts.
The result reproduces the vacuum, one-particle, and lowest two-particle
centered cohomology and its parity/Gram decomposition.
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

from bridge.residual_bfv import (
    CoefficientCEComplex,
    CoefficientModule,
    ConformalCE,
    columns_to_matrix,
    compose,
    modular_rank,
)
from bridge.transfer import (
    RawResidualModule,
    energy_two_metric_form,
    energy_two_parity,
    energy_two_symmetric_module,
    induced_on_span,
    normalized_kernel_basis,
    symmetric_square_finite_action,
    symmetric_square_form,
)


CERTIFICATE_PATH = ROOT / "bridge" / "certificates" / "metric_to_residual.json"
LATEX_PATH = ROOT / "bridge" / "generated" / "metric_to_residual.tex"


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def window(complex_: CoefficientCEComplex):
    bases = tuple(complex_.basis(number, 0) for number in (3, 4, 5))
    d3 = complex_.differential(bases[0], bases[1])
    d4 = complex_.differential(bases[1], bases[2])
    check(
        "S4-I0: transferred CE differential is exactly nilpotent",
        all(not column for column in compose(d3, d4)),
    )
    return bases, d3, d4


def certificate_data() -> dict[str, object]:
    ce = ConformalCE.build()
    ce.verify_ce(5)
    raw = RawResidualModule.build(4)
    check(
        "S4-M1: metric BV transfer supplies the 10+40+82 residual buffer",
        raw.dimensions == {2: 10, 3: 40, 4: 82},
    )

    # Vacuum row.
    vacuum_module = CoefficientModule((sp.zeros(1),) * 15, (0,))
    vacuum_bases, vacuum_d3, vacuum_d4 = window(
        CoefficientCEComplex(ce, vacuum_module)
    )
    vacuum_ranks = (
        modular_rank(vacuum_d3, len(vacuum_bases[1])),
        modular_rank(vacuum_d4, len(vacuum_bases[2])),
    )
    check(
        "S4-V1: centered vacuum H4 vanishes",
        sum(vacuum_ranks) == len(vacuum_bases[1]),
    )

    # One-particle row, with every coefficient action induced from raw
    # metric/ghost/antifield matrices.
    one_module = CoefficientModule(raw.matrices, raw.state_energies)
    one_bases, one_d3, one_d4 = window(CoefficientCEComplex(ce, one_module))
    one_ranks = (
        modular_rank(one_d3, len(one_bases[1])),
        modular_rank(one_d4, len(one_bases[2])),
    )
    check(
        "S4-O1: parity-complete transferred one-particle H4 vanishes",
        one_ranks == (520, 2102)
        and sum(one_ranks) == len(one_bases[1]),
    )

    # Lowest two-particle row.
    two_module = energy_two_symmetric_module(raw)
    two_complex = CoefficientCEComplex(ce, two_module)
    two_bases = tuple(two_complex.basis(number, 0) for number in (4, 5, 6))
    two_d4 = two_complex.differential(two_bases[0], two_bases[1])
    two_d5 = two_complex.differential(two_bases[1], two_bases[2])
    check(
        "S4-T1: transferred two-particle differential is exactly nilpotent",
        all(not column for column in compose(two_d4, two_d5)),
    )
    two_rank = modular_rank(two_d4, len(two_bases[1]))
    check(
        "S4-T2: lowest two-particle H4 has dimension exactly two",
        len(two_bases[0]) == 55 and two_rank == 53,
    )
    d4_matrix = columns_to_matrix(two_d4, len(two_bases[1]))
    kernel = sp.Matrix.hstack(*d4_matrix.nullspace())
    check("S4-T2: exact kernel basis has two columns", kernel.cols == 2)

    matter_form = symmetric_square_form(energy_two_metric_form(raw))
    normalized, raw_gram = normalized_kernel_basis(kernel, matter_form)
    ghost_norm = ce.polarized_pair(ce.lowering_ghosts, ce.lowering_ghosts)
    check(
        "S4-G1: metric matter form times canonical ghost norm gives I2",
        ghost_norm == 1
        and sp.simplify(normalized.T * matter_form * normalized) == sp.eye(2),
    )

    parity = symmetric_square_finite_action(energy_two_parity(raw))
    kernel_parity = induced_on_span(parity, kernel)
    check(
        "S4-P1: the two classes split into odd and even parity directions",
        kernel_parity == sp.diag(-1, 1),
    )

    return {
        "schema": "pure-weyl-metric-to-residual-integration-v1",
        "pipeline": [
            "raw polynomial metric BV complex",
            "exact homotopy transfer",
            "induced residual so(4,2) module",
            "independent residual CE ghosts",
            "centered absolute cohomology",
        ],
        "vacuum": {
            "cochain_dimensions": [len(value) for value in vacuum_bases],
            "ranks": list(vacuum_ranks),
            "h4": 0,
        },
        "one_particle": {
            "module_dimensions": raw.dimensions,
            "cochain_dimensions": [len(value) for value in one_bases],
            "ranks": list(one_ranks),
            "h4": 0,
        },
        "two_particle": {
            "cochain_dimensions": [len(value) for value in two_bases],
            "rank_d4": two_rank,
            "h4": 2,
            "raw_gram": [[str(value) for value in row] for row in raw_gram.tolist()],
            "normalized_gram": [[1, 0], [0, 1]],
            "parity": [-1, 1],
            "interpretation": ["Pontryagin/odd", "Weyl-square/even"],
        },
        "scope": {
            "proved": [
                "end-to-end algebraic polynomial metric-to-residual calculation",
                "strict induced residual CE differential on the physical row",
                "vacuum and one-particle vanishing",
                "two weight-four classes",
                "positive normalized representative Gram I2",
                "dynamical/topological parity split",
            ],
            "remaining": [
                "cross-energy cyclicity of the complete local BV pairing",
                "derivation of the selected closed-universe BFV polarization",
                "analytic completion and quantum anomaly questions",
            ],
        },
    }


def latex(data: dict[str, object]) -> str:
    return "\n".join(
        [
            "% Generated by symbolic/verify_conformal_metric_to_residual_integration.py",
            r"\begin{tabular}{c|rrr|r}",
            r"sector & $\dim C^3$ & $\dim C^4$ & $\dim C^5$ & $\dim H^4$ \\",
            r"\hline",
            "vacuum & {} & {} & {} & 0 \\\\".format(
                *data["vacuum"]["cochain_dimensions"]
            ),
            "one particle & {} & {} & {} & 0 \\\\".format(
                *data["one_particle"]["cochain_dimensions"]
            ),
            "two particles & {} & {} & {} & 2 \\\\".format(
                *data["two_particle"]["cochain_dimensions"]
            ),
            r"\end{tabular}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument(
        "--claim-complete-bv-bfv-pairing",
        action="store_true",
        help="fail closed: the full cross-energy BV/BFV normalization is open",
    )
    args = parser.parse_args()
    if args.claim_complete_bv_bfv_pairing:
        raise SystemExit(
            "REFUSED: the algebraic metric-to-residual cohomology is integrated, "
            "but the full cross-energy cyclic BV/BFV normalization is not derived"
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
    print("CONFORMAL METRIC-TO-RESIDUAL INTEGRATION: ALL PASS")


if __name__ == "__main__":
    main()
